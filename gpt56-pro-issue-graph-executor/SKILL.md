---
name: gpt56-pro-issue-graph-executor
description: Execute and merge GitHub issue dependency graphs from a parent tracker in the GPT-5.6 Pro ChatGPT harness. Use the connected GitHub adapter first, replace subagent delegation with isolated multi-worktree lanes and interleaved execution, build and test gomap locally, persist resumable graph state, and make later invocations idempotently continue branches, PRs, CI, reviews, and topological merges.
---

# GPT-5.6 Pro Issue Graph Executor

Use this skill when the user gives a parent GitHub issue such as `snissn/gomap#4051` and asks GPT-5.6 Pro to implement as much of the child graph as possible.

Invocation defaults to **execute, review, and merge the selected graph**. Inspect live state, implement ready nodes, open or resume PRs, run tests and performance evidence, resolve review and CI findings, and merge in dependency order when repository policy permits. Do not stop after writing a plan or opening empty PRs. If the current invocation cannot finish the graph, leave durable remote state that a later invocation can reconcile and continue without duplicating work.

## Harness Contract

This is not the Codex subagent executor.

- GPT-5.6 Pro is the sole graph coordinator, implementer, integrator, and final reviewer.
- Do not invoke Codex subagents, Orca, Pi, or imaginary background workers.
- “Parallel” means maintaining several isolated issue lanes and interleaving useful work while tests, builds, CI, or reviews run. Use separate worktrees and branches; start concurrent shell processes only when the runtime supports them and observe their results in the current invocation.
- Never claim asynchronous work will continue after the response. Before ending, publish coherent progress and update the durable handoff.
- Prefer the connected GitHub adapter for repository, issue, branch, file, PR, review, CI, and merge operations. `gh` is optional, not a prerequisite.
- Use the shell for local source, builds, tests, benchmarks, diffs, and git worktrees when available. A missing `gh` binary or shell DNS failure does not by itself block GitHub work.
- Preserve unrelated user changes. Never use destructive git cleanup merely to simplify lane management.

## Inputs

Required:

- repository, inferred from an issue URL or stated as `owner/repo`;
- parent tracker issue number or URL.

Optional:

- execution mode: `execute-and-merge` (default), `readiness-only`, or `no-merge`;
- maximum active lanes;
- explicitly excluded nodes;
- permission for speculative descendants before predecessors merge.

Resolve missing repository identity from the parent issue or current checkout. Ask only when neither source identifies it.

## Compose With

Load and apply these skills when available:

- `gh-tracker-issue` for tracker structure, authoritative gate ownership, and graph mutation;
- `github-pr-mergeable` for latest-head CI, review, performance, and merge gates;
- `github:gh-fix-ci` for GitHub Actions diagnosis;
- `github:gh-address-comments` for actionable PR review findings;
- `build-gomap` whenever the target is `snissn/gomap`.

Read:

- [lane execution](references/lane-execution.md) before selecting active lanes;
- [state and resume](references/state-and-resume.md) before writing graph state;
- [gomap local execution](references/gomap-local-execution.md) before modifying or testing `snissn/gomap`.

## Default Authorization And Scope

A request such as “implement as much of #4051 as you can” authorizes implementation, PR creation, review/fix loops, and merge of PRs that are:

- children or explicitly adopted dependencies of the selected parent;
- within the parent’s declared scope;
- allowed by repository policy;
- objectively mergeable on their exact latest head.

Do not merge unrelated nearby PRs. Respect explicit no-merge instructions and human-approval requirements. Never merge with stale CI, unresolved material findings, missing required evidence, or an unaccepted material performance regression.

## GitHub Adapter First

Use the connected GitHub adapter as the source of truth for remote state.

Typical adapter operations include:

- repository and policy inventory: `get_repo`, `fetch_file`, `search`;
- graph inventory: `fetch_issue`, `fetch_issue_comments`, `search_issues`;
- branch and PR discovery: `search_branches`, `search_prs`, `fetch_pr`;
- branch and file publication: `create_branch`, `create_blob`, `create_tree`, `create_commit`, `update_ref`, `create_file`, `update_file`;
- PR lifecycle: `create_pull_request`, `update_pull_request`;
- CI and reviews: `get_commit_combined_status`, `fetch_commit_workflow_runs`, `list_pull_request_reviews`, `list_pull_request_review_threads`, `fetch_pr_comments`;
- final merge: `merge_pull_request`.

Prefer one tree/commit update for a coherent multi-file patch when the adapter exposes Git data operations. If only contents operations are practical, serialize writes to the same branch and verify the final head.

