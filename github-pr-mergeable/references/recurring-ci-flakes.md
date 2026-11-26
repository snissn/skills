# Recurring CI failures without blocking unrelated delivery

Use this when a CI failure may be an existing intermittent fixture or infrastructure
problem. A flaky test is repair work, not a reason to park the whole execution graph.

## Establish history before classification

Capture and preserve the failing run ID, attempt, job ID/URL, exact test or gate
name, and decisive failure/race/timing log lines **before** running
`gh run rerun --failed` (rerunning can hide the failed attempt behind a new
attempt). Search the exact test identity and failure signature in current and
closed issues, PRs, and retained logs. Inspect earlier merged fixes and current
owners before creating another ticket. Record the failing head/job and
distinguish a documented recurring test from proof that this occurrence has the
same cause. A passing retry does not establish either the cause or a repair.
Preserve the original failure.

## Dispatch asynchronously on sight (do not idle for reruns)

Do **not** classify a CI failure as an "unrelated flake" or "runner noise", plan
`gh run rerun --failed` after sibling shards finish, and then sit idle waiting
for the run to complete. Observing an unrelated CI flake or noisy gate with no
active repair PR/owner is an immediate trigger to launch an asynchronous repair
lane in parallel with the waiting CI run:

- **Spawn an isolated async worker immediately** (for example, an Antigravity
  `graph-worker` via `invoke_subagent` or a Codex subagent) on a clean,
  disjoint `git worktree add` lane branched off `origin/main` within the active
  concurrency budget (normally 1–2 workers). Share the graph `GOCACHE` with a
  lane-local `TMPDIR`/`GOTMPDIR`.
- **Fallback when delegation is unavailable:** if no subagent slot can be used,
  use the CI wait locally in a separate worktree off `origin/main` to search
  history, reproduce, and open the focused repair while the background CI
  watcher monitors the primary PR.
- **Deduplicate before launching:** check live open issues, open PRs, and active
  workers for the same test/gate signature first so two lanes never fix the same
  flake concurrently. When multiple distinct flakes appear at once, prioritize
  the most recurring or highest-impact flake within the concurrency budget.
- **Stay disjoint and non-blocking:** branch the flake repair off `origin/main`
  (never stack it on the product PR unless shared code requires it), respect
  measurement-host isolation if any benchmark host is busy, and never delay the
  primary PR's bounded rerun or eligible merge waiting for the flake PR to land.

## Start a bounded repair completion packet

Compose `gh-issue-planner`, the active issue-graph executor
(`agy-issue-graph-executor` in Antigravity or `codex-issue-graph-executor` in
Codex), and `github-pr-mergeable` into one issue-to-repair-to-merge loop. Reuse an existing
active owner/ticket when its scope fits; otherwise create one focused recurrence
issue linking the historical fix and new failure. Keep source ownership disjoint
from product work where possible. Use an available execution slot and the existing
heavy-test owner rather than creating a competing test campaign.

Use the planner's documentation/code preflight to reconcile canonical contracts,
fixture assumptions, and durable issue/PR claims. The executor owns the bounded
repair lane, coordination with the product candidate, and completion rather than
stopping after ticket creation. Test-only changes need no unrelated product
documentation; record that rationale. Production changes own their actual
contract/docs/cost impact.

Prefer the smallest causal repair: an existing committed/current-term readiness
fence, deterministic coordination, retained listener ownership, isolated global
measurement, or a context beginning at the phase it actually bounds. Refresh an
incidental fixture deadline or loaded-CI allowance when source and observed timing
justify it; record which invariant it bounds and validate at the relevant CI
scope. Do not preserve a demonstrably unsuitable incidental budget merely because
it is old. Do preserve intentional short-deadline assertions, workload geometry,
durability, membership and result checks. Never retry an ambiguously committed
mutation, suppress a real failure, or add an unconditional sleep to obtain green.

Use a deterministic old-versus-repaired control when feasible, focused repetitions
or race checks that answer the changed risk, then the affected current-base CI.
Collect failures into one coherent repair batch. Finish source review, necessary
documentation, latest-head review/CI and merge under normal policy; an issue alone
is not completion. Reassess a recurring cause instead of rerolling indefinitely.

## Keep product execution moving

Continue independent implementation, local qualification, and eligible merges
while the flake repair proceeds. Do not make all graph nodes depend on a test-only
repair; add an edge only where code, safety, or an actual required gate needs it.
If a fixture repair is needed in the product candidate, integrate it once in the
next coherent batch. Otherwise prefer an independently useful maintenance PR;
avoid repeated rebases or whole-suite reruns merely to chase its branch.

A bounded rerun of an affected failed gate can refresh CI when policy permits and
documented recurrence or infrastructure evidence supports it. Record the original
failure, classification, rerun count/result and linked repair owner. Do not rerun
already-green gates or use retry-until-pass as the repair/qualification method.
Required latest-head checks still must pass unless an actual repository policy
authorizes a recorded exception. A known flaky red check is not automatically
waived. When fresh required CI is green, do not hold an otherwise eligible product
merge solely for the adjacent fixture-repair issue to close.
