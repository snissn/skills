---
name: codex-issue-graph-executor
description: "Execute dependency graphs of GitHub issues and PRs with Codex-native subagents: infer dependencies, dispatch minimum-reasoning workers under an xhigh coordinator, enforce mature-PR review gates, latest-head CI, performance evidence, topological merge order, and merge after gates when authorized."
---

# Codex Issue Graph Executor

Use this skill when the user asks Codex to execute a dependency graph of GitHub
issues, tickets, or PRs and drive them to mergeability and merge. This is the
Codex-native counterpart to Orca graph execution: do not use Orca or Pi
commands. Use Codex subagent tools when available, with this rollout acting as
the xhigh graph coordinator.

## Compose With

- `github-pr-mergeable` for PR readiness, review, latest-head CI, and merge
  execution.
- `github:gh-fix-ci` when GitHub Actions failures need targeted diagnosis.
- `github:gh-address-comments` when unresolved PR review threads must be
  inspected and fixed.
- `gh-tracker-issue` when a graph needs a durable parent tracker or issue body
  updates before implementation.

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
5. Present the graph and execution plan unless the user already authorized
   immediate execution. If authorized, proceed and state the assumption.
6. Dispatch safe independent work to Codex subagents. Keep the coordinator on
   the critical path: graph state, integration, final review, merge gates.
7. Track node state transitions in a local manifest or concise working notes:
   `pending`, `running`, `dependency-ready`, `fix-needed`,
   `mergeable-candidate`, `merged`, or `blocked`.
8. Use sync windows instead of constant rebasing: initial snapshot,
   predecessor contract change, predecessor merge, pre-final-review, and
   conflict/test trigger.
9. Use `github-pr-mergeable` for each PR before final merge. Merge only after
   latest-head CI/reviews are acceptable, required evidence is current, and all
   predecessors are merged.
10. Merge in topological order. After each merge, update descendants to the
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

See `references/worker-prompts.md` and
`references/dependency-execution.md` for dispatch templates and manifest
details.
