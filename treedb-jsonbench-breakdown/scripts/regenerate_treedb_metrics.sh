#!/usr/bin/env bash
set -euo pipefail

MODE="local"
SSH_HOST="mikers@192.168.0.185"
GOMAP_REPO="${GOMAP_REPO:-}"
JSONBENCH_REPO="${JSONBENCH_REPO:-}"
if [[ -z "${DATA_DIR+x}" ]]; then
  DATA_DIR="$HOME/data/bluesky"
  DATA_DIR_DEFAULTED=1
else
  DATA_DIR_DEFAULTED=0
fi
OUT_ROOT="${OUT_ROOT:-}"
ROWS="${ROWS:-1000000}"
TRIES="${TRIES:-1}"
BATCH_SIZE="${BATCH_SIZE:-16000}"
PROFILE="${PROFILE:-durable}"
DATA_ROOT="${DATA_ROOT:-fast}"
STORAGE_LAYOUTS="${STORAGE_LAYOUTS:-column-store-full-prepared}"
SUITE="${SUITE:-full}"
COMPACT_AFTER_LOAD="${COMPACT_AFTER_LOAD:-1}"
VALIDATE_RECONSTRUCTION="${VALIDATE_RECONSTRUCTION:-1}"
RUN_PARITY="${RUN_PARITY:-0}"
PARITY_ROWS="${PARITY_ROWS:-100000}"
FETCH_MAIN=1
KEEP_WORKTREES=0
REMOTE_CHILD=0
COLLECT_DIR="${COLLECT_DIR:-}"
RUN_BREAKDOWN=1
RUN_PROFILES=0
PROFILE_FOCUSES="${PROFILE_FOCUSES:-q1_prepared q2_prepared q3_prepared q4_prepared q5_prepared}"
PROFILE_BENCHTIME="${PROFILE_BENCHTIME:-20x}"
PROFILE_COUNT="${PROFILE_COUNT:-1}"
PROFILE_ALLOW_ERRORS=1
CLICKHOUSE_RESULT="${CLICKHOUSE_RESULT:-}"
COLGRANULE_RAW="${COLGRANULE_RAW:-}"

usage() {
  cat <<'EOF'
Usage: regenerate_treedb_metrics.sh [options]

Regenerate standardized TreeDB JSONBench metrics from fresh gomap main and
JSONBench main worktrees. Supports local execution and execution over SSH.

Common options:
  --mode local|ssh             Run locally or via SSH. Default: local.
  --host user@host             SSH host. Default: mikers@192.168.0.185.
  --gomap-repo PATH            Existing gomap git repo used to create a main worktree.
  --jsonbench-repo PATH        Existing JSONBench git repo used to create a main worktree.
  --data-dir PATH              JSONBench Bluesky data dir. Default: ~/data/bluesky.
  --out-root PATH              Output root. Default: /tmp/treedb_jsonbench_metrics_<timestamp>.
  --rows N                     Headline row count. Default: 1000000.
  --tries N                    Query attempts. Default: 1.
  --layouts LIST               Headline layouts. Default: column-store-full-prepared.
  --suite minimal|full|all     JSONBench suite. Default: full.
  --compact 0|1                Run compact-after-load. Default: 1.
  --validate-reconstruction 0|1 Validate full retained JSON reconstruction. Default: 1.
  --run-parity                 Also run 100k row/direct/prepared parity.
  --parity-rows N              Parity rows. Default: 100000.
  --clickhouse-result PATH     Optional ClickHouse result JSON for final breakdown.
  --colgranule-raw PATH        Optional colgranule raw JSON for final breakdown.
  --with-profiles              Also run focused TreeDB/collections pprof captures.
  --profile-focuses LIST       Space-separated profile focuses. Default: prepared q1-q5.
                               Use "all" for direct+prepared q1-q5.
  --profile-benchtime VALUE    Go benchmark benchtime for profiles. Default: 20x.
  --profile-count N            Go benchmark count for profiles. Default: 1.
  --profile-fail-fast          Treat a profile benchmark failure as fatal.
  --no-fetch                   Do not fetch origin/main before creating worktrees.
  --keep-worktrees             Keep temporary gomap/JSONBench worktrees.
  --no-breakdown               Only regenerate artifacts; do not run the Markdown parser.

SSH options:
  --collect-dir PATH           Local directory for copied remote report/result JSONs.
                               Default: /tmp/treedb_jsonbench_metrics_remote_<timestamp>.

Examples:
  # Local final 1M full-retained production row from fresh main worktrees.
  regenerate_treedb_metrics.sh \
    --mode local \
    --gomap-repo /path/to/gomap \
    --jsonbench-repo /path/to/JSONBench \
    --data-dir ~/data/bluesky \
    --run-parity

  # Remote on mikers@192.168.0.185, then copy reports/profiles back locally.
  regenerate_treedb_metrics.sh \
    --mode ssh \
    --host mikers@192.168.0.185 \
    --gomap-repo /home/mikers/gomap \
    --jsonbench-repo /home/mikers/JSONBench \
    --data-dir /home/mikers/data/bluesky \
    --run-parity \
    --with-profiles \
    --profile-focuses "q2_prepared q3_prepared q5_prepared"

The script fails rather than silently using partial input data. For non-standard
row counts, run_matrix uses the subset scale with SUBSET_ROWS=N.
EOF
}