Do not invent shell-only blockers. If local git cannot push, publish the tested patch through the adapter. If local source cannot be acquired, follow the gomap source fallback and record exactly what could and could not be tested.

## Startup Reconciliation

Every invocation begins by reconstructing reality rather than trusting prior prose.

1. Read repository policy, the parent issue, every linked child, relevant comments, open/closed PRs, and current default-branch SHA.
2. Locate the parent comment marked:

   ```text
   <!-- gpt56-pro-issue-graph-executor:state:v1 -->
   ```

3. Reconcile the saved state against live branches, PR heads, merges, CI, review threads, issue states, and current dependencies.
4. Reuse existing issue branches and PRs. Never create a second implementation PR for the same node without recording why the first was superseded.
5. Recompute the DAG, contract surfaces, conflict surfaces, ready nodes, and critical path.
6. Refresh the state comment before implementation if the saved graph is materially stale.
7. Present a concise graph snapshot and continue immediately.

A previous invocation’s `running` state is only a hint. Live GitHub state wins.

## DAG And Gate Ownership

Construct edges from, in order:

1. explicit `depends on`, `blocked by`, and parent ledger links;
2. predecessor PR/base relationships;
3. issue wording and completion gates;
4. shared public contracts, storage formats, schemas, or migration decisions that make parallel work unsafe.

Assign each node exactly one authoritative exit gate. Record:

- predecessors and successors;
- contract surface;
- likely conflict files/modules;
- required tests and benchmarks;
- performance class;
- local build target;
- branch, PR, base SHA, and head SHA;
- exact next action.

Do not turn every related issue into a dependency. Keep historical/evidence issues separate from executable nodes.

## Lane Budget

Optimize wall time without sacrificing correctness.

- Default to **three active implementation lanes**.
- Raise to four only when the fourth lane is genuinely disjoint, the repository and machine can support it, and coordinator attention will not become the bottleneck.
- Keep at most **two CPU- or I/O-heavy Go build/test processes** active simultaneously.
- Use one canonical branch and worktree per issue.
- Keep one writer per contract/conflict surface.
- Serialize storage-format, public API, shared manifest, migration, authentication, authorization, and heavily overlapping command-dispatch work.
- Prefer graph-multiplier foundations that unblock the most successors.
- After foundations merge, fill available lanes with ready independent children.
- Do not start descendants before direct predecessors merge unless the user explicitly authorizes speculative work and the predecessor contract is stable enough to snapshot.
- A lane waiting on hosted CI or external review should not monopolize implementation capacity; switch to another ready lane and return later.

“Active lane” means a node with real implementation, test, review-fix, or merge work in this invocation. Do not count merely open PRs as active work.

## Interleaved Execution Round

Use short rounds rather than finishing one independent lane while all others remain idle.

1. **Prepare:** create or resume each lane’s worktree and verify its exact base.
2. **Red:** add the smallest failing test or record an allowed instrumentation/docs exception.
3. **Implement:** make the smallest coherent change for that issue.
4. **Start validation:** run focused tests or a bounded build. When supported, leave the process in a named shell session.
5. **Switch lanes:** work on another ready issue while the first lane’s validation runs.
6. **Collect:** inspect every process result; do not leave unobserved background jobs.
7. **Publish:** commit and push or adapter-publish coherent progress; update the PR body.
8. **Review:** perform an internal deep review before requesting external AI review.
9. **Gate:** move the lane to review, CI, fix, merge, or durable handoff state.

Prefer merging a completed predecessor over accumulating several speculative descendants.

## Local Worktrees

Canonical branch naming:

```text
gpt56/issue-<issue-number>-<short-slug>
```

Canonical worktree hint:

```text
<work-root>/worktrees/issue-<issue-number>
```

Resume rules:

- existing remote branch plus open PR: fetch and resume it;
- existing remote branch without PR: inspect it, test it, then open or intentionally abandon it;
- open PR on another branch that clearly owns the issue: adopt that PR instead of creating a duplicate;
- merged PR: mark the node merged and recompute descendants;
- closed unmerged PR: inspect disposition before reusing or replacing its branch.

Use `scripts/prepare-gomap-worktree.sh` for `snissn/gomap` when a normal local git checkout is available.

## Test-First And Performance Rules

Every implementation PR must identify the first externally meaningful behavior or invariant.

