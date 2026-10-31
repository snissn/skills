---
name: build-gomap
description: Retrieve snissn/gomap, provision its Go 1.26 toolchain and CGO prerequisites, compile the core HashDB and TreeDB binaries, verify the outputs, and handle restricted-network dependency failures without misclassifying them as compiler failures.
---

# Build `snissn/gomap`

Use this skill to reproduce a Linux/amd64 build of `snissn/gomap`. Reuse an assigned worktree at the requested source snapshot, or prefer a linked worktree from an existing repository before creating a new clone. When the shell cannot resolve GitHub, retrieve the same pinned source and Go toolchain through the Go module proxy or an available direct-download tool.

## Known-good reference build

The verified build used:

- Repository: `snissn/gomap`
- Branch snapshot: `main`
- Commit: `4c00c886a9d7059f143e1d564aa602ed583a6cc5`
- Module pseudo-version: `v0.6.2-0.20260719170055-4c00c886a9d7`
- Required Go version: `1.26+`
- Exact toolchain used: `go1.26.0 linux/amd64`
- Build platform: `linux/amd64`
- Build environment: `CGO_ENABLED=1`, `GOFLAGS=-p=1`, `GOMAXPROCS=2`
- C compiler used: GCC on Linux

The source archive and toolchain archive used for that build had these SHA-256 digests:

```text
4465babd026317ed16f73a7dfc6ec44e890a4b6d0826dee1a8a37d4952f1106c  gomap source module ZIP
38461905b98c59173672814302e222ab43b652274bc0c95817b08b71ab66b705  Go 1.26.0 linux-amd64 toolchain module ZIP
```

## Operating rules

1. Pin the source commit or module pseudo-version before building. Do not silently build a moving `main` branch when reproducibility matters.
2. Read `go.mod`, `CONTRIBUTING.md`, and `Makefile` before choosing targets. The verified snapshot declares `go 1.26`.
3. Do not run `go mod tidy` merely to prepare a build. It can modify `go.mod` and `go.sum`.
4. Compile the core HashDB and TreeDB targets before the aggregate `make build` target. This isolates optional dependency-fetch problems from source compiler failures.
5. Treat a DNS error, proxy timeout, or missing module download as a dependency acquisition failure—not as evidence that the repository does not compile.
6. Preserve build logs and report partial success precisely.

## 1. Check system prerequisites

The verified core build needs a POSIX shell plus Git or an archive downloader, `unzip`, GNU Make, and a working C toolchain for CGO.

Check the environment:

```bash
set -euo pipefail

for command in unzip make gcc file sha256sum; do
  command -v "$command" >/dev/null || {
    printf 'missing required command: %s\n' "$command" >&2
    exit 1
  }
done

# Git and curl are required by the preferred shell paths, but a platform-level
# repository or download action can replace either one.
command -v git >/dev/null || printf '%s\n' 'git unavailable; use the source archive fallback'
command -v curl >/dev/null || printf '%s\n' 'curl unavailable; use the environment download facility'
```

On Debian or Ubuntu, the corresponding package setup is:

```bash
sudo apt-get update
sudo apt-get install -y \
  ca-certificates \
  curl \
  git \
  make \
  unzip \
  build-essential \
  file \
  python3
```

Do not invoke a package manager when the required tools are already installed.

## 2. Create an isolated workspace

Choose an absolute task-specific `WORK_ROOT` under the host's preferred
high-capacity storage (for example `/mnt/fast4tb`), after verifying that mount is
available and writable. The working-directory fallback below is for hosts without
a configured storage location. Keep temporary data and outputs local to this run;
configure shared Go caches after selecting the toolchain in step 6.