quote_args() {
  local out=()
  local arg
  for arg in "$@"; do
    out+=("$(printf '%q' "$arg")")
  done
  printf '%s ' "${out[@]}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --host) SSH_HOST="$2"; shift 2 ;;
    --gomap-repo) GOMAP_REPO="$2"; shift 2 ;;
    --jsonbench-repo) JSONBENCH_REPO="$2"; shift 2 ;;
    --data-dir) DATA_DIR="$2"; DATA_DIR_DEFAULTED=0; shift 2 ;;
    --out-root) OUT_ROOT="$2"; shift 2 ;;
    --rows) ROWS="$2"; shift 2 ;;
    --tries) TRIES="$2"; shift 2 ;;
    --batch-size) BATCH_SIZE="$2"; shift 2 ;;
    --profile) PROFILE="$2"; shift 2 ;;
    --data-root) DATA_ROOT="$2"; shift 2 ;;
    --layouts) STORAGE_LAYOUTS="$2"; shift 2 ;;
    --suite) SUITE="$2"; shift 2 ;;
    --compact) COMPACT_AFTER_LOAD="$2"; shift 2 ;;
    --validate-reconstruction) VALIDATE_RECONSTRUCTION="$2"; shift 2 ;;
    --run-parity) RUN_PARITY=1; shift ;;
    --parity-rows) PARITY_ROWS="$2"; shift 2 ;;
    --clickhouse-result) CLICKHOUSE_RESULT="$2"; shift 2 ;;
    --colgranule-raw) COLGRANULE_RAW="$2"; shift 2 ;;
    --collect-dir) COLLECT_DIR="$2"; shift 2 ;;
    --with-profiles) RUN_PROFILES=1; shift ;;
    --profile-focuses) PROFILE_FOCUSES="$2"; shift 2 ;;
    --profile-benchtime) PROFILE_BENCHTIME="$2"; shift 2 ;;
    --profile-count) PROFILE_COUNT="$2"; shift 2 ;;
    --profile-fail-fast) PROFILE_ALLOW_ERRORS=0; shift ;;
    --no-fetch) FETCH_MAIN=0; shift ;;
    --keep-worktrees) KEEP_WORKTREES=1; shift ;;
    --remote-child) REMOTE_CHILD=1; shift ;;
    --no-breakdown) RUN_BREAKDOWN=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$MODE" in local|ssh) ;; *) echo "--mode must be local or ssh" >&2; exit 2 ;; esac

