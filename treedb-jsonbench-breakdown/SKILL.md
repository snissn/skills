---
name: treedb-jsonbench-breakdown
description: "Generate a standardized TreeDB JSONBench optimization breakdown: production q1-q5 timings, WAL-excluded durable storage, correctness gates, ClickHouse/colgranule context, caveats, and optimization targets from JSONBench/TreeDB artifacts."
---

# TreeDB JSONBench Breakdown

## When To Use

Use this skill when asked to:

- summarize TreeDB JSONBench q1-q5 performance and storage;
- compare TreeDB durable storage excluding WAL against ClickHouse storage;
- standardize what TreeDB column-store optimization work is targeting;
- prepare a tracker/PR/comment breakdown from JSONBench artifacts.

Do **not** use this skill to claim fresh ClickHouse parity unless ClickHouse was actually rerun for the same row set. Do **not** treat `experiments/colgranule` as production evidence; it is historical/prototype context only.

## Inputs Needed

Prefer these artifacts, in order:

1. Production TreeDB JSONBench `report.json` for the headline run.
2. Matching production TreeDB cell `result.json` when available; use it for reconstruction hashes and detailed storage categories.
3. Optional TreeDB parity `report.json` containing row/direct/prepared rows.
4. Optional ClickHouse JSONBench result JSON, e.g. `clickhouse/results/..._1m.json`.
5. Optional colgranule raw comparison, e.g. `experiments/colgranule/JSONBENCH_COMPARISON_RAW.json`.
6. gomap and JSONBench commit heads, if not already in nearby evidence summaries.

If a critical artifact is missing, ask for it or clearly label the corresponding table cell as unavailable.

## Required Evidence Semantics

For the production headline row, require or explicitly report the absence of:

- `storage_layout=column-store-full-prepared`
- `data_shape=full-retained-json`
- `execution_mode=prepared`
- `storage_source=typed_column_part`
- `typed_column_owner=typed_column_part`
- `retained_payload_policy=non-column`
- `fallback_reason=none`
- `document_scan_fallback=false`
- reconstruction status valid via canonical JSON hash when available
- q1-q5 run from the same loaded DB/artifact

Storage comparison target:

- Use **TreeDB durable storage excluding WAL** for ClickHouse storage comparison.
- Still report TreeDB total bytes and WAL bytes separately.
- Durable excluding WAL must continue to include durable `leaf_vlog`, `value_vlog`, `index.db`/primary index, column assets, and manifest/control bytes.

## Workflow

1. Read the TreeDB report/result artifacts.
2. Select the headline production rows (`column-store-full-prepared`, preferably 1M/full-retained JSON).
3. Extract q1-q5 best/median/attempt timings, rows scanned, result hashes, and fallback fields.
4. Extract storage:
   - total bytes;
   - durable bytes excluding WAL;
   - WAL bytes excluded;
   - leaf_vlog, value_vlog, column assets, typed-column part bytes, primary index, and other categories when available.
5. If a parity report is provided, extract row scan, full direct, and full prepared q1-q5 timings and hash parity.
6. If ClickHouse is provided, extract `total_size`, `data_size`, `index_size`, q1-q5 attempts and best times, loaded rows, version, and machine/date.
7. If colgranule raw data is provided, extract q1-q5 historical kernel best timings and mark them as prototype/historical.
8. Compute ratios:
   - TreeDB durable excluding WAL / ClickHouse total;
   - TreeDB production q time / ClickHouse best q time;
   - TreeDB production q time / colgranule kernel q time when present.
9. Produce the standard report using the template in [references/breakdown-template.md](references/breakdown-template.md).

## Regenerating Metrics From `main`

Use the regeneration helper when the task is to produce fresh TreeDB metrics from current `origin/main`. It creates temporary detached worktrees for gomap main and JSONBench main, wires JSONBench `treedb/go.mod` to the gomap main worktree, runs `run_matrix.sh`, and then renders the standardized Markdown breakdown.

Default headline run:

- `ROWS=1000000`
- `TRIES=1`
- `STORAGE_LAYOUTS=column-store-full-prepared`
- `SUITE=full`
- `PROFILE=durable`
- `COMPACT_AFTER_LOAD=1`
- `VALIDATE_RECONSTRUCTION=1`
- `GOWORK=off`

Local example:

```sh
~/.codex/skills/treedb-jsonbench-breakdown/scripts/regenerate_treedb_metrics.sh \
  --mode local \
  --gomap-repo /path/to/gomap \
  --jsonbench-repo /path/to/JSONBench \
  --data-dir "$HOME/data/bluesky" \
  --run-parity \
  --with-profiles \
  --profile-focuses "q2_prepared q3_prepared q5_prepared"
```

SSH example for the standard remote host:

```sh
~/.codex/skills/treedb-jsonbench-breakdown/scripts/regenerate_treedb_metrics.sh \
  --mode ssh \
  --host mikers@192.168.0.185 \
  --gomap-repo /home/mikers/path/to/gomap \
  --jsonbench-repo /home/mikers/path/to/JSONBench \
  --data-dir /home/mikers/data/bluesky \
  --run-parity \
  --with-profiles \
  --profile-focuses "q2_prepared q3_prepared q5_prepared" \
  --collect-dir /tmp/treedb_jsonbench_metrics_remote
```

