---
name: treedb-repo-mcp-ops
description: Install, configure, deploy, upgrade, safely regenerate, and maintain a treedb-repo-mcp server for any GitHub repository. Use when building the binary, running initial or cache-accelerated sync, enabling optional semantic vector embeddings, wiring MCP clients (Antigravity, Claude, Codex, Cursor), supervising the daemon, or troubleshooting storage, fsnotify, or GitHub sync issues.
---

# TreeDB Repo MCP Operations

Use this skill to install, configure, operate, upgrade, and maintain `treedb-repo-mcp` (embedded TreeDB full-text + optional vector/hybrid MCP server and realtime sync daemon) for any GitHub repository.

## When To Use

Use this skill when:

- cloning, building, or upgrading `snissn/treedb-repo-mcp`;
- indexing a new repository (with or without GitHub issues/PRs/comments, and with or without embeddings);
- running the realtime sync daemon (`fsnotify` + default-on safe remote git fast-forward poller + GitHub poller + Unix socket / Streamable HTTP) and connecting MCP clients;
- upgrading the binary or TreeDB format with an atomic zero-data-loss DB regeneration;
- monitoring O(1) index health, open-FD and disk-footprint hygiene, running maintenance, or troubleshooting watcher/git-poll/auth/storage errors.

Do not use this skill for:

- day-to-day code/issue search queries against a running server (use `treedb-repo-mcp-search`).

## Inputs Needed

- Target local git checkout path (`--repo`) and optional `owner/repo` (`--github-repo`, auto-detected from `origin` if omitted).
- Persistent TreeDB data directory (`--data-dir`) and optional socket (`--socket`) / HTTP bind (`--http`).
- Whether GitHub indexing is enabled (requires `GITHUB_TOKEN`, `GH_TOKEN`, or `gh auth login`) or disabled (`--no-github`).
- Whether semantic embeddings are enabled (`--embed-provider`, `--embed-dims`, plus URL/model/API-key-env for `openai_compat`).

## Workflow

### 1. Build from source (Go 1.26+)

```sh
git clone https://github.com/snissn/treedb-repo-mcp.git
cd treedb-repo-mcp
! grep -q '^replace' go.mod
go vet ./...
go test -race ./...
go build -trimpath -o /path/to/bin/treedb-repo-mcp ./cmd/treedb-repo-mcp
/path/to/bin/treedb-repo-mcp version
```

Keep `go.mod` pinned directly to a merged `github.com/snissn/gomap` commit with zero `replace` directives.

### 2. Run initial one-shot sync

- **Standard sync** (indexes repo prose/code + GitHub issues/PRs/comments + seals 100% of text-v2 posting blocks + compacts storage):
  ```sh
  treedb-repo-mcp sync \
    --repo /path/to/repo \
    --data-dir /path/to/repo-db
  ```
- **Local-only (skip GitHub)**: add `--no-github`.
- **Tune corpus defaults**: by default numeric/structured dumps and binaries (`.json`, `.jsonl`, `.csv`, `.tsv`, `.log`, `.npz`, `.pdf`, images, archives) are excluded; override with `--include-ext json,csv`, `--exclude-ext ...`, `--max-file-bytes`, `--chunk-size`, `--chunk-overlap`, or extra `--bot-login` values.
- **Optional semantic vector + Hybrid RRF**: pass `--embed-provider openai_compat --embed-url <base> --embed-model <model> --embed-dims <N> --embed-api-key-env <ENV_VAR>` (or `--embed-provider hashing --embed-dims <N>`, or set `TREEDB_MCP_EMBED_*` env vars). Additional tuning flags:
  - `--embed-max-tokens <N>` (`TREEDB_MCP_EMBED_MAX_TOKENS`): embedder context window in tokens (e.g. `8192` for `BAAI/bge-m3`); write paths validate `--chunk-size` against this budget fail-closed to prevent silent truncation.
  - `--embed-encoding-format base64|float` (`TREEDB_MCP_EMBED_ENCODING_FORMAT`, default `base64` for `openai_compat`): uses compact base64 float32 wire encoding when supported by the embedding server.
  - `--embed-vector-mode quantized_rerank|exact` (`TREEDB_MCP_EMBED_VECTOR_MODE`, default `quantized_rerank`): selects `scalar_u8` quantized candidate generation + exact FP32 rerank vs full FP32 graph search (also overridable per query via `vector_mode`).
  - `--embed-query-prefix <str>` (`TREEDB_MCP_EMBED_QUERY_PREFIX`): optional instruction prefix prepended only to live search queries for asymmetric retrieval models.
  - `--embed-batch-size <N>` (`TREEDB_MCP_EMBED_BATCH_SIZE`, default `128`): batch size for pipelined ingest embedding calls.
  - Vector mode automatically selects `ProfileCommandWALDurable` with `ColumnRetainedPayloadNonColumn` float32 column projection + `scalar_u8` quantization while still running unified `MaintainTextIndexes` sealing and compaction.
  - **Important**: changing embedding provider/model/dimensions or chunking configuration changes `EmbeddingConfig.Fingerprint()` / `ChunkConfigFingerprint()` and requires regenerating the DB cleanly.