if [[ "$MODE" == "ssh" ]]; then
  if [[ -z "$COLLECT_DIR" ]]; then
    COLLECT_DIR="/tmp/treedb_jsonbench_metrics_remote_$(date -u +%Y%m%d_%H%M%S)"
  fi
  mkdir -p "$COLLECT_DIR"
  remote_args=(
    --mode local
    --remote-child
    --rows "$ROWS"
    --tries "$TRIES"
    --batch-size "$BATCH_SIZE"
    --profile "$PROFILE"
    --data-root "$DATA_ROOT"
    --layouts "$STORAGE_LAYOUTS"
    --suite "$SUITE"
    --compact "$COMPACT_AFTER_LOAD"
    --validate-reconstruction "$VALIDATE_RECONSTRUCTION"
    --parity-rows "$PARITY_ROWS"
    --no-breakdown
  )
  [[ "$DATA_DIR_DEFAULTED" == "0" ]] && remote_args+=(--data-dir "$DATA_DIR")
  [[ -n "$GOMAP_REPO" ]] && remote_args+=(--gomap-repo "$GOMAP_REPO")
  [[ -n "$JSONBENCH_REPO" ]] && remote_args+=(--jsonbench-repo "$JSONBENCH_REPO")
  [[ -n "$OUT_ROOT" ]] && remote_args+=(--out-root "$OUT_ROOT")
  [[ "$RUN_PARITY" == "1" ]] && remote_args+=(--run-parity)
  if [[ "$RUN_PROFILES" == "1" ]]; then
    remote_args+=(--with-profiles --profile-focuses "$PROFILE_FOCUSES" --profile-benchtime "$PROFILE_BENCHTIME" --profile-count "$PROFILE_COUNT")
    [[ "$PROFILE_ALLOW_ERRORS" == "0" ]] && remote_args+=(--profile-fail-fast)
  fi
  [[ "$FETCH_MAIN" == "0" ]] && remote_args+=(--no-fetch)
  [[ "$KEEP_WORKTREES" == "1" ]] && remote_args+=(--keep-worktrees)

  tmp_log="$COLLECT_DIR/remote.log"
  echo "==> running remote TreeDB metrics on $SSH_HOST"
  # shellcheck disable=SC2029
  ssh "$SSH_HOST" "bash -s -- $(quote_args "${remote_args[@]}")" < "$0" | tee "$tmp_log"

  remote_report=$(awk -F= '/^TREEDB_METRICS_REPORT_JSON=/{print $2}' "$tmp_log" | tail -1)
  remote_result=$(awk -F= '/^TREEDB_METRICS_RESULT_JSON=/{print $2}' "$tmp_log" | tail -1)
  remote_parity=$(awk -F= '/^TREEDB_METRICS_PARITY_REPORT_JSON=/{print $2}' "$tmp_log" | tail -1)
  remote_profiles=$(awk -F= '/^TREEDB_METRICS_PROFILES_DIR=/{print $2}' "$tmp_log" | tail -1)
  remote_gomap=$(awk -F= '/^TREEDB_METRICS_GOMAP_HEAD=/{print $2}' "$tmp_log" | tail -1)
  remote_jsonbench=$(awk -F= '/^TREEDB_METRICS_JSONBENCH_HEAD=/{print $2}' "$tmp_log" | tail -1)

  if [[ -n "$remote_report" ]]; then scp "$SSH_HOST:$remote_report" "$COLLECT_DIR/treedb_report.json" >/dev/null; fi
  if [[ -n "$remote_result" ]]; then scp "$SSH_HOST:$remote_result" "$COLLECT_DIR/treedb_result.json" >/dev/null; fi
  if [[ -n "$remote_parity" ]]; then scp "$SSH_HOST:$remote_parity" "$COLLECT_DIR/parity_report.json" >/dev/null; fi
  if [[ -n "$remote_profiles" ]]; then scp -r "$SSH_HOST:$remote_profiles" "$COLLECT_DIR/profiles" >/dev/null; fi

  echo "==> collected remote reports in $COLLECT_DIR"
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
  parser="$script_dir/treedb_jsonbench_breakdown.py"
  if [[ "$RUN_BREAKDOWN" == "1" && -x "$parser" && -f "$COLLECT_DIR/treedb_report.json" ]]; then
    breakdown_args=(--treedb-report "$COLLECT_DIR/treedb_report.json" --gomap-head "${remote_gomap:-unknown}" --jsonbench-head "${remote_jsonbench:-unknown}")
    [[ -f "$COLLECT_DIR/treedb_result.json" ]] && breakdown_args+=(--treedb-result "$COLLECT_DIR/treedb_result.json")
    [[ -f "$COLLECT_DIR/parity_report.json" ]] && breakdown_args+=(--parity-report "$COLLECT_DIR/parity_report.json")
    [[ -n "$CLICKHOUSE_RESULT" ]] && breakdown_args+=(--clickhouse-result "$CLICKHOUSE_RESULT")
    [[ -n "$COLGRANULE_RAW" ]] && breakdown_args+=(--colgranule-raw "$COLGRANULE_RAW")
    python3 "$parser" "${breakdown_args[@]}" | tee "$COLLECT_DIR/breakdown.md"
    echo "==> breakdown: $COLLECT_DIR/breakdown.md"
  fi
  insights="$script_dir/profile_insights.py"
  if [[ "$RUN_PROFILES" == "1" && -x "$insights" && -d "$COLLECT_DIR/profiles" ]]; then
    insight_args=(--profiles-dir "$COLLECT_DIR/profiles")
    [[ -f "$COLLECT_DIR/treedb_report.json" ]] && insight_args+=(--treedb-report "$COLLECT_DIR/treedb_report.json")
    python3 "$insights" "${insight_args[@]}" | tee "$COLLECT_DIR/profile_insights.md"
    echo "==> profile insights: $COLLECT_DIR/profile_insights.md"
  fi
  exit 0