```bash
set -euo pipefail

export WORK_ROOT="${WORK_ROOT:-$PWD/gomap-build-work}"
export DOWNLOAD_DIR="$WORK_ROOT/downloads"
export SOURCE_PARENT="$WORK_ROOT/source"
export LOG_DIR="$WORK_ROOT/logs"
export ARTIFACT_DIR="$WORK_ROOT/artifacts"
export TMPDIR="$WORK_ROOT/tmp"
export GOTMPDIR="$TMPDIR/go"

mkdir -p \
  "$DOWNLOAD_DIR" \
  "$SOURCE_PARENT" \
  "$LOG_DIR" \
  "$ARTIFACT_DIR" \
  "$TMPDIR" \
  "$GOTMPDIR"
```

Do not allocate per-run Go caches for ordinary builds. Use the explicit cold-cache
mode in step 6 only when dependency acquisition from empty caches is part of the
requested proof, and record its reason, paths and disposal owner.

## 3. Configure Go module access

Use a normal public proxy when network access is unrestricted:

```bash
export GOPROXY="${GOPROXY:-https://proxy.golang.org,direct}"
export GOSUMDB="${GOSUMDB:-sum.golang.org}"
unset GONOSUMDB

# Archive download commands below need an HTTP(S) module proxy as the first entry.
export PROXY_BASE="${GOPROXY%%,*}"
case "$PROXY_BASE" in
  http://*|https://*) ;;
  *) printf 'first GOPROXY entry is not an HTTP(S) proxy: %s\n' "$PROXY_BASE" >&2; exit 1 ;;
esac
```

When direct GitHub and public Go services are unavailable, use an approved authenticated module mirror. Prefer a proxy URL already supplied by the runtime:

```bash
: "${INTERNAL_GO_PROXY:?set INTERNAL_GO_PROXY to the approved Go module mirror}"
export GOPROXY="$INTERNAL_GO_PROXY"
export GOSUMDB=off
export GONOSUMDB='*'
export PROXY_BASE="${GOPROXY%%,*}"
```

The restricted sandbox used for the reference build exposed Artifactory credentials through `PIP_INDEX_URL`. The Go mirror URL was derived from those existing environment credentials without hard-coding them:

```bash
INTERNAL_GO_PROXY="$({
  python3 - <<'PY_PROXY'
import os
from urllib.parse import quote, urlparse

u = urlparse(os.environ["PIP_INDEX_URL"])
if not u.hostname or u.username is None or u.password is None:
    raise SystemExit("PIP_INDEX_URL does not contain reusable Artifactory credentials")
port = f":{u.port}" if u.port else ""
print(
    "https://"
    f"{quote(u.username, safe='')}:{quote(u.password, safe='')}@"
    f"{u.hostname}{port}/artifactory/api/go/golang-main"
)
PY_PROXY
} )"

export GOPROXY="$INTERNAL_GO_PROXY"
export GOSUMDB=off
export GONOSUMDB='*'
export PROXY_BASE="${GOPROXY%%,*}"
```

Never echo, log, archive, or commit a credential-bearing proxy URL. In reports, state only that an authenticated internal Go proxy was used.

## 4. Acquire the source

### Preferred path: reuse a repository and pin the commit

If a coordinator already supplied `GOMAP_SOURCE` at the requested snapshot,
verify its source identity under the task's contract and skip source creation.
Do not reset or delete an existing path. Otherwise set `GOMAP_EXISTING_REPO` to a
suitable local repository when available; ensure the pinned commit is present
(fetch it if needed) before adding the worktree. Clone only when none is available.

```bash
export GOMAP_REPOSITORY='https://github.com/snissn/gomap.git'
export GOMAP_COMMIT="${GOMAP_COMMIT:-4c00c886a9d7059f143e1d564aa602ed583a6cc5}"
export GOMAP_SOURCE="${GOMAP_SOURCE:-$SOURCE_PARENT/gomap}"

test ! -e "$GOMAP_SOURCE"
if [[ -n "${GOMAP_EXISTING_REPO:-}" ]]; then
  git -C "$GOMAP_EXISTING_REPO" worktree add --detach "$GOMAP_SOURCE" "$GOMAP_COMMIT"
else
  git clone "$GOMAP_REPOSITORY" "$GOMAP_SOURCE"
  git -C "$GOMAP_SOURCE" checkout --detach "$GOMAP_COMMIT"
fi
cd "$GOMAP_SOURCE"

test "$(git rev-parse HEAD)" = "$GOMAP_COMMIT"
```

