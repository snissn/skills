# Local Execution For `snissn/gomap`

Load the repository skill `build-gomap` before using this reference. That skill remains authoritative for full source/toolchain acquisition and its restricted-network fallbacks. This file adapts it for multi-issue graph execution.

## Goals

A gomap lane should be:

- pinned to an exact base SHA;
- isolated from sibling issue work;
- buildable with Go 1.26+, CGO, Make, and a C compiler;
- tested with issue-specific commands before broad suites;
- publishable through local git or the GitHub adapter;
- reproducible by a later invocation.

## Resolve The Exact Base

Use the GitHub adapter to resolve:

```text
repository: snissn/gomap
base branch: normally main
base SHA: exact current commit
issue branch/PR: existing ownership if any
```

Record the full adapter-resolved SHA in graph state and export it as `GOMAP_BASE_SHA` before creating a worktree. Pass that immutable SHA to the helper separately from any optional fetch ref; do not silently build a moving `main`.

## Preferred Source Path

Reuse an existing clean gomap checkout when available.

```sh
export GOMAP_REPO_DIR="${GOMAP_REPO_DIR:-$HOME/src/gomap}"
git -C "$GOMAP_REPO_DIR" status --short
git -C "$GOMAP_REPO_DIR" remote -v
git -C "$GOMAP_REPO_DIR" rev-parse HEAD
```

If no checkout exists and shell GitHub access works:

```sh
git clone https://github.com/snissn/gomap.git "$GOMAP_REPO_DIR"
git -C "$GOMAP_REPO_DIR" fetch origin main
```

Use `scripts/prepare-gomap-worktree.sh` to create or resume one issue worktree.

## Restricted-Network Source Fallback

A shell DNS or GitHub failure is a source-acquisition failure, not a compiler failure.

Use the first available fallback:

1. repository already mounted by the runtime;
2. platform download facility for a GitHub source archive pinned to the adapter-resolved SHA;
3. `build-gomap` Go module proxy archive flow;
4. another approved internal mirror.

When using a source archive:

- verify repository identity and exact commit/archive identity;
- keep the archive checksum;
- do not claim a local git base unless you initialized and verified one;
- use the archive for builds/tests;
- publish changed files through the GitHub adapter if local push is unavailable.

For a branch or PR patch, materialize the exact base source, then apply the adapter-fetched patch or the locally produced diff before testing. Record the base SHA and patch head in the artifact directory.

Never expose credential-bearing proxy URLs in logs, state comments, PR bodies, or artifacts.

## Toolchain And Prerequisites

Required:

```text
Go 1.26+
CGO_ENABLED=1
make
gcc or another supported C compiler
git for normal worktree flow
python3
```

Check:

```sh
set -euo pipefail

for command in git go make python3; do
  command -v "$command" >/dev/null || {
    printf 'missing required command: %s\n' "$command" >&2
    exit 1
  }
done

export CC="${CC:-cc}"
command -v "$CC" >/dev/null || {
  printf 'missing configured C compiler: %s\n' "$CC" >&2
  exit 1
}

go version
go env GOVERSION GOOS GOARCH CGO_ENABLED
```

If the host Go version is too old, follow `build-gomap` to provision the Go 1.26 toolchain module. Do not rely on an automatic toolchain download when network access is uncertain.

Do not run a package manager when prerequisites already exist.

## Shared Workspace

Use one graph workspace with shared download/module/build caches and isolated worktrees/data:

```sh
export GOMAP_WORK_ROOT="${GOMAP_WORK_ROOT:-$PWD/gomap-gpt56-work}"
export GOMODCACHE="${GOMODCACHE:-$GOMAP_WORK_ROOT/cache/go-mod}"
export GOCACHE="${GOCACHE:-$GOMAP_WORK_ROOT/cache/go-build}"
export GOMAP_LOG_ROOT="$GOMAP_WORK_ROOT/logs"
export GOMAP_ARTIFACT_ROOT="$GOMAP_WORK_ROOT/artifacts"

mkdir -p \
  "$GOMODCACHE" \
  "$GOCACHE" \
  "$GOMAP_LOG_ROOT" \
  "$GOMAP_ARTIFACT_ROOT" \
  "$GOMAP_WORK_ROOT/worktrees"
```