- Add a test that fails for the intended baseline reason before implementation.
- Documentation-only, pure instrumentation, benchmark-harness, or mechanical changes may record an explicit exception and alternative evidence.
- Run focused tests first, then broader affected tests.
- Use reopen, crash/recovery, corruption, race, fault-injection, or official-driver tests when they express the real risk.
- For hot-path, query, storage, wire, concurrency, cache, I/O, encoding, bulk, or maintenance changes, require relevant before/after evidence.
- A material regression in runtime, throughput, latency, allocation, memory, storage, rebuild, checkpoint, recovery, or domain counters blocks mergeability until optimized or explicitly accepted with evidence.
- An optimization issue that misses its stated improvement gate is incomplete even when CI is green.

For `snissn/gomap`, use the repository’s current issue-specific commands and the environment described in [gomap local execution](references/gomap-local-execution.md). Never run `go mod tidy` merely to make a build start.

## Publishing And PR Bodies

Each PR body must contain:

```text
Parent tracker:
Child issue:
Executor state marker:
Base branch/SHA:
Current head SHA:
Owned contract surface:
Non-goals:
Red-test evidence or exception:
Tests and exact commands:
Performance classification and evidence:
CI status:
Review status:
Known risks:
Exact next action:
```

Add this marker:

```text
<!-- gpt56-pro-issue-graph-executor:node:v1 -->
```

When the implementation is incomplete but useful, publish a draft PR with a coherent WIP commit and precise failing evidence. Do not rely on an ephemeral local patch as the only handoff.

## Review And CI Loop

Use `github-pr-mergeable` semantics.

Before requesting Codex, Copilot, CodeRabbit, or other review-credit-consuming reviewers:

- implementation is coherent;
- focused and broader affected tests are green or an exact blocker is documented;
- required benchmark evidence is posted;
- PR body is current;
- latest-head CI is running or green;
- internal deep review has no known blocker.

Use the adapter to inventory exact-head comments, formal reviews, and review threads when `gh` or the bundled classifier is unavailable. A clean Codex artifact must identify the current head, and unresolved Codex findings supersede older clean results.

Do useful work in other lanes while CI or review is pending. Revisit at deliberate sync points rather than polling continuously.

## Merge Gate

A node may merge only when:

- all predecessors are merged;
- the branch is updated to the intended final base;
- required checks were rerun after the final base update;
- the PR diff matches the issue and does not absorb sibling scope;
- latest-head CI is acceptable;
- all material review findings and threads are resolved or explicitly rejected with rationale;
- required exact-head Codex state is clean or a permitted bounded unavailability disposition exists;
- performance and persistence evidence is current;
- repository policy permits the coordinator to merge.

Merge independent nodes in whichever order reaches the gate first. After each merge, update the parent state and resynchronize affected descendants.

## Durable Handoff

Before ending every invocation:

1. Push or adapter-publish every coherent lane state.
2. Update each PR body or child issue with current head, tests, blockers, and next action.
3. Update the parent state comment using [state and resume](references/state-and-resume.md).
4. Record `dispatchable_now`, `review_or_ci_pending`, `fix_needed`, and `blocked`.
5. Record any local-only limitation and how to reconstruct the tested source.
6. Ensure no node is labeled `merged`, `mergeable`, or `dependency-ready` from stale evidence.
7. Validate a saved state file with:

   ```sh
   python3 scripts/validate_graph_state.py <state.json>
   ```

A later invocation should be able to continue using GitHub alone even if the previous local worktrees no longer exist.

## Example: Parent `snissn/gomap#4051`

Always reread the live tracker; this is only an execution-shape example.

- Start the independent foundations `#4052` and `#4061` in separate lanes.
- Prioritize finishing and merging `#4052` because it unlocks several gateway children.
- After `#4052` merges, fill lanes with ready independent nodes such as `#4053`, `#4054`, and `#4055`, while `#4061` or its successor continues in another lane if capacity permits.
- Keep each child on its own branch and PR.
- If the invocation ends with those PRs in implementation, CI, or review, publish exact heads and state so the next call resumes rather than recreates them.
- Do not begin `#4056` before `#4054`, or compound planner work before its index and explain predecessors, unless the live tracker has changed.

## Completion

Continue until every selected node is:

- merged;
- intentionally deferred to a linked owner with accepted scope;
- or blocked by external state with a durable blocker, owner, and exact next action.

## Final Report

Report:

- parent tracker and durable state comment;
- nodes merged, open, review/CI pending, fix-needed, and blocked;
- branches, PR URLs, exact heads, and merge SHAs;
- tests, benchmarks, CI, and review evidence;
- local source/build method and any network/tool fallback;
- active-lane strategy used;
- exact dispatchable nodes for the next idempotent invocation.