fi

require_positive_int() {
  local name="$1" value="$2"
  if ! [[ "$value" =~ ^[1-9][0-9]*$ ]]; then
    echo "$name must be a positive integer, got: $value" >&2
    exit 2
  fi
}
require_positive_int ROWS "$ROWS"
require_positive_int TRIES "$TRIES"
require_positive_int BATCH_SIZE "$BATCH_SIZE"
require_positive_int PARITY_ROWS "$PARITY_ROWS"
require_positive_int PROFILE_COUNT "$PROFILE_COUNT"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || pwd)"
if [[ -z "$OUT_ROOT" ]]; then
  OUT_ROOT="/tmp/treedb_jsonbench_metrics_$(date -u +%Y%m%d_%H%M%S)"
fi
mkdir -p "$OUT_ROOT"

find_repo() {
  local kind="$1" explicit="$2"
  shift 2 || true
  local candidates=()
  [[ -n "$explicit" ]] && candidates+=("$explicit")
  candidates+=("$@")
  local c
  for c in "${candidates[@]}"; do
    [[ -d "$c/.git" || -f "$c/.git" ]] || continue
    case "$kind" in
      gomap)
        [[ -f "$c/go.mod" ]] && grep -q 'module github.com/snissn/gomap' "$c/go.mod" && { printf '%s\n' "$c"; return; }
        ;;
      jsonbench)
        [[ -d "$c/treedb" && -f "$c/treedb/run_matrix.sh" ]] && { printf '%s\n' "$c"; return; }
        ;;
    esac
  done
  return 1
}

GOMAP_REPO_RESOLVED="$(find_repo gomap "$GOMAP_REPO" "$PWD" "$HOME/orca/workspaces/gomap/Nautilus" "$HOME/gomap" "$HOME/src/gomap" 2>/dev/null || true)"
JSONBENCH_REPO_RESOLVED="$(find_repo jsonbench "$JSONBENCH_REPO" "$HOME/orca/workspaces/JSONBench-1955-final-evidence" "$HOME/orca/workspaces/JSONBench-snissn" "$HOME/JSONBench" "$HOME/src/JSONBench" 2>/dev/null || true)"

if [[ -z "$GOMAP_REPO_RESOLVED" ]]; then
  echo "Could not find gomap repo. Pass --gomap-repo PATH." >&2
  exit 2
fi
if [[ -z "$JSONBENCH_REPO_RESOLVED" ]]; then
  echo "Could not find JSONBench repo. Pass --jsonbench-repo PATH." >&2
  exit 2
fi
if [[ ! -d "$DATA_DIR" ]]; then
  echo "DATA_DIR does not exist: $DATA_DIR" >&2
  exit 2
fi

create_main_worktree() {
  local repo="$1" dest="$2"
  if [[ "$FETCH_MAIN" == "1" ]]; then
    git -C "$repo" fetch origin main
  fi
  rm -rf "$dest"
  if git -C "$repo" rev-parse --verify origin/main >/dev/null 2>&1; then
    git -C "$repo" worktree add --detach "$dest" origin/main >/dev/null
  else
    git -C "$repo" worktree add --detach "$dest" main >/dev/null
  fi
}

