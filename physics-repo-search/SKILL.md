---
name: physics-repo-search
description: Search the live snissn/physics repository (markdown papers, notes, Lean proofs, Python code) and all GitHub issues, pull requests, reviews, and comments via the hosted treedb-repo-mcp server on host185 (http://192.168.0.185:7337/mcp). Use when researching prior claims, theorems, provenance, issues, or PR discussions in snissn/physics instead of slow local grep or GitHub API pagination.
---

# Physics Repo MCP Search (`snissn/physics`)

Use this skill to query the live `treedb-repo-mcp` instance indexing `snissn/physics` (prose, code, Lean proofs, plus all GitHub issues, PRs, reviews, and inline review comments) hosted on `host185`.

For general `treedb-repo-mcp` query methodology and full tool schemas, see the companion skill `treedb-repo-mcp-search` ([tool reference](../treedb-repo-mcp-search/references/tool-reference.md)). For upgrades, regeneration, or daemon troubleshooting, use `treedb-repo-mcp-ops`.

## When To Use

Use this skill when:

- looking up prior definitions, theorems, claims, provenance, or design decisions across `snissn/physics` files and GitHub discussions (default `mode: "hybrid"` when embeddings are enabled, or explicit `mode: "lexical"` / `mode: "vector"`);
- running conceptual or terminology-bridging queries via `mode: "hybrid"` (weighted RRF over BM25F + `BAAI/bge-m3` 1024d / 8,192-token cosine ANN with `scalar_u8` `quantized_rerank` default and optional `vector_mode: "exact"` override) or pure semantic `mode: "vector"`;
- running exact phrase or proximity queries (for example `"elastic electron"`, `"Bell inequality"`, `"common-past preparation"`) across the full corpus;
- searching GitHub issues, PRs, reviews, and comments in `snissn/physics` with bot exclusion, state, label, author, number range, or date filters;
- reconstructing full file chunks or chronological GitHub issue/PR threads without burning GitHub API quota.

Do not use this skill for:

- searching excluded numeric/structured output dumps (`.json`, `.jsonl`, `.csv`, `.tsv`, `.log`, `.npz`, `.f64le`, `.pdf`) — inspect those files directly in the workspace or on `host185`.

## Live Endpoints & Corpus Profile

- **Streamable HTTP MCP** (reachable from Mike's laptop and LAN): `http://192.168.0.185:7337/mcp`
  - Health: `http://192.168.0.185:7337/health`
  - Status JSON: `http://192.168.0.185:7337/status`
- **Unix socket on `host185`**: `/home/mikers/treedb-mcp-work/physics.sock`
- **Daemon binary / data dir on `host185`**: `/home/mikers/treedb-mcp-work/bin/treedb-repo-mcp` serving `/home/mikers/treedb-mcp-work/physics-db`
- **Local GPU embedding service on `host185`**: `/home/mikers/treedb-mcp-work/bin/embed_server.py` serving `BAAI/bge-m3` (1024d, 8,192-token context window, FP16 CUDA on RTX 3060 Ti, `encoding_format=base64` wire transport) at `http://127.0.0.1:8089/v1/embeddings` (health: `http://127.0.0.1:8089/health`)
- **Capabilities**:
  - Full-text BM25F (`text-v2`, camelCase/snake_case splitting, `MaxTokenBytes: 256` with phrase-gap preservation, and automatic `OR -> AND` / single-digit token budget retry for decimal literals like `"0.497092635"`)
  - Format-aware chunking (`Markdown`, `Code`, `LaTeX` presets, `SeparatorPlacementStart`, `SnapOverlapToBoundary`, fenced-code / display-math guards, and `H1 > H2 > H3` heading breadcrumbs) with fail-closed chunk-vs-embedder context-window validation
  - Semantic vector & weighted hybrid RRF search (`embedding.enabled: true`, `BAAI/bge-m3` 1024d cosine `column_graph` ANN with `scalar_u8` `quantized_rerank` default + optional `vector_mode: "exact"` FP32 override across `repo_chunks`, `gh_items`, and `gh_comments`): supports `mode: "hybrid"` (default), `mode: "lexical"`, and `mode: "vector"` on `search`, `search_code`, and `search_github`, with graceful lexical fallback during transient vector-graph rebuilds
  - Column-projected vector storage (`ColumnRetainedPayloadNonColumn` + `ExcludePaths: ["embedding"]` on doc fetches, zero JSON vector decode overhead) and compressed outer B+tree leaves in `leaf_vlog` (`IndexOuterLeavesInValueLog=true`, compact internal-node-only `index.db` ~53 MiB, ~3.2 GiB fresh DB footprint) with automatic `ColumnAssetGC` on superseded vector graph assets
  - Native streaming Block-Max WAND exact/proximity `phrase_search` (zero app-side fallback even on 15k-DF terms like `"elastic electron"`) with `match_fields`, `match_line`..`match_end_line`, `match_excerpt`, plus optional `body_only`, `exact_literal`, and `dedupe_content` filters
  - Snapshot provenance (`snapshot: {repo, indexed_head_sha, repo_synced_at, github_synced_at}`) and rank/collapse/truncation counters (`stats: {returned_hits, unique_parents, candidates_evaluated, omitted_by_parent_cap, omitted_by_post_filter, truncated, candidate_budget_exhausted}`) on search responses
  - Explicit `status` (`indexed`, `excluded`, `not_found`, `unindexed`) and `skip_reason` (e.g. `excluded_extension` for `.json`/`.csv`, `gitignored`, `too_large`, `not_indexed_yet`) on `get_file_context`
  - O(1) `status` (~12 ms across ~918k sealed posting blocks)
  - Realtime `fsnotify` watching + default-on 60 s safe remote git fast-forward polling + 60 s incremental GitHub polling (with live vector-graph rebuilds) + 15 m periodic maintenance

## Quick Commands

If native MCP tools for `physics` are already mounted in your client, call them directly. Otherwise use the shared helper [../treedb-repo-mcp-search/scripts/mcp_call.py](../treedb-repo-mcp-search/scripts/mcp_call.py):

```sh
export TREEDB_MCP_URL="http://192.168.0.185:7337/mcp"
MCP="$HOME/.codex/skills/treedb-repo-mcp-search/scripts/mcp_call.py"

# 1. Check health, indexed HEAD SHA, and O(1) block counts
"$MCP" health
"$MCP" call status

# 2. Broad search across repo + GitHub (lexical, semantic vector, or fused hybrid RRF)
"$MCP" call search --arg query="local measurement-dependent CHSH" --arg exclude_bots=true --arg top_k=8
"$MCP" call search --arg query="how does pilot-wave guidance distribute kinetic energy across modes" --arg mode=hybrid --arg exclude_bots=true --arg top_k=8
"$MCP" call search_code --arg query="Bohmian kinetic energy budget stability" --arg mode=vector --arg top_k=8

# 3. Targeted code/paper search inside a lane or extension
"$MCP" call search_code --arg query="elastic electron" --arg top_dir=qm-foundations --arg ext=md --arg top_k=8
"$MCP" call search_code --arg query="torsion inflation" --arg top_dir=docs --arg ext=md --arg top_k=5

# 4. Native exact phrase / proximity search (high-DF safe, zero fallback)
"$MCP" call phrase_search --arg phrase="elastic electron" --arg collection=repo --arg body_only=true --arg dedupe_content=true --arg top_k=5 --arg explain=true
"$MCP" call phrase_search --arg phrase="Kaluza Klein" --arg slop=1 --arg collection=gh_comments --arg exclude_bots=true --arg top_k=5

# 5. Filtered GitHub issue/PR/comment search
"$MCP" call search_github --arg query="Bell" --arg scope=all --arg state=open --arg exclude_bots=true --arg top_k=10

# 6. Reconstruct full context before citing
"$MCP" call get_file_context --arg path="qm-foundations/PHASE-BELL-RESET-2026-09.md" --arg chunk_ordinal=0
"$MCP" call get_github_thread --arg number=2760 --arg exclude_bots=true --arg limit=30
```

Trigger an immediate incremental catch-up only when a commit or GitHub comment just landed and is not yet reflected in `status`:

```sh
"$MCP" --allow-write call sync_now --arg repo=true --arg github=true --arg maintain=false
```

## `snissn/physics` High-Signal Filter Hints

- **Top-level directories (`top_dir`)**: `qm-foundations`, `docs`, `ec-simulation`, `research-intake`, `.` (root files like `AGENTS.md`, `README.md`).
- **Two-level prefixes (`sub_dir`)**: e.g. `qm-foundations/research-atlas-2026-09`, `qm-foundations/elastic-particle-atlas-2026-10`, `qm-foundations/phase-synthesis-2026-09`.
- **Common extensions (`ext`)**: `md`, `tex`, `py`, `lean`, `go`, `txt`.
- **GitHub noise control**: pass `--arg exclude_bots=true` by default so automated review bots do not crowd out substantive physics discussions.

## Validation & Failure Handling

- Check `snapshot.indexed_head_sha` on search/context responses (and `status.current_head_sha` vs `status.repo_sync_state.head_sha`) when asserting claims about recent commits.
- Check `stats.truncated` / `stats.omitted_by_parent_cap` before concluding a hit list is exhaustive; narrow by `top_dir`, `sub_dir`, `ext`, or raise `top_k` / `max_chunks_per_file` when truncated.
- Always reconstruct matches with `get_file_context` or `get_github_thread` before making scientific or provenance claims. When `get_file_context` returns `status: "excluded"` (for example `skip_reason: "excluded_extension"` on `.json`/`.csv` summary files) or `unindexed`, corroborate directly against the exact file or commit via `git show origin/main:<path>`.
- If `http://192.168.0.185:7337/health` is unreachable, check connectivity to `host185` (via `dot-laptop-to-111`) and use `treedb-repo-mcp-ops` to inspect `/home/mikers/treedb-mcp-work/daemon.log` or restart the daemon.
