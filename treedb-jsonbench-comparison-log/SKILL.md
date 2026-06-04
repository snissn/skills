---
name: treedb-jsonbench-comparison-log
description: Produce a concise TreeDB JSONBench comparison log for size and query throughput versus ClickHouse and the historical colgranule prototype, with the correct WAL-excluded TreeDB storage basis and reproduction commands.
---

# TreeDB JSONBench Comparison Log

Use this skill when asked to summarize, log, or reproduce TreeDB JSONBench size/query throughput differences versus ClickHouse and/or `experiments/colgranule`.

## Non-negotiable storage basis

For TreeDB, compare **durable excluding command WAL**:

- Exclude only command WAL files under `wal/`.
- Include persistent TreeDB data: `leaf_vlog/`, `value_vlog/`, `index.db`, column assets / typed-column parts, manifests and control metadata.
- Do not misclassify `leaf_vlog/value-l255-*.log` as WAL. Path matters: `leaf_vlog/` is durable B-tree leaf storage.

## Workflow

1. Gather artifacts:
   - TreeDB report JSON(s), usually from `treedb-jsonbench-breakdown` runs.
   - Optional ClickHouse result JSON(s).
   - Optional colgranule raw JSON, usually `experiments/colgranule/JSONBENCH_COMPARISON_RAW.json`.
2. Generate a comparison log:

```sh
~/.codex/skills/treedb-jsonbench-comparison-log/scripts/jsonbench_compare_log.py \
  --treedb-1m-report /path/to/treedb_1m/report.json \
  --clickhouse-1m-result /path/to/clickhouse_1m/result.json \
  --colgranule-raw /path/to/JSONBENCH_COMPARISON_RAW.json \
  --output /tmp/treedb_jsonbench_comparison_log.md
```

For 10M evidence, add:

```sh
  --treedb-10m-report /path/to/treedb_10m/report.json \
  --clickhouse-10m-result /path/to/clickhouse_10m/result.json
```

3. Verify the log states:
   - TreeDB size basis is WAL-excluded durable bytes.
   - `leaf_vlog` and `value_vlog` remain counted.
   - query times and rows/sec are separated from storage sizes.
   - ClickHouse/colgranule are not described as freshly rerun unless the supplied artifacts prove it.

## Reproduction

Use the existing TreeDB regeneration helper for fresh TreeDB runs:

```sh
~/.codex/skills/treedb-jsonbench-breakdown/scripts/regenerate_treedb_metrics.sh \
  --mode ssh \
  --host mikers@192.168.0.185 \
  --gomap-repo /home/mikers/dev/snissn/gomap \
  --jsonbench-repo /home/mikers/dev/snissn/JSONBench \
  --data-dir /home/mikers/data/bluesky \
  --rows 1000000 \
  --tries 1 \
  --run-parity
```

For 10M, use `--rows 10000000`. If the canonical data contains malformed physical JSON lines, log that as an input blocker; any repaired-input/no-compact run must be labeled as directional only.

See [current snapshot and reproduction notes](references/current-snapshot.md) for the latest logged numbers and caveats.

## Final report checklist

- [ ] Size table: TreeDB vs ClickHouse vs colgranule, with TreeDB durable excluding WAL.
- [ ] Query-time table: q1–q5 times, separate from size.
- [ ] Throughput table: q1–q5 rows/sec or explicit time-ratio/throughput-ratio note.
- [ ] Reproduction commands and artifact paths.
- [ ] Caveats for repaired data, no-compact runs, prototype colgranule, or stale ClickHouse artifacts.
