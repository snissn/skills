#!/usr/bin/env python3
"""Generate a standardized TreeDB JSONBench optimization breakdown."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

Q_NAMES = ["q1", "q2", "q3", "q4", "q5"]
MIB = 1024 * 1024


def load_json(path: str | Path | None) -> Any | None:
    if not path:
        return None
    p = Path(path)
    with p.open() as f:
        return json.load(f)


def fmt_seconds(value: Any) -> str:
    if value is None or value == "":
        return ""
    try:
        s = float(value)
    except (TypeError, ValueError):
        return str(value)
    if s < 0.001:
        return f"{s * 1_000_000:.1f}us"
    if s < 1:
        return f"{s:.4f}s"
    return f"{s:.3f}s"


def fmt_int(value: Any) -> str:
    if value is None or value == "":
        return ""
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def fmt_mb(value: Any) -> str:
    if value is None or value == "":
        return ""
    b = float(value)
    return f"{b / 1_000_000:.2f}"


def fmt_mib(value: Any) -> str:
    if value is None or value == "":
        return ""
    b = float(value)
    return f"{b / MIB:.2f}"


def fmt_ratio(num: Any, den: Any) -> str:
    if num in (None, "") or den in (None, "", 0):
        return ""
    try:
        return f"{float(num) / float(den):.2f}x"
    except (TypeError, ValueError, ZeroDivisionError):
        return ""


def median_or_none(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def load_report_rows(path: str | Path) -> list[dict[str, Any]]:
    data = load_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("rows"), list):
        raise SystemExit(f"{path} is not a JSONBench report.json with rows[]")
    return data["rows"]


def group_score(key: tuple[Any, ...], rows: list[dict[str, Any]]) -> tuple[int, int, int]:
    storage_layout, data_shape, execution_mode, storage_source, scale, dataset_size = key
    score = 0
    if storage_layout == "column-store-full-prepared":
        score += 1000
    if data_shape == "full-retained-json":
        score += 500
    if execution_mode == "prepared":
        score += 100
    if storage_source == "typed_column_part":
        score += 50
    if set(r.get("query") for r in rows) >= set(Q_NAMES):
        score += 25
    try:
        row_count = int(dataset_size or 0)
    except (TypeError, ValueError):
        row_count = 0
    scale_bonus = 10 if scale == "1m" else 0
    return (score, scale_bonus, row_count)


def select_headline_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        if r.get("system") != "TreeDB" or r.get("query") not in Q_NAMES:
            continue
        key = (
            r.get("storage_layout"),
            r.get("data_shape"),
            r.get("execution_mode"),
            r.get("storage_source"),
            r.get("scale"),
            r.get("dataset_size") or r.get("row_count") or r.get("requested_rows"),
        )
        groups[key].append(r)
    if not groups:
        raise SystemExit("No TreeDB q1-q5 rows found in report")
    best_key, best_rows = max(groups.items(), key=lambda kv: group_score(kv[0], kv[1]))
    by_q = {r.get("query"): r for r in best_rows if r.get("query") in Q_NAMES}
    return {q: by_q[q] for q in Q_NAMES if q in by_q}


def find_matching_result(report_path: str | Path, headline: dict[str, dict[str, Any]]) -> Path | None:
    first = next(iter(headline.values()), None)
    if not first:
        return None
    source = first.get("source")
    if source and Path(source).is_file():
        return Path(source)
    root = Path(report_path).parent
    for p in root.glob("**/result.json"):
        try:
            data = load_json(p)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        if data.get("storage_layout") == first.get("storage_layout") and (
            data.get("dataset_size") == first.get("dataset_size")
            or data.get("scale") == first.get("scale")
        ):
            return p
    return None


def result_categories(result: dict[str, Any] | None) -> dict[str, int]:
    if not isinstance(result, dict):
        return {}
    storage = result.get("storage") or {}
    cats = storage.get("categories") if isinstance(storage, dict) else None
    out: dict[str, int] = {}
    if isinstance(cats, list):
        for c in cats:
            if isinstance(c, dict):
                name = c.get("category")
                if name:
                    out[str(name)] = int(c.get("bytes") or 0)
    return out


def extract_result_hashes(result_path: str | Path | None) -> dict[str, str]:
    if not result_path or not Path(result_path).is_file():
        return {}
    try:
        data = load_json(result_path)
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    hashes: dict[str, str] = {}
    for q in data.get("queries") or []:
        if isinstance(q, dict) and q.get("name") and q.get("result_hash"):
            hashes[str(q["name"])] = str(q["result_hash"])
    return hashes


def parse_parity_report(path: str | Path | None) -> dict[str, dict[str, Any]]:
    if not path:
        return {}
    rows = load_report_rows(path)
    selected: dict[str, dict[str, Any]] = {q: {} for q in Q_NAMES}
    source_hash_cache: dict[str, dict[str, str]] = {}
    for r in rows:
        q = r.get("query")
        if q not in selected:
            continue
        mode = r.get("execution_mode")
        layout = r.get("storage_layout")
        label = None
        if mode == "row_scan" or layout == "row":
            label = "row_scan"
        elif layout == "column-store-full" and mode == "direct":
            label = "full_direct"
        elif layout == "column-store-full-prepared" and mode == "prepared":
            label = "full_prepared"
        if not label:
            continue
        selected[q][label] = r
        src = r.get("source")
        if src and src not in source_hash_cache:
            source_hash_cache[src] = extract_result_hashes(src)
        if src:
            selected[q][label + "_hash"] = source_hash_cache.get(src, {}).get(q)
    for q, v in selected.items():
        hashes = [v.get(k) for k in ("row_scan_hash", "full_direct_hash", "full_prepared_hash")]
        present = [h for h in hashes if h]
        v["hash_parity"] = bool(len(present) >= 2 and len(set(present)) == 1)
    return selected


def parse_clickhouse(path: str | Path | None) -> dict[str, Any]:
    data = load_json(path) if path else None
    if not isinstance(data, dict):
        return {}
    timings: dict[str, dict[str, Any]] = {}
    for idx, attempts in enumerate(data.get("result") or [], start=1):
        vals = [float(x) for x in attempts]
        timings[f"q{idx}"] = {
            "attempts": vals,
            "best": min(vals) if vals else None,
            "median": median_or_none(vals),
        }
    return {"raw": data, "timings": timings}


def parse_colgranule(path: str | Path | None) -> dict[str, Any]:
    data = load_json(path) if path else None
    if not isinstance(data, dict):
        return {}
    timings: dict[str, dict[str, Any]] = {}
    for row in data.get("query_timings") or []:
        name = str(row.get("query", "")).lower()
        if name in Q_NAMES:
            best_ns = row.get("best")
            attempts_ns = row.get("attempts") or []
            timings[name] = {
                "best": (float(best_ns) / 1_000_000_000) if best_ns is not None else None,
                "attempts": [float(x) / 1_000_000_000 for x in attempts_ns],
            }
    return {"raw": data, "timings": timings}


def parse_compression_audit(path: str | Path | None) -> dict[str, Any]:
    data = load_json(path) if path else None
    return data if isinstance(data, dict) else {}


def bool_label(value: Any) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def first_non_empty(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def audit_values_cell(fields: Any, limit: int = 3) -> str:
    if not isinstance(fields, list):
        return ""
    values: list[str] = []
    seen: set[str] = set()
    for field in fields:
        if not isinstance(field, dict):
            continue
        value = field.get("value")
        if value in (None, ""):
            continue
        text = str(value)
        if text in seen:
            continue
        values.append(text)
        seen.add(text)
        if len(values) >= limit:
            break
    return ", ".join(values)


def compression_final_status(audit: dict[str, Any]) -> str:
    if not audit:
        return "non-final: compression audit missing"
    issues: list[str] = []
    result_compression = audit.get("result_compression_summary") or {}
    retained_status = audit.get("retained_payload_status_audit") or {}
    retained_audit = audit.get("retained_payload_audit") or {}
    column_audit = audit.get("column_section_audit") or {}
    frame = audit.get("vlog_frame_audit") or {}
    value_vlog = frame.get("value_vlog") or {}

    if result_compression.get("silent_none_suspected"):
        issues.append("silent requested/actual none suspected")
    if retained_status.get("retained_payload_encoding_status_missing"):
        issues.append("retained encoding status missing")
    if retained_status.get("retained_payload_encoding_inactive"):
        issues.append("retained encoding inactive")
    if retained_status.get("retained_payload_compression_status_missing"):
        issues.append("retained compression status missing")
    if retained_status.get("retained_payload_compression_inactive"):
        issues.append("retained compression inactive")
    if retained_audit.get("required_for_final_claim") and retained_audit.get("status") != "passed":
        issues.append("path-aware retained audit not passed")
    if column_audit.get("status") == "filesystem_oracle_only":
        issues.append("column section audit is filesystem-only")

    raw_fraction = value_vlog.get("raw_mode_payload_fraction")
    if isinstance(raw_fraction, (int, float)) and raw_fraction > 0.01:
        issues.append("value_vlog raw-mode payload above budget")

    if not issues:
        return "pass"
    shown = "; ".join(issues[:6])
    if len(issues) > 6:
        shown += f"; +{len(issues) - 6} more"
    return f"non-final: {shown}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--treedb-report", required=True, help="Production TreeDB JSONBench report.json")
    ap.add_argument("--treedb-result", help="Matching TreeDB cell result.json; inferred from report source when omitted")
    ap.add_argument("--parity-report", help="Optional row/direct/prepared parity report.json")
    ap.add_argument("--clickhouse-result", help="Optional ClickHouse JSONBench result JSON")
    ap.add_argument("--clickhouse-fresh", action="store_true", help="Mark ClickHouse result as freshly rerun for this comparison")
    ap.add_argument("--colgranule-raw", help="Optional experiments/colgranule/JSONBENCH_COMPARISON_RAW.json")
    ap.add_argument("--compression-audit", help="Optional compression_audit.json from scripts/treedb_jsonbench_storage_audit.py")
    ap.add_argument("--gomap-head", default="unknown")
    ap.add_argument("--jsonbench-head", default="unknown")
    ap.add_argument("--title", default="TreeDB JSONBench Breakdown")
    args = ap.parse_args()

    report_rows = load_report_rows(args.treedb_report)
    headline = select_headline_rows(report_rows)
    first = next(iter(headline.values()))

    result_path = Path(args.treedb_result) if args.treedb_result else find_matching_result(args.treedb_report, headline)
    result = load_json(result_path) if result_path else None
    categories = result_categories(result)
    parity = parse_parity_report(args.parity_report)
    clickhouse = parse_clickhouse(args.clickhouse_result)
    colgranule = parse_colgranule(args.colgranule_raw)
    compression_audit = parse_compression_audit(args.compression_audit)
    retained_status_audit = compression_audit.get("retained_payload_status_audit") if compression_audit else {}
    if not isinstance(retained_status_audit, dict):
        retained_status_audit = {}

    ch_raw = clickhouse.get("raw", {})
    ch_timings = clickhouse.get("timings", {})
    col_timings = colgranule.get("timings", {})

    storage_total = first.get("storage_bytes") or (result or {}).get("storage", {}).get("total_bytes") if isinstance(result, dict) else first.get("storage_bytes")
    storage_durable = first.get("storage_durable_bytes_wal_excluded")
    storage_wal_excluded = first.get("storage_wal_bytes_excluded_from_durable_storage")
    click_total = ch_raw.get("total_size") if isinstance(ch_raw, dict) else None

    reconstruction = (result or {}).get("reconstruction") if isinstance(result, dict) else None
    reconstruction_valid = None
    if isinstance(reconstruction, dict):
        reconstruction_valid = reconstruction.get("valid")
    if reconstruction_valid is None:
        reconstruction_valid = first.get("reconstruction_valid") or first.get("reconstruction_status")

    print(f"# {args.title}\n")
    print("## Evidence\n")
    print(f"- TreeDB report: `{args.treedb_report}`")
    print(f"- TreeDB result: `{result_path}`" if result_path else "- TreeDB result: `n/a`")
    print(f"- parity report: `{args.parity_report}`" if args.parity_report else "- parity report: `n/a`")
    if args.clickhouse_result:
        freshness = "fresh run" if args.clickhouse_fresh else "reference only / freshness not asserted"
        print(f"- ClickHouse result: `{args.clickhouse_result}` ({freshness})")
    else:
        print("- ClickHouse result: `n/a`")
    print(f"- colgranule raw: `{args.colgranule_raw}` (historical/prototype only)" if args.colgranule_raw else "- colgranule raw: `n/a`")
    print(f"- compression audit: `{args.compression_audit}`" if args.compression_audit else "- compression audit: `n/a`")
    print(f"- gomap head: `{args.gomap_head}`")
    print(f"- JSONBench head: `{args.jsonbench_head}`\n")

    print("## Headline TreeDB Row\n")
    fields = [
        ("scale", first.get("scale") or first.get("dataset_size")),
        ("requested rows", fmt_int(first.get("requested_rows") or first.get("dataset_size"))),
        ("data shape", first.get("data_shape")),
        ("layout", first.get("storage_layout")),
        ("execution", first.get("execution_mode")),
        ("storage source", first.get("storage_source")),
        ("typed column owner", first.get("typed_column_owner")),
        ("retained payload", first.get("retained_payload_policy")),
        (
            "retained payload encoding",
            first_non_empty(
                first.get("retained_payload_encoding"),
                first.get("retained_payload_encoding_policy"),
                audit_values_cell(retained_status_audit.get("retained_payload_encoding_fields")),
            ),
        ),
        (
            "retained payload encoding status",
            first_non_empty(
                first.get("retained_payload_encoding_status"),
                audit_values_cell(retained_status_audit.get("retained_payload_encoding_status_fields")),
            ),
        ),
        (
            "retained payload compression",
            first_non_empty(
                first.get("retained_payload_compression"),
                first.get("retained_payload_compression_policy"),
                audit_values_cell(retained_status_audit.get("retained_payload_compression_fields")),
            ),
        ),
        (
            "retained payload compression status",
            first_non_empty(
                first.get("retained_payload_compression_status"),
                audit_values_cell(retained_status_audit.get("retained_payload_compression_status_fields")),
            ),
        ),
        (
            "typed column compression",
            first_non_empty(
                first.get("typed_column_compression"),
                first.get("typed_column_compression_policy"),
                first.get("compression_policy_label"),
            ),
        ),
        ("fallback", first.get("fallback_reason")),
        ("document scan fallback", bool_label(first.get("document_scan_fallback"))),
        ("reconstruction", bool_label(reconstruction_valid)),
        ("storage phase", first.get("storage_measurement_phase")),
    ]
    print("| field | value |")
    print("|---|---|")
    for k, v in fields:
        if v is None:
            v = "unknown"
        print(f"| {k} | `{v}` |")
    print()

    print("## Storage\n")
    print("| system/basis | bytes | decimal MB | MiB | notes |")
    print("|---|---:|---:|---:|---|")
    storage_rows = [
        ("TreeDB total", storage_total, "includes WAL if present"),
        ("TreeDB durable excluding WAL", storage_durable, "comparison target"),
        ("TreeDB WAL excluded", storage_wal_excluded, "command WAL bytes removed from durable comparison"),
    ]
    if isinstance(ch_raw, dict) and ch_raw:
        storage_rows.extend([
            ("ClickHouse total", ch_raw.get("total_size"), "fresh" if args.clickhouse_fresh else "reference/freshness not asserted"),
            ("ClickHouse data", ch_raw.get("data_size"), ""),
            ("ClickHouse index", ch_raw.get("index_size"), ""),
        ])
    for name, b, note in storage_rows:
        print(f"| {name} | {fmt_int(b)} | {fmt_mb(b)} | {fmt_mib(b)} | {note} |")
    if storage_durable and click_total:
        print(f"\nTreeDB durable-excluding-WAL / ClickHouse total: **{fmt_ratio(storage_durable, click_total)}**.\n")
    else:
        print()

    print("### TreeDB storage category breakdown\n")
    if not categories:
        # Fall back to report row fields.
        categories = {
            "leaf_vlog": int(first.get("storage_leaf_vlog_bytes") or 0),
            "column_asset_segments": int(first.get("storage_column_asset_bytes") or 0),
            "typed_column_part_sections": int(first.get("storage_typed_column_part_bytes") or 0),
            "primary_index": int(first.get("storage_primary_index_bytes") or 0),
            "wal": int(first.get("storage_wal_bytes") or 0),
        }
    print("| category | bytes | decimal MB | MiB |")
    print("|---|---:|---:|---:|")
    for name, b in sorted(categories.items(), key=lambda kv: kv[1], reverse=True):
        print(f"| {name} | {fmt_int(b)} | {fmt_mb(b)} | {fmt_mib(b)} |")
    print()

    print("## q1-q5 timings\n")
    print("| query | TreeDB production full-prepared | TreeDB direct (parity artifact) | colgranule historical kernel | ClickHouse | TreeDB/ClickHouse | notes |")
    print("|---|---:|---:|---:|---:|---:|---|")
    for q in Q_NAMES:
        tr = headline.get(q, {})
        tbest = tr.get("best_seconds")
        direct_best = None
        direct_cell = ""
        if q in parity and parity[q].get("full_direct"):
            direct_row = parity[q]["full_direct"]
            direct_best = direct_row.get("best_seconds")
            direct_cell = fmt_seconds(direct_best)
            direct_rows = direct_row.get("dataset_size") or direct_row.get("row_count") or direct_row.get("requested_rows")
            headline_rows = first.get("dataset_size") or first.get("row_count") or first.get("requested_rows")
            if direct_cell and direct_rows and headline_rows and direct_rows != headline_rows:
                direct_cell += f" ({fmt_int(direct_rows)} rows)"
        cgbest = col_timings.get(q, {}).get("best") if isinstance(col_timings, dict) else None
        chbest = ch_timings.get(q, {}).get("best") if isinstance(ch_timings, dict) else None
        notes = []
        if tr.get("rows_scanned") is not None:
            notes.append(f"TreeDB scanned {fmt_int(tr.get('rows_scanned'))}")
        if tr.get("fallback_reason") is not None:
            notes.append(f"fallback={tr.get('fallback_reason')}")
        print(
            f"| {q} | {fmt_seconds(tbest)} | {direct_cell} | "
            f"{fmt_seconds(cgbest)} | {fmt_seconds(chbest)} | {fmt_ratio(tbest, chbest)} | {'; '.join(notes)} |"
        )
    print()

    if parity:
        print("## Row/direct/prepared parity\n")
        print("Parity timings are from the parity artifact and may be a smaller scale than the headline run.\n")
        print("| query | row scan | full direct | full prepared | hash parity |")
        print("|---|---:|---:|---:|---|")
        for q in Q_NAMES:
            v = parity.get(q, {})
            row = v.get("row_scan", {}).get("best_seconds") if isinstance(v.get("row_scan"), dict) else None
            direct = v.get("full_direct", {}).get("best_seconds") if isinstance(v.get("full_direct"), dict) else None
            prepared = v.get("full_prepared", {}).get("best_seconds") if isinstance(v.get("full_prepared"), dict) else None
            parity_label = "true" if v.get("hash_parity") else "unknown/false"
            print(f"| {q} | {fmt_seconds(row)} | {fmt_seconds(direct)} | {fmt_seconds(prepared)} | {parity_label} |")
        print()

    print("## Correctness and fallback gates\n")
    all_q = all(q in headline for q in Q_NAMES)
    same_sources = {headline[q].get("source") for q in headline if headline[q].get("source")}
    same_db = "yes" if len(same_sources) <= 1 and all_q else "unknown"
    print(f"- q1-q5 present: `{bool_label(all_q)}`")
    print(f"- q1-q5 same loaded DB/source: `{same_db}`")
    print(f"- reconstruction valid: `{bool_label(reconstruction_valid)}`")
    print(f"- fallback reason: `{first.get('fallback_reason')}`")
    print(f"- document scan fallback: `{bool_label(first.get('document_scan_fallback'))}`")
    if isinstance(reconstruction, dict):
        print(f"- reconstruction source hash: `{reconstruction.get('source_canonical_json_hash')}`")
        print(f"- reconstruction stored hash: `{reconstruction.get('stored_canonical_json_hash')}`")
    print()

    print("## Compression and storage audit gates\n")
    if not compression_audit:
        print("- compression audit: `missing`")
        print("- final storage-compression claim: `non-final until gzip/vlog/column/retained audits are attached`\n")
    else:
        frame = compression_audit.get("vlog_frame_audit") or {}
        gzip_oracle = compression_audit.get("gzip_oracle") or {}
        column_audit = compression_audit.get("column_section_audit") or {}
        retained_audit = compression_audit.get("retained_payload_audit") or {}
        retained_status = compression_audit.get("retained_payload_status_audit") or {}
        result_compression = compression_audit.get("result_compression_summary") or {}

        print(f"- final storage-compression claim: `{compression_final_status(compression_audit)}`")
        if result_compression:
            print(f"- result compression summary source: `{result_compression.get('path')}`")
            print(f"- silent requested/actual none suspected: `{bool_label(result_compression.get('silent_none_suspected'))}`")
        print(f"- retained payload status audit status: `{retained_status.get('status', 'result_json_status_fields_only')}`")
        print(f"- retained encoding status missing: `{bool_label(retained_status.get('retained_payload_encoding_status_missing'))}`")
        print(f"- retained encoding inactive: `{bool_label(retained_status.get('retained_payload_encoding_inactive'))}`")
        print(f"- retained compression status missing: `{bool_label(retained_status.get('retained_payload_compression_status_missing'))}`")
        print(f"- retained compression inactive: `{bool_label(retained_status.get('retained_payload_compression_inactive'))}`")
        print(f"- retained payload audit status: `{retained_audit.get('status', 'unknown')}`")
        print(f"- retained audit required for final claim: `{bool_label(retained_audit.get('required_for_final_claim'))}`")
        print(f"- column section audit status: `{column_audit.get('status', 'unknown')}`")
        if column_audit.get("reason"):
            print(f"- column section audit reason: {column_audit.get('reason')}")
        if column_audit.get("total_bytes") is not None:
            column_ratio = column_audit.get("gzip_to_raw_ratio")
            column_ratio_cell = f"{column_ratio:.3f}" if isinstance(column_ratio, (int, float)) else "unknown"
            print(f"- column assets gzip headroom: `{fmt_int(column_audit.get('total_bytes'))}` raw -> `{fmt_int(column_audit.get('gzip_bytes'))}` gzip ({column_ratio_cell})")

        print("\n### gzip oracle\n")
        print("| subtree | files | raw bytes | gzip bytes | gzip/raw |")
        print("|---|---:|---:|---:|---:|")
        for row in gzip_oracle.get("subtrees") or []:
            ratio = row.get("gzip_to_raw_ratio")
            ratio_cell = f"{ratio:.3f}" if isinstance(ratio, (int, float)) else ""
            print(f"| `{row.get('subtree')}` | {fmt_int(row.get('files'))} | {fmt_int(row.get('raw_bytes'))} | {fmt_int(row.get('gzip_bytes'))} | {ratio_cell} |")

        print("\n### vlog frame audit\n")
        print("| log | records | raw payload | stored payload | raw-mode bytes | raw-mode fraction | stored/raw |")
        print("|---|---:|---:|---:|---:|---:|---:|")
        for name in ("leaf_vlog", "value_vlog"):
            row = frame.get(name) or {}
            raw_fraction = row.get("raw_mode_payload_fraction")
            stored_ratio = row.get("stored_to_raw_ratio")
            raw_fraction_cell = f"{raw_fraction:.3f}" if isinstance(raw_fraction, (int, float)) else ""
            stored_ratio_cell = f"{stored_ratio:.3f}" if isinstance(stored_ratio, (int, float)) else ""
            print(
                f"| `{name}` | {fmt_int(row.get('records'))} | {fmt_int(row.get('raw_payload_bytes'))} | "
                f"{fmt_int(row.get('stored_payload_bytes'))} | {fmt_int(row.get('raw_mode_payload_bytes'))} | "
                f"{raw_fraction_cell} | {stored_ratio_cell} |"
            )
        print()

    print("## Optimization targets\n")
    durable_categories = {k: v for k, v in categories.items() if k != "wal" and v}
    print("\nStorage priorities:")
    for i, (name, b) in enumerate(sorted(durable_categories.items(), key=lambda kv: kv[1], reverse=True)[:5], start=1):
        print(f"{i}. `{name}` — {fmt_int(b)} bytes ({fmt_mib(b)} MiB)")
    print("\nQuery priorities:")
    slow = []
    for q in Q_NAMES:
        b = headline.get(q, {}).get("best_seconds")
        if b is not None:
            slow.append((q, float(b)))
    for i, (q, s) in enumerate(sorted(slow, key=lambda kv: kv[1], reverse=True), start=1):
        print(f"{i}. `{q}` — {fmt_seconds(s)}")
    print("\nCaveats:")
    print("- Optimize storage against durable excluding WAL unless the task explicitly targets WAL volume.")
    if args.clickhouse_result and not args.clickhouse_fresh:
        print("- ClickHouse numbers are reference artifacts; do not claim a fresh latest-head comparison.")
    if args.colgranule_raw:
        print("- colgranule numbers are historical/prototype kernel context, not production TreeDB evidence.")
    print("- Keep direct, prepared, row-scan, and metadata-only rows separately labeled.")


if __name__ == "__main__":
    main()