### 3. Start the realtime daemon and wire MCP clients

Start the persistent single-writer daemon (`--skip-initial-sync` skips a redundant full scan immediately after Step 2):

```sh
nohup setsid /path/to/bin/treedb-repo-mcp daemon \
  --repo /path/to/repo \
  --data-dir /path/to/repo-db \
  --socket /path/to/repo.sock \
  --http 127.0.0.1:7337 \
  --skip-initial-sync \
  </dev/null >>/path/to/daemon.log 2>&1 &
```

- **Default-on remote git fast-forward polling**: `daemon` runs safe `git fetch` + `merge --ff-only` every `--git-poll` (`60s` by default; pass `--git-poll 0` to disable, or override upstream with `--git-remote` / `--git-branch`). It automatically skips without mutating the worktree if the checkout is dirty, detached, or diverged, and surfaces skip/error reasons on `/status`.
- **Carry embedding config across every command**: `treedb-repo-mcp` reads `EmbeddingConfig` strictly from the current invocation's `--embed-*` flags or `TREEDB_MCP_EMBED_*` environment variables (it does not reload embedder URL/model/API-key settings from disk). If embeddings were enabled in Step 2, pass the exact same `--embed-*` flags (or export `TREEDB_MCP_EMBED_*` plus your API key env var) to `daemon`, `sync`, and `mcp`.
- **Network safety**: bind `--http 127.0.0.1:7337` by default; bind `0.0.0.0:7337` only on a trusted LAN or behind authentication, since `/mcp` exposes repository contents and `sync_now` without built-in auth.
- **Socket path length**: keep `--socket` under 92 bytes (Unix `sun_path` limit).
- **Client wiring & service units**: see [references/deployment-and-maintenance.md](references/deployment-and-maintenance.md) for Antigravity, Claude Code/Desktop, Codex, Cursor, `systemd`, and `launchd` templates.

### 4. Monitor health, FD/disk hygiene, and routine maintenance

Check `/health` and O(1) `/status` (sub-50 ms even on 880k+ posting blocks):

```sh
curl -fsS http://127.0.0.1:7337/health
curl -fsS http://127.0.0.1:7337/status | jq '{head: .current_head_sha, disk_bytes: .disk_usage_bytes, daemon: .daemon, collections: .collections}'
```

Healthy post-maintenance indicators:

- Per collection (`.collections[]`):
  - `sealed_posting_blocks == posting_blocks`
  - `micro_posting_blocks == 0`, `delta_posting_blocks == 0`
  - `deleted_documents == 0`, `stale_postings == 0`
- Daemon runtime (`.daemon`):
  - `watching == true` and `watch_degraded` absent/`false`
  - When `--git-poll > 0` (the default `60s`): `git_polling == true`, `last_git_poll` recent, and `last_git_skip` / `last_git_error` absent or `""` (JSON `omitempty` omits empty strings and zero counters like `git_pulls_applied` when healthy / no fast-forwards have landed yet)
