---
name: treedb-repo-mcp-search
description: Search any repository's prose, source code, and GitHub issues, pull requests, reviews, and comments through a treedb-repo-mcp server. Use when answering codebase or issue-history questions via MCP tools, Streamable HTTP, Unix socket proxy, or CLI queries, choosing search filters, running native Block-Max WAND phrase searches, reconstructing file chunks or GitHub threads, or checking index freshness.
---

# TreeDB Repo MCP Search

Use this skill to get fast, high-precision answers from any `treedb-repo-mcp` server (embedded TreeDB full-text BM25F, native streaming Block-Max WAND phrase search, optional semantic vector / Hybrid RRF, and full GitHub issue/PR/comment history).

## When To Use

Use this skill when:

- searching repository documentation, code, or design history indexed by `treedb-repo-mcp`;
- hunting exact phrases, identifiers, citations, or error strings across prose, code, issues, PRs, and review comments;
- filtering GitHub threads by state, author, label, bot exclusion, number range, or update window;
- reconstructing surrounding file chunks or full chronological GitHub discussions without scraping the GitHub API;
- checking index freshness (`status`) or triggering an incremental refresh (`sync_now`).

Do not use this skill for:

- installing, configuring, upgrading, regenerating, or troubleshooting a `treedb-repo-mcp` daemon (use `treedb-repo-mcp-ops`);
- searching excluded numeric/binary artifacts (`.json`, `.jsonl`, `.csv`, `.tsv`, `.log`, `.npz`, `.pdf`, images, archives) unless the server was explicitly configured with `--include-ext`.

## Inputs Needed

Determine which transport is available:

1. **Connected MCP tools** (preferred when the server is mounted in your client's `mcp_config.json`): call `status`, `search`, `search_code`, `search_github`, `phrase_search`, `get_file_context`, `get_github_thread`, `sync_now` directly.
2. **Streamable HTTP endpoint** (`--url http://<host>:<port>/mcp` or `TREEDB_MCP_URL`): use [scripts/mcp_call.py](scripts/mcp_call.py) or `POST /mcp`.
3. **Unix domain socket** (`--socket /path/to/daemon.sock` or `TREEDB_MCP_SOCKET`): use [scripts/mcp_call.py](scripts/mcp_call.py) or `treedb-repo-mcp mcp --no-autostart --socket <sock>`.
4. **Offline read-only CLI**: `treedb-repo-mcp query --repo <repo> --data-dir <db> ...` (no running daemon required).

If none of these endpoints or paths are known, ask the user for the MCP server URL, socket path, or `--data-dir`.

## Tool Selection Matrix

| Goal | Primary Tool | Follow-Up Tool |
| --- | --- | --- |
| Check HEAD parity, `embedding.enabled`, O(1) index health | `status` | `sync_now` if stale |
| Broad cross-source discovery (code + issues + PRs + comments) | `search` | `get_file_context` / `get_github_thread` |
| Targeted code or doc search by directory, extension, language, or path | `search_code` | `get_file_context` |
| Issues, PRs, reviews, or comments with author/state/bot/date filters | `search_github` | `get_github_thread` |
| Exact multi-word phrase or proximity (`slop`) match | `phrase_search` | `get_file_context` / `get_github_thread` |
| Read surrounding lines/chunks of a matched file | `get_file_context` | Direct file read if editing |
| Read an entire issue/PR body plus chronological comments/reviews | `get_github_thread` | Paginate with `offset` / `limit` |
| Pull freshly pushed commits or GitHub updates right now | `sync_now` | `status` to confirm new HEAD/watermark |

For complete parameter schemas and response shapes, see [references/tool-reference.md](references/tool-reference.md).

## Workflow

### 1. Check `status` first (O(1), sub-50 ms)

Call `status` once at the start of an investigation to confirm:

- **Freshness**: compare `current_head_sha` vs `repo_sync_state.head_sha` and check `github_sync_state.synced_at` and `daemon.watching`.
- **Available search modes**: check `embedding.enabled`. Only pass `mode: "hybrid"` or `mode: "vector"` when `embedding.enabled` is `true`; otherwise stay on the default `mode: "lexical"`.
- **Index cleanliness**: check `collections[]` (`live_documents`, `deleted_documents`, `sealed_posting_blocks`, `micro_posting_blocks`, `stale_postings`, `root_generation`).

### 2. Choose the narrowest high-signal query

- **Start broad only when unsure where a topic lives**: use `search` with `exclude_bots: true` and `max_per_parent: 2`, or restrict `sources` (e.g. `["repo", "issues", "prs"]`).
- **Filter repo searches early with `search_code`**: narrow by `top_dir`, `sub_dir`, `ext` (`md`, `go`, `py`, `lean`, `tex`, `rs`, `ts`), `lang`, `path`, or `path_prefix`. Keep `max_chunks_per_file: 2` (or `1` for wide file discovery).
- **Filter GitHub searches early with `search_github`**: pass `exclude_bots: true` by default unless inspecting bot logs (CodeRabbit, Codex, CI bots). Combine `scope` (`all`, `issues`, `prs`, `comments`), `state` (`open`, `closed`, `merged`), `author`, `label`, `comment_kind` (`issue_comment`, `review`, `review_comment`), `number_min`/`number_max`, and `updated_after`/`updated_before`.
- **Use boolean or AND mode when `or` is noisy**:
  - `operator: "and"` requires all query terms without needing boolean syntax.
  - `query_mode: "boolean"` supports `AND`, `OR`, `NOT`, and quoted phrases (for example `"bell inequality" AND CHSH NOT nonlocal`).
- **Use `phrase_search` for exact terminology and identifiers**:
  - TreeDB executes native streaming Block-Max WAND phrase intersection with zero app-side fallback, even when individual terms appear in tens of thousands of documents.
  - Use `slop: 0` for exact adjacency; use `slop: 1` or `2` for light phrasing variation or to bridge a skipped oversized token (`> 256` bytes, where TreeDB preserves a position gap).
  - Scope with `collection` (`repo`, `gh_items`, `gh_comments`) plus `top_dir`/`ext` (repo) or `exclude_bots`/`state` (GitHub).
  - Inspect `match_fields`, `match_line`..`match_end_line`, and `match_excerpt` to see whether a match came from prose vs path/heading and what exact punctuation/line break appeared. Pass `body_only: true` to exclude path/heading-only matches, `exact_literal: true` for a single-line literal substring match, and `dedupe_content: true` to collapse identical mirrored pages into `duplicate_paths`.

### 3. Reconstruct full context before citing or concluding

Never rely solely on truncated search snippets:

- **Files**: call `get_file_context` with `path` plus either `chunk_ordinal` (returns `ordinal-1..ordinal+1` neighbor chunks) or `start_line`/`end_line`. Inspect `status` (`indexed`, `excluded`, `not_found`, `unindexed`), `skip_reason` (e.g. `excluded_extension` for `.json`), `snapshot`, and `chunks[]`. For authoritative citations or excluded files, read the exact Git object directly (`git show origin/main:<path> | nl -ba`).
- **GitHub threads**: call `get_github_thread` with `number`, `exclude_bots: true`, and paginate large threads with `offset` and `limit` (default `30`). Check `snapshot.repo` to avoid confusing similarly numbered issues across repositories.
- **Check `stats` on search responses**: inspect `stats.unique_parents`, `stats.omitted_by_parent_cap`, `stats.truncated`, and `stats.candidate_budget_exhausted` before concluding a result set is exhaustive.

### 4. Refresh when stale (only when needed)

- If `repo_sync_state.head_sha != current_head_sha`, `daemon.watching` is false, or a GitHub comment was just posted, call `sync_now` with `{"repo": true, "github": true, "maintain": false}`.
- Only pass `"maintain": true` when deliberately sealing accumulated `micro_posting_blocks` or purging tombstones (`deleted_documents`/`stale_postings`); normal maintenance runs automatically on the daemon schedule.

### 5. Diagnose unexpected hits or latency with `explain: true`

Pass `explain: true` on `search`, `search_code`, `search_github`, or `phrase_search` to inspect `text_stats` / `hybrid_stats` / `explain.serving`:

- Confirm `TextBlockMaxFallbacks == 0` and `FullDocumentScanFallbacks == 0`.
- Check `TextPostingBlocksSkipped`, `TextPhraseCandidatesChecked`, and `TextPositionLookups`.
- For `phrase_search`, note that `explain: true` with no scalar filters runs directly on TreeDB `SearchText`, while filtered or non-explain calls run through `SearchHybrid` with `index_state_postfilter`.

## Fallback Helper Commands

When native MCP tools are not wired into the active client, run the stdlib helper [scripts/mcp_call.py](scripts/mcp_call.py) (read-only by default; blocks `sync_now` unless `--allow-write` is passed):

```sh
# Health and O(1) status over Streamable HTTP
python3 scripts/mcp_call.py --url http://127.0.0.1:7337/mcp health
python3 scripts/mcp_call.py --url http://127.0.0.1:7337/mcp call status

# Native phrase search with explain telemetry
python3 scripts/mcp_call.py --url http://127.0.0.1:7337/mcp call phrase_search \
  --arg phrase="elastic electron" --arg collection=repo --arg top_k=5 --arg explain=true

# Filtered GitHub search excluding bots, then full thread fetch
python3 scripts/mcp_call.py --url http://127.0.0.1:7337/mcp call search_github \
  --arg query="Bell" --arg scope=all --arg exclude_bots=true --arg top_k=5
python3 scripts/mcp_call.py --url http://127.0.0.1:7337/mcp call get_github_thread \
  --arg number=254 --arg exclude_bots=true --arg limit=20

# Over a local Unix domain socket instead of HTTP
python3 scripts/mcp_call.py --socket /path/to/daemon.sock call status
```

## Common Pitfalls

- **Requesting `hybrid` or `vector` on a lexical-only store**: returns an error when `status.embedding.enabled` is `false`. Check `status` first.
- **Searching `.json`, `.csv`, or `.log` files**: excluded by default to prevent numeric-dump noise. Do not conclude a JSON/CSV file lacks a value based on MCP search alone.
- **Fewer than `top_k` hits on `phrase_search` or `search_code`**: parent collapsing (`max_per_parent` / `max_chunks_per_file`, default `2`) merges multiple high-scoring chunks from the same file or thread. Increase `top_k` or `max_per_parent` if you want more chunks per file.
- **Expecting `get_file_context` to return a flat `content` string**: it returns `{"path": "...", "chunks": [{"chunk_ordinal", "start_line", "end_line", "heading", "body"}, ...]}`.
- **Tokens longer than 256 bytes**: TreeDB's `TextAnalyzerSimple` skips contiguous runs over `MaxTokenBytes` (256 B default) while incrementing position by 1, preserving phrase-gap semantics (`slop: 0` will not bridge an elided token; `slop: 1` will).

## Validation

Before citing findings from `treedb-repo-mcp`:

- [ ] Confirmed index freshness via `status` (`head_sha` and `github_sync_state.synced_at`).
- [ ] Reconstructed relevant matches with `get_file_context` or `get_github_thread` rather than quoting truncated snippets.
- [ ] Checked whether missing results could be due to default excluded extensions or `exclude_bots` filters.

## Failure Handling

Pause and report if:

- `/health` or the Unix socket is unreachable (hand off to `treedb-repo-mcp-ops` to inspect or restart the daemon);
- `status` reports a fail-closed text index error (indicates an un-migrated or corrupted store that needs `treedb-repo-mcp-ops` regeneration);
- `sync_now` fails on GitHub authentication or rate limits (check `GITHUB_TOKEN` / `gh auth status`).

## Final Report Format

When answering a user query using this server, cite:

- indexed commit (`head_sha`) or GitHub watermark when freshness matters;
- exact repo-relative file paths + line ranges and/or GitHub issue/PR numbers;
- any filters applied (`top_dir`, `ext`, `exclude_bots`, `state`, `slop`);
- any coverage limits (e.g. excluded `.json`/`.csv` files or lexical-only mode).
