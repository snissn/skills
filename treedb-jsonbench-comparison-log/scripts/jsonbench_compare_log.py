#!/usr/bin/env python3
"""Generate a concise TreeDB JSONBench comparison log.

The report intentionally uses TreeDB durable bytes excluding only command WAL.
Persistent `leaf_vlog/` and `value_vlog/` bytes remain counted.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

QUERIES = ["q1", "q2", "q3", "q4", "q5"]


def load_json(path: Optional[str]) -> Optional[dict]:
    if not path:
        return None
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_audit(path: Optional[str]) -> Optional[dict]:
    data = load_json(path)
    return data if isinstance(data, dict) else None


def fmt_bytes(n: Optional[float]) -> str:
    if n is None:
        return ""
    return f"{int(n):,}"


def fmt_mb(n: Optional[float]) -> str:
    if n is None:
        return ""
    return f"{n / 1_000_000:.2f} MB"


def fmt_time(s: Optional[float]) -> str:
    if s is None:
        return ""
    if s < 0.01:
        return f"{s:.4f}s"
    if s < 1:
        return f"{s:.3f}s"
    return f"{s:.3f}s"


def fmt_rate(rows: Optional[float], seconds: Optional[float]) -> str:
    if not rows or not seconds or seconds <= 0:
        return ""
    r = rows / seconds
    if r >= 1_000_000:
        return f"{r / 1_000_000:.2f}M rows/s"
    if r >= 1_000:
        return f"{r / 1_000:.1f}k rows/s"
    return f"{r:.1f} rows/s"


def fmt_ratio(x: Optional[float]) -> str:
    if x is None or not math.isfinite(x):
        return ""
    return f"{x:.2f}x"


def fmt_bool(value: Any) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def compression_final_status(audit: Optional[dict]) -> str:
    if not audit:
        return "non-final: audit missing"
    issues: List[str] = []
    result_compression = audit.get("result_compression_summary") or {}
    retained_status = audit.get("retained_payload_status_audit") or {}
    retained_audit = audit.get("retained_payload_audit") or {}
    column_audit = audit.get("column_section_audit") or {}
    frame = audit.get("vlog_frame_audit") or {}
    value_vlog = frame.get("value_vlog") or {}

    if result_compression.get("silent_none_suspected"):
        issues.append("silent none")
    if retained_status.get("retained_payload_encoding_status_missing"):
        issues.append("encoding status missing")
    if retained_status.get("retained_payload_encoding_inactive"):
        issues.append("encoding inactive")
    if retained_status.get("retained_payload_compression_status_missing"):
        issues.append("compression status missing")
    if retained_status.get("retained_payload_compression_inactive"):
        issues.append("compression inactive")
    if retained_audit.get("required_for_final_claim") and retained_audit.get("status") != "passed":
        issues.append("path audit not passed")
    if column_audit.get("status") == "filesystem_oracle_only":
        issues.append("column audit filesystem-only")
    raw_fraction = value_vlog.get("raw_mode_payload_fraction")
    if isinstance(raw_fraction, (int, float)) and raw_fraction > 0.01:
        issues.append("value_vlog raw payload")

    if not issues:
        return "pass"
    shown = "; ".join(issues[:4])
    if len(issues) > 4:
        shown += f"; +{len(issues) - 4}"
    return f"non-final: {shown}"


def scale_label(rows: Optional[int], fallback: str) -> str:
    if rows is None:
        return fallback
    if rows >= 9_000_000:
        return "10M"
    if rows >= 900_000:
        return "1M"
    return f"{rows:,} rows"


def best_from_attempts(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, list):
        vals: List[float] = []
        for v in value:
            if isinstance(v, list):
                vals.extend(float(x) for x in v if isinstance(x, (int, float)))
            elif isinstance(v, (int, float)):
                vals.append(float(v))
        if vals:
            return min(vals)
    return None


def parse_treedb_report(path: Optional[str], label: str, caveat: str = "") -> Optional[dict]:
    data = load_json(path)
    if not data:
        return None
    rows = data.get("rows") or []
    if not rows:
        raise ValueError(f"{path}: expected report JSON with rows[]")
    first = rows[0]
    requested = first.get("requested_rows") or first.get("rows_scanned")
    try:
        requested = int(requested) if requested is not None else None
    except Exception:
        requested = None
    times: Dict[str, float] = {}
    scanned: Dict[str, int] = {}
    for r in rows:
        q = str(r.get("query", "")).lower()
        if q in QUERIES:
            t = r.get("best_seconds") or r.get("seconds") or r.get("time_seconds")
            if t is not None:
                times[q] = float(t)
            rs = r.get("rows_scanned") or requested
            if rs is not None:
                scanned[q] = int(rs)
    size = first.get("storage_durable_bytes_wal_excluded")
    if size is None:
        size = first.get("durable_storage_bytes_wal_excluded")
    if size is None:
        raise ValueError(f"{path}: missing TreeDB durable WAL-excluded storage field")
    return {
        "kind": "treedb",
        "name": "TreeDB production" if label == "1M" else "TreeDB",
        "scale": label or scale_label(requested, "TreeDB"),
        "rows": requested,
        "size_bytes": int(size),
        "total_bytes": first.get("storage_bytes"),
        "wal_bytes": first.get("storage_wal_bytes"),
        "phase": first.get("storage_measurement_phase") or first.get("measurement_phase"),
        "fallback": first.get("fallback_reason"),
        "document_scan_fallback": first.get("document_scan_fallback"),
        "reconstruction": first.get("reconstruction_valid"),
        "times": times,
        "rows_by_query": scanned,
        "path": path,
        "caveat": caveat,
    }


def parse_treedb_result(path: Optional[str], label: str, caveat: str = "") -> Optional[dict]:
    data = load_json(path)
    if not data:
        return None
    storage = data.get("storage") or {}
    queries = data.get("queries") or []
    reconstruction = data.get("reconstruction") or {}
    rows = (
        data.get("requested_rows")
        or data.get("rows")
        or reconstruction.get("rows")
        or max((q.get("rows_scanned") or 0 for q in queries if isinstance(q, dict)), default=0)
    )
    try:
        rows = int(rows) if rows is not None else None
    except Exception:
        rows = None

    times: Dict[str, float] = {}
    scanned: Dict[str, int] = {}
    for qrow in queries:
        if not isinstance(qrow, dict):
            continue
        q = str(qrow.get("name") or qrow.get("query") or "").lower()
        if q not in QUERIES:
            continue
        t = qrow.get("best_seconds") or qrow.get("seconds") or qrow.get("time_seconds")
        if t is not None:
            times[q] = float(t)
        rs = qrow.get("rows_scanned") or rows
        if rs is not None:
            scanned[q] = int(rs)

    size = storage.get("durable_storage_bytes_wal_excluded")
    if size is None:
        size = storage.get("storage_durable_bytes_wal_excluded")
    if size is None:
        raise ValueError(f"{path}: missing TreeDB durable WAL-excluded storage field")

    return {
        "kind": "treedb",
        "name": "TreeDB production" if label == "1M" else "TreeDB",
        "scale": label or scale_label(rows, "TreeDB"),
        "rows": rows,
        "size_bytes": int(size),
        "total_bytes": storage.get("total_bytes") or storage.get("storage_bytes"),
        "wal_bytes": storage.get("wal_bytes_excluded_from_durable_storage") or storage.get("storage_wal_bytes"),
        "phase": storage.get("measurement_phase") or storage.get("storage_measurement_phase"),
        "fallback": data.get("fallback_reason"),
        "document_scan_fallback": data.get("document_scan_fallback"),
        "reconstruction": reconstruction.get("valid") if reconstruction else data.get("reconstruction_valid"),
        "times": times,
        "rows_by_query": scanned,
        "path": path,
        "caveat": caveat,
    }


def attach_audit(record: Optional[dict], audit_path: Optional[str]) -> Optional[dict]:
    if not record:
        return record
    audit = load_audit(audit_path)
    if audit:
        record["audit_path"] = audit_path
        record["audit"] = audit
    return record


def parse_clickhouse(path: Optional[str], label: str, name: str) -> Optional[dict]:
    data = load_json(path)
    if not data:
        return None
    rows = data.get("dataset_size") or data.get("num_loaded_documents") or data.get("requested_rows")
    rows = int(rows) if rows is not None else None
    result = data.get("result") or []
    times: Dict[str, float] = {}
    for q, attempts in zip(QUERIES, result):
        best = best_from_attempts(attempts)
        if best is not None:
            times[q] = best
    return {
        "kind": "clickhouse",
        "name": name,
        "scale": label or scale_label(rows, "ClickHouse"),
        "rows": rows,
        "size_bytes": int(data["total_size"]) if data.get("total_size") is not None else None,
        "data_size": data.get("data_size"),
        "index_size": data.get("index_size"),
        "times": times,
        "rows_by_query": {q: rows for q in times if rows is not None},
        "path": path,
        "caveat": "prior/supplied ClickHouse artifact; not fresh unless just rerun",
    }


def parse_colgranule(path: Optional[str]) -> Optional[dict]:
    data = load_json(path)
    if not data:
        return None
    rows = int(data.get("rows") or data.get("limit") or 0) or None
    remaining = data.get("remaining_treedb_template_v1", {}).get("after_compact_bytes")
    derived = sum(int(c.get("stored_bytes", 0)) for c in data.get("best_column_storage", []))
    size = int(remaining + derived) if remaining is not None else None
    times: Dict[str, float] = {}
    for item in data.get("query_timings", []):
        q = str(item.get("query", "")).lower()
        if q in QUERIES and item.get("best") is not None:
            # colgranule stores nanoseconds.
            times[q] = float(item["best"]) / 1_000_000_000
    return {
        "kind": "colgranule",
        "name": "colgranule prototype retained",
        "scale": scale_label(rows, "colgranule"),
        "rows": rows,
        "size_bytes": size,
        "remaining_template_v1_bytes": remaining,
        "derived_column_bytes": derived,
        "times": times,
        "rows_by_query": {q: rows for q in times if rows is not None},
        "path": path,
        "caveat": "historical prototype/kernel artifact, not production TreeDB",
    }


def record_for(records: Iterable[dict], scale: str, kind: str) -> Optional[dict]:
    for r in records:
        if r.get("scale") == scale and r.get("kind") == kind:
            return r
    return None


def emit_markdown(records: List[dict], args: argparse.Namespace) -> str:
    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: List[str] = []
    lines.append("# TreeDB JSONBench Size and Throughput Comparison")
    lines.append("")
    lines.append(f"Generated: `{now}`")
    lines.append("")
    lines.append("## Storage basis")
    lines.append("")
    lines.append("TreeDB size is **durable bytes excluding only command WAL**. `leaf_vlog/`, `value_vlog/`, `index.db`, column assets / typed-column parts, manifests and control metadata remain counted. Do not treat `leaf_vlog/value-l255-*.log` as WAL.")
    lines.append("")

    lines.append("## Size comparison")
    lines.append("")
    lines.append("| scale | system | compared bytes | decimal size | TreeDB / system | notes |")
    lines.append("|---|---|---:|---:|---:|---|")
    for scale in sorted({r["scale"] for r in records}, key=lambda x: ("10" in x, x)):
        tree = record_for(records, scale, "treedb")
        for r in [x for x in records if x["scale"] == scale]:
            ratio = "1.00x" if r["kind"] == "treedb" else fmt_ratio((tree or {}).get("size_bytes") / r["size_bytes"] if tree and r.get("size_bytes") else None)
            note_bits = []
            if r["kind"] == "treedb":
                note_bits.append("durable excluding command WAL")
                if r.get("phase"):
                    note_bits.append(f"phase={r['phase']}")
                if r.get("wal_bytes") is not None:
                    note_bits.append(f"WAL excluded={fmt_mb(float(r['wal_bytes']))}")
                if r.get("audit_path"):
                    note_bits.append("compression audit attached")
                else:
                    note_bits.append("compression audit missing/non-final")
            if r.get("caveat"):
                note_bits.append(str(r["caveat"]))
            lines.append(f"| {scale} | {r['name']} | {fmt_bytes(r.get('size_bytes'))} | {fmt_mb(r.get('size_bytes'))} | {ratio} | {'; '.join(note_bits)} |")
    lines.append("")

    tree_records = [r for r in records if r.get("kind") == "treedb"]
    if tree_records:
        lines.append("## Compression audit gates")
        lines.append("")
        lines.append("| scale | final claim | audit | value_vlog raw-mode bytes | value_vlog raw fraction | leaf_vlog raw-mode bytes | retained encoding inactive | retained compression inactive | retained path audit | column audit |")
        lines.append("|---|---|---|---:|---:|---:|---|---|---|---|")
        for r in tree_records:
            audit = r.get("audit") or {}
            frame = audit.get("vlog_frame_audit") or {}
            value = frame.get("value_vlog") or {}
            leaf = frame.get("leaf_vlog") or {}
            retained = audit.get("retained_payload_audit") or {}
            retained_status = audit.get("retained_payload_status_audit") or {}
            column = audit.get("column_section_audit") or {}
            raw_fraction = value.get("raw_mode_payload_fraction")
            raw_fraction_cell = f"{raw_fraction:.3f}" if isinstance(raw_fraction, (int, float)) else ""
            lines.append(
                f"| {r['scale']} | `{compression_final_status(audit)}` | `{r.get('audit_path') or 'missing'}` | "
                f"{fmt_bytes(value.get('raw_mode_payload_bytes'))} | {raw_fraction_cell} | "
                f"{fmt_bytes(leaf.get('raw_mode_payload_bytes'))} | "
                f"`{fmt_bool(retained_status.get('retained_payload_encoding_inactive'))}` | "
                f"`{fmt_bool(retained_status.get('retained_payload_compression_inactive'))}` | "
                f"`{retained.get('status', 'missing')}` | `{column.get('status', 'missing')}` |"
            )
        lines.append("")

    lines.append("## Query times")
    lines.append("")
    lines.append("| scale | query | TreeDB | ClickHouse | TreeDB/ClickHouse time | colgranule | TreeDB/colgranule time |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for scale in sorted({r["scale"] for r in records}, key=lambda x: ("10" in x, x)):
        tree = record_for(records, scale, "treedb")
        click = record_for(records, scale, "clickhouse")
        col = record_for(records, scale, "colgranule")
        for q in QUERIES:
            tt = (tree or {}).get("times", {}).get(q)
            ct = (click or {}).get("times", {}).get(q)
            gt = (col or {}).get("times", {}).get(q)
            lines.append(
                f"| {scale} | {q} | {fmt_time(tt)} | {fmt_time(ct)} | {fmt_ratio(tt / ct if tt and ct else None)} | {fmt_time(gt)} | {fmt_ratio(tt / gt if tt and gt else None)} |"
            )
    lines.append("")

    lines.append("## Query throughput")
    lines.append("")
    lines.append("Rows/sec is derived as rows scanned divided by best query time. Time ratios are the inverse of throughput ratios.")
    lines.append("")
    lines.append("| scale | query | TreeDB throughput | ClickHouse throughput | colgranule throughput |")
    lines.append("|---|---|---:|---:|---:|")
    for scale in sorted({r["scale"] for r in records}, key=lambda x: ("10" in x, x)):
        tree = record_for(records, scale, "treedb")
        click = record_for(records, scale, "clickhouse")
        col = record_for(records, scale, "colgranule")
        for q in QUERIES:
            lines.append(
                f"| {scale} | {q} | "
                f"{fmt_rate((tree or {}).get('rows_by_query', {}).get(q) or (tree or {}).get('rows'), (tree or {}).get('times', {}).get(q))} | "
                f"{fmt_rate((click or {}).get('rows_by_query', {}).get(q) or (click or {}).get('rows'), (click or {}).get('times', {}).get(q))} | "
                f"{fmt_rate((col or {}).get('rows_by_query', {}).get(q) or (col or {}).get('rows'), (col or {}).get('times', {}).get(q))} |"
            )
    lines.append("")

    lines.append("## Inputs")
    lines.append("")
    for r in records:
        lines.append(f"- {r['scale']} {r['name']}: `{r.get('path')}`")
    lines.append("")

    if not args.no_repro:
        lines.append("## Reproduction")
        lines.append("")
        lines.append("Regenerate TreeDB evidence from fresh main worktrees with:")
        lines.append("")
        lines.append("```sh")
        lines.append("~/.codex/skills/treedb-jsonbench-breakdown/scripts/regenerate_treedb_metrics.sh \\")
        lines.append("  --mode ssh \\")
        lines.append("  --host mikers@192.168.0.185 \\")
        lines.append("  --gomap-repo /home/mikers/dev/snissn/gomap \\")
        lines.append("  --jsonbench-repo /home/mikers/dev/snissn/JSONBench \\")
        lines.append("  --data-dir /home/mikers/data/bluesky \\")
        lines.append("  --rows 1000000 \\")
        lines.append("  --tries 1 \\")
        lines.append("  --run-parity")
        lines.append("```")
        lines.append("")
        lines.append("For 10M, use `--rows 10000000`. If canonical input has malformed physical JSON lines or compact-storage failures, log those blockers and label repaired/no-compact runs as directional only.")
        lines.append("")
        lines.append("Regenerate this comparison log with this script and the resulting report JSONs plus supplied ClickHouse/colgranule artifacts.")
        lines.append("")

    if args.note:
        lines.append("## Notes")
        lines.append("")
        for note in args.note:
            lines.append(f"- {note}")
        lines.append("")

    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--treedb-1m-report")
    ap.add_argument("--treedb-10m-report")
    ap.add_argument("--treedb-1m-result", help="Optional single-cell TreeDB result.json for the 1M run")
    ap.add_argument("--treedb-10m-result", help="Optional single-cell TreeDB result.json for the 10M run")
    ap.add_argument("--treedb-1m-audit", help="Optional compression_audit.json for the 1M TreeDB report")
    ap.add_argument("--treedb-10m-audit", help="Optional compression_audit.json for the 10M TreeDB report")
    ap.add_argument("--treedb-10m-caveat", default="")
    ap.add_argument("--clickhouse-1m-result")
    ap.add_argument("--clickhouse-10m-result")
    ap.add_argument("--colgranule-raw")
    ap.add_argument("--output", "-o")
    ap.add_argument("--note", action="append", default=[])
    ap.add_argument("--no-repro", action="store_true")
    args = ap.parse_args(argv)

    records: List[dict] = []
    treedb_1m = parse_treedb_report(args.treedb_1m_report, "1M")
    if treedb_1m is None:
        treedb_1m = parse_treedb_result(args.treedb_1m_result, "1M")
    treedb_10m = parse_treedb_report(args.treedb_10m_report, "10M", args.treedb_10m_caveat)
    if treedb_10m is None:
        treedb_10m = parse_treedb_result(args.treedb_10m_result, "10M", args.treedb_10m_caveat)
    for rec in [
        attach_audit(treedb_1m, args.treedb_1m_audit),
        attach_audit(treedb_10m, args.treedb_10m_audit),
        parse_clickhouse(args.clickhouse_1m_result, "1M", "ClickHouse reported"),
        parse_clickhouse(args.clickhouse_10m_result, "10M", "ClickHouse prior report"),
        parse_colgranule(args.colgranule_raw),
    ]:
        if rec:
            records.append(rec)
    if not records:
        ap.error("provide at least one artifact")
    out = emit_markdown(records, args)
    if args.output:
        p = Path(args.output).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(out + "\n", encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
