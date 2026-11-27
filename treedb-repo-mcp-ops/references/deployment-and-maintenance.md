# TreeDB Repo MCP — Deployment, Client Wiring & Maintenance Reference

## CLI Flags & Environment Variables

### Common Flags (`sync`, `daemon`, `mcp`, `query`, `status`)

| Flag | Env Var | Default | Purpose |
| --- | --- | --- | --- |
| `--repo` | — | `.` | Local git repository path |
| `--github-repo` | — | auto from `origin` | Explicit `owner/repo` |
| `--data-dir` | — | `~/.local/share/treedb-repo-mcp/<slug>-<hash>` | TreeDB + `gh-cache` directory |
| `--socket` | — | `<data-dir>/daemon.sock` (or `/tmp/treedb-mcp-<hash>.sock` if `>92B`) | Daemon Unix domain socket |
| `--http` | — | *(disabled)* | Streamable HTTP bind address (e.g. `127.0.0.1:7337`) |
| `--no-github` | — | `false` | Disable GitHub indexing/polling |
| `--no-watch` | — | `false` | Disable `fsnotify` filesystem watcher |
| `--git-poll` | — | `60s` | Periodic safe `git fetch` + `merge --ff-only` interval in daemon mode for clean checkouts (`0` disables) |
| `--git-remote` | — | *(branch upstream or `origin`)* | Optional git remote name to fetch when `--git-poll` is enabled |
| `--git-branch` | — | *(current branch upstream)* | Optional git branch to track when `--git-poll` is enabled |
| `--gh-poll` | — | `60s` | GitHub incremental poll interval (`0` disables) |
| `--watch-debounce` | — | `500ms` | Filesystem change debounce window |
| `--maintain-interval` | — | `15m` | Periodic `MaintainTextIndexes` sealing/compaction (`0` disables) |
| `--max-file-bytes` | — | `2097152` (2 MiB) | Max single indexed file size |
| `--chunk-size` | — | `3000` | Target chunk size in runes |
| `--chunk-overlap` | — | `300` | Chunk overlap in runes |
| `--include-ext` | — | — | Comma-separated extra extensions to include (e.g. `json,csv`) |
| `--exclude-ext` | — | — | Comma-separated extensions to exclude |
| `--bot-login` | — | — | Extra GitHub logins to classify as bots |
| `--embed-provider` | `TREEDB_MCP_EMBED_PROVIDER` | *(disabled)* | `openai_compat` or `hashing` |
| `--embed-dims` | `TREEDB_MCP_EMBED_DIMS` | `0` | Embedding vector dimensions (required with `--embed-provider`) |
| `--embed-url` | `TREEDB_MCP_EMBED_URL` | — | Base URL for `openai_compat` `/v1/embeddings` |
| `--embed-model` | `TREEDB_MCP_EMBED_MODEL` | — | Model name for `openai_compat` |
| `--embed-api-key-env` | `TREEDB_MCP_EMBED_API_KEY_ENV` | — | Env var name holding API bearer token |
| `--embed-batch-size` | `TREEDB_MCP_EMBED_BATCH_SIZE` | `64` | Batch size for embedding requests |
| `--embed-normalize` | — | `true` | L2-normalize returned embeddings |
| `--embed-send-dims` | — | `false` | Send `dimensions` parameter to endpoint |

### Subcommand-Specific Flags

- `sync`: `--gh-from-cache`, `--no-repo`, `--no-maintain`
- `daemon`: `--skip-initial-sync`
- `mcp`: `--readonly` (direct RO TreeDB open, no daemon), `--no-autostart` (fail instead of spawning daemon if socket missing)

## Default Corpus Filter Rules

