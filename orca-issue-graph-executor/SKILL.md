---
name: orca-issue-graph-executor
description: "Execute a flexible dependency graph of GitHub issues with Orca Pi subagent managers: infer ticket dependencies, run independent layers in parallel, pipeline one or more speculative successors once predecessors are dependency-ready, and enforce predecessor merges before dependent mergeability."
---

# Orca Issue Graph Executor

Use this skill when the user provides a list of GitHub issues/tickets that may contain dependency relationships and wants Orca agents to execute as much work in parallel as safely possible.

This skill extends the serial contract in `/skill:orca-issue-list-executor` with graph scheduling. It composes:

- `/skill:orca-issue-list-executor` for per-issue lifecycle gates, coordinator final review, default merge-after-gates behavior, and merge sequencing.
- `/skill:orca-subagent-manager` for one xhigh manager per issue/task.
- `/skill:github-pr-mergeable` for PR readiness, CI, AI reviews, PR body quality, and latest-head evidence.

See [dependency execution model](references/dependency-execution.md) and [manager prompts](references/manager-prompts.md) for detailed templates.

## When To Use

Use this skill when:

- a user asks to execute multiple issues with dependencies and parallelism;
- some issues can run in independent topological layers;
- downstream issues can begin speculative implementation before predecessors merge, but must remain blocked on predecessor merge/revalidation;
- the user wants to minimize churn from repeatedly rebasing/upstreaming changes down a dependency tree.

Do not use this skill when:

- the user explicitly requests strict serial execution only; use `/skill:orca-issue-list-executor` instead;
- dependency relationships are unknown and cannot be inferred without a product decision;
- the task is one standalone PR with no graph scheduling concern.

## Inputs Needed

- Repo selector and issue/ticket list.
- Explicit dependency constraints, if the user has them.
- Merge opt-out status, if any. Default assumption is that the user wants mergeable PRs merged.
- Maximum parallel manager count, if the user wants a limit.
- Scheduling mode/pipeline window, if relevant: `strict-serial`, `layer-parallel`, `pipelined`, or `adaptive`, plus max speculative successors/depth.
- Current base branch/ref and Orca parent worktree.

If dependency edges are ambiguous, ask a concise clarifying question before dispatching managers. Do not ask for merge authorization unless the user’s merge intent is explicitly unclear or contradictory; default intent is merge after gates pass.

## Hard Invariants

- The coordinator owns the dependency graph and merge gates; managers own individual issue execution.
- No dependent PR may be called mergeable, moved out of draft/WIP, or merged until all predecessor PRs are merged and the dependent branch is rebased/revalidated on the final base.
- Downstream speculative managers must know they are blocked on predecessor merge and must treat predecessor contracts as snapshots, not final facts.
- Avoid continuous churn: propagate upstream changes to descendants only at defined sync windows or when a public contract/blocker changes.
- Do not let minor, local, non-contract predecessor review churn idle the whole graph. If the predecessor contract is stable and its remaining blocker is local/non-contract (for example a flaky test, docs wording, small review fix, CI retry, or isolated bug not changing exposed APIs/semantics), mark it dependency-ready with a local-fix note and dispatch bounded speculative successors. Keep successors blocked from final review/merge until the predecessor merges and final revalidation passes.
- Prefer wall-time-efficient pipelining with churn control: start useful downstream work from a stable predecessor snapshot, but do not repeatedly rebase descendants for every upstream review-fix commit. Sync only on contract change, predecessor merge, pre-final-review, or stale-test/conflict trigger.
- Managers must keep context bounded: write long logs/diffs/review transcripts and benchmark output to artifact files and summarize them instead of pasting or streaming large terminal output into Pi context.
- Coordinator must actively run the graph loop while any manager is `running` or `gate-review`: poll manager terminals and git/PR state, classify progress, unstick or recover stalled managers, update the manifest, and repeat until each active node reaches `dependency-ready`, `mergeable-candidate`, `merged`, or `blocked/fix-needed`. Do not idle the graph while one predecessor churns on a local/non-contract fix if bounded speculative successors can safely proceed.
- Coordinator must not treat "manager spawned/running" as a stopping condition unless the user explicitly asks to pause. A response to the user while managers remain active must state the coordinator loop is continuing and must include the next poll/recovery action.
- Coordinator must not silently take over manager-owned implementation/finalization work. If a manager stalls, overflows, or loses context, either unstick that manager with a concise prompt or replace it with a fresh manager instance using an artifact-backed handoff.
- Managers must not merge unless the coordinator explicitly delegates merge authority. Coordinator merge rules from `/skill:orca-issue-list-executor` still apply, with default merge intent after gates pass.
- Managers must not request Codex, Copilot, CodeRabbit, or other review-credit-consuming AI reviews until a PR is mature enough to avoid review-credit churn: coherent code, focused tests, required benchmark evidence or rationale, current PR body/status evidence, no known local blockers, and latest-head CI running or green.
- Before spawning managers, produce a graph/execution plan and pause for user approval unless the user has already explicitly authorized immediate execution.
- Cross-cutting format, API, or shared-hot-path changes require a design/contract gate before parallel implementation proceeds.
- Material performance regressions from a PR’s own changes are graph-level blockers: the node stays `fix-needed`/blocked until optimized away or explicitly accepted by the coordinator/user with evidence.
- Insufficient improvement is also a blocker for optimization nodes: if a node's stated gate or the parent north-star metric does not move enough, the coordinator must not treat the node as complete merely because CI/reviews pass. Keep it `fix-needed`, revise the implementation, or create/link a replacement blocker before successors/final gates proceed.
- Do not "give up" by closing a graph as insufficient unless the user explicitly asks to stop. Default behavior is iterative: diagnose the failed gate, update the manifest, dispatch fixes or new blocker nodes, and continue until the gate passes, is explicitly waived, or the user stops execution.