GOMAP_MAIN_DIR="$OUT_ROOT/gomap-main"
JSONBENCH_MAIN_DIR="$OUT_ROOT/jsonbench-main"
cleanup_worktrees() {
  if [[ "$KEEP_WORKTREES" != "1" ]]; then
    git -C "$GOMAP_REPO_RESOLVED" worktree remove --force "$GOMAP_MAIN_DIR" >/dev/null 2>&1 || true
    git -C "$JSONBENCH_REPO_RESOLVED" worktree remove --force "$JSONBENCH_MAIN_DIR" >/dev/null 2>&1 || true
  fi
}
trap cleanup_worktrees EXIT

create_main_worktree "$GOMAP_REPO_RESOLVED" "$GOMAP_MAIN_DIR"
create_main_worktree "$JSONBENCH_REPO_RESOLVED" "$JSONBENCH_MAIN_DIR"

GOMAP_HEAD="$(git -C "$GOMAP_MAIN_DIR" rev-parse HEAD)"
JSONBENCH_HEAD="$(git -C "$JSONBENCH_MAIN_DIR" rev-parse HEAD)"
TREEDB_DIR="$JSONBENCH_MAIN_DIR/treedb"

scale_for_rows() {
  case "$1" in
    1000000) echo "1m" ;;
    10000000) echo "10m" ;;
    100000000) echo "100m" ;;
    1000000000) echo "1000m" ;;
    *) echo "subset" ;;
  esac
}

run_matrix() {
  local out_dir="$1" rows="$2" layouts="$3" suite="$4"
  local scale subset_rows
  scale="$(scale_for_rows "$rows")"
  subset_rows="$rows"
  mkdir -p "$out_dir"
  (
    cd "$TREEDB_DIR"
    backup_dir="$(mktemp -d "$OUT_ROOT/gomod_backup_XXXXXX")"
    cp go.mod "$backup_dir/go.mod"
    cp go.sum "$backup_dir/go.sum"
    restore() { cp "$backup_dir/go.mod" go.mod; cp "$backup_dir/go.sum" go.sum; rm -rf "$backup_dir"; }
    trap restore EXIT
    go mod edit -replace=github.com/snissn/gomap="$GOMAP_MAIN_DIR"
    env GOWORK=off \
      DATA_DIR="$DATA_DIR" \
      OUT_DIR="$out_dir" \
      SCALES="$scale" \
      SUBSET_ROWS="$subset_rows" \
      FORMATS="json" \
      STORAGE_LAYOUTS="$layouts" \
      SUITE="$suite" \
      QUERY_CELLS="q1 q2 q3 q4 q5" \
      TRIES="$TRIES" \
      PROFILE="$PROFILE" \
      DATA_ROOT="$DATA_ROOT" \
      BATCH_SIZE="$BATCH_SIZE" \
      COMPACT_AFTER_LOAD="$COMPACT_AFTER_LOAD" \
      VALIDATE_RECONSTRUCTION="$VALIDATE_RECONSTRUCTION" \
      ./run_matrix.sh
  )
}

profile_focuses_expanded() {
  if [[ "$PROFILE_FOCUSES" == "all" ]]; then
    printf '%s\n' q1_prepared q2_prepared q3_prepared q4_prepared q5_prepared q1_direct q2_direct q3_direct q4_direct q5_direct
  else
    # shellcheck disable=SC2086
    printf '%s\n' $PROFILE_FOCUSES
  fi
}

bench_regex_for_focus() {
  case "$1" in
    q1_prepared) echo '^BenchmarkColumnPhysicalQ1DenseTypedColumn1950/prepared_runner_Run$' ;;
    q1_direct) echo '^BenchmarkColumnPhysicalQ1DenseTypedColumn1950/direct_RunColumnPhysicalQuery$' ;;
    q2_prepared) echo '^BenchmarkTypedColumnQ2SortedGroupedDistinct1950/prepared/sorted_prefix$' ;;
    q2_direct) echo '^BenchmarkTypedColumnQ2SortedGroupedDistinct1950/direct/sorted_prefix$' ;;
    q3_prepared) echo '^BenchmarkColumnPhysicalQ3DenseTypedColumn1950/prepared_runner_Run$' ;;
    q3_direct) echo '^BenchmarkColumnPhysicalQ3DenseTypedColumn1950/direct_RunColumnPhysicalQuery$' ;;
    q4_prepared) echo '^BenchmarkTypedColumnQ4BTopK1950/prepared/clickhouse_mark_pruned$' ;;
    q4_direct) echo '^BenchmarkTypedColumnQ4BTopK1950/direct/clickhouse_mark_pruned$' ;;
    q5_prepared) echo '^BenchmarkColumnPhysicalQ5DenseTypedColumn1950/prepared_runner_Run$' ;;
    q5_direct) echo '^BenchmarkColumnPhysicalQ5DenseTypedColumn1950/direct_RunColumnPhysicalQuery$' ;;
    *) echo "$1" ;;
  esac
}