Shared Go caches reduce repeated dependency and compile cost. Each lane must use separate:

- worktree;
- database/test data directory;
- temporary directory;
- profile and benchmark artifact directory;
- server port.

## Build Environment

Use conservative defaults from `build-gomap`:

```sh
export CGO_ENABLED=1
export CC="${CC:-cc}"
export GOFLAGS="${GOFLAGS:--p=1}"
export GOMAXPROCS="${GOMAXPROCS:-2}"
export GOWORK=off
```

For multiple active lanes:

- no more than two heavy builds/tests at once;
- avoid concurrent broad `go test ./...`;
- use focused package tests in parallel;
- collect every process result before ending the invocation.

Do not run `go mod tidy` merely to prepare a build.

## Worktree Flow

For issue `4053`:

```sh
bash <skill-dir>/scripts/prepare-gomap-worktree.sh \
  --repo "$GOMAP_REPO_DIR" \
  --issue 4053 \
  --slug compat-diff \
  --base-sha "$GOMAP_BASE_SHA" \
  --fetch-ref main \
  --work-root "$GOMAP_WORK_ROOT"
```

The helper:

- accepts a primary checkout or an existing linked Git worktree as `--repo`;
- reuses an existing issue worktree;
- adopts an existing local or remote branch only when it contains the requested exact base SHA;
- refuses stale-base adoption and requires an explicit branch synchronization plus test rerun instead of silently relabeling the lane;
- otherwise creates `gpt56/issue-4053-compat-diff`;
- prints exact base, branch, worktree, and environment paths;
- optionally runs build/smoke checks.

Always inspect:

```sh
git -C "$WORKTREE" status --short
git -C "$WORKTREE" log --oneline --decorate -n 8
git -C "$WORKTREE" diff --stat "$BASE_SHA"...HEAD
```

## Read Repository Policy

Before implementation, read at least:

```text
AGENTS.md
CONTRIBUTING.md
go.mod
Makefile
.github/PULL_REQUEST_TEMPLATE/opt_sprint.md
the parent and child issue bodies
relevant docs/contracts and compatibility files
```

The current repository requires Go 1.26+ and treats tests as the north star. Semantics and durability changes must update the relevant contracts/spec tests.

## Build Targets For Mongo Graph Work

First isolate core TreeDB compilation:

```sh
make build-treedb
```

For Mongo gateway changes:

```sh
make build-mongo-gateway
```

Attempt aggregate build only after the relevant targets succeed:

```sh
make build
```

A cold optional dependency fetch failure in `make build` does not negate a successful focused build. Preserve logs and state the boundary precisely.

Useful log shape:

```sh
LANE_ARTIFACT="$GOMAP_ARTIFACT_ROOT/issue-4053/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$LANE_ARTIFACT"

set -o pipefail
make build-mongo-gateway 2>&1 | tee "$LANE_ARTIFACT/build-mongo-gateway.log"
```

## Test Selection

Use the child issue’s exact commands first.

Common Mongo gateway baseline:

```sh
GOWORK=off go test ./TreeDB/mongo_gateway -count=1
```

When the command harness changes:

```sh
GOWORK=off go test ./cmd/mongo_gateway_bench -count=1
```

When collection/index behavior changes:

```sh
GOWORK=off go test ./TreeDB/collections -count=1
```

When persistence or root metadata changes, add affected packages such as:

```sh
GOWORK=off go test ./TreeDB/db ./TreeDB/caching -count=1
```

For concurrency changes, run a focused race subset:

```sh
GOWORK=off go test -race ./TreeDB/mongo_gateway -run '<focused-regex>' -count=1
```

Use forced ValueLog pointers, command-WAL, checkpoint/reopen, corruption, and maintenance tests when the issue requires them.

Do not replace issue-specific tests with one broad suite. Broad tests supplement focused evidence.

## Red-Green Evidence

Before implementation:

```sh
GOWORK=off go test <affected-package> -run '<new-test>' -count=1
```

Capture the intended failure. After implementation, rerun the exact command and preserve the result with the head SHA.

An allowed exception must state why a meaningful red test is unavailable and what alternative evidence bounds the change.

## Performance Evidence

Classify each PR before implementation.

For performance-sensitive gomap work, record:

- exact baseline and candidate SHAs;
- identical command and fixture;
- hardware/OS/Go context;
- timed boundary;
- throughput or latency;
- `B/op` and `allocs/op` where relevant;
- peak/live memory when residency is at risk;
- storage, build, checkpoint, or maintenance overhead;
- domain counters such as candidates, documents fetched, roots applied, bytes read/written, or sync counts.

Use separate artifact directories for baseline and candidate. Do not compare a warm candidate to a cold baseline without saying so.

## Concurrent Test Sessions

When the shell tool supports named sessions, a lane may start a focused test and switch to another lane:

```sh
# Session issue-4053-test
GOWORK=off go test ./TreeDB/mongo_gateway -run 'Test.*CompatDiff.*' -count=1

# Session issue-4054-test
GOWORK=off go test ./TreeDB/mongo_gateway -run 'Test.*Stats.*' -count=1
```

Rules:

- observe both exits in the current invocation;
- do not start more than two heavy jobs;
- use separate worktrees and temp/data directories;
- cancel obsolete runs after a new head is published;
- never promise the process will finish later.

## Publishing Without Shell GitHub Access

If local git push works, use normal branch/commit/push.

If it does not:

1. keep the tested local diff against the exact remote base;
2. fetch current remote file SHAs through the GitHub adapter;
3. create/update the issue branch through adapter Git data or contents operations;
4. verify the remote head and diff;
5. open or update the PR through the adapter;
6. record that local source acquisition and remote publication used different transports.

Prefer an atomic multi-file adapter commit:

```text
create_branch
create_blob for changed files
create_tree based on remote base tree
create_commit
update_ref
```

Fall back to serialized `create_file`/`update_file` writes when needed. Never update the same path concurrently.

After adapter publication, fetch the PR diff and verify it matches the locally tested patch.

## Dependency Failures

Classify failures accurately:

| Failure | Classification |
| --- | --- |
| DNS, proxy timeout, missing module download | dependency/source acquisition |
| missing Go 1.26 toolchain | environment |
| missing configured C compiler or CGO library | environment |
| Go compiler/type error in repository source | compile failure |
| test assertion failure | behavior/correctness |
| benchmark regression | performance blocker |
| shell cannot push but adapter can | publication transport fallback |

Do not claim gomap fails to compile when the compiler never received all dependencies.

## Reproducibility Record

Each lane handoff should include:

```text
repo/base SHA:
branch/head SHA:
source acquisition method:
Go version:
GOOS/GOARCH:
CGO/CC:
GOPROXY class (public/internal; never credentials):
worktree:
build commands/results:
test commands/results:
benchmark/profile artifacts:
publication method:
```

## Closeout

Before a gomap PR is considered mature:

- [ ] exact issue scope is implemented;
- [ ] focused tests pass on the current head;
- [ ] broader affected tests pass;
- [ ] persistence/race/fault evidence matches the risk;
- [ ] required benchmark evidence is current;
- [ ] build target succeeds, or an acquisition-only limitation is documented;
- [ ] PR body contains exact commands and artifact paths;
- [ ] remote diff matches the tested local patch;
- [ ] latest-head CI and review gates are satisfied before merge.