## Workflow

### 1. Load contracts and inspect requirements

1. Load `/skill:orca-issue-list-executor`, `/skill:orca-subagent-manager`, and `/skill:github-pr-mergeable`.
2. Read each issue from GitHub with current title/body/labels/comments as needed.
3. Identify per-ticket execution requirements: tests, benchmarks, review requirements, format/migration constraints, merge gates, and non-goals.
4. Create or update an execution manifest containing issues, edges, layers, state, managers, PRs, base SHAs, sync windows, and blockers.

### 2. Build the dependency graph

1. Parse explicit edges from the user first.
2. Infer additional edges from issue bodies/comments: `depends on`, `blocked by`, `after`, parent tracker ordering, PR stack notes, and required predecessor contracts.
3. Treat the provided order as a weak dependency only when no stronger evidence exists; ask if the order conflicts with inferred independence.
4. Validate the graph is acyclic.
5. Compute topological layers and mark all zero-in-degree nodes as ready.

Pause on cycles, ambiguous foundation edges, or dependency constraints that would make parallel execution unsafe.

### 3. Run conflict and contract risk analysis

Before dispatch, classify each issue by conflict and contract surface:

- touched files/modules and expected overlap;
- public API, on-disk format, benchmark harness, or test contract changes;
- whether a small predecessor/foundation issue should land before broad parallel work;
- whether an issue can run independently, should be speculative, or must be conflict-serialized.

For cross-cutting storage/format work, pick a single contract owner or require a short design gate before starting sibling implementations. Prefer adding explicit edges over allowing high-churn speculative branches.

### 4. Pre-dispatch approval gate

Produce a concise execution plan and stop before spawning managers unless the user already authorized execution. The plan must include:

- inferred dependency graph and layers;
- conflict/contract risk table;
- scheduling mode: `strict-serial`, `layer-parallel`, `pipelined`, or `adaptive`;
- proposed parallel batches, max concurrency, max speculative successors per chain, and max speculative depth;
- which issues, if any, will start speculatively and what they are blocked on;
- merge order and final revalidation gates;
- expected churn risks and sync windows.

Ask for one of: approve execution, revise graph, force serial execution, or stop.

### 5. Dispatch ready work according to the scheduling mode

For each approved ready issue, spawn an isolated xhigh manager using the manager spawn pattern from `/skill:orca-issue-list-executor`.

