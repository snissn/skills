# Current TreeDB JSONBench Comparison Snapshot

This snapshot captures the latest known comparison discussed during the #1945 closeout. Re-run before making fresh benchmark claims. It predates the Template-v1 retained encoding and retained value-log placement PR stack for issues #2355/#2357/#2356, so treat it as a baseline/regression anchor, not current-head storage evidence.

## Size basis

TreeDB is compared using **durable bytes excluding command WAL**. Count `leaf_vlog/`, `value_vlog/`, `index.db`, column assets / typed-column parts, manifests and control metadata. Exclude only command WAL under `wal/`.

## 1M size

| system | size | note |
|---|---:|---|
| TreeDB production | 355.0 MB | durable excluding WAL; includes `leaf_vlog`, `value_vlog`, index, column assets |
| ClickHouse reported | 98.5 MB | prior 1M ClickHouse reference |
| colgranule prototype retained | 60.9 MB | historical prototype: all derived columns + Template-v1 remaining fields |

Ratios:

- TreeDB / ClickHouse: **3.60x larger**
- TreeDB / colgranule prototype: **5.83x larger**

TreeDB total including command WAL was 850.8 MB, but total including WAL is not the fair steady-state comparison basis.

## 10M size

| system | size | note |
|---|---:|---|
| TreeDB repaired/no-compact | 3.57 GB | durable excluding WAL; directional only |
| ClickHouse prior report | 1.03 GB | prior 10M ClickHouse report |
| colgranule | n/a | no comparable 10M retained report |

Ratio:

- TreeDB / ClickHouse: **3.45x larger**

TreeDB total including command WAL was 8.58 GB.

## Query times

| scale/system | q1 | q2 | q3 | q4 | q5 |
|---|---:|---:|---:|---:|---:|
| 1M TreeDB production | 0.065s | 0.539s | 0.206s | 0.195s | 0.197s |
| 1M ClickHouse reported | 0.004s | 0.022s | 0.012s | 0.017s | 0.019s |
| 1M colgranule kernel | 0.0043s | 0.0389s | 0.0066s | 0.0099s | 0.0100s |
| 10M TreeDB repaired/no-compact | 0.664s | 7.962s | 2.608s | 2.339s | 2.579s |
| 10M ClickHouse prior report | 0.022s | 0.200s | 0.100s | 0.074s | 0.066s |

## Current artifacts

1M TreeDB artifact:

- `/tmp/treedb_jsonbench_metrics_1m_ssh_20260603_222419/treedb_report.json`
- `/tmp/treedb_jsonbench_metrics_1m_ssh_20260603_222419/treedb_result.json`
- `/tmp/treedb_jsonbench_metrics_1m_ssh_20260603_222419/breakdown.md`

10M TreeDB directional artifact:

- `/tmp/treedb_jsonbench_metrics_10m_repaired_nocompact_ssh_20260604_004431/treedb_report.json`
- `/tmp/treedb_jsonbench_metrics_10m_repaired_nocompact_ssh_20260604_004431/treedb_result.json`
- `/tmp/treedb_jsonbench_metrics_10m_repaired_nocompact_ssh_20260604_004431/breakdown.md`

Historical colgranule artifact:

- `experiments/colgranule/JSONBENCH_COMPARISON_RAW.json`
- `experiments/colgranule/JSONBENCH_COMPARISON_REPORT.md`

Known ClickHouse references:

- 1M: `/private/tmp/jsonbench-2117/clickhouse/results/m6i.8xlarge_bluesky_1m.json`
- 10M remote: `/home/mikers/jsonbench_runs/current_status_typedcolumn_20260531_220752/clickhouse_compare_10m/clickhouse/result.json`

Known compression audit state:

- formal `compression_audit.json`, `gzip_oracle.json`, `vlog_frame_audit.json`, `column_section_audit.json`, and `retained_payload_audit.json` artifacts were not present in the original 1M snapshot.
- Current ad hoc evidence showed `value_vlog` raw payload dominance in the LZ4 probe and raw/uncompressed dictionary sections. Treat storage-parity claims as non-final until formal audits are attached.
- Fresh comparison logs should also show retained payload encoding/compression status fields and an explicit final storage-compression claim status (`pass` or `non-final: ...`).

## Reproduction notes

Fresh TreeDB 1M over SSH:

```sh
~/.codex/skills/treedb-jsonbench-breakdown/scripts/regenerate_treedb_metrics.sh \
  --mode ssh \
  --host mikers@192.168.0.185 \
  --gomap-repo /home/mikers/dev/snissn/gomap \
  --jsonbench-repo /home/mikers/dev/snissn/JSONBench \
  --data-dir /home/mikers/data/bluesky \
  --rows 1000000 \
  --tries 1 \
  --compression-audit \
  --run-parity \
  --with-profiles \
  --profile-focuses "q1_prepared q2_prepared q3_prepared q4_prepared q5_prepared"
```

Fresh TreeDB 10M canonical attempt:

```sh
~/.codex/skills/treedb-jsonbench-breakdown/scripts/regenerate_treedb_metrics.sh \
  --mode ssh \
  --host mikers@192.168.0.185 \
  --gomap-repo /home/mikers/dev/snissn/gomap \
  --jsonbench-repo /home/mikers/dev/snissn/JSONBench \
  --data-dir /home/mikers/data/bluesky \
  --rows 10000000 \
  --tries 1
```

Known 10M canonical blockers at the time of this snapshot:

- malformed physical JSON lines in `file_0005.json.gz`, `file_0006.json.gz`, and `file_0007.json.gz`;
- a compacted repaired-input run failed on a missing `leaf_vlog/value-l255-000064.log` during compact storage.

Therefore the current 10M TreeDB row is explicitly **repaired-input / no-compact / reconstruction-not-validated** and is for bottleneck direction only.
