---
name: codex-issue-graph-executor
description: "Execute and merge dependency graphs of GitHub issues and PRs with Astra-aware Codex delegation, conservative concurrency, mature-PR review, and current-head CI and performance gates. Use for graph execution, not requests to review or edit this skill."
---

# Codex Issue Graph Executor

Use this skill when the user asks Codex to execute a dependency graph of GitHub
issues, tickets, or PRs and drive them to completion. This is the Codex-native
counterpart to Orca graph execution: do not use Orca or Pi commands. Use Codex
subagent tools for bounded work that benefits from delegation, with this rollout
remaining the graph coordinator and sole owner of final merge decisions.

For a graph execution request, invocation means `execute-and-merge`: inspect live state,
delegate safe independent work, open/update PRs, drive each PR through readiness
gates, and merge in topological order after gates pass. Do not stop at a plan or
after opening PRs. Do not ask for separate merge approval unless the user
explicitly narrowed the request to planning or no-merge execution.

## Astra Execution Guidance

Apply the [official Astra prompting guidance](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices)
(checked 2026-09-04) to this workflow:

- Resolve routine choices and finish authorized work. Clarify only consequential
  unknowns; keep independent work moving. Preserve prior authorization.
- User direction overrides skill defaults. If a rule blocks progress, cite its
  exact file and wording; distinguish a requirement from your interpretation.
- Treat new messages as steering; propagate corrections to affected workers.
  Answer status questions briefly and resume unless the user cancels the task.
- Delegate a bounded task when useful coordinator work can proceed alongside it.
  Otherwise work locally. The budget below governs every reference/template.
- Run required and risk-relevant checks. After they pass, repeat or broaden them
  only for changed code, failures, or unresolved risks. Avoid redundant tests.
- Keep updates and handoffs concise, readable, and evidence-linked. On resume,
  recover scope, authorization, heads, completed checks, and next actions from
  durable state, then refresh live facts that may have changed.

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
- `scientific-portfolio-governance` for scientific lanes: owner direction or a
  clear issue assignment, one writer per issue branch, and overlap checks. No
  scheduler, slot pool, activation PR, or workflow-authored scientific/governance
  authority. One scientific decision per PR; unrelated main changes do not
  invalidate a lane. Scientific successors need merged predecessor authority
  and their own owner direction or assignment; merging does not activate them.
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

- Default to **one active subagent when useful work can run in parallel**,
  otherwise zero. The coordinator handles live inventory,
  DAG/state updates, CI polling, straightforward diagnosis, integration, and
  merge execution locally.
- Raise to **two active subagents** only when two ready assignments are independent,
  use isolated worktrees for writes, have disjoint contract/conflict surfaces, and each is
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
- Reuse completed workers for their fix loops. Stop blocked, capacity-starved,
  or unnecessary work through the available lifecycle tools. Close/release agents
  when supported; interruption alone does not prove a runtime slot was freed.
- Do not keep an agent pending for model capacity. After one capacity error or
  two minutes without starting useful work, stop its work and either fall back once
  to an available lower-cost route or perform the task locally. Never cycle
  through several frontier models for the same assignment.
- Time-box delegated read/review work to about 10 minutes and implementation
  milestones to about 25 minutes without visible progress. Request a concise
  handoff once; if no useful handoff arrives promptly, preserve the worktree,
  stop the agent, and continue locally or defer the node.
- Prefer sequential depth on the critical path over keeping every slot busy.

## Agent and Model Routing

Inspect the runtime's exposed model catalog, spawn schema, and concurrency
limit once. Record unavailable facts as unknown; do not change global config.
Keep the current coordinator and its effective effort. For an Astra session,
inherit `gpt-6-astra` unless a bounded role below warrants an explicit override.
These routes are workflow choices, not guaranteed cost or quality rankings.

| Role | Preferred route when available | Use for |
| --- | --- | --- |
| Coordinator and final gate | current model/effort | Graph, integration, blockers, and merge decisions. Never spawn a replacement coordinator. |
| Complex implementation or specialist | `gpt-6-astra`, inherited effort | Ambiguous multi-file work, architecture, persistence/concurrency, security, or disputed evidence. Use `medium` for a fresh unconfigured worker; `high` for demonstrated complexity. |
| Routine implementation | `gpt-5.6-terra`, `medium` | A bounded issue with a clear contract, focused tests, and its fix loop. |
| Fast support | `gpt-5.6-luna`, `low` | A substantial independent inventory or triage task that saves elapsed time. |
| Independent review | `gpt-6-astra`, `high` | A mature high-risk candidate or disputed finding, read-only in fresh context. Required reviewer identity is governed by repo policy. |

Preserve explicitly selected models/efforts. Do not escalate to `max` or `ultra`
as a default; use higher effort only for a named unresolved difficulty. Keep
agent depth at one. If Astra is unavailable, use an immediately available
`gpt-5.6-sol` for complex work or execute locally; never relabel the fallback.