- Disk footprint and open-FD hygiene:
  ```sh
  du -sh /path/to/repo-db /path/to/repo-db/treedb/maindb/*
  # On Linux, confirm bounded FDs and zero genuinely unlinked (nlink == 0) handles after maintenance
  # (hard-linked leaf_vlog/manifest.stage.tmp.* or promoted pack handles show "(deleted)" with nlink > 0 and are live):
  python3 - "$PID" <<'PY'
  import os, sys
  d = f"/proc/{sys.argv[1]}/fd"
  total, dead = 0, []
  for name in os.listdir(d):
      p = os.path.join(d, name)
      try:
          target = os.readlink(p)
          total += 1
          if target.endswith(" (deleted)") and os.stat(p).st_nlink == 0:
              dead.append(target)
      except OSError:
          continue
  print(f"total_fds={total} unlinked_nlink0_fds={len(dead)}")
  for target in dead:
      print("  DEAD:", target)
  PY
  ```
  Confirm `0` genuinely unlinked (`nlink == 0`) FDs after maintenance/GC (allowing ~5–8 s for `index.db.bak` ghost drain), bounded total FDs across both `value_vlog` and `leaf_vlog` that do not grow across repeated maintenance cycles, and expected on-disk footprint (compact internal-node-only `index.db` plus compressed `leaf_vlog` and `value_vlog` segments). Note that Linux `/proc/$PID/fd` shows `(deleted)` on live hard-linked `leaf_vlog/manifest.stage.tmp.*` / promoted pack handles whose `nlink > 0`; those are active inodes pinned by TreeDB durable-root tokens, not leaks.

Periodic maintenance runs every `--maintain-interval` (default `15m`). To force sealing/compaction immediately without restarting, invoke MCP `sync_now` with `{"repo": true, "github": true, "maintain": true}`.

### 5. Safe upgrades & atomic DB regeneration (preserving `gh-cache`)

Never overwrite a live `--data-dir` in place or delete `<data-dir>/gh-cache/items.jsonl` (re-fetching thousands of GitHub threads takes minutes and burns GraphQL quota). Follow this atomic swap sequence:

1. **Build staged binary**: `go build -trimpath -o <bin>/treedb-repo-mcp.new ./cmd/treedb-repo-mcp`.
2. **Seed GitHub cache into `<db>.new`**:
   ```sh
   mkdir -p <db>.new/gh-cache
   cp <db>/gh-cache/items.jsonl <db>.new/gh-cache/items.jsonl
   ```
3. **Refresh repo checkout** (`git -C <repo> fetch origin main && git -C <repo> reset --hard origin/main` if dedicated mirror checkout).
4. **Two-pass sync into `<db>.new`** while the old daemon continues serving undisturbed:
   ```sh
   <bin>/treedb-repo-mcp.new sync --repo <repo> --data-dir <db>.new --gh-from-cache
   <bin>/treedb-repo-mcp.new sync --repo <repo> --data-dir <db>.new
   ```
5. **Pre-swap read-only verification on `<db>.new`**:
   ```sh
   <bin>/treedb-repo-mcp.new status --repo <repo> --data-dir <db>.new
   <bin>/treedb-repo-mcp.new query --repo <repo> --data-dir <db>.new --target phrase --collection repo --top-k 5 --explain "<known phrase>"
   ```
   Confirm `0` micro/delta/stale postings and `TextBlockMaxFallbacks: 0`.
6. **Gracefully stop ONLY the target daemon and swap**:
   - Match the process by BOTH exact binary name (`treedb-repo-mcp`) AND the exact target `--data-dir <db>` argument (see [references/deployment-and-maintenance.md](references/deployment-and-maintenance.md)). Never use bare `pgrep -f` (which can match your own SSH shell command) or bare `pgrep -x treedb-repo-mcp` (which would stop daemons serving other repositories on the same host).
   - Send `SIGTERM` to that target PID and wait for clean exit before touching files.
   - `mv <bin>/treedb-repo-mcp <bin>/treedb-repo-mcp.bak && mv <bin>/treedb-repo-mcp.new <bin>/treedb-repo-mcp`
   - `mv <db> <db>.bak && mv <db>.new <db>`
   - Remove any stale socket file and start the fresh daemon (passing the same `--embed-*` flags or `TREEDB_MCP_EMBED_*` environment variables if embeddings are enabled).