- Independent roots use the current intended base, usually latest `origin/main`.
- `strict-serial`: start the next dependent only after predecessor merge.
- `layer-parallel`: start all ready independent nodes in topological layers, subject to max parallelism.
- `pipelined`: allow a bounded successor window, commonly one predecessor in finalization plus one speculative descendant. Use this when a predecessor is in CI/review/local-fix churn but its public contract is stable.
- `adaptive`: use `layer-parallel` for independent low-conflict nodes and `pipelined` for high-overlap dependency chains. Prefer adaptive for performance stacks where evidence/review iterations can be long but downstream planning/implementation can proceed against stable contracts.
- Speculative dependents use the most stable predecessor contract snapshot available and are explicitly marked blocked.
- Apply max parallelism, max speculative successors per chain, and max speculative depth from the manifest; otherwise use a conservative number and report it.

Prompt managers with the templates in [manager prompts](references/manager-prompts.md). Require managers to load:

```text
/skill:orca-subagent-manager
/skill:github-pr-mergeable
```

### 6. Track manager states

Use this state model from [dependency execution model](references/dependency-execution.md):

```text
pending -> running -> gate-review -> dependency-ready -> mergeable-candidate -> merged
                       \-> blocked/fix-needed
```

A predecessor becomes **dependency-ready** only when its public contract is stable enough for descendants:

- PR exists and manager reports scope is substantially complete.
- Tests/benchmarks required for the exposed contract have passed locally or in CI.
- Manager has completed at least one implementation/review/fix loop.
- The coordinator/evidence reviewer has completed `gate-review`: command identity, before/after baseline, intended-path counters, north-star/exit thresholds, regressions, and PR/issue claims were checked.
- Any insufficient-improvement result has been fixed, explicitly re-scoped as instrumentation/safety-only, or converted into a linked blocker with graph edges that prevent false final completion.
- Remaining work is expected to be review polish, CI, or non-contract-changing cleanup.
- Handoff states changed APIs, formats, files, branch/head SHA, and known risks.

Dependency-ready is not mergeable. It only permits blocked descendants to start speculative work. If the predecessor still has a minor local blocker, record it as dependency-ready with `local_fix_pending` in the manifest notes/blockers: descendants may start, but the predecessor remains not mergeable until that local blocker is fixed.

### 6.5. Active coordinator poll loop

While any issue manager is in `running` or `gate-review` state, the coordinator must run an active poll loop instead of passively waiting or ending the turn after dispatch.

Poll cadence:

- Active implementation/review loop: poll each running manager at least every 2-5 minutes when the coordinator is active in the conversation.
- CI-only wait: poll PR checks/reviews at least every 10-15 minutes, or sooner when GitHub/webhook output indicates progress.
- Long benchmark/profile runs: record the command, host, artifact directory, expected duration, and poll the process/artifact status at a documented interval appropriate to the run.

Each poll must collect and classify:

- terminal status, latest output cursor/tail, and whether the manager is idle, working, waiting on CI/benchmark, blocked, or requesting input;
- local worktree state: `git status --short`, branch, recent commits, and whether expected files/tests changed;
- PR state if one exists: head SHA, draft/ready state, mergeability, CI, reviews, unresolved threads, and PR body/evidence freshness;
- current node state and the next expected transition;
- manifest changes needed for new commits, PRs, artifacts, blockers, or state transitions.

Coordinator loop:

```text
poll running managers -> classify progress -> update manifest ->
if progress continues: schedule next poll
if input needed: answer or route to user
if idle/stalled: send concise unstick prompt
if still stalled after recovery window: replace/recover manager
if dependency-ready/mergeable/blocked: apply graph gate and proceed
```

Stall handling:

- If a manager is idle with no git/PR/test progress for two consecutive active polls, or roughly 10-15 minutes during an expected implementation phase, send an unstick prompt asking for a concise status, current blocker, and next concrete command/edit.
- If there is still no useful progress after the next poll window, follow Manager continuity and recovery: save facts to the manifest, then restart or replace the manager rather than letting the graph sit idle.
- If the manager is only passively watching CI or a long benchmark and has documented the wait condition, do not treat it as stalled; poll the external condition instead.

