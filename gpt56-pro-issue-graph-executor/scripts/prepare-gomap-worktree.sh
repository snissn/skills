#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Prepare or resume one isolated snissn/gomap issue worktree.

Usage:
  prepare-gomap-worktree.sh \
    --repo /path/to/gomap \
    --issue 4053 \
    --slug compat-diff \
    --base-sha <adapter-resolved-40-or-64-hex-commit> \
    [--work-root /path/to/work] \
    [--branch gpt56/issue-4053-compat-diff] \
    [--no-fetch] [--build] [--smoke]

The immutable --base-sha is required. Unless --no-fetch is used, the helper
refreshes all normal origin refs before branch reconciliation.
The script does not install packages, run go mod tidy, push, or open a PR.
EOF
}

REPO=""
ISSUE=""
SLUG=""
EXPECTED_BASE_SHA=""
WORK_ROOT=""
BRANCH=""
DO_FETCH=1
DO_BUILD=0
DO_SMOKE=0

while (($#)); do
  case "$1" in
    --repo)
      REPO="${2:?missing value for --repo}"
      shift 2
      ;;
    --issue)
      ISSUE="${2:?missing value for --issue}"
      shift 2
      ;;
    --slug)
      SLUG="${2:?missing value for --slug}"
      shift 2
      ;;
    --base-sha)
      EXPECTED_BASE_SHA="${2:?missing value for --base-sha}"
      shift 2
      ;;
    --work-root)
      WORK_ROOT="${2:?missing value for --work-root}"
      shift 2
      ;;
    --branch)
      BRANCH="${2:?missing value for --branch}"
      shift 2
      ;;
    --no-fetch)
      DO_FETCH=0
      shift
      ;;
    --build)
      DO_BUILD=1
      shift
      ;;
    --smoke)
      DO_SMOKE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$REPO" || -z "$ISSUE" || -z "$SLUG" || -z "$EXPECTED_BASE_SHA" ]]; then
  usage >&2
  exit 2
fi

if ! [[ "$ISSUE" =~ ^[0-9]+$ ]]; then
  printf 'issue must be numeric: %s\n' "$ISSUE" >&2
  exit 2
fi

if ! [[ "$SLUG" =~ ^[a-z0-9]+([a-z0-9-]*[a-z0-9])?$ ]]; then
  printf 'slug must use lowercase letters, numbers, and hyphens: %s\n' "$SLUG" >&2
  exit 2
fi

if ! [[ "$EXPECTED_BASE_SHA" =~ ^([0-9a-fA-F]{40}|[0-9a-fA-F]{64})$ ]]; then
  printf 'base SHA must be an exact 40- or 64-character hexadecimal commit: %s\n' \
    "$EXPECTED_BASE_SHA" >&2
  exit 2
fi
EXPECTED_BASE_SHA="${EXPECTED_BASE_SHA,,}"

REPO="${REPO/#\~/$HOME}"
REPO="$(python3 - "$REPO" <<'PY'
import os
import sys
print(os.path.abspath(os.path.expanduser(sys.argv[1])))
PY
)"

if [[ -z "$WORK_ROOT" ]]; then
  WORK_ROOT="$(dirname "$REPO")/gomap-gpt56-work"
fi
WORK_ROOT="${WORK_ROOT/#\~/$HOME}"
WORK_ROOT="$(python3 - "$WORK_ROOT" <<'PY'
import os
import sys
print(os.path.abspath(os.path.expanduser(sys.argv[1])))
PY
)"

if [[ -z "$BRANCH" ]]; then
  BRANCH="gpt56/issue-${ISSUE}-${SLUG}"
fi

for command in git go make python3 awk; do
  command -v "$command" >/dev/null || {
    printf 'missing required command: %s\n' "$command" >&2
    exit 10
  }
done

CC_BIN="${CC:-cc}"
command -v "$CC_BIN" >/dev/null || {
  printf 'missing configured C compiler: %s\n' "$CC_BIN" >&2
  exit 10
}

