# TreeDB Repo MCP — Tool & Transport Reference

Complete parameter reference, response shapes, and transport fallback recipes for `treedb-repo-mcp`.

## MCP Tools

### 1. `status`

O(1) store and daemon diagnostics (no parameters). Reads TreeDB text-v2 status counters directly without full index scans.

**Key response fields:**

```json
{
  "repo_dir": "/path/to/repo",
  "github_repo": "owner/repo",
  "current_head_sha": "0008ebf0...",
  "repo_sync_state": {
    "head_sha": "0008ebf0...",
    "files_indexed": 29523,
    "chunks_indexed": 172519,
    "files_skipped": 26363,
    "synced_at": "2026-11-26T09:16:38Z"
  },
  "github_sync_state": {
    "issues_count": 2212,
    "prs_count": 2407,
    "comments_count": 23160,
    "last_issue_at": "2026-11-26T09:14:03Z",
    "last_pr_at": "2026-11-26T09:15:57Z",
    "synced_at": "2026-11-26T09:16:42Z"
  },
  "embedding": {
    "enabled": false
  },
  "disk_usage_bytes": 6370735823,
  "collections": [
    {
      "collection": "repo_chunks",
      "live_documents": 172519,
      "deleted_documents": 0,
      "posting_blocks": 647979,
      "sealed_posting_blocks": 647979,
      "micro_posting_blocks": 0,
      "delta_posting_blocks": 0,
      "stale_postings": 0,
      "root_generation": 329
    }
  ],
  "daemon": {
    "uptime_seconds": 120,
    "watching": true,
    "watched_dirs": 7484,
    "github_polling": true,
    "repo_changes_applied": 0
  }
}
```

### 2. `search`

Unified search fanning out concurrently across repo code/docs, GitHub issues, PRs, and comments.

| Parameter | Type | Default | Values / Notes |
| --- | --- | --- | --- |
| `query` *(required)* | string | — | Search query text |
| `sources` | string[] | all four | Subset of `repo`, `issues`, `prs`, `comments` |
| `mode` | string | `lexical` | `lexical`, `hybrid`, `vector` (`hybrid`/`vector` require `embedding.enabled: true`) |
| `operator` | string | `or` | `or`, `and` |
| `query_mode` | string | `literal` | `literal`, `boolean` (`AND`/`OR`/`NOT`/quoted phrases) |
| `exclude_bots` | boolean | `false` | Exclude bot-authored GitHub items and comments (`index_state_postfilter`) |
| `top_k` | integer | `10` | `1..100` |
| `max_per_parent` | integer | `2` | Max chunks per file or comments per thread |
| `explain` | boolean | `false` | Include TreeDB execution telemetry |

### 3. `search_code`

Targeted search over indexed repository file chunks (`repo_chunks`).

| Parameter | Type | Default | Values / Notes |
| --- | --- | --- | --- |
| `query` *(required)* | string | — | Search query text |
| `mode` | string | `lexical` | `lexical`, `hybrid`, `vector` |
| `operator` | string | `or` | `or`, `and` |
| `query_mode` | string | `literal` | `literal`, `boolean` |
| `top_dir` | string | — | Top-level directory (e.g. `docs`, `src`, `.` for repo root) |
| `sub_dir` | string | — | Two-level directory prefix (e.g. `qm-foundations/research-atlas-2026-09`) |
| `ext` | string | — | Extension without dot (e.g. `md`, `go`, `py`, `lean`, `tex`, `rs`) |
| `lang` | string | — | Detected language (e.g. `markdown`, `python`, `lean`, `go`, `latex`) |
| `path` | string | — | Exact repo-relative file path |
| `path_prefix` | string | — | Repo-relative path prefix |
| `top_k` | integer | `10` | `1..100` |
| `max_chunks_per_file` | integer | `2` | Max chunks returned per file |
| `explain` | boolean | `false` | Include TreeDB execution telemetry |

### 4. `search_github`

Targeted search across `gh_items` (issues & PRs) and `gh_comments` (issue comments, PR reviews, inline review comments).

| Parameter | Type | Default | Values / Notes |
| --- | --- | --- | --- |
| `query` *(required)* | string | — | Search query text |
| `scope` | string | `all` | `all`, `issues`, `prs`, `comments` |
| `mode` | string | `lexical` | `lexical`, `hybrid`, `vector` |
| `operator` | string | `or` | `or`, `and` |
| `query_mode` | string | `literal` | `literal`, `boolean` |
| `state` | string | — | `open`, `closed`, `merged` |
| `author` | string | — | GitHub login (case-insensitive) |
| `exclude_bots` | boolean | `false` | Exclude bot-authored items and comments |
| `label` | string | — | Issue/PR label (case-insensitive) |
| `comment_kind` | string | — | `issue_comment`, `review`, `review_comment` |
| `number_min` | integer | — | Inclusive minimum issue/PR number |
| `number_max` | integer | — | Inclusive maximum issue/PR number |
| `updated_after` | string | — | RFC3339 timestamp or `YYYY-MM-DD` |
| `updated_before` | string | — | RFC3339 timestamp or `YYYY-MM-DD` |
| `top_k` | integer | `10` | `1..100` |
| `max_per_thread` | integer | `2` | Max comment hits per issue/PR thread |
| `explain` | boolean | `false` | Include TreeDB execution telemetry |

### 5. `phrase_search`

Native streaming Block-Max WAND exact phrase and proximity (`slop`) search over TreeDB text-v2 positional postings (zero app-side fallback).