### 6.6. Gate-driven evidence review and graph mutation

Before any performance/scaling node can become `dependency-ready`, run a gate review. This is separate from code review and CI.

Gate review checks:

- the benchmark commands match the tracker and use identical before/after dataset shape, hardware/context, durability/cache/compression settings, and measured boundary;
- counters prove the intended path ran and fallback/smoke paths did not satisfy the milestone accidentally;
- the node's explicit exit gate and any parent north-star gates moved by the required threshold;
- no material regression remains unoptimized/unaccepted;
- the PR body and issue comments do not overclaim beyond the evidence.

Gate outcomes:

- **pass**: transition to `dependency-ready` or `mergeable-candidate` as appropriate.
- **fix-needed**: keep the node active and dispatch a fix/profiling loop. Do not start new dependent work if the fix may change public contracts, benchmark semantics, counters, formats, durability behavior, or files consumed by successors. If the blocker is minor/local/non-contract, allow bounded speculative successors while recording `local_fix_pending`.
- **new-blocker**: if the implementation exposed a different bottleneck, pause dependent starts only when the blocker changes downstream assumptions. Otherwise add the blocker to the graph and continue independent or safely speculative work from the stable snapshot.
- **waived**: only with explicit coordinator/user acceptance recorded in the manifest and PR/issue, including the impact and why continuing is acceptable.

Default action on a failed gate is **continue iterating**, not close or document insufficiency. A final/docs/policy node may record a decision, but it must not close the parent graph as complete while north-star gates are unmet unless linked replacement blockers remain open and the user explicitly accepts that outcome.

### 7. Start downstream speculative work

When all direct predecessors of an issue are dependency-ready, start that issue's manager even if predecessors are not merged, unless doing so would cause high churn, exceed the configured pipeline window, or require unresolved product decisions.

Pipeline controls:

- `max_speculative_successors_per_chain`: maximum unmerged descendants that may be running behind a dependency-ready predecessor on a single chain. Use `1` for the common "one next PR while the blocker finalizes" pattern.
- `max_speculative_depth`: how many unmerged edges may separate a speculative node from the nearest merged base. Use `1` for conservative stacks; increase only for stable contracts and low conflict risk.
- `dependency_ready_starts_allowed`: set false to temporarily freeze downstream starts when reviews/benchmarks may still change a public contract.
- `minor_blocker_pipeline_allowed`: default true for adaptive/pipelined execution. Allows successors to start when predecessors have only non-contract local review/CI/test-fix churn. Set false if the remaining blocker might alter APIs, storage formats, durability semantics, benchmark definitions, counters, or downstream file contracts.

The downstream prompt must include:

- predecessor issue/PR URLs and head SHAs;
- contract snapshot it may rely on;
- explicit blocked status and pipeline window limits;
- instruction not to claim mergeability, request final AI review, or request final merge until predecessors merge;
- sync policy and revalidation requirements after predecessor merges.

### 8. Manager continuity and recovery

If a manager is stuck, near context exhaustion, auto-compacting repeatedly, or no longer producing useful concise handoffs:

1. Interrupt or pause the stale manager before starting a replacement, unless it is only passively watching CI and still healthy.
2. Save current facts to the execution manifest: issue, PR, branch, head SHA, base, tests/benchmarks, CI/review state, blockers, and artifact paths.
3. Start a fresh manager terminal in the existing manager worktree when the branch/PR already exists; create a new manager worktree only if the old worktree is dirty, conflicted, or unsafe.
4. Prompt the replacement manager to load required skills, re-read the issue/PR from GitHub, verify local state, and continue from the manifest/handoff.
5. The replacement manager owns remaining manager duties: final test/benchmark reruns, PR body updates, AI review loop, and mergeability handoff. The coordinator may still do independent final review and merge after the manager handoff passes.
6. Do not convert manager recovery into coordinator-owned implementation except for tiny, explicitly documented emergency edits needed to unblock the manager infrastructure itself.

### 9. Minimize churn with sync windows

Do not continuously rebase or upstream every predecessor change down the tree. Sync descendants only:

- when a predecessor first reaches dependency-ready;
- when a predecessor changes a public contract used by descendants;
- when a predecessor merges;
- before dependent final review/mergeability;
- when conflicts or tests show the snapshot is stale.

When syncing, send a concise delta to downstream managers instead of asking them to rediscover the whole upstream diff.

Minimal-churn rule: if a predecessor accumulates multiple non-contract review-fix commits while a descendant is running, do not sync each commit. Batch them and sync only after the predecessor merges or after a contract-affecting change. If the descendant must use a specific predecessor head, record that snapshot SHA and defer restacking until the final base update.

### 10. Final review and merge gates

For every issue, use the coordinator final review and review/fix loop from `/skill:orca-issue-list-executor`.

Before declaring any PR mergeable, and especially a dependent PR:

- no unaccepted material regression remains in runtime, throughput, allocations, storage/rebuild overhead, or relevant counters;
- all predecessor PRs are merged;
- dependent branch is rebased/updated onto the merged base;
- focused tests/benchmarks are rerun after that update;
- PR body reflects final predecessor facts, not speculative snapshots;
- CI/reviews are latest-head, AI reviews were requested only after the final mature head was ready for review, and no blocking threads remain.

Merge in topological order. If a descendant reaches implementation completion early, keep it blocked as `mergeable-candidate` until predecessors merge and final revalidation passes.

## Commands / Examples

Inventory issues:

```sh
gh issue view <ISSUE> --repo <OWNER>/<REPO> \
  --json number,title,url,state,body,labels,comments
```

Inspect PR readiness:

```sh
gh pr view <PR> --repo <OWNER>/<REPO> \
  --json number,title,url,state,headRefName,baseRefName,headRefOid,mergeStateStatus,isDraft,reviewDecision,statusCheckRollup,comments,reviews

gh pr checks <PR> --repo <OWNER>/<REPO>
```

Monitor Orca managers:

```sh
orca terminal read --terminal <manager-term> --limit 300 --json
orca terminal wait --terminal <manager-term> --for tui-idle --timeout-ms 600000
orca terminal list --json
```

## Validation

Before claiming graph execution is complete or paused, verify:

- [ ] Dependency graph and layers are recorded in the manifest.
- [ ] No cycle or unresolved edge remains.
- [ ] Every spawned manager has an issue, base/snapshot, state, terminal, and worktree recorded.
- [ ] Every active `running` or `gate-review` manager has a recent poll record or current wait condition, and the next poll/recovery action is known.
- [ ] No manager is silently idle/stalled without an unstick or recovery action in progress.
- [ ] Every speculative descendant is explicitly blocked on predecessor merge.
- [ ] No dependent PR is called mergeable before predecessors merge.
- [ ] Every mergeable PR has latest-head CI/review evidence after final base update.
- [ ] Merge order follows the dependency graph.

## Failure Handling

Pause and report if:

- graph edges are ambiguous and unsafe to infer;
- conflict/contract risk shows a likely shared on-disk format, API, benchmark, or helper design that should be settled before implementation;
- a predecessor changes public contracts too often for downstream speculative work to remain useful;
- a descendant depends on unresolved predecessor review findings;
- a manager attempts to mark a blocked descendant mergeable before predecessors merge;
- merge conflicts require broad restacking;
- required CI/AI review infrastructure is unavailable and repo policy requires it;
- a manager hits context overflow, exceeds roughly 85% context, or repeatedly auto-compacts; interrupt if needed, ask for an artifact-backed concise handoff, and if recovery is not immediate create a fresh manager instance instead of taking over the manager role;
- benchmark or correctness evidence regresses after final predecessor merge or on the PR’s latest head;
- a performance/scaling node is neutral or insufficient against its stated exit gate and no fix loop, blocker issue, or explicit user waiver has been recorded.

## Final Report Format

Return:

- graph summary: layers, completed nodes, blocked nodes;
- managers spawned with worktree/terminal IDs;
- PRs, branches, head SHAs, review/CI state;
- dependency-ready events and sync windows used;
- merges completed in topological order with merge commits;
- tests/benchmarks by issue;
- blockers, risks, deferred follow-ups, and cleanup recommendations.
