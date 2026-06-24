---
name: codex-issue-graph-executor
description: "Execute dependency graphs of GitHub issues and PRs with Codex-native subagents. Always dispatch workers when available, treat skill invocation as scoped merge authorization for the selected graph, enforce mature-PR review gates, latest-head CI, performance evidence, and merge in topological order after gates pass."
---

# Codex Issue Graph Executor

Use this skill when the user asks Codex to execute a dependency graph of GitHub
issues, tickets, or PRs and drive them to completion. This is the Codex-native
counterpart to Orca graph execution: do not use Orca or Pi commands. Use Codex
subagent tools when available, with this rollout acting as the xhigh graph
coordinator.

Invocation of this skill means `execute-and-merge`: dispatch workers when
subagent tools are available, open/update PRs, drive each PR through readiness
gates, and merge in topological order after gates pass. Do not stop at a plan,
do not stop after opening PRs, and do not ask for separate merge approval unless
the user explicitly narrowed the request to planning or no-merge execution.

## Default Authorization

- Merge authorization is granted by default for PRs in the selected graph.
- Authorization is scoped to the target repo, parent tracker, child issues, and
  PRs created or explicitly adopted during this execution.
- The coordinator may merge after all gates pass; workers may not merge unless
  the coordinator explicitly delegates that action for a specific PR.
- Do not merge PRs outside the selected graph, even if they are nearby.
- Do not merge if repo policy or branch protection requires missing human
  approval.
- Do not merge with stale, missing, red, or inconclusive latest-head CI unless
  repo policy has no CI requirement and the coordinator records the rationale.
- Do not merge with unresolved requested changes, material review findings,
  missing required tests/benchmarks, or unaccepted material performance
  regressions.
- If a hard blocker prevents completion, update durable graph state with the
  blocker, owner, and next action before reporting.

## Compose With

- `github-pr-mergeable` for PR readiness, review, latest-head CI, and merge
  execution.
- `github:gh-fix-ci` when GitHub Actions failures need targeted diagnosis.
- `github:gh-address-comments` when unresolved PR review threads must be
  inspected and fixed.
- `gh-tracker-issue` when a graph needs a durable parent tracker or issue body
  updates before implementation.

At startup, verify which helper skills/tools are available and record any
fallback in the graph state. Missing helper skills do not stop execution unless
their absence makes a required gate impossible to verify.

## Reasoning Allocation

Use the cheapest competent Codex agent for each bounded task:

- Coordinator: xhigh. Owns graph construction, dependency gates, final review,
  merge order, and user-facing status.
- Inventory/check agents: low. Use for issue/PR metadata, labels, check status,
  branch names, and concise summaries.
- Focused implementation agents: medium by default. Give each a disjoint file or
  module ownership boundary.
- Risky semantic agents: high. Use for shared hot paths, storage formats,
  correctness/idempotency, benchmark meaning, or changes likely to affect
  downstream contracts.
- xhigh workers: rare. Use only for an isolated architecture decision, a severe
  blocker, or a final independent correctness review.

If subagent tools are unavailable, execute locally and record the fallback in the
manifest. Do not pretend work was delegated.

## Hard Invariants

- The coordinator owns the dependency graph and final merge decisions.
- Workers may open or update PRs, but they must not merge unless explicitly
  delegated by the coordinator.
- Do not declare or merge a dependent PR until all predecessors are merged and
  the dependent branch has been updated/revalidated on the final base.
- Downstream speculative work is allowed only after every direct predecessor is
  `dependency-ready`.
- Avoid review-credit churn: do not request Codex, Copilot, CodeRabbit, or other
  AI reviews until the PR is mature. Mature means coherent code pushed, focused
  tests and required benchmarks run or explicitly justified, PR body/status is
  current, no known local blockers remain, and latest-head CI is running or
  green.
- Treat material performance regressions as blockers unless the user or
  coordinator explicitly accepts them with evidence.
- Keep user changes safe. Do not revert unrelated local changes. Do not use
  destructive git commands unless explicitly requested.
- Continue until every node is merged, intentionally deferred to a linked
  follow-up, or blocked by external state that is recorded in durable graph
  state.

## Workflow

1. Load repo policy and relevant skills.
2. Inventory all issue and PR nodes from GitHub live state. Include title, URL,
   state, branch, base, current head SHA, CI status, linked issues, and existing
   review status.
3. Build a DAG. Use explicit dependencies first, then issue wording, PR stack
   notes, tracker order, and conflict/contract risk.
4. Record a conflict/contract risk table for every node:
   `contract_surface`, `conflict_surface`, `execution_mode`, and
   `contract_owner`.
5. Post or update durable graph state before implementation. Prefer a parent
   issue comment with marker `<!-- codex-issue-graph-executor:state -->`;
   otherwise use a local manifest and report the fallback.
6. Present a concise graph snapshot and proceed immediately. Do not wait for
   plan approval because this skill defaults to execute-and-merge.
7. Dispatch safe independent work to Codex subagents. Keep the coordinator on
   the critical path: graph state, integration, final review, merge gates.
8. Track node state transitions in durable graph state and any local manifest:
   `pending`, `running`, `dependency-ready`, `fix-needed`,
   `mergeable-candidate`, `merged`, or `blocked`.
9. Use sync windows instead of constant rebasing: initial snapshot,
   predecessor contract change, predecessor merge, pre-final-review, and
   conflict/test trigger.
10. Use `github-pr-mergeable` for each PR before final merge. Merge only after
   latest-head CI/reviews are acceptable, required evidence is current, and all
   predecessors are merged.
11. Merge in topological order. After each merge, update descendants to the
    final base and rerun their required checks before declaring them mergeable.

## Dependency Ready

A node may be marked `dependency-ready` when:

- A PR exists with branch and latest head SHA.
- Implementation scope is substantially complete.
- Public contract surface is documented: APIs, formats, files, behavior, tests,
  benchmark expectations.
- Required local tests/benchmarks for that contract passed, or unrelated
  failures are documented.
- No unaccepted material performance regression remains.
- A review/fix loop or explicit self-review completed.
- Remaining work is expected to be CI, review polish, docs wording, or
  non-contract-changing cleanup.
- Known risks and possible contract churn are listed.

Do not mark dependency-ready if unresolved findings could change APIs, storage
formats, public semantics, test harness shape, or benchmark interpretation used
by descendants.

## Final Report

Report:

- Graph nodes and final state.
- PRs merged, merge commits if available, and any issues closed/updated.
- Tests, benchmarks, CI, and review evidence used for each merge.
- Confirmation that AI reviews were requested only after mature PR heads, or not
  requested.
- Any deferred nodes with blocker, owner, and next action.
- Durable graph-state location and whether any fallback execution path was used.

See `references/worker-prompts.md` and
`references/dependency-execution.md` for dispatch templates and manifest
details.