if ! git -C "$REPO" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if [[ -e "$REPO" && -n "$(find "$REPO" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]]; then
    printf 'repo path exists but is not a git worktree: %s\n' "$REPO" >&2
    printf '%s\n' 'Use the build-gomap archive fallback for testing, or choose an empty path for clone.' >&2
    exit 20
  fi
  mkdir -p "$(dirname "$REPO")"
  if ! git clone https://github.com/snissn/gomap.git "$REPO"; then
    printf '%s\n' 'git clone failed. Treat this as source acquisition, not a compile failure.' >&2
    printf '%s\n' 'Follow build-gomap: use a pinned GitHub/module-proxy archive or an approved runtime download facility.' >&2
    exit 20
  fi
fi

if [[ "$(git -C "$REPO" config --get remote.origin.url || true)" != *"snissn/gomap"* ]]; then
  printf 'warning: origin does not visibly identify snissn/gomap: %s\n' \
    "$(git -C "$REPO" config --get remote.origin.url || true)" >&2
fi

if ((DO_FETCH)); then
  if ! git -C "$REPO" fetch --prune origin "+refs/heads/*:refs/remotes/origin/*"; then
    printf '%s\n' 'fetch failed; remote branch freshness is unverified.' >&2
    printf '%s\n' 'Retry with working remote access, or use --no-fetch only after separately verifying the recorded base and issue-branch objects.' >&2
    exit 20
  fi
fi

if ! BASE_SHA="$(git -C "$REPO" rev-parse --verify "${EXPECTED_BASE_SHA}^{commit}" 2>/dev/null)"; then
  printf 'immutable base commit is unavailable locally: %s\n' "$EXPECTED_BASE_SHA" >&2
  printf '%s\n' 'Fetch the recorded ref or use the build-gomap pinned-source fallback, then retry.' >&2
  exit 20
fi
BASE_SHA="${BASE_SHA,,}"
if [[ "$BASE_SHA" != "$EXPECTED_BASE_SHA" ]]; then
  printf 'resolved base %s does not exactly match requested base %s\n' \
    "$BASE_SHA" "$EXPECTED_BASE_SHA" >&2
  exit 20
fi

verify_local_branch_against_remote() {
  local local_ref="refs/heads/$BRANCH"
  local remote_ref="refs/remotes/origin/$BRANCH"
  local local_tip remote_tip

  if ! git -C "$REPO" show-ref --verify --quiet "$local_ref" || \
     ! git -C "$REPO" show-ref --verify --quiet "$remote_ref"; then
    return 0
  fi

  local_tip="$(git -C "$REPO" rev-parse "$local_ref")"
  remote_tip="$(git -C "$REPO" rev-parse "$remote_ref")"
  if [[ "$local_tip" == "$remote_tip" ]]; then
    return 0
  fi

  if git -C "$REPO" merge-base --is-ancestor "$local_tip" "$remote_tip"; then
    printf 'local issue branch %s is behind fetched origin/%s: local=%s remote=%s\n' \
      "$BRANCH" "$BRANCH" "$local_tip" "$remote_tip" >&2
    printf '%s\n' 'Fast-forward or otherwise synchronize the local branch explicitly, then retry.' >&2
    exit 32
  fi

  if git -C "$REPO" merge-base --is-ancestor "$remote_tip" "$local_tip"; then
    printf 'warning: local issue branch %s is ahead of origin/%s: local=%s remote=%s\n' \
      "$BRANCH" "$BRANCH" "$local_tip" "$remote_tip" >&2
    return 0
  fi

  printf 'local issue branch %s has diverged from fetched origin/%s: local=%s remote=%s\n' \
    "$BRANCH" "$BRANCH" "$local_tip" "$remote_tip" >&2
  printf '%s\n' 'Reconcile the branch explicitly without discarding either side, then retry.' >&2
  exit 32
}

verify_local_branch_against_remote

CANONICAL_WORKTREE="$WORK_ROOT/worktrees/issue-$ISSUE"
EXISTING_BRANCH_WORKTREE="$(
  git -C "$REPO" worktree list --porcelain |
    awk -v target="refs/heads/$BRANCH" '
      /^worktree / { path = substr($0, 10) }
      $0 == "branch " target { print path; exit }
    '
)"
if [[ -n "$EXISTING_BRANCH_WORKTREE" ]]; then
  WORKTREE="$EXISTING_BRANCH_WORKTREE"
  if [[ "$WORKTREE" != "$CANONICAL_WORKTREE" ]]; then
    printf 'warning: reusing existing worktree for branch %s: %s\n' \
      "$BRANCH" "$WORKTREE" >&2
  fi
else
  WORKTREE="$CANONICAL_WORKTREE"
fi

CACHE_ROOT="$WORK_ROOT/cache"
LOG_DIR="$WORK_ROOT/logs/issue-$ISSUE"
ARTIFACT_DIR="$WORK_ROOT/artifacts/issue-$ISSUE"
TMP_DIR="$WORK_ROOT/tmp/issue-$ISSUE"

mkdir -p \
  "$WORK_ROOT/worktrees" \
  "$CACHE_ROOT/go-mod" \
  "$CACHE_ROOT/go-build" \
  "$LOG_DIR" \
  "$ARTIFACT_DIR" \
  "$TMP_DIR"

if [[ -d "$WORKTREE/.git" || -f "$WORKTREE/.git" ]]; then
  CURRENT_BRANCH="$(git -C "$WORKTREE" branch --show-current)"
  if [[ "$CURRENT_BRANCH" != "$BRANCH" ]]; then
    printf 'existing worktree uses branch %s, expected %s: %s\n' \
      "$CURRENT_BRANCH" "$BRANCH" "$WORKTREE" >&2
    exit 30
  fi
else
  if [[ -e "$WORKTREE" ]]; then
    printf 'worktree path exists but is not the expected git worktree: %s\n' \
      "$WORKTREE" >&2
    printf '%s\n' 'Inspect and clean or relocate it explicitly before retrying.' >&2
    exit 30
  fi
  if git -C "$REPO" show-ref --verify --quiet "refs/heads/$BRANCH"; then
    git -C "$REPO" worktree add "$WORKTREE" "$BRANCH"
  elif git -C "$REPO" show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
    git -C "$REPO" worktree add -b "$BRANCH" "$WORKTREE" "origin/$BRANCH"
  else
    git -C "$REPO" worktree add -b "$BRANCH" "$WORKTREE" "$BASE_SHA"
  fi
fi

CURRENT_HEAD="$(git -C "$WORKTREE" rev-parse HEAD)"
if ! git -C "$WORKTREE" merge-base --is-ancestor "$BASE_SHA" "$CURRENT_HEAD"; then
  printf 'issue branch %s at %s does not contain requested base %s\n' \
    "$BRANCH" "$CURRENT_HEAD" "$BASE_SHA" >&2
  printf '%s\n' 'Synchronize the branch explicitly, rerun affected tests, then invoke this helper again.' >&2
  exit 31
fi

if [[ ! -f "$WORKTREE/go.mod" || ! -f "$WORKTREE/Makefile" ]]; then
  printf 'worktree does not look like gomap: %s\n' "$WORKTREE" >&2
  exit 40
fi

grep -Fx 'module github.com/snissn/gomap' "$WORKTREE/go.mod" >/dev/null || {
  printf 'unexpected module identity in %s/go.mod\n' "$WORKTREE" >&2
  exit 40
}

GO_VERSION="$(go env GOVERSION)"
python3 - "$GO_VERSION" <<'PY'
import re
import sys
m = re.fullmatch(r"go(\d+)\.(\d+)(?:\.\d+)?", sys.argv[1])
if not m:
    raise SystemExit(f"cannot parse Go version: {sys.argv[1]}")
major, minor = map(int, m.groups())
if (major, minor) < (1, 26):
    raise SystemExit(f"Go 1.26+ required, found {sys.argv[1]}")
PY

ENV_FILE="$WORK_ROOT/env-issue-$ISSUE.sh"
cat >"$ENV_FILE" <<EOF
export GOMAP_REPO_DIR=$(printf '%q' "$REPO")
export GOMAP_WORK_ROOT=$(printf '%q' "$WORK_ROOT")
export GOMAP_WORKTREE=$(printf '%q' "$WORKTREE")
export GOMAP_BASE_SHA=$(printf '%q' "$BASE_SHA")
export GOMAP_ISSUE=$(printf '%q' "$ISSUE")
export GOMAP_BRANCH=$(printf '%q' "$BRANCH")
export GOMODCACHE=$(printf '%q' "$CACHE_ROOT/go-mod")
export GOCACHE=$(printf '%q' "$CACHE_ROOT/go-build")
export TMPDIR=$(printf '%q' "$TMP_DIR")
export CGO_ENABLED=1
export CC=$(printf '%q' "$CC_BIN")
export GOFLAGS=-p=1
export GOMAXPROCS=2
export GOWORK=off
EOF

run_in_lane() {
  (
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    cd "$WORKTREE"
    "$@"
  )
}

if ((DO_BUILD)); then
  set -o pipefail
  run_in_lane make build-treedb 2>&1 | tee "$LOG_DIR/build-treedb.log"
  run_in_lane make build-mongo-gateway 2>&1 | tee "$LOG_DIR/build-mongo-gateway.log"
fi

if ((DO_SMOKE)); then
  set -o pipefail
  run_in_lane go test ./TreeDB/mongo_gateway -count=1 2>&1 | tee "$LOG_DIR/mongo-gateway-smoke.log"
fi

HEAD_SHA="$(git -C "$WORKTREE" rev-parse HEAD)"
STATUS="$(git -C "$WORKTREE" status --short)"
cat <<EOF
gomap issue worktree ready
  issue:       $ISSUE
  branch:      $BRANCH
  worktree:    $WORKTREE
  base sha:    $BASE_SHA
  current sha: $HEAD_SHA
  Go:          $GO_VERSION
  CC:          $CC_BIN
  env file:    $ENV_FILE
  logs:        $LOG_DIR
  artifacts:   $ARTIFACT_DIR
EOF

if [[ -n "$STATUS" ]]; then
  printf '%s\n' '  status:       dirty'
  printf '%s\n' "$STATUS"
else
  printf '%s\n' '  status:       clean'
fi
