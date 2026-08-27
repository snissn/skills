---
name: codex-issue-graph-executor
description: "Execute and merge dependency graphs of GitHub issues and PRs with conservative Codex-native delegation. Default to one subagent, cap normal concurrency at two, avoid speculative fan-out, enforce mature-PR reviews, latest-head CI and performance evidence, and merge the selected graph in topological order."
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

- `github-pr-mergeable` for PR readiness, review, latest-head CI, and merge execution. Use its bundled `scripts/codex_review_gate.py` for Codex state; never infer Codex completion from formal reviews alone. Repository-local proportionality and review-stop rules override that skill's default Codex cadence.
- `github:gh-fix-ci` when GitHub Actions failures need targeted diagnosis.
- `github:gh-address-comments` when unresolved PR review threads must be
  inspected and fixed.
- `gh-issue-planner` when a graph needs a durable parent tracker or issue body
  updates before implementation.

At startup, verify which helper skills/tools are available and record any
fallback in the graph state. Missing helper skills do not stop execution unless
their absence makes a required gate impossible to verify.

## Retained Evidence Nodes

- Apply the canonical Retained Evidence Velocity policy linked from `github-pr-mergeable`.
- Where dependency policy permits, model `product -> reviewed/landed harness or schema -> artifact-only evidence`. Focused pre-review MUST cover provenance, concurrency/isolation, fail-closed validation, and wording; freeze exact runtime and harness subtree/blob identities before expensive collection.
- Prefer a dedicated high-capacity runner with persistent build cache and durable artifact storage. Otherwise record `INFRASTRUCTURE_UNAVAILABLE: <runner|cache|storage>: <reason>` and the actual fallback; never invent infrastructure.
- Classify candidate failures separately from proven unrelated CI flakes, rerun only affected gates, and require current-head merge gates. Artifact-only descendants preserve evidence only under exact runtime/harness subtree and implementation-blob identity; product or harness drift invalidates affected evidence.

## Conservative Execution Budget

Optimize for completed graph nodes per usage window, not maximum parallelism.

- Default to **one active subagent**. The coordinator handles live inventory,
  DAG/state updates, CI polling, straightforward diagnosis, integration, and
  merge execution locally.
- Raise to **two active subagents** only when two ready nodes are independent,
  use isolated worktrees, have disjoint contract/conflict surfaces, and each is
  expected to save substantial elapsed time. Two is the normal hard ceiling.
- Never use three or more concurrent subagents unless the user explicitly opts
  into high-concurrency execution for the current graph.
- Keep at most one implementation worker per node. Reuse that worker for its
  fix loop; do not launch parallel implementer, benchmark, and review agents for
  the same PR.
- Do not delegate inventory, status polling, simple CI log extraction, tracker
  edits, branch synchronization, or merge commands unless the coordinator is
  genuinely blocked and delegation will save meaningful time.
- Disable speculative descendant implementation by default. Start a node only
  after its direct predecessors merge. Record an explicit user-approved
  exception before speculative work.
- Do not duplicate evidence. If exact-head CI or a worker already ran a broad
  suite, reviewers run only bounded tests that target a concrete risk.
- Close completed, blocked, capacity-starved, or no-longer-needed agents
  immediately. An open idle agent still consumes the concurrency budget.
- Do not keep an agent pending for model capacity. After one capacity error or
  two minutes without starting useful work, close it and either fall back once
  to an available lower-cost route or perform the task locally. Never cycle
  through several frontier models for the same assignment.
- Time-box delegated read/review work to about 10 minutes and implementation
  milestones to about 25 minutes without visible progress. Request a concise
  handoff once; if no useful handoff arrives promptly, preserve the worktree,
  close the agent, and continue locally or defer the node.
- Prefer sequential depth on the critical path over keeping every slot busy.

## Agent and Model Routing

At startup, inspect the active coordinator model/effort, the available model
catalog, configured custom agents, spawn controls, and concurrency limit. Keep
model choice and reasoning effort separate: raising effort is not a substitute
for choosing the right model.

Use this routing only when delegation passes the budget above and the exact
GPT-5.6 variant is immediately available:

| Role | Preferred route | Use for |
| --- | --- | --- |
| Coordinator and final gate | current coordinator model | DAG inference, contract ownership, live state, integration, review, blocker resolution, and merge decisions. Do not spawn a coordinator substitute. |
| High-risk specialist | `gpt-5.6-sol`, `high` | One bounded architecture, persistence/concurrency, security, public-contract, or disputed benchmark question. Never keep Sol waiting on capacity. |
| Default implementation worker | `gpt-5.6-terra`, `medium` | One ready issue implementation, focused tests, PR updates, and its fix loop. Raise effort only for demonstrated semantic complexity. |
| Fast support worker | `gpt-5.6-luna`, `low` | Rare bounded mapping or CI-triage sidecar that can run concurrently with implementation and save meaningful time. |

Do not use `max` or `ultra` by default. Use Sol `xhigh` only for a genuinely
exceptional one-off decision with a written reason. Keep agent depth at one;
workers must not spawn descendants.