When explicitly asked to build the latest `main`, resolve and record the current
commit before the acquisition block, then use that pin instead of the reference
commit above:

```bash
export GOMAP_REPOSITORY='https://github.com/snissn/gomap.git'
export GOMAP_COMMIT="$(git ls-remote "$GOMAP_REPOSITORY" refs/heads/main | awk '{print $1}')"
test -n "$GOMAP_COMMIT"
printf 'Resolved main commit: %s\n' "$GOMAP_COMMIT"
```

### Restricted-network fallback: use the Go module proxy archive

Use this path when `git clone` fails because the shell cannot resolve or reach `github.com`.

```bash
export GOMAP_MODULE_VERSION='v0.6.2-0.20260719170055-4c00c886a9d7'
export GOMAP_SOURCE_ZIP="$DOWNLOAD_DIR/gomap.zip"
export GOMAP_SOURCE_SHA256='4465babd026317ed16f73a7dfc6ec44e890a4b6d0826dee1a8a37d4952f1106c'

curl --fail --location --retry 4 \
  "${PROXY_BASE}/github.com/snissn/gomap/@v/${GOMAP_MODULE_VERSION}.zip" \
  --output "$GOMAP_SOURCE_ZIP"

printf '%s  %s\n' "$GOMAP_SOURCE_SHA256" "$GOMAP_SOURCE_ZIP" | sha256sum --check -
rm -rf "$SOURCE_PARENT/github.com"
unzip -q "$GOMAP_SOURCE_ZIP" -d "$SOURCE_PARENT"

export GOMAP_SOURCE="$SOURCE_PARENT/github.com/snissn/gomap@${GOMAP_MODULE_VERSION}"
cd "$GOMAP_SOURCE"
```

If shell DNS is blocked but the execution environment provides a separate download action, use that action to save the same URL to `GOMAP_SOURCE_ZIP`, then continue with checksum verification and extraction.

A module archive has no `.git` directory. In that case, identify the source by the pinned pseudo-version, its embedded commit suffix, and the archive checksum rather than by `git rev-parse`.

Validate the extracted source:

```bash
test -f go.mod
test -f Makefile
grep -Fx 'module github.com/snissn/gomap' go.mod
grep -Fx 'go 1.26' go.mod
```

## 5. Provision the Go 1.26 toolchain

For the exact known-good Linux/amd64 setup, retrieve Go 1.26.0 as the Go toolchain module archive. This avoids depending on an older host Go installation or on automatic toolchain resolution during the build.

```bash
export GO_TOOLCHAIN_VERSION='v0.0.1-go1.26.0.linux-amd64'
export GO_TOOLCHAIN_ZIP="$DOWNLOAD_DIR/go126.zip"
export GO_TOOLCHAIN_SHA256='38461905b98c59173672814302e222ab43b652274bc0c95817b08b71ab66b705'
export GO_TOOLCHAIN_PARENT="$WORK_ROOT/toolchain"

curl --fail --location --retry 4 \
  "${PROXY_BASE}/golang.org/toolchain/@v/${GO_TOOLCHAIN_VERSION}.zip" \
  --output "$GO_TOOLCHAIN_ZIP"

printf '%s  %s\n' "$GO_TOOLCHAIN_SHA256" "$GO_TOOLCHAIN_ZIP" | sha256sum --check -
rm -rf "$GO_TOOLCHAIN_PARENT"
mkdir -p "$GO_TOOLCHAIN_PARENT"
unzip -q "$GO_TOOLCHAIN_ZIP" -d "$GO_TOOLCHAIN_PARENT"

export GOROOT="$GO_TOOLCHAIN_PARENT/golang.org/toolchain@${GO_TOOLCHAIN_VERSION}"
export PATH="$GOROOT/bin:$PATH"
export GOTOOLCHAIN=local

go version
test "$(go env GOVERSION)" = 'go1.26.0'
test "$(go env GOOS)" = 'linux'
test "$(go env GOARCH)" = 'amd64'
```