run_profiles() {
  local profiles_dir="$OUT_ROOT/profiles"
  local focus regex dir status
  mkdir -p "$profiles_dir"
  echo "==> TreeDB focused profiles" >&2
  echo "    focuses: $PROFILE_FOCUSES" >&2
  echo "    out:     $profiles_dir" >&2
  while IFS= read -r focus; do
    [[ -n "$focus" ]] || continue
    regex="$(bench_regex_for_focus "$focus")"
    dir="$profiles_dir/$focus"
    mkdir -p "$dir"
    echo "==> profile $focus ($regex)" >&2
    status=0
    (
      cd "$GOMAP_MAIN_DIR"
      env GOWORK=off go test ./TreeDB/collections \
        -run '^$' \
        -bench "$regex" \
        -benchmem \
        -benchtime="$PROFILE_BENCHTIME" \
        -count="$PROFILE_COUNT" \
        -cpuprofile "$dir/cpu.pprof"
    ) > "$dir/bench_cpu.out" 2>&1 || status=$?
    cp "$dir/bench_cpu.out" "$dir/bench.out"
    if [[ "$status" -ne 0 ]]; then
      echo "cpu profile $focus failed with status $status; see $dir/bench_cpu.out" | tee "$dir/run_error.txt" >&2
      if [[ "$PROFILE_ALLOW_ERRORS" == "0" ]]; then
        return "$status"
      fi
      continue
    fi
    status=0
    (
      cd "$GOMAP_MAIN_DIR"
      env GOWORK=off go test ./TreeDB/collections \
        -run '^$' \
        -bench "$regex" \
        -benchmem \
        -benchtime="$PROFILE_BENCHTIME" \
        -count="$PROFILE_COUNT" \
        -memprofile "$dir/allocs.pprof" \
        -memprofilerate=1
    ) > "$dir/bench_allocs.out" 2>&1 || status=$?
    if [[ "$status" -ne 0 ]]; then
      echo "alloc profile $focus failed with status $status; see $dir/bench_allocs.out" | tee "$dir/run_error.txt" >&2
      if [[ "$PROFILE_ALLOW_ERRORS" == "0" ]]; then
        return "$status"
      fi
    fi
    (cd "$GOMAP_MAIN_DIR" && go tool pprof -top -nodecount=30 "$dir/cpu.pprof") > "$dir/cpu_top.txt" 2>&1 || true
    (cd "$GOMAP_MAIN_DIR" && go tool pprof -top -nodecount=30 -alloc_space "$dir/allocs.pprof") > "$dir/allocs_top.txt" 2>&1 || true
    (cd "$GOMAP_MAIN_DIR" && go tool pprof -top -nodecount=30 -alloc_objects "$dir/allocs.pprof") > "$dir/alloc_objects_top.txt" 2>&1 || true
  done < <(profile_focuses_expanded)
  printf '%s\n' "$profiles_dir"
}

HEADLINE_OUT="$OUT_ROOT/headline_${ROWS}_$(date -u +%Y%m%d_%H%M%S)"
echo "==> TreeDB headline metrics"
echo "    gomap main:     $GOMAP_HEAD"
echo "    JSONBench main: $JSONBENCH_HEAD"
echo "    data:           $DATA_DIR"
echo "    out:            $HEADLINE_OUT"
run_matrix "$HEADLINE_OUT" "$ROWS" "$STORAGE_LAYOUTS" "$SUITE"
HEADLINE_REPORT="$HEADLINE_OUT/report.json"
HEADLINE_RESULT="$(find "$HEADLINE_OUT" -mindepth 2 -maxdepth 2 -name result.json | head -1 || true)"