Use actual tool fields: this collaboration runtime exposes `model` and
`reasoning_effort`; custom-agent config may use `model_reasoning_effort`.
Full-history forks inherit model/effort and cannot take overrides here. For an
explicit override use `fork_turns="none"` or a supported bounded history and
supply the task context. An independent reviewer gets fresh context, the exact
candidate, requirements, and raw evidence, without the implementer's conclusions.
Record requested versus actual routing only when observable. Never invent model
selection, async flags, lifecycle tools, or capacity that the harness lacks.

Delegate only work with a clear outcome, ownership boundary, base SHA, non-goals,
required evidence, stop conditions, time box, and handoff format. Prefer a
single implementation worker in an isolated worktree. Serialize shared
contract and conflict surfaces, and leave the second slot unused unless a
specific independent assignment justifies it.

If subagent tools are unavailable or no task has a safe delegation boundary,
execute locally and record why. Do not pretend work was delegated.

## Hard Invariants

- The coordinator owns the dependency graph and final merge decisions.
- Workers may open or update PRs, but they must not merge unless explicitly
  delegated by the coordinator.
- Workers are direct children by default and may not delegate recursively.
- Normal subagent concurrency is at most one, may rise to two under the conservative
  budget, and may not exceed two without explicit user opt-in.
- Keep one writer per contract/conflict surface. A named `contract_owner`
  resolves cross-node decisions before parallel workers continue.
- Do not declare a dependent PR mergeable or merge it until all predecessors are merged and
  the dependent branch has been updated/revalidated on the final base.
- Downstream speculative work is disabled unless the user explicitly opts in;
  `dependency-ready` alone does not authorize a speculative worker.
- Audit policy for every node from that PR's actual worktree or head commit, not only from the coordinator checkout. Enumerate all root/nested `AGENTS.md` files at that head and map every changed path to its applicable policy chain, including policy files added by the PR. Record local review-round caps and scientific acceptance/stop rules in graph state before review.
- Avoid review-credit churn: do not request Codex, Copilot, CodeRabbit, or other AI reviews until the PR is mature. Mature means coherent code pushed, focused tests and required benchmarks run or explicitly justified, PR body/status is current, no known local blockers remain, and latest-head CI is running or green.
- Before every `@codex review`, run the `github-pr-mergeable` Codex gate classifier. An exact-head no-findings issue comment is a completed clean result even without a formal review object. Stop requesting immediately when clean; any later unresolved Codex finding supersedes it. Keep the three-request exact-head anti-spam cap. PR-lifetime counts are advisory by default: six requests or three finding-bearing heads emit `review_churn_warning`, but a resolved, mature new head may continue.
- A new repair SHA does not erase review history, but advisory history does not change node state. Enter `review-scope-reset` only for an exhausted explicit repository/user hard cap or a coordinator-confirmed recurring material contract/architecture failure. Provider exhaustion is reviewer unavailability. Continue independent nodes; only the affected node and actual descendants wait when its required review is unavailable.
- Record hosted Codex quota, usage-limit, rate-limit, capacity, or service
  unavailability as `CODEX_REVIEW_UNAVAILABLE_QUOTA`: the review did not run.
  When repo policy permits, use an independent read-only GPT-5.6 Pro reviewer or
  documented clean-room `LOCAL_GPT56_REVIEW` bound to the exact candidate. Record
  paths/claims, checks, findings, `ACCEPT` or `REJECT`, and no candidate edits.
  Later scientific edits invalidate it. An Astra review is not that named
  fallback unless policy explicitly permits it; self-review is not independent.
- Treat material performance regressions as blockers unless the user or
  coordinator explicitly accepts them with evidence.
- Keep user changes safe. Do not revert unrelated local changes. Do not use
  destructive git commands unless explicitly requested.
- Continue until every node is merged, intentionally deferred to a linked follow-up, or blocked by external state with an exact next action. Pause at `review-scope-reset` only under an explicit hard review policy or coordinator-confirmed recurring material scope failure, never from advisory counts alone.

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
7. Delegate one ready issue when useful local work can proceed alongside it;
   otherwise implement locally. Add a second worker only when the conservative budget permits it. Keep inventory,
   graph state, integration, routine review, CI triage, blocker resolution, and
   merge gates with the coordinator. Use an independent review agent only for a
   high-risk mature PR or a concrete disputed finding, and never concurrently
   with that PR's implementation worker.
8. Track node state transitions in durable graph state and any local manifest: `pending`, `running`, `dependency-ready`, `fix-needed`, `review-scope-reset`, `mergeable-candidate`, `merged`, or `blocked`. Track requested and actual agent routing separately.
9. Use sync windows instead of constant rebasing or polling: initial snapshot,
   predecessor contract change, predecessor merge, pre-final-review, and
   conflict/test trigger. Poll remote CI locally at coarse intervals while
   doing other work; do not dedicate an agent to waiting.
10. Use `github-pr-mergeable` for each PR before final merge, including its deterministic Codex classifier across issue comments, formal reviews, and threads. Apply the node's effective repository policy when deciding whether Codex is required. Record `review_churn_warning` as telemetry and continue a mature head. Stop at `review-scope-reset` only when the classifier reports an exhausted explicit hard cap or the coordinator confirms recurring material contract/architecture failure. Merge only after latest-head CI/reviews are acceptable under that policy, required evidence is current, and all predecessors are merged.
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

Lead with the outcome; summarize evidence and link detailed state. Report:

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
