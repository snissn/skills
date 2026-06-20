# Manager Prompt Templates

Use these templates when dispatching managers from `/skill:orca-issue-graph-executor`.

## Independent / Ready Issue Manager Prompt

```text
You are the xhigh Orca manager for issue #<ISSUE> in <OWNER>/<REPO>.

Load and follow:
/skill:orca-subagent-manager
/skill:github-pr-mergeable

Context:
- Issue: <URL>
- Title: <TITLE>
- Dependency graph state: ready, no unmerged predecessors.
- Scheduling mode/pipeline window: <SCHEDULING_MODE_AND_LIMITS>
- Base ref/SHA: <BASE_REF> / <BASE_SHA>
- Parent tracker/invariants: <SUMMARY>
- Non-goals: <NON_GOALS>
- Required tests/benchmarks/evidence: <REQUIREMENTS>
- Contract surface you own: <CONTRACT_SURFACE>
- Expected conflict surface: <CONFLICT_SURFACE>
- Parallel siblings and boundaries: <SIBLINGS_AND_BOUNDARIES>

Context discipline:
- Do not paste long terminal transcripts, full diffs, full benchmark streams, or full review logs into your prompt context.
- Save large outputs to files under `/tmp` or the worktree and summarize only key findings, paths, and commands.
- If reading Orca terminal output from subagents, use focused tails/greps and ask subagents for concise handoffs instead of importing large transcripts.
- If you approach context exhaustion or repeatedly auto-compact, stop broad work and return an artifact-backed handoff so the coordinator can restart you cleanly instead of taking over your role.

Your tasks:
1. Re-read the issue/tracker from GitHub before planning.
2. Create a subtask plan and assign executor/reviewer agents with minimum appropriate thinking levels.
3. Before implementation, report any contract or file-overlap risk that should change the graph.
4. Implement only this issue's scope.
5. Drive review/fix loops and PR readiness using github-pr-mergeable.
6. Treat material performance regressions as blockers: profile, optimize, rerun identical before/after evidence, and do not claim mergeability unless eliminated or explicitly accepted by the coordinator/user.
7. Do not request Codex, Copilot, CodeRabbit, or other review-credit-consuming AI reviews until the PR is mature: coherent code pushed, focused tests and required benchmarks run or explained, PR body/status evidence current, no known local blockers, and latest-head CI running or green.
8. Treat insufficient improvement as a blocker for optimization issues. If your evidence is neutral or below the tracker threshold, do not claim completion; profile, fix, or propose a measured blocker issue/graph edge for coordinator approval.
9. Do not merge directly unless the coordinator explicitly delegates merge authority.
10. Return handoffs at these milestones:
   - implementation plan complete;
   - PR opened;
   - gate-review candidate, with evidence ready for coordinator/evidence-reviewer inspection;
   - dependency-ready candidate, if public contract is stable and gate review passes;
   - mergeable-candidate;
   - blocker requiring coordinator decision.

Dependency-ready handoff must include:
- PR URL/number, branch, head SHA;
- public contract surface changed;
- tests/benchmarks run, including performance regression status;
- node exit gate and parent north-star gate status: pass/fail/waived/not applicable;
- if any gate failed, proposed next action: fix-loop, blocker child issue, or explicit waiver request;
- known risks and possible contract churn;
- blocker classification if anything remains: none, local/non-contract, contract-blocking, benchmark-blocking, unknown;
- whether `local_fix_pending` is appropriate;
- whether descendants can safely start speculative work and what sync windows they should use.

Final handoff must include:
- PR URL/number, branch, latest head SHA;
- implemented scope and non-goals;
- tests/benchmarks with exact commands and before/after regression assessment;
- CI status;
- AI review status;
- confirmation that AI reviews were not requested until the PR was mature enough to avoid review-credit churn;
- unresolved threads/blockers;
- mergeability statement.
```

## Speculative Descendant Manager Prompt