SSH mode sends the helper over `ssh`, runs on the remote, copies the remote `report.json`/`result.json` artifacts back into `--collect-dir`, and renders `breakdown.md` locally when the parser is available. If `--data-dir` is omitted in SSH mode, the remote child uses its own `$HOME/data/bluesky` default.

### Optional profiling and bottleneck insights

Add `--with-profiles` to run focused `go test ./TreeDB/collections` benchmark profiles against the same fresh gomap main worktree. The profile pass is separate from the canonical JSONBench timing run; use it for attribution and optimization planning, not as the headline throughput number.

Default profile focuses are prepared q1-q5:

```sh
--with-profiles \
--profile-focuses "q1_prepared q2_prepared q3_prepared q4_prepared q5_prepared"
```

Use `--profile-focuses all` for direct+prepared q1-q5, or pass a custom Go benchmark regex as a focus. Profile artifacts are written under `<out-root>/profiles/<focus>/`:

- `bench.out` / `bench_cpu.out`
- `cpu.pprof`, `cpu_top.txt`
- `bench_allocs.out`
- `allocs.pprof`, `allocs_top.txt`, `alloc_objects_top.txt`
- `profile_insights.md` at the output root or local SSH collection dir when the insights helper is available

The insights helper classifies common bottleneck signals:

- map/string hashing -> dictionary/global-code setup, sorted-prefix/grouped-distinct work;
- allocation/zeroing -> scratch reuse, prepared state, result-buffer reuse;
- JSON/document functions -> possible fallback/reconstruction leakage;
- value-log/leaf/pager reads -> storage/read batching and durable layout work;
- typed-column decode -> direct views, codec/block layout, reducer fusion;
- heap/sort/top-k -> bounded heaps, aggregate metadata, reusable result buffers;
- locks/atomics -> hot-loop stat/lock overhead.

Important options:

- `--rows N`: headline row count; standard is `1000000`.
- `--run-parity --parity-rows 100000`: also run row/full-direct/full-prepared parity.
- `--with-profiles`: capture CPU/allocation profiles and generate profile insights.
- `--profile-focuses LIST`: choose prepared/direct q1-q5 focuses; use `all` for both modes.
- `--profile-benchtime 20x`: profile benchmark benchtime.
- `--profile-fail-fast`: make a missing/failing profile benchmark fatal.
- `--clickhouse-result PATH`: include a reference ClickHouse result in the rendered breakdown; this does not rerun ClickHouse.
- `--colgranule-raw PATH`: include historical colgranule kernel context.
- `--keep-worktrees`: preserve temporary main worktrees for debugging.
- `--no-breakdown`: only generate raw artifacts.

## Parser Script

A portable parser is included for already-existing artifacts:

```sh
python3 ~/.codex/skills/treedb-jsonbench-breakdown/scripts/treedb_jsonbench_breakdown.py \
  --treedb-report /path/to/treedb/report.json \
  --treedb-result /path/to/treedb/cell/result.json \
  --parity-report /path/to/100k/parity/report.json \
  --clickhouse-result /path/to/clickhouse/results/m6i.8xlarge_bluesky_1m.json \
  --colgranule-raw /path/to/experiments/colgranule/JSONBENCH_COMPARISON_RAW.json
```

All inputs except `--treedb-report` are optional. The script prints Markdown to stdout.

## Reporting Rules

Always include:

- artifact paths and commit heads when known;
- unit clarity: decimal MB and MiB;
- storage basis labels (`total`, `durable excluding WAL`, `WAL excluded`);
- timing basis labels (`best`, attempts/median when available);
- correctness/fallback gates;
- caveats for stale or reference-only ClickHouse/colgranule data;
- an optimization target section naming the largest storage categories and slowest q1-q5 rows.

Never silently collapse:

- total TreeDB bytes with durable-WAL-excluded bytes;
- production TreeDB with colgranule;
- direct rows with prepared rows;
- same-scale evidence with smaller parity smoke evidence.

## Validation

Before presenting the breakdown, verify:

- [ ] q1-q5 are all present for the headline row.
- [ ] Storage bytes are internally labeled and ratios use the intended basis.
- [ ] `fallback_reason` and `document_scan_fallback` are shown.
- [ ] If ClickHouse is included, the answer says whether it was freshly rerun or a reference artifact.
- [ ] If colgranule is included, it is labeled historical/prototype.
- [ ] Missing direct/full parity evidence is called out rather than inferred.
- [ ] For regenerated metrics, gomap and JSONBench heads are recorded and the output paths are preserved.
- [ ] For SSH regeneration, copied local artifacts and remote artifact paths are both reported.
- [ ] For profiling, pprof artifacts, `cpu_top.txt`/`allocs_top.txt`, and `profile_insights.md` paths are reported.
- [ ] Profile findings are framed as hypotheses requiring before/after reruns, not as proof of optimization impact.

## Failure Handling

Pause and ask for clarification if:

- multiple plausible TreeDB headline artifacts disagree and no preferred artifact is stated;
- the TreeDB artifact is not production `TreeDB/collections` evidence;
- a requested ClickHouse comparison lacks a ClickHouse result JSON;
- storage fields are absent or ambiguous enough that durable-excluding-WAL cannot be computed.