- **Included by default**: prose and source code (`.md`, `.mdx`, `.txt`, `.rst`, `.tex`, `.bib`, `.org`, `.adoc`, `.go`, `.py`, `.rs`, `.ts`, `.tsx`, `.js`, `.jsx`, `.c`, `.cc`, `.cpp`, `.h`, `.hpp`, `.lean`, `.jl`, `.sh`, `.bash`, `.zsh`, `.sql`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.mk`, `.proto`, `.graphql`, `Makefile`, `Dockerfile`, `README`, `LICENSE`, etc.).
- **Excluded by default**: numeric/structured data dumps, logs, and binaries (`.json`, `.jsonl`, `.ndjson`, `.csv`, `.tsv`, `.parquet`, `.npz`, `.npy`, `.f64le`, `.bin`, `.dat`, `.log`, `.out`, `.pdf`, `.png`, `.jpg`, `.svg`, `.zip`, `.tar`, `.gz`, `.wasm`, `.so`, `.dylib`, `.exe`, `._*`, `.DS_Store`, `*.part`, `*.bak-*`, plus any file containing a NUL byte in the first 4 KiB).

## MCP Client Configuration Templates

### Streamable HTTP (Antigravity / Claude Code / Codex / Cursor)

For Antigravity (`~/.gemini/config/mcp_config.json`) or clients supporting Streamable HTTP MCP servers:

```json
{
  "mcpServers": {
    "repo-search": {
      "url": "http://127.0.0.1:7337/mcp"
    }
  }
}
```

### Stdio Proxy (auto-starts per-repo daemon over Unix socket)

```json
{
  "mcpServers": {
    "repo-search": {
      "command": "/path/to/bin/treedb-repo-mcp",
      "args": [
        "mcp",
        "--repo", "/path/to/repo",
        "--data-dir", "/path/to/repo-db",
        "--socket", "/path/to/repo.sock"
      ]
    }
  }
}
```

Pass `--no-autostart` in `args` when the daemon is managed externally (for example by `systemd` or `launchd`).

## Service Supervision Templates

### Linux `systemd` User Unit (`~/.config/systemd/user/treedb-repo-mcp@.service`)

Create a `chmod 600` env file at `~/.config/treedb-repo-mcp/env` containing `GITHUB_TOKEN=ghp_...` (and any `TREEDB_MCP_EMBED_*` / API key variables when embeddings are enabled) and load it via `EnvironmentFile=`:

```ini
[Unit]
Description=TreeDB Repo MCP Daemon (%i)
After=network-online.target

[Service]
Type=simple
EnvironmentFile=%h/.config/treedb-repo-mcp/env
ExecStart=/path/to/bin/treedb-repo-mcp daemon \
  --repo /path/to/repos/%i \
  --data-dir /path/to/data/%i-db \
  --socket /path/to/data/%i.sock \
  --http 127.0.0.1:7337
Restart=on-failure
RestartSec=5
TimeoutStopSec=20
KillSignal=SIGTERM

[Install]
WantedBy=default.target
```

### macOS `launchd` Agent (`~/Library/LaunchAgents/com.treedb.repo-mcp.plist`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.treedb.repo-mcp</string>
  <key>ProgramArguments</key>
  <array>
    <string>/path/to/bin/treedb-repo-mcp</string>
    <string>daemon</string>
    <string>--repo</string><string>/path/to/repo</string>
    <string>--data-dir</string><string>/path/to/repo-db</string>
    <string>--socket</string><string>/path/to/repo.sock</string>
    <string>--http</string><string>127.0.0.1:7337</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/path/to/daemon.log</string>
  <key>StandardErrorPath</key><string>/path/to/daemon.log</string>
</dict>
</plist>
```

## Atomic Upgrade & Regeneration Script Pattern

If semantic embeddings are enabled, export `TREEDB_MCP_EMBED_*` (plus your provider API key env var) before running this script, or append the exact same `--embed-*` flags to `EXTRA_FLAGS` below so `sync` and `daemon` share identical embedding configuration.

```sh
set -euo pipefail
BIN_DIR=/path/to/bin
REPO_DIR=/path/to/repo
DB_DIR=/path/to/repo-db
SOCK=/path/to/repo.sock
HTTP_ADDR=127.0.0.1:7337
LOG=/path/to/daemon.log
EXTRA_FLAGS=() # e.g. (--embed-provider openai_compat --embed-dims 1536 ...)

# 1. Seed GitHub JSONL cache without touching live DB
rm -rf "${DB_DIR}.new"
mkdir -p "${DB_DIR}.new/gh-cache"
if [ -f "${DB_DIR}/gh-cache/items.jsonl" ]; then
  cp "${DB_DIR}/gh-cache/items.jsonl" "${DB_DIR}.new/gh-cache/items.jsonl"
fi

# 2. Build fresh DB from cache + live incremental catch-up
"${BIN_DIR}/treedb-repo-mcp.new" sync --repo "$REPO_DIR" --data-dir "${DB_DIR}.new" "${EXTRA_FLAGS[@]}" --gh-from-cache
"${BIN_DIR}/treedb-repo-mcp.new" sync --repo "$REPO_DIR" --data-dir "${DB_DIR}.new" "${EXTRA_FLAGS[@]}"

# 3. Verify cold status before swapping
"${BIN_DIR}/treedb-repo-mcp.new" status --repo "$REPO_DIR" --data-dir "${DB_DIR}.new"

# 4. Gracefully stop ONLY the daemon serving $DB_DIR (preserve daemons for other repos!)
OLD_PIDS=$(python3 - "$DB_DIR" <<'PY'
import os, shlex, subprocess, sys
want_db = os.path.realpath(sys.argv[1])
def match_argv(argv):
    if not argv or os.path.basename(argv[0]) != "treedb-repo-mcp" or "daemon" not in argv[1:3]:
        return False
    for i, arg in enumerate(argv):
        if arg == "--data-dir" and i + 1 < len(argv) and os.path.realpath(argv[i + 1]) == want_db:
            return True
        if arg.startswith("--data-dir=") and os.path.realpath(arg.split("=", 1)[1]) == want_db:
            return True
    return False
if os.path.isdir("/proc"):
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            argv = open(f"/proc/{pid}/cmdline", "rb").read().decode("utf-8", "replace").split("\0")
        except OSError:
            continue
        if match_argv([a for a in argv if a]):
            print(pid)
else:
    out = subprocess.check_output(["ps", "-eo", "pid=,args="], text=True)
    for line in out.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        try:
            argv = shlex.split(parts[1])
        except ValueError:
            continue
        if match_argv(argv):
            print(parts[0])
PY
)
for pid in $OLD_PIDS; do
  kill -TERM "$pid"
  for _ in $(seq 1 30); do
    kill -0 "$pid" 2>/dev/null || break
    sleep 0.5
  done
  if kill -0 "$pid" 2>/dev/null; then
    echo "ERROR: daemon PID $pid did not stop cleanly" >&2
    exit 1
  fi
done

rm -rf "${DB_DIR}.bak" "${BIN_DIR}/treedb-repo-mcp.bak"
mv "${BIN_DIR}/treedb-repo-mcp" "${BIN_DIR}/treedb-repo-mcp.bak"
mv "${BIN_DIR}/treedb-repo-mcp.new" "${BIN_DIR}/treedb-repo-mcp"
mv "${DB_DIR}" "${DB_DIR}.bak"
mv "${DB_DIR}.new" "${DB_DIR}"
rm -f "$SOCK"

nohup setsid "${BIN_DIR}/treedb-repo-mcp" daemon \
  --repo "$REPO_DIR" \
  --data-dir "$DB_DIR" \
  --socket "$SOCK" \
  --http "$HTTP_ADDR" \
  --skip-initial-sync \
  "${EXTRA_FLAGS[@]}" \
  </dev/null >>"$LOG" 2>&1 &
```

Delete `${DB_DIR}.bak` and `${BIN_DIR}/treedb-repo-mcp.bak` only after `/health`, cold `status`, open-FD/disk checks, and a live `phrase_search` pass.

## Live `/status`, Open-FD, and Disk-Footprint Checks

```sh
# 1. Verify /status git-poll and collection telemetry (empty strings / zero counters are omitted via json omitempty)
curl -fsS "http://${HTTP_ADDR}/status" | jq '{
  head: .current_head_sha,
  disk_usage_bytes: .disk_usage_bytes,
  daemon: {
    watching: .daemon.watching,
    watch_degraded: (.daemon.watch_degraded // false),
    git_polling: (.daemon.git_polling // false),
    git_pulls_applied: (.daemon.git_pulls_applied // 0),
    last_git_poll: (.daemon.last_git_poll // ""),
    last_git_skip: (.daemon.last_git_skip // ""),
    last_git_error: (.daemon.last_git_error // "")
  },
  collections: [.collections[] | {name: .collection, blocks: .posting_blocks, sealed: .sealed_posting_blocks, micro: .micro_posting_blocks, delta: .delta_posting_blocks, stale: .stale_postings}]
}'

# 2. Check disk footprint breakdown
du -sh "$DB_DIR" "$DB_DIR/treedb/maindb" "$DB_DIR/treedb/maindb"/* 2>/dev/null || du -sh "$DB_DIR"

# 3. On Linux, check open FDs for the daemon serving $DB_DIR and ensure zero genuinely unlinked (nlink == 0) handles remain after maintenance
#    (live hard-linked leaf_vlog/manifest.stage.tmp.* or promoted pack handles have nlink > 0 and are active inodes, not leaks)
PID=$(python3 - "$DB_DIR" <<'PY'
import os, sys
want_db = os.path.realpath(sys.argv[1])
for pid in os.listdir("/proc") if os.path.isdir("/proc") else []:
    if not pid.isdigit():
        continue
    try:
        argv = [a for a in open(f"/proc/{pid}/cmdline", "rb").read().decode("utf-8", "replace").split("\0") if a]
    except OSError:
        continue
    if argv and os.path.basename(argv[0]) == "treedb-repo-mcp" and "daemon" in argv[1:3]:
        for i, arg in enumerate(argv):
            if (arg == "--data-dir" and i + 1 < len(argv) and os.path.realpath(argv[i + 1]) == want_db) or (arg.startswith("--data-dir=") and os.path.realpath(arg.split("=", 1)[1]) == want_db):
                print(pid)
                raise SystemExit(0)
PY
)
if [ -n "$PID" ] && [ -d "/proc/$PID/fd" ]; then
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
print(f"total_fds={total}")
print(f"unlinked_nlink0_fds={len(dead)}")
for target in dead:
    print(f"  dead_fd={target}")
PY
fi
```