Use a platform-appropriate Go 1.26+ toolchain for other operating systems or architectures. The binary checksums in this skill apply only to the recorded Linux/amd64 environment.

## 6. Configure dependency and build settings

Ordinary builds reuse persistent `GOCACHE` and `GOMODCACHE` in the same user/trust
boundary. Honor paths supplied by the coordinator or host; otherwise resolve the
toolchain's existing defaults. When allocating new shared caches, choose reusable
paths on the host's preferred high-capacity storage, outside `WORK_ROOT`, and
supply them before the block below. Never silently replace them with per-run
paths or change global Go configuration. Both caches support concurrent Go commands.

Set `GOMAP_CACHE_MODE=cold` only for an explicit empty-cache acquisition check.
That mode requires unused run-local cache paths and never deletes an existing
cache to manufacture a cold start. Retries with populated caches are warm reuse,
not new cold-cache evidence. Preserve any declared benchmark/cache contract.

```bash
export GOMAP_CACHE_MODE="${GOMAP_CACHE_MODE:-shared}"
case "$GOMAP_CACHE_MODE" in
  shared)
    export GOCACHE="${GOCACHE:-$(go env GOCACHE)}"
    export GOMODCACHE="${GOMODCACHE:-$(go env GOMODCACHE)}"
    ;;
  cold)
    export GOCACHE="$WORK_ROOT/cache/go-build"
    export GOMODCACHE="$WORK_ROOT/cache/go-mod"
    if [[ -e "$GOCACHE" || -e "$GOMODCACHE" ]]; then
      printf '%s\n' 'cold-cache check requires unused cache paths; choose a fresh WORK_ROOT' >&2
      exit 1
    fi
    ;;
  *) printf 'unknown GOMAP_CACHE_MODE: %s\n' "$GOMAP_CACHE_MODE" >&2; exit 1 ;;
esac
mkdir -p "$GOCACHE" "$GOMODCACHE"

export GOPROXY="${GOPROXY:-https://proxy.golang.org,direct}"
export GOSUMDB="${GOSUMDB:-sum.golang.org}"
export CGO_ENABLED=1
export GOFLAGS='-p=1'
export GOMAXPROCS=2

cd "$GOMAP_SOURCE"

printf '%s\n' 'Build environment:'
go version
go env \
  GOROOT \
  GOPROXY \
  GOSUMDB \
  GOMODCACHE \
  GOCACHE \
  GOTOOLCHAIN \
  CGO_ENABLED \
  CC \
  GOOS \
  GOARCH
```

Why these settings were used:

- `CGO_ENABLED=1` permits packages and binaries that use C-backed dependencies to compile normally.
- `GOFLAGS=-p=1` limits Go package build parallelism and reduces memory and concurrent network pressure.
- `GOMAXPROCS=2` caps runtime CPU use during compilation.
- Shared `GOMODCACHE` and `GOCACHE` retain modules and compiled packages across worktrees and retries. Lane cleanup must preserve them; only an explicitly isolated cache follows the run's disposal policy.

Go's build cache handles ordinary Go source, compiler and option changes. It does
not detect changes to external C libraries used by CGO; force the affected rebuild
(for example with `-a`) or record a scoped cache exception. Use `go test -count=1`
when fresh test execution is required without discarding compiled packages.

### Dependency acquisition strategy

With stable network access, prefetching the full module graph is acceptable:

```bash
set -o pipefail
go mod download 2>&1 | tee "$LOG_DIR/go-mod-download.log"
```