7. **Post-swap live verification** (only delete `<db>.bak` and `<bin>.bak` AFTER every check passes):
   - `GET /health` returns `200 OK`;
   - Cold MCP `status` completes in `< 100 ms` with exact counts and `stale_postings: 0`;
   - Native `phrase_search` returns hits with empty `notes`;
   - Unix socket stdio proxy (`treedb-repo-mcp mcp --no-autostart --socket <sock>`) responds cleanly.

## Troubleshooting

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| `daemon.watch_degraded: true` | Linux `fs.inotify.max_user_watches` exhausted on large directory trees | Raise `fs.inotify.max_user_watches` (e.g. `524288`) via `sysctl`; daemon falls back to periodic polling until raised |
| `daemon.last_git_skip` or `daemon.last_git_error` populated | Checkout is dirty/detached/diverged, remote unreachable, or non-fast-forward history | Clean/reconcile the mirror checkout (`git status`, `git fetch`), or disable remote polling on active developer worktrees with `--git-poll 0` |
| Growing `(deleted)` FDs or oversized `index.db` | Older `gomap` pin or pre-compressed-outer-leaf DB (`index_outer_leaves_in_vlog: false`) | Upgrade to current `main` (compressed outer leaves in `leaf_vlog` + leaf-log/value-log GC fixes) and run Step 5 atomic regeneration |
| `status` returns fail-closed text index error | Un-migrated pre-D3 DB layout or non-ready index | Run Step 5 atomic regeneration into `<db>.new` |
| `open treedb ... lock` error | Second read-write `sync` or `daemon` opened on active `--data-dir` | Only one RW process may hold `--data-dir`; use `sync_now` on the running daemon or `--readonly` / `query` / `status` for RO reads |
| GitHub sync auth or rate-limit error | Missing `GITHUB_TOKEN`/`GH_TOKEN`/`gh auth` or exhausted GraphQL points | Run `gh auth status`, export `GITHUB_TOKEN`, or pass `--gh-poll 5m` / `--no-github` |
| `hybrid`/`vector` search error | Store opened without `--embed-provider` + `--embed-dims` | Check `status.embedding.enabled`; regenerate DB with embedding flags if semantic search is desired |

## Validation

Before declaring an install, upgrade, or regeneration complete:

- [ ] Binary built cleanly from merged `main` (`go vet`, `go test -race`, zero `replace` in `go.mod`).
- [ ] `GET /health` responds `200 OK` and cold `status` returns `< 100 ms` with `stale_postings: 0`, `micro_posting_blocks: 0`, and (when `--git-poll > 0`) `daemon.git_polling: true` with `last_git_error` / `last_git_skip` absent or `""`.
- [ ] On Linux, `/proc/<pid>/fd` shows `0` genuinely unlinked (`nlink == 0`) FDs after ghost drain and bounded total FDs across maintenance cycles, and `du -sh <db>` confirms expected disk usage.
- [ ] Live search (`search`, `phrase_search` with zero fallback notes) passes over HTTP and/or Unix socket proxy.
- [ ] Backup dirs (`.bak`) cleaned up only after live verification passes, and disk usage checked (`df -h`).

## Failure Handling

Pause and report (leaving `.bak` intact for rollback) if:

- `sync` or `MaintainTextIndexes` exits non-zero;
- the old daemon fails to exit cleanly after `SIGTERM` within 15 seconds;
- post-swap `/health`, cold `status`, or `phrase_search` fails (roll back by stopping the new daemon and swapping `.bak` back into place).

## Final Report Format

Report:

- binary version/commit and pinned `gomap` version;
- live endpoints (`--http`, `--socket`), PID, and indexed `head_sha` + GitHub counts;
- cold `status` latency, per-collection block/stale counters, and on-disk DB size;
- verification checks run and backup/disk cleanup status.
