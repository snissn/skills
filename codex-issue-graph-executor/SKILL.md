---
name: codex-issue-graph-executor
description: "Execute and merge dependency graphs of GitHub issues and PRs with Codex-native subagents. Use GPT-5.6 Sol, Terra, and Luna by task risk when available; parallelize bounded work, enforce mature-PR reviews, latest-head CI and performance evidence, and merge the selected graph in topological order."
---

# Codex Issue Graph Executor

Use this skill when the user asks Codex to execute a dependency graph of GitHub
issues, tickets, or PRs and drive them to completion. This is the Codex-native
counterpart to Orca graph execution: do not use Orca or Pi commands. Use Codex
subagent tools for bounded work that benefits from delegation, with this rollout
remaining the graph coordinator and sole owner of final merge decisions.

Invocation of this skill means `execute-and-merge`: inspect live state,
delegate safe independent work, open/update PRs, drive each PR through readiness
gates, and merge in topological order after gates pass. Do not stop at a plan or
after opening PRs. Do not ask for separate merge approval unless the user
explicitly narrowed the request to planning or no-merge execution.

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

## Agent and Model Routing

At startup, inspect the active coordinator model/effort, the available model
catalog, configured custom agents, spawn controls, and concurrency limit. Keep
model choice and reasoning effort separate: raising effort is not a substitute
for choosing the right model.

Use this routing when the exact GPT-5.6 variants are available:

| Role | Preferred route | Use for |
| --- | --- | --- |
| Coordinator and final gate | `gpt-5.6-sol`, `xhigh` | DAG inference, contract ownership, integration, final review, blocker resolution, and merge decisions. |
| High-risk specialist | `gpt-5.6-sol`, `high` or `xhigh` | Architecture, shared hot paths, persistence/concurrency, security, public APIs or formats, and disputed benchmark meaning. |
| Default implementation worker | `gpt-5.6-terra`, `medium` | Bounded issue implementation, focused tests, PR updates, and everyday review/fix loops. Raise to `high` for bounded semantic complexity. |
| Fast support worker | `gpt-5.6-luna`, `low` or `medium` | Live-state inventory, codebase mapping, CI triage, documentation checks, mechanical edits, and concise evidence summaries. |

Use Sol `max` only for a genuinely exceptional one-off reasoning problem. Do
not use `ultra` for this workflow: the coordinator already owns delegation, and
automatic recursive fan-out weakens graph control. Keep agent depth at one;
workers must not spawn descendants unless the coordinator records a specific
exception.

Pin `model` and `model_reasoning_effort` through custom-agent configuration or
spawn parameters when the runtime supports them. If the spawn surface does not
support model selection, use the available agent, record requested versus actual
routing when observable, and do not claim a model was pinned.

Delegate only work with a clear outcome, ownership boundary, base SHA, non-goals,
required evidence, stop conditions, and handoff format. Prefer parallel
read-heavy work. Parallelize writes only across isolated worktrees or genuinely
disjoint files/modules; serialize shared contract and conflict surfaces. Leave
coordinator capacity available instead of filling every concurrency slot.

If subagent tools are unavailable or no task has a safe delegation boundary,
execute locally and record why. Do not pretend work was delegated.

## Hard Invariants

- The coordinator owns the dependency graph and final merge decisions.
- Workers may open or update PRs, but they must not merge unless explicitly
  delegated by the coordinator.
- Workers are direct children by default and may not delegate recursively.
- Keep one writer per contract/conflict surface. A named `contract_owner`
  resolves cross-node decisions before parallel workers continue.
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

1. Load repo policy and relevant skills. Inspect model, custom-agent, spawn, and
   concurrency capabilities; record routing fallbacks.
2. Inventory all issue and PR nodes from GitHub live state. Prefer Luna for this
   read-only pass. Include title, URL,
   state, branch, base, current head SHA, CI status, linked issues, and existing
   review status.
3. Build a DAG. Use explicit dependencies first, then issue wording, PR stack
   notes, tracker order, and conflict/contract risk.
4. Record a conflict/contract and routing table for every node:
   `contract_surface`, `conflict_surface`, `execution_mode`, `contract_owner`,
   `agent_role`, `requested_model`, `requested_effort`, and routing rationale.
5. Post or update durable graph state before implementation. Prefer a parent
   issue comment with marker `<!-- codex-issue-graph-executor:state -->`;
   otherwise use a local manifest and report the fallback.
6. Present a concise graph snapshot and proceed immediately. Do not wait for
   plan approval because this skill defaults to execute-and-merge.
7. Dispatch safe independent work to Codex subagents. Use Luna for fast support,
   Terra for bounded implementation, and Sol for high-risk specialists. Keep the
   coordinator—preferably Sol/xhigh when selectable—on the critical path: graph
   state, integration, final review, blocker resolution, and merge gates.
8. Track node state transitions in durable graph state and any local manifest:
   `pending`, `running`, `dependency-ready`, `fix-needed`,
   `mergeable-candidate`, `merged`, or `blocked`. Track requested and actual
   agent routing separately.
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
- Agent routing used for coordinator, implementation, inventory, and independent
  review, including any requested-versus-actual fallback.
- Any deferred nodes with blocker, owner, and next action.
- Durable graph-state location and whether any fallback execution path was used.

Read `references/worker-prompts.md` before dispatching workers. Read
`references/dependency-execution.md` when constructing or updating the DAG,
manifest, sync log, or merge gate.