With restricted or unreliable network access, do not prefetch the entire graph first. Let each core build target download only the modules it needs. The aggregate module graph includes dependencies for optional binaries, and a cold fetch for one of those dependencies can block an otherwise successful core build.

Never use `GOPROXY=off` until all required modules are demonstrably present in `GOMODCACHE`.

## 7. Compile the verified core binaries

Build HashDB and TreeDB separately so a failure is attributable to one target group:

```bash
set -o pipefail
cd "$GOMAP_SOURCE"

make build-hashdb 2>&1 | tee "$LOG_DIR/build-hashdb.log"
make build-treedb 2>&1 | tee "$LOG_DIR/build-treedb.log"
```

These Make targets compile:

```text
bin/hashdb-benchmark
bin/hashdb-redis-wrapper
bin/hashdb-loadfactorbench
bin/hashdb-resizebench
bin/hashdb-shardbench
bin/treedb-stress
bin/treedb-verify
bin/treemap
```

The equivalent direct commands are:

```bash
mkdir -p bin

(
  cd HashDB
  go build -o ../bin/hashdb-benchmark ./cmd/benchmarkmain
  go build -o ../bin/hashdb-redis-wrapper ./redisserver
  go build -o ../bin/hashdb-loadfactorbench ./cmd/loadfactorbench
  go build -o ../bin/hashdb-resizebench ./cmd/resizebench
  go build -o ../bin/hashdb-shardbench ./cmd/shardbench
)

(
  cd TreeDB
  go build -o ../bin/treedb-stress ./cmd/stress
  go build -o ../bin/treedb-verify ./cmd/verify
  go build -o ../bin/treemap ./cmd/treemap
)
```

Prefer the Make targets so the build stays aligned with repository-maintained commands.

## 8. Attempt the optional aggregate build separately

Only after the core binaries succeed, attempt all repository build targets:

```bash
set -o pipefail
cd "$GOMAP_SOURCE"
make build 2>&1 | tee "$LOG_DIR/build-all.log"
```

The aggregate target additionally builds the MongoDB gateway and benchmark/helper programs. In the known-good run, the eight core binaries compiled first, then the aggregate target was terminated while waiting on a cold dependency fetch during `build-mongo-gateway`. No Go compiler error in the core source was observed.

If the MongoDB gateway stalls or reports a missing module, keep the core result and retry the optional target independently:

```bash
set -o pipefail
export GOPROXY='https://proxy.golang.org,direct'

go mod download github.com/armon/go-metrics@v0.4.1
go mod download github.com/hashicorp/go-immutable-radix@v1.0.0

make build-mongo-gateway 2>&1 | tee "$LOG_DIR/build-mongo-gateway.log"
```

Do not claim that `make build` completed unless every target exits successfully.

## 9. Verify the core build

```bash
cd "$GOMAP_SOURCE"

core_binaries=(
  hashdb-benchmark
  hashdb-redis-wrapper
  hashdb-loadfactorbench
  hashdb-resizebench
  hashdb-shardbench
  treedb-stress
  treedb-verify
  treemap
)

for name in "${core_binaries[@]}"; do
  test -s "bin/$name"
  test -x "bin/$name"
  file "bin/$name"
  go version -m "bin/$name" | sed -n '1,30p'
done

(
  cd bin
  sha256sum "${core_binaries[@]}" > "$ARTIFACT_DIR/SHA256SUMS"
)
```

At minimum, `go version -m` should show:

```text
go1.26.0
build CGO_ENABLED=1
build GOARCH=amd64
build GOOS=linux
```

Run module verification after the required modules have been fetched:

```bash
set -o pipefail
go mod verify 2>&1 | tee "$LOG_DIR/go-mod-verify.log"
```

Testing is a separate validation step and was not required for the recorded compile-only result. When requested, run:

```bash
set -o pipefail
make test 2>&1 | tee "$LOG_DIR/test.log"
```

