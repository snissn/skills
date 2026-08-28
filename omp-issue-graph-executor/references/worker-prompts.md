# OMP Worker Dispatch Templates

Use these formats when dispatching workers from `omp-issue-graph-executor`.
Delegation is always the native `task` tool; coordination is `hub`. All lanes
run on the session model (`openrouter/stealth/ox-alpha`); route by agent type,
never by claiming model pinning.

## Batch Shape

One batch per wave; never serialize genuinely independent ready nodes.

- `context` (applies to every task in the batch): `# Goal`, `# Constraints`,
  `# Contract`. State cross-task interfaces here so siblings never negotiate
  them later. Always include: repo/base SHA, depth-one rule, no-merge rule,
  no-AI-review-request rule, skip-validation-mid-flight rule (formatter/linter/
  test suites run once at integration), and the shared contract surfaces with
  their named owners.
- Each `task`: `# Target` (exact files/symbols and non-goals), `# Change`
  (step-by-step, APIs and patterns to reuse), `# Acceptance` (observable
  result; no project-wide commands).
- Pass large payloads via `local://<path>` URIs written before dispatch.
- Attach a `name` per worker (stable CamelCase id) so `hub send` steering and
  `hub cancel` address the right lane.

## Handoff Contract

Require every worker to end with a milestone handoff covering:

```text
state: implementation-complete|pr-opened|dependency-ready|fix-needed|review-scope-reset|mergeable-candidate|blocked
branch / base sha / head sha:
pr url:
changed files + contract changes:
tests/benchmarks run + results:
performance gate status:
effective policy + review counts:
unresolved risks/blockers:
exact next action for coordinator:
```

For machine-readable results, attach an `outputSchema` to the task instead of
prose parsing. Workers return distilled evidence, not raw command output.

## Ready-Issue Implementation Worker (`agent: task`)

```text
You are the direct implementation worker for issue #<ISSUE> in <OWNER>/<REPO>.
The parent session is the graph coordinator; you are a depth-one child.

Time box: <TIME_BOX, normally 25 minutes to a visible milestone>.

Before editing:
- Verify branch <BRANCH>, base <BASE_REF>/<BASE_SHA>, clean worktree <WORKTREE>.
- Read every root/nested AGENTS.md applicable to your owned paths at this head;
  report its review cap/stop rules.

Graph assignment:
- Direct predecessors: <NONE_OR_MERGED_PREDECESSORS>
- Parent tracker invariants: <SUMMARY>
- Ownership boundary: <FILES_OR_MODULES>
- Contract surface: <CONTRACT>
- Parallel siblings and disjoint boundaries: <SIBLINGS>
- Required tests/benchmarks/evidence: <REQUIREMENTS>
- Non-goals: <NON_GOALS>
- Stop immediately when: <STOP_CONDITIONS>

Rules:
- You are not alone in the repository. Never revert unrelated work.
- Implement only this issue's scope, preferably test-first.
- Treat material performance regressions and missed optimization gates as
  blockers; report evidence rather than normalizing them.
- You may commit, push, and open/update this issue's PR when instructed.
- Do not merge, request Codex/Copilot/CodeRabbit review, edit graph state
  outside your assignment, or spawn subagents/descendants.
- If policy, base, contract, ownership, or scope is ambiguous, stop and hand
  back instead of inventing a decision.
```

## Inventory / Research Scout (`agent: scout`, optional)

Do not use by default; the coordinator inventories locally. Use only when a
read-only live-state pass runs beside an active implementation worker without
raising concurrency above two. Time box ~10 minutes.

```text
Read-only inventory for an issue graph. Do not edit files or GitHub artifacts,
request reviews, or spawn subagents.
Nodes: <ISSUES_OR_PRS>.
Return concise facts only: title, state, labels, linked PRs/issues, branch,
base, head SHA, CI status, review/thread status, dependency hints. Distilled
evidence, not raw command output.
```

## High-Risk Specialist (`agent: scout` for analysis, `reviewer` for code risk)

One bounded question only - architecture, persistence/concurrency, security,
public contract, or disputed benchmark semantics. Time box ~10 minutes.

```text
Resolve exactly this question: <QUESTION>.
Base <BASE_REF>/<BASE_SHA>; affected nodes <NODES>; contract owner <OWNER>;
surfaces <SURFACES>; evidence required <REQUIREMENTS>; non-goals <NON_GOALS>.
Do not broaden scope, edit, spawn subagents, request reviews, or merge.
Return: concrete decision, evidence inspected, alternatives rejected, affected
descendants, invalidated snapshots, required follow-up checks, remaining
uncertainty needing owner action.
```

## Independent PR Readiness Review (`agent: reviewer`, optional)

Only for a mature high-risk PR or a concrete disputed finding, and never
concurrently with that PR's implementation worker. The coordinator still runs
the final merge gate. Time box ~10 minutes.

```text
Read-only readiness check of PR <PR_URL> at head <HEAD_SHA>.
Inspect only: exact-head CI; unresolved threads/requested changes; required
tests/benchmarks evidence; PR body accuracy; whether AI reviews were requested
only after a mature head. Use github-pr-mergeable/scripts/codex_review_gate.py
for Codex state; do not request another review when an exact-head clean comment
exists. Report advisory lifetime churn without changing node state. Recommend
review-scope-reset only when the classifier names an exhausted explicit hard
cap or the coordinator supplied a recurring material contract/architecture
failure. Run only bounded checks tied to concrete risk. Return blockers first,
then evidence and a mergeability recommendation.
```

## Speculative Descendant (explicit user opt-in only)

```text
Speculative downstream work on issue #<ISSUE>. Predecessors not merged:
<PREDECESSORS>. Authorized contract snapshot: <SHA_AND_CONTRACT>.
Keep the PR draft/WIP and explicitly blocked; do not claim mergeability,
request AI reviews, or merge. Stop on any predecessor contract mismatch. After
predecessors merge, the coordinator updates this branch to the final base and
reruns required checks before final review.
<INCLUDE THE READY-ISSUE ASSIGNMENT FIELDS AND HANDOFF FORMAT>
```

## Coordinator Loop Commands

While workers run, keep working locally; poll at milestones, not continuously.

```text
hub jobs                      # snapshot all lanes; settled rows = delivered results
hub logs name=<NAME>          # inspect a lane's recent output
hub wait timeoutMs=60000      # block for next delivery/message when truly idle
hub send to=<NAME> message=…  # steer once; delivery wakes idle workers
hub cancel ids=[<JOB_ID>]     # kill stalled/obsolete lanes; preserve worktree
```

Verify claimed changes against real git/PR state before accepting any handoff.
Before replying to the user: harvest or cancel every job, confirm via
`hub jobs` that nothing is still running, and update durable graph state.