Pin `model` and `model_reasoning_effort` through custom-agent configuration or
spawn parameters when the runtime supports them. If the spawn surface does not
support model selection, use the available agent, record requested versus actual
routing when observable, and do not claim a model was pinned.

Delegate only work with a clear outcome, ownership boundary, base SHA, non-goals,
required evidence, stop conditions, time box, and handoff format. Prefer a
single implementation worker in an isolated worktree. Serialize shared
contract and conflict surfaces, and leave the second slot unused unless a
specific independent node justifies it.

If subagent tools are unavailable or no task has a safe delegation boundary,
execute locally and record why. Do not pretend work was delegated.

## Hard Invariants

- The coordinator owns the dependency graph and final merge decisions.
- Workers may open or update PRs, but they must not merge unless explicitly
  delegated by the coordinator.
- Workers are direct children by default and may not delegate recursively.
- Normal subagent concurrency is one, may rise to two under the conservative
  budget, and may not exceed two without explicit user opt-in.
- Keep one writer per contract/conflict surface. A named `contract_owner`
  resolves cross-node decisions before parallel workers continue.
- Do not declare or merge a dependent PR until all predecessors are merged and
  the dependent branch has been updated/revalidated on the final base.
- Downstream speculative work is disabled unless the user explicitly opts in;
  `dependency-ready` alone does not authorize a speculative worker.
- Audit policy for every node from that PR's actual worktree or head commit, not only from the coordinator checkout. Enumerate all root/nested `AGENTS.md` files at that head and map every changed path to its applicable policy chain, including policy files added by the PR. Record local review-round caps and scientific acceptance/stop rules in graph state before review.
- Avoid review-credit churn: do not request Codex, Copilot, CodeRabbit, or other AI reviews until the PR is mature. Mature means coherent code pushed, focused tests and required benchmarks run or explicitly justified, PR body/status is current, no known local blockers remain, and latest-head CI is running or green.
- Before every `@codex review`, run the `github-pr-mergeable` Codex gate classifier. An exact-head no-findings issue comment is a completed clean result even without a formal review object. Stop requesting immediately when clean; any later unresolved Codex finding supersedes it. Default to no more than three total requests per exact head, six across the PR, or three finding-bearing heads, with any lower repo-local cap taking precedence.
- A new repair SHA does not reset the PR-lifetime review budget. On `review_churn_blocked`, disposition current threads, transition the node to `review-scope-reset`, update durable state, and stop review triggers until the project owner authorizes a narrowed/split/resumed path.
- Treat material performance regressions as blockers unless the user or
  coordinator explicitly accepts them with evidence.
- Keep user changes safe. Do not revert unrelated local changes. Do not use
  destructive git commands unless explicitly requested.
- Continue until every node is merged, intentionally deferred to a linked follow-up, blocked by external state, or deliberately paused at `review-scope-reset` under a repository review-stop rule. Record the owner and next decision in durable graph state; execute-and-merge does not authorize bypassing a churn stop.

## Workflow

1. Load repo policy and relevant skills. For every adopted node, enumerate applicable root/nested policy files from its actual worktree or PR-head tree, inspect their exact bytes, and record review caps/stop rules separately. Inspect model, custom-agent, spawn, and concurrency capabilities; record routing fallbacks.
2. Inventory all issue and PR nodes from GitHub live state locally. Include title, URL,
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
7. Dispatch at most one ready issue to a bounded implementation worker. Add a
   second worker only when the conservative budget permits it. Keep inventory,
   graph state, integration, routine review, CI triage, blocker resolution, and
   merge gates with the coordinator. Use an independent review agent only for a
   high-risk mature PR or a concrete disputed finding, and never concurrently
   with that PR's implementation worker.
8. Track node state transitions in durable graph state and any local manifest: `pending`, `running`, `dependency-ready`, `fix-needed`, `review-scope-reset`, `mergeable-candidate`, `merged`, or `blocked`. Track requested and actual agent routing separately.
9. Use sync windows instead of constant rebasing or polling: initial snapshot,
   predecessor contract change, predecessor merge, pre-final-review, and
   conflict/test trigger. Poll remote CI locally at coarse intervals while
   doing other work; do not dedicate an agent to waiting.
10. Use `github-pr-mergeable` for each PR before final merge, including its deterministic Codex classifier across issue comments, formal reviews, and threads. Apply the node's effective repository policy when deciding whether Codex is required. If the classifier reports lifetime churn exhaustion, stop at `review-scope-reset` rather than creating another head/request loop. Merge only after latest-head CI/reviews are acceptable under that policy, required evidence is current, and all predecessors are merged.
11. Merge in topological order. After each merge, update descendants to the
    final base and rerun their required checks before declaring them mergeable.
12. When a merged node is resolved and no descendant or provenance obligation
    still needs its branch/worktree, apply `github-pr-mergeable` post-merge
    cleanup immediately rather than accumulating completed local streams.

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
- Per-node local worktree, local branch, and GitHub remote-branch cleanup status.
- Durable graph-state location and whether any fallback execution path was used.

Read `references/worker-prompts.md` before dispatching workers. Read
`references/dependency-execution.md` when constructing or updating the DAG,
manifest, sync log, or merge gate.