| Parameter | Type | Default | Values / Notes |
| --- | --- | --- | --- |
| `phrase` *(required)* | string | — | Ordered phrase terms |
| `slop` | integer | `0` | Max intervening tokens (`0` = exact adjacency; `1+` bridges light edits or skipped `>256B` tokens) |
| `collection` | string | `repo` | `repo`, `gh_items`, `gh_comments` |
| `top_dir` | string | — | Repo top-level directory filter (`repo` collection) |
| `ext` | string | — | Extension filter without dot (`repo` collection) |
| `exclude_bots` | boolean | `false` | Bot filter (`gh_items` / `gh_comments`) |
| `state` | string | — | `open`, `closed`, `merged` (`gh_items`) |
| `body_only` | boolean | `false` | Require the phrase match to appear in chunk body text (exclude path/heading/title-only matches) |
| `exact_literal` | boolean | `false` | Require a case-insensitive single-line exact substring match (preserving punctuation/whitespace) on top of native positional candidate retrieval |
| `dedupe_content` | boolean | `false` | Collapse repo hits with identical chunk bodies (e.g. canonical/mirrored pages) and record collapsed paths in `duplicate_paths` |
| `top_k` | integer | `10` | `1..100` |
| `max_per_parent` | integer | `2` | Max chunks/comments per parent file/thread |
| `explain` | boolean | `false` | Include TreeDB execution telemetry |

Phrase hits include match provenance fields (`match_fields`, `match_line`, `match_end_line`, `match_excerpt`, and `duplicate_paths` when `dedupe_content: true`), with `snippet` centered on the verified phrase span.

All search responses (`search`, `search_code`, `search_github`, `phrase_search`) also include:
- `snapshot`: `{"repo", "indexed_head_sha", "repo_synced_at", "github_synced_at"}`
- `stats`: `{"returned_hits", "unique_parents", "candidates_evaluated", "omitted_by_parent_cap", "omitted_by_post_filter", "truncated", "candidate_budget_exhausted"}`

### 6. `get_file_context`

Reconstructs indexed chunk(s) for a repo-relative path.

| Parameter | Type | Default | Values / Notes |
| --- | --- | --- | --- |
| `path` *(required)* | string | — | Repo-relative file path |
| `chunk_ordinal` | integer | — | Returns `ordinal-1..ordinal+1` neighbor chunks |
| `start_line` | integer | — | Return chunks overlapping `[start_line, end_line]` |
| `end_line` | integer | — | Inclusive end line |

Returns: `{"path": "...", "status": "indexed|excluded|not_found|unindexed", "skip_reason": "...", "detail": "...", "snapshot": {...}, "chunks": [{"path", "chunk_ordinal", "chunk_count", "heading", "start_line", "end_line", "body"}, ...]}`. When a file is excluded (for example `.json` -> `skip_reason: "excluded_extension"`), read it directly from disk or via `git show origin/main:<path>`.

### 7. `get_github_thread`

Reconstructs an issue or PR body plus chronological comments, reviews, and inline review comments, including top-level `snapshot` provenance (`repo`, `indexed_head_sha`, `github_synced_at`).

| Parameter | Type | Default | Values / Notes |
| --- | --- | --- | --- |
| `number` *(required)* | integer | — | Issue or PR number |
| `exclude_bots` | boolean | `false` | Omit bot-authored comments/reviews |
| `offset` | integer | `0` | Chronological comment pagination offset |
| `limit` | integer | `30` | Maximum comments returned |

### 8. `sync_now`

Triggers an immediate incremental sync and/or maintenance on the live daemon.

| Parameter | Type | Default | Values / Notes |
| --- | --- | --- | --- |
| `repo` | boolean | `true` | Incremental local repository sync |
| `github` | boolean | `true` | Incremental GitHub `updatedAt` sync |
| `maintain` | boolean | `false` | Force TreeDB `MaintainTextIndexes` sealing + compaction |

## Direct Transport Recipes

### Streamable HTTP (`curl`)

```sh
# Health and status (plain HTTP endpoints)
curl -fsS http://127.0.0.1:7337/health
curl -fsS http://127.0.0.1:7337/status | jq .

# MCP JSON-RPC tool call
curl -fsS -X POST http://127.0.0.1:7337/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"phrase_search","arguments":{"phrase":"elastic electron","collection":"repo","top_k":5,"explain":true}}}'
```

### Unix Domain Socket (`curl` or stdio proxy)

```sh
# HTTP over Unix domain socket
curl -fsS --unix-socket /path/to/daemon.sock http://unix/health

# Newline-delimited stdio JSON-RPC proxy
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"status","arguments":{}}}' \
  | treedb-repo-mcp mcp --no-autostart --socket /path/to/daemon.sock
```

### Read-Only CLI (`treedb-repo-mcp query` / `status`)

```sh
treedb-repo-mcp status --repo /path/to/repo --data-dir /path/to/db
treedb-repo-mcp query --repo /path/to/repo --data-dir /path/to/db --target code --ext md "bell inequality"
treedb-repo-mcp query --repo /path/to/repo --data-dir /path/to/db --target github --exclude-bots "CHSH"
treedb-repo-mcp query --repo /path/to/repo --data-dir /path/to/db --target phrase --collection repo --explain "elastic electron"
```

## Interpreting `explain: true` Telemetry

- `explain.serving.block_max_enabled`: confirms Block-Max WAND pruning was active.
- `text_stats.TextBlockMaxFallbacks` / `hybrid_stats.text_block_max_fallbacks`: should be `0` on sealed blocks.
- `text_stats.FullDocumentScanFallbacks`: should be `0`.
- `text_stats.TextPostingBlocksSkipped`: posting blocks pruned by Block-Max upper bounds without decoding.
- `text_stats.TextPhraseCandidatesChecked` / `TextPositionLookups`: documents that passed BM25F upper-bound pruning and entered positional phrase verification.