PARITY_REPORT=""
PROFILES_DIR=""
if [[ "$RUN_PARITY" == "1" ]]; then
  PARITY_OUT="$OUT_ROOT/parity_${PARITY_ROWS}_$(date -u +%Y%m%d_%H%M%S)"
  echo "==> TreeDB row/direct/prepared parity metrics"
  echo "    rows: $PARITY_ROWS"
  echo "    out:  $PARITY_OUT"
  run_matrix "$PARITY_OUT" "$PARITY_ROWS" "row column-store-full column-store-full-prepared" "full"
  PARITY_REPORT="$PARITY_OUT/report.json"
fi

PROFILE_INSIGHTS_MD=""
if [[ "$RUN_PROFILES" == "1" ]]; then
  PROFILES_DIR="$(run_profiles | tail -1)"
fi

cat > "$OUT_ROOT/heads.env" <<EOF
GOMAP_HEAD=$GOMAP_HEAD
JSONBENCH_HEAD=$JSONBENCH_HEAD
TREEDB_REPORT_JSON=$HEADLINE_REPORT
TREEDB_RESULT_JSON=$HEADLINE_RESULT
TREEDB_PARITY_REPORT_JSON=$PARITY_REPORT
TREEDB_PROFILES_DIR=$PROFILES_DIR
TREEDB_PROFILE_INSIGHTS_MD=$PROFILE_INSIGHTS_MD
EOF

parser="$script_dir/treedb_jsonbench_breakdown.py"
if [[ "$RUN_BREAKDOWN" == "1" && -x "$parser" && -f "$HEADLINE_REPORT" ]]; then
  breakdown_args=(--treedb-report "$HEADLINE_REPORT" --gomap-head "$GOMAP_HEAD" --jsonbench-head "$JSONBENCH_HEAD")
  [[ -n "$HEADLINE_RESULT" && -f "$HEADLINE_RESULT" ]] && breakdown_args+=(--treedb-result "$HEADLINE_RESULT")
  [[ -n "$PARITY_REPORT" && -f "$PARITY_REPORT" ]] && breakdown_args+=(--parity-report "$PARITY_REPORT")
  [[ -n "$CLICKHOUSE_RESULT" ]] && breakdown_args+=(--clickhouse-result "$CLICKHOUSE_RESULT")
  [[ -n "$COLGRANULE_RAW" ]] && breakdown_args+=(--colgranule-raw "$COLGRANULE_RAW")
  python3 "$parser" "${breakdown_args[@]}" | tee "$OUT_ROOT/breakdown.md"
fi

insights="$script_dir/profile_insights.py"
if [[ "$RUN_PROFILES" == "1" && -x "$insights" && -n "$PROFILES_DIR" && -d "$PROFILES_DIR" ]]; then
  PROFILE_INSIGHTS_MD="$OUT_ROOT/profile_insights.md"
  insight_args=(--profiles-dir "$PROFILES_DIR")
  [[ -f "$HEADLINE_REPORT" ]] && insight_args+=(--treedb-report "$HEADLINE_REPORT")
  python3 "$insights" "${insight_args[@]}" | tee "$PROFILE_INSIGHTS_MD"
fi
if [[ -f "$OUT_ROOT/heads.env" ]]; then
  tmp_heads="$OUT_ROOT/heads.env.tmp"
  grep -v '^TREEDB_PROFILE_INSIGHTS_MD=' "$OUT_ROOT/heads.env" > "$tmp_heads" || true
  echo "TREEDB_PROFILE_INSIGHTS_MD=$PROFILE_INSIGHTS_MD" >> "$tmp_heads"
  mv "$tmp_heads" "$OUT_ROOT/heads.env"
fi

echo "TREEDB_METRICS_OUT_ROOT=$OUT_ROOT"
echo "TREEDB_METRICS_REPORT_JSON=$HEADLINE_REPORT"
echo "TREEDB_METRICS_RESULT_JSON=$HEADLINE_RESULT"
echo "TREEDB_METRICS_PARITY_REPORT_JSON=$PARITY_REPORT"
echo "TREEDB_METRICS_PROFILES_DIR=$PROFILES_DIR"
echo "TREEDB_METRICS_PROFILE_INSIGHTS_MD=$PROFILE_INSIGHTS_MD"
echo "TREEDB_METRICS_GOMAP_HEAD=$GOMAP_HEAD"
echo "TREEDB_METRICS_JSONBENCH_HEAD=$JSONBENCH_HEAD"

if [[ "$REMOTE_CHILD" != "1" ]]; then
  echo "==> outputs: $OUT_ROOT"
fi
