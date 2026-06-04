#!/usr/bin/env python3
"""Summarize TreeDB pprof captures into bottleneck and optimization notes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

Q_NAMES = ["q1", "q2", "q3", "q4", "q5"]


def load_json(path: str | Path | None) -> Any | None:
    if not path:
        return None
    with Path(path).open() as f:
        return json.load(f)


def fmt_seconds(value: Any) -> str:
    if value is None:
        return ""
    s = float(value)
    if s < 0.001:
        return f"{s * 1_000_000:.1f}us"
    if s < 1:
        return f"{s:.4f}s"
    return f"{s:.3f}s"


def parse_bench_out(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"benchmarks": []}
    if not path.exists():
        return out
    text = path.read_text(errors="replace")
    out["raw_error"] = "FAIL" in text or "run_error" in text.lower()
    for line in text.splitlines():
        if not line.startswith("Benchmark"):
            continue
        fields = line.split()
        if len(fields) < 3:
            continue
        row: dict[str, Any] = {"name": fields[0], "samples": fields[1]}
        i = 2
        while i < len(fields) - 1:
            val, unit = fields[i], fields[i + 1]
            if unit == "ns/op":
                row["ns_per_op"] = float(val)
            elif unit == "B/op":
                row["bytes_per_op"] = float(val)
            elif unit == "allocs/op":
                row["allocs_per_op"] = float(val)
            i += 1
        out["benchmarks"].append(row)
    return out


def parse_top(path: Path, limit: int = 10) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    # Example CPU row:
    #      40ms 10.00% 20.00%      80ms 20.00%  pkg.Func
    # Example alloc row:
    #   12.34MB 30.00% 30.00% 12.34MB 30.00% pkg.Func
    rx = re.compile(r"^\s*(\S+)\s+([0-9.]+)%\s+([0-9.]+)%\s+(\S+)\s+([0-9.]+)%\s+(.+)$")
    for line in path.read_text(errors="replace").splitlines():
        m = rx.match(line)
        if not m:
            continue
        func = m.group(6).strip()
        rows.append({
            "flat": m.group(1),
            "flat_pct": float(m.group(2)),
            "cum": m.group(4),
            "cum_pct": float(m.group(5)),
            "function": func,
        })
        if len(rows) >= limit:
            break
    return rows


def classify_function(func: str) -> list[str]:
    f = func.lower()
    notes: list[str] = []
    if any(x in f for x in ["runtime.map", "mapaccess", "mapassign", "aeshash", "memeq", "strhash"]):
        notes.append("dictionary/global map or string-hash overhead; prefer code-space reuse, sorted-prefix execution, prepared dictionaries, or fewer per-query string maps")
    if any(x in f for x in ["mallocgc", "makeslice", "growslice", "newobject", "memclr", "typedmemclr"]):
        notes.append("allocation/zeroing overhead; reuse scratch buffers, move setup into prepared state, and avoid per-row temporary objects")
    if any(x in f for x in ["encoding/json", "simdjson", "canonical", "reconstruct", "document", "json"]):
        notes.append("JSON/document work visible; verify no document-scan fallback and keep reconstruction outside timed query hot paths")
    if any(x in f for x in ["valuelog", "vlog", "leaf", "pager", "readat", "mmap", "syscall", "pread"]):
        notes.append("storage/read path overhead; inspect leaf_vlog/value_vlog layout, read batching, mmap/direct views, and compacted storage shape")
    if any(x in f for x in ["typedcolumn", "columnpart", "decode", "varint", "dictionarycode", "int64"]):
        notes.append("typed-column decode/reducer overhead; consider direct views, prepared decoded state, codec/block shape, and fused reducers")
    if any(x in f for x in ["sort", "heap", "topk", "less", "sift"]):
        notes.append("TopK/sort/result-shaping overhead; use bounded heaps, aggregate metadata, or reusable result buffers")
    if any(x in f for x in ["sync.", "mutex", "rwmutex", "atomic"]):
        notes.append("synchronization/stat overhead; reduce hot-loop counters/locks or snapshot state before execution")
    if any(x in f for x in ["crc", "checksum", "xxhash", "hash"]):
        notes.append("checksum/hash overhead; separate integrity verification from hot scans where safe")
    return notes


def headline_slowest(report_path: str | None) -> list[tuple[str, float]]:
    data = load_json(report_path) if report_path else None
    if not isinstance(data, dict):
        return []
    best: dict[str, float] = {}
    for r in data.get("rows") or []:
        if r.get("storage_layout") == "column-store-full-prepared" and r.get("query") in Q_NAMES:
            try:
                best[r["query"]] = float(r["best_seconds"])
            except Exception:
                pass
    return sorted(best.items(), key=lambda kv: kv[1], reverse=True)


def focus_query(focus: str) -> str:
    m = re.match(r"^(q[1-5])_", focus)
    return m.group(1) if m else focus


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profiles-dir", required=True)
    ap.add_argument("--treedb-report", help="Optional JSONBench report.json for headline slow-query context")
    args = ap.parse_args()

    root = Path(args.profiles_dir)
    if not root.is_dir():
        raise SystemExit(f"profiles dir not found: {root}")

    focuses = [p for p in sorted(root.iterdir()) if p.is_dir()]
    slowest = headline_slowest(args.treedb_report)

    print("# TreeDB Profile Insights\n")
    print(f"- profiles dir: `{root}`")
    if args.treedb_report:
        print(f"- TreeDB report: `{args.treedb_report}`")
    if slowest:
        print("- headline slow-query order: " + ", ".join(f"`{q}` {fmt_seconds(s)}" for q, s in slowest))
    print()

    print("## Benchmark/profile captures\n")
    print("| focus | benchmark ns/op | B/op | allocs/op | profile files |")
    print("|---|---:|---:|---:|---|")
    for d in focuses:
        bench = parse_bench_out(d / "bench.out")
        row = (bench.get("benchmarks") or [{}])[0]
        files = []
        for name in ["cpu.pprof", "allocs.pprof", "cpu_top.txt", "allocs_top.txt", "alloc_objects_top.txt"]:
            if (d / name).exists():
                files.append(name)
        print(
            f"| `{d.name}` | {row.get('ns_per_op', '')} | {row.get('bytes_per_op', '')} | "
            f"{row.get('allocs_per_op', '')} | {', '.join(files)} |"
        )
    print()

    print("## Top CPU / allocation signals\n")
    for d in focuses:
        cpu = parse_top(d / "cpu_top.txt", 8)
        alloc = parse_top(d / "allocs_top.txt", 8)
        if not cpu and not alloc:
            if (d / "run_error.txt").exists():
                print(f"### `{d.name}`\n")
                print(f"Profile failed: `{(d / 'run_error.txt').read_text(errors='replace').strip()}`\n")
            continue
        print(f"### `{d.name}`\n")
        if cpu:
            print("CPU top:")
            for r in cpu[:5]:
                print(f"- {r['flat_pct']:.1f}% flat / {r['cum_pct']:.1f}% cum — `{r['function']}`")
        if alloc:
            print("\nAllocation top:")
            for r in alloc[:5]:
                print(f"- {r['flat_pct']:.1f}% flat / {r['cum_pct']:.1f}% cum — `{r['function']}`")
        seen: list[str] = []
        for r in cpu[:8] + alloc[:8]:
            for note in classify_function(r["function"]):
                if note not in seen:
                    seen.append(note)
        if seen:
            print("\nOptimization hypotheses:")
            for note in seen[:6]:
                print(f"- {note}.")
        print()

    print("## Suggested optimization workflow\n")
    print("1. Start with the slowest headline query and match it to the corresponding profile focus.")
    print("2. Confirm the top functions are in the timed scan/reduce path, not setup-only or test harness code.")
    print("3. If allocation/zeroing is visible, add a prepared/scratch-buffer variant before changing on-disk format.")
    print("4. If typed-column decode dominates, inspect section/block layout, direct-view eligibility, and reducer fusion.")
    print("5. If map/string hashing dominates q2, prioritize sorted-prefix/grouped-distinct or prepared global-code reuse.")
    print("6. After an optimization, rerun the same metric and profile command; treat material regressions as blockers unless explicitly accepted.")


if __name__ == "__main__":
    main()