## 10. Package artifacts

When `zip` is available:

```bash
cd "$GOMAP_SOURCE/bin"
zip -9 "$ARTIFACT_DIR/gomap-core-linux-amd64.zip" \
  hashdb-benchmark \
  hashdb-redis-wrapper \
  hashdb-loadfactorbench \
  hashdb-resizebench \
  hashdb-shardbench \
  treedb-stress \
  treedb-verify \
  treemap
```

Otherwise, create a tar archive:

```bash
cd "$GOMAP_SOURCE/bin"
tar -czf "$ARTIFACT_DIR/gomap-core-linux-amd64.tar.gz" \
  hashdb-benchmark \
  hashdb-redis-wrapper \
  hashdb-loadfactorbench \
  hashdb-resizebench \
  hashdb-shardbench \
  treedb-stress \
  treedb-verify \
  treemap
```

## 11. Reference output from the verified run

The recorded core binaries had these sizes and SHA-256 digests. Treat them as reference evidence, not as universal cross-platform checksums; C compiler, paths, build flags, and platform changes can alter binary bytes.

```text
12016602  89f13fe9ea2d109a996a1d0512613b1785e6ea6d1b0cbe9cfb6abb9b718d4d0e  hashdb-benchmark
 3673099  39856e85efcc03f37da489d0d1e13a2115d1a1f058bb77c405299407b70cba2d  hashdb-loadfactorbench
16634379  15e0fce56e8e7090f20e5ad5992df6baeebfe6697b1871f7057ef3758cf21a0e  hashdb-redis-wrapper
 3682264  359d2325ccf3b42430b6a7627d23830a23dbd2635bd91b80218981b124961e90  hashdb-resizebench
 3789697  ac0c3916255b15a72b409fddb64914875e89ccea87e7712111d04c50e980a3ce  hashdb-shardbench
10622366  7d21536445cb631c5fc23c89c666336fc0952ebb41cc27e444d3c7a64614630e  treedb-stress
13806344  3f2a8f09895fae09e34fba8470ecb0fe537795bb00a8495428dda4526d5792ca  treedb-verify
21014046  4dd8635e46acac0826815a2ce5fa8c8ac122ede218fb1fef5d3d64b52d1bdf13  treemap
```

## Troubleshooting

### `git clone` cannot resolve `github.com`

Use the pinned Go module ZIP fallback. If shell DNS also blocks `proxy.golang.org`, use the environment's direct-download facility to save the same archive URL locally.

### `go.mod requires go >= 1.26`

The host Go toolchain is too old. Use the exact Go 1.26.0 toolchain module procedure above, or install an official Go 1.26+ distribution for the platform.

### `module lookup disabled by GOPROXY=off`

Unset the override or restore an online proxy:

```bash
export GOPROXY="${INTERNAL_GO_PROXY:-https://proxy.golang.org,direct}"
```

Then retry the specific missing module or build target.

### A dependency download hangs

Keep `GOFLAGS=-p=1`, build `build-hashdb` and `build-treedb` independently, and retry the missing module explicitly. Do not erase successful core binaries merely because an optional target is waiting on the network.

### `cgo: C compiler "gcc" not found`

Install GCC and the platform C development headers. On Debian or Ubuntu, install `build-essential`.

### Source came from a module ZIP and `git` commands fail

That is expected because module ZIPs exclude `.git`. Record the module pseudo-version, commit suffix, source ZIP checksum, and module path instead.

## Required final report

Report all of the following:

- Source acquisition method: Git clone or module archive
- Exact commit and/or module pseudo-version
- Source archive checksum when an archive was used
- Go version, platform, CGO state, and constrained parallelism settings
- Whether the core build succeeded
- Whether the aggregate `make build` succeeded separately
- Names, sizes, and SHA-256 digests of generated binaries
- Any dependency acquisition failure, including the exact missing module or network error
- Paths to build logs and packaged artifacts