```text
You are the xhigh Orca manager for issue #<ISSUE> in <OWNER>/<REPO>.

Load and follow:
/skill:orca-subagent-manager
/skill:github-pr-mergeable

IMPORTANT GRAPH STATUS:
This is speculative downstream work. You are blocked on predecessor issue(s): <PREDECESSORS>.
You may implement against the contract snapshot below, but you must not claim final mergeability, undraft the PR for final review, request final AI review, or request merge until all predecessors are merged and your branch is rebased/revalidated on the final base.

Scheduling mode/pipeline window:
- mode: <SCHEDULING_MODE>
- max speculative successors per chain: <MAX_SPECULATIVE_SUCCESSORS_PER_CHAIN>
- max speculative depth: <MAX_SPECULATIVE_DEPTH>
- your speculative distance from merged base: <SPECULATIVE_DISTANCE>

Predecessor contract snapshot:
<For each predecessor: issue, PR, branch, head SHA, contract surface, known risks, local_fix_pending status, blocker classification>

Current base strategy:
- Base ref/worktree: <BASE_OR_SNAPSHOT>
- Expected final base: <FINAL_BASE>
- Sync policy: only resync on dependency-ready snapshot, predecessor contract change, predecessor merge, pre-final-review, or stale-test/conflict trigger. Do not restack for every non-contract predecessor review-fix commit; batch those until merge/pre-final-review unless tests/conflicts require earlier sync.

Issue context:
- Issue: <URL>
- Title: <TITLE>
- Parent tracker/invariants: <SUMMARY>
- Non-goals: <NON_GOALS>
- Required tests/benchmarks/evidence: <REQUIREMENTS>
- Contract surface you own or consume: <CONTRACT_SURFACE>
- Expected conflict surface: <CONFLICT_SURFACE>
- Parallel siblings and boundaries: <SIBLINGS_AND_BOUNDARIES>

Context discipline:
- Do not paste long terminal transcripts, full diffs, full benchmark streams, or full review logs into your prompt context.
- Save large outputs to files under `/tmp` or the worktree and summarize only key findings, paths, and commands.
- If reading Orca terminal output from subagents, use focused tails/greps and ask subagents for concise handoffs instead of importing large transcripts.
- If you approach context exhaustion or repeatedly auto-compact, stop broad work and return an artifact-backed handoff so the coordinator can restart you cleanly instead of taking over your role.

Your tasks:
1. Re-read this issue and predecessor PR(s)/issues from GitHub.
2. Produce a plan that explicitly separates work that can proceed now from work blocked on predecessor merge.
3. Before implementation, report any contract or file-overlap risk that should change the graph.
4. Implement against the snapshot with minimal churn.
5. Keep PR draft/WIP or clearly marked blocked if opened before predecessors merge.
6. Report any predecessor contract mismatch immediately.
7. If the predecessor is still `local_fix_pending`, proceed only on work that does not depend on that local fix and keep your PR draft/WIP or clearly blocked. After predecessor merge, rebase/update to final base, rerun required tests/benchmarks, resolve any material performance regression or insufficient improvement by profiling/optimization, linked blocker creation, or explicit coordinator/user acceptance, update PR body, and only then request AI review/final mergeability review.

Handoff requirements:
- current blocked/unblocked state;
- pipeline window consumed and whether it should remain open to further descendants;
- predecessor snapshot SHAs consumed, including any `local_fix_pending` notes;
- local tests/benchmarks run, regression status, gate status, and whether they rely on unmerged predecessor code;
- files likely to conflict on final rebase;
- what remains blocked until predecessor merge and what can proceed without further upstream churn.
```

## Downstream Sync Prompt

```text
Dependency update for your issue #<ISSUE>.

Apply this sync only if it is a configured sync window: contract change, predecessor merge, pre-final-review, or stale-test/conflict trigger. Non-contract review-fix commits should normally be batched to avoid churn.

Predecessor #<PRED> changed:
- old snapshot/head: <OLD_SHA>
- new head or merge commit: <NEW_SHA>
- reason: <dependency-ready|contract-change|merged|pre-final-review|conflict-trigger>
- contract delta: <DELTA>
- affected files/APIs/formats/tests: <AFFECTED>

Required action:
- <rebase/merge/cherry-pick/inspect only>
- rerun: <TESTS/BENCHMARKS> and compare regression status
- update PR body/comments: <YES/NO>

Do not broaden scope. Report back with sync result, conflicts, updated head SHA, and any downstream contract changes.
```

## Coordinator Review Return Prompt

```text
Coordinator final review found blockers for issue #<ISSUE> / PR <PR>.

Blocking findings:
1. <FINDING>
2. <FINDING>

Required response:
- fix or explicitly reject each finding with rationale;
- rerun required tests/benchmarks; profile and optimize any material regression or insufficient improvement before claiming mergeability;
- update PR body/comments;
- request AI review again if meaningful code changed, but only after the PR is mature again and no known local blocker remains;
- return a fresh mergeability handoff with latest head SHA and CI/review state.

Do not merge directly unless the coordinator explicitly delegates merge authority.
```
