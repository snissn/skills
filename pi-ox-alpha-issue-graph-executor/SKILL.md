---
name: pi-ox-alpha-issue-graph-executor
description: "Execute and merge GitHub issue and PR dependency graphs from Pi using only the OpenRouter stealth/ox-alpha model for the coordinator and every child agent. Enforce a fail-closed model lock, conservative isolated workers, durable graph state, exact-head review/CI/performance gates, and topological merges."
---

# Pi Ox Alpha Issue Graph Executor

Use this skill when the user asks Pi to execute a dependency graph of GitHub
issues, tickets, or PRs using **only** `openrouter/stealth/ox-alpha`. This is a
strict model-pinned copy of `pi-issue-graph-executor`: do not invoke Orca,
Codex-native subagent APIs, or any Pi agent/subagent on another model. The
current Pi session is the graph coordinator and sole owner of final integration
and merge decisions.

Invocation means **execute-and-merge** unless the user requests planning,
readiness-only, or no-merge execution. Inspect live state, implement or delegate
ready nodes, open/update PRs, run review/fix loops, and merge eligible nodes in
topological order. Do not stop after planning or opening PRs.

Read [dependency execution](references/dependency-execution.md) before creating
or updating the DAG/manifest. Read [worker prompts](references/worker-prompts.md)
before dispatching a child Pi worker.

## Harness And Model-Lock Contract

- Before any graph inventory or implementation, require
  `PI_PROVIDER=openrouter` and `PI_MODEL=stealth/ox-alpha`. If the current Pi
  coordinator differs, stop and ask the user to switch to
  `openrouter/stealth/ox-alpha`; do not execute the graph under the wrong model.
- Verify the exact route exists with `pi --list-models 'stealth/ox-alpha'`.
  Authentication, quota, capacity, or provider failure blocks execution. Never
  fall back to another provider or model.
- Pi core has no built-in subagents or background-bash facility. Never assume a
  worker tool exists.
- Prefer the bundled `scripts/pi_worker.py` for an isolated child Pi process. It
  hard-pins `openrouter/stealth/ox-alpha`, rejects another requested route,
  disables extensions, adds a no-recursion worker system prompt, and preserves
  JSONL/stderr artifacts.
- If a registered `subagent` extension is available, use it only when the agent
  definition either inherits the exact coordinator route or explicitly names
  `openrouter/stealth/ox-alpha`, its actual route is observable, it uses an
  isolated `cwd`, and it obeys the same ownership/recursion limits. Never use an
  unverified, project-local, or differently pinned agent definition.
- If neither worker transport is safe, execute locally only because the current
  coordinator already passed the exact model gate. Record a transport fallback,
  never a model fallback, and do not pretend delegation occurred.
- Child Pi processes are not durable autonomous services. Before replying to
  the user, harvest or stop every child and update durable graph state. Never
  claim work will continue after the response.
- Verify each child event stream reports provider `openrouter` and model
  `stealth/ox-alpha`. Stop and reject any handoff with a missing, unverifiable,
  or mismatched route.
- The model lock covers the Pi coordinator and all Pi implementation, support,
  and review workers. Repository-required hosted GitHub review bots are external
  policy gates, not substitute agents; if the user also forbids those services,
  stop at the repository's permitted handoff boundary.

## Default Authorization

- This skill grants merge authorization by default only for the selected
  repository, parent tracker, child issues, and PRs created or explicitly
  adopted during this execution.
- Workers may push and open/update PRs, but may not merge or request external AI
  reviews. The coordinator owns those actions.
- Repository policy, branch protection, required human approval, and explicit
  user restrictions override default authorization.
- Never merge with stale/missing/red required latest-head CI, unresolved
  requested changes or review threads, missing required evidence, or an
  unaccepted material performance regression.
- Do not merge unrelated nearby PRs.

## Compose With

Load these skills when available:

- `github-pr-mergeable` for exact-head CI, internal review, AI-review state,
  performance evidence, merge execution, and cleanup. Run its bundled
  `scripts/codex_review_gate.py`; do not infer Codex completion from formal
  reviews alone.
- `gh-issue-planner` when a durable parent tracker or dependency ledger needs
  creation or restructuring.
- `github:gh-fix-ci` for targeted GitHub Actions diagnosis.
- `github:gh-address-comments` for unresolved review-thread work.
- `scientific-mainline-workflow` when a node changes scientific authority,
  claims, theorem/model decisions, or provenance-bearing outputs.

Repository-local proportionality, review-stop, scientific acceptance, and
human-approval rules always take precedence. Composing skills contribute gates,
not alternate model routing: if a required local reviewer or fallback would need
a different agent model, record the conflict and stop for an allowed human or
external-policy handoff rather than violating this skill's model lock.

## Retained Evidence Nodes

- Apply the canonical Retained Evidence Velocity policy linked from `github-pr-mergeable`.
- Where dependency policy permits, model `product -> reviewed/landed harness or schema -> artifact-only evidence`. Focused pre-review MUST cover provenance, concurrency/isolation, fail-closed validation, and wording; freeze exact runtime and harness subtree/blob identities before expensive collection.
- Prefer a dedicated high-capacity runner with persistent build cache and durable artifact storage. Otherwise record `INFRASTRUCTURE_UNAVAILABLE: <runner|cache|storage>: <reason>` and the actual fallback; never invent infrastructure.
- Classify candidate failures separately from proven unrelated CI flakes, rerun only affected gates, and require current-head merge gates. Artifact-only descendants preserve evidence only under exact runtime/harness subtree and implementation-blob identity; product or harness drift invalidates affected evidence.

## Conservative Execution Budget

Optimize completed graph nodes per usage window, not maximum fan-out.

- Default to **one active child Pi worker**. The coordinator performs live
  inventory, DAG/state updates, straightforward diagnosis, CI polling,
  integration, final review, and merge locally.
- Raise to **two active workers** only for independent ready nodes in isolated
  worktrees with disjoint contract/conflict surfaces and a clear elapsed-time
  benefit. Two is the normal hard ceiling.
- Never run three or more child workers unless the user explicitly opts into
  high concurrency for this graph.
- Keep one implementation worker per node and reuse its lane for fixes. Do not
  launch implementer, benchmark, and reviewer workers for the same PR.
- Do not delegate inventory, status polling, simple CI-log extraction, tracker
  edits, branch synchronization, or merge commands unless delegation will save
  meaningful time.
- Disable speculative descendants by default. Start a node only after all
  direct predecessors merge. Record explicit user approval before speculative
  implementation.
- Do not duplicate broad tests or exact-head evidence. Reviewers run only
  bounded checks tied to a concrete risk.
- Time-box read/review tasks to roughly 10 minutes and implementation to roughly
  25 minutes without a visible milestone. Harvest a concise handoff once, then
  stop the worker and continue locally or defer the node.
- After one `openrouter/stealth/ox-alpha` capacity, quota, authentication, or
  service failure, record `model-blocked` and stop model work. Do not retry via
  another model, provider, agent definition, or external implementation worker.

## Fixed Model Routing

Every Pi role uses the same exact provider/model. Thinking level may vary by
role, but the model may not:

| Role | Required Pi route | Default thinking | Use for |
| --- | --- | --- | --- |
| Coordinator/final gate | `openrouter/stealth/ox-alpha` | current, normally `xhigh` | DAG ownership, integration, deep review, blockers, and merge decisions. Never spawn a replacement coordinator. |
| High-risk specialist | `openrouter/stealth/ox-alpha` | `high` | One bounded persistence, concurrency, security, architecture, public-contract, or disputed benchmark question. |
| Implementation worker | `openrouter/stealth/ox-alpha` | `medium` | One ready issue, focused tests, PR updates, and its fix loop. |
| Fast support worker | `openrouter/stealth/ox-alpha` | `low` | Rare bounded mapping or CI-triage sidecar that genuinely saves time. |

Do not use `max` by default. Use `xhigh` for a child only for an exceptional,
written high-risk reason. Record requested and actual provider/model/thinking in
the manifest. A missing or mismatched actual route is a hard failure, not a
routing fallback.

## Hard Invariants

- The coordinator owns the DAG, contract decisions, final review, and merges.
- The coordinator and every child must report `openrouter/stealth/ox-alpha`;
  no model fallback or mixed-model lane is permitted.
- Workers are direct children and may not launch Pi, subagents, or descendants.
- Keep one writer per branch/worktree and per contract/conflict surface. Assign
  a `contract_owner` before parallel work touches shared APIs, formats,
  migrations, benchmark semantics, or hot-loop helpers.
- A dependent PR cannot be called mergeable or merged until every predecessor
  is merged, its branch is updated to the final base, and required validation is
  rerun.
- Audit policy for every adopted node from that node's actual worktree or PR
  head. Enumerate root and nested `AGENTS.md`, including policy files added by
  the PR, and map changed paths to the applicable policy chain.
- Do not request Codex, Copilot, CodeRabbit, or another review-credit-consuming
  reviewer until the PR is mature: coherent code pushed, tests/benchmarks run or
  justified, PR body current, no known local blocker, and exact-head CI running
  or green.
- Before every `@codex review`, run the `github-pr-mergeable` classifier. Stop
  immediately on an exact-head clean result. Keep the three-request exact-head
  anti-spam cap. PR-lifetime counts are advisory by default: six requests or
  three finding-bearing heads emit `review_churn_warning` without blocking a
  resolved, mature new head. Lower explicit repository caps still win.
- Enter `review-scope-reset` only for an exhausted explicit hard cap or a
  coordinator-confirmed recurring material contract/architecture failure.
  Provider exhaustion is reviewer unavailability. Continue independent nodes;
  only the affected node and actual descendants wait on its required review.
- Material regressions in runtime, throughput, latency, allocations, memory,
  storage/rebuild/checkpoint/recovery cost, or relevant domain counters block
  mergeability until optimized away or explicitly accepted with evidence.
- Optimization nodes that miss their stated improvement gate remain incomplete
  even when CI is green; iterate, re-scope explicitly, or add a linked blocker.
- Preserve unrelated user changes. Never use destructive git cleanup merely to
  simplify lane management.

## Workflow

1. **Enforce the model lock, then load policy.** Inspect `PI_PROVIDER` and
   `PI_MODEL` first. Continue only when they equal `openrouter` and
   `stealth/ox-alpha`; confirm the exact catalog route. Then read repository
   policy and composing skills and inspect active tools and GitHub access.
   Record transport fallbacks; model fallback is forbidden.
2. **Inventory live state locally.** Gather each issue/PR title, URL, state,
   branch/base/head SHA, linked nodes, CI, reviews, threads, tests, benchmarks,
   and existing worktrees. Live GitHub state wins over old notes.
3. **Build and validate the DAG.** Use explicit dependencies first, then issue
   language, PR stack/base relationships, tracker ordering, and real shared
   contract risk. Detect cycles.
4. **Classify every node.** Record `contract_surface`, `conflict_surface`,
   `contract_owner`, execution mode, worktree/branch, worker transport,
   requested/actual route, required evidence, and exact next action.
5. **Persist graph state.** Prefer one parent-issue comment marked
   `<!-- pi-ox-alpha-issue-graph-executor:state:v1 -->`. If no parent exists or remote
   updates are unavailable, use a local manifest and report that fallback.
6. **Show a concise snapshot and continue.** Execute immediately under the
   default authorization; pause only for an ambiguous unsafe edge, explicit
   plan-only mode, or a policy-required approval gate.
7. **Prepare isolated lanes.** Use one branch/worktree per node based on the
   recorded SHA. Verify clean ownership before dispatch.
8. **Dispatch bounded work.** Start one worker with the bundled helper. Add a
   second only under the conservative budget. Give each worker a base SHA,
   exact scope, non-goals, policy chain, evidence, stop conditions, time box,
   and handoff format.
9. **Run the coordinator loop.** While workers run, inspect their status/artifact
   files and do useful local graph/CI/integration work. At each milestone,
   harvest results, verify git/PR reality independently, and update state. Stop
   stalled, obsolete, or completed workers promptly.
10. **Mature each PR.** Perform internal deep review, fix findings, run focused
    and broader affected tests, gather required performance evidence, and make
    the PR body exact-head accurate before external AI review.
11. **Apply merge gates.** Use `github-pr-mergeable`, including deterministic
    Codex classification and repository-specific review-stop rules. A worker's
    `mergeable-candidate` recommendation is not a final decision.
12. **Merge topologically.** After every predecessor merge, update affected
    descendants to the final base, rerun required checks, refresh PR facts, and
    only then consider them mergeable.
13. **Clean up safely.** Remove merged worktrees/branches only after no
    descendant, recovery, or provenance obligation needs them. Update the
    durable state after every merge and before the final response.

## Worker Helper

Typical launch:

```sh
SKILL_DIR="${HOME}/.codex/skills/pi-ox-alpha-issue-graph-executor"
RUN_DIR="$(mktemp -d /tmp/pi-ox-alpha-issue-123-XXXXXX)"

python3 "$SKILL_DIR/scripts/pi_worker.py" start \
  --run-dir "$RUN_DIR" \
  --cwd "/absolute/path/to/issue-worktree" \
  --prompt-file "/absolute/path/to/worker-prompt.md" \
  --model openrouter/stealth/ox-alpha \
  --thinking medium

python3 "$SKILL_DIR/scripts/pi_worker.py" status --run-dir "$RUN_DIR"
python3 "$SKILL_DIR/scripts/pi_worker.py" wait --run-dir "$RUN_DIR" --timeout 1500
python3 "$SKILL_DIR/scripts/pi_worker.py" result --run-dir "$RUN_DIR"
```

Use `stop` before abandoning a lane. Preserve `meta.json`, `events.jsonl`, and
`stderr.log` until the handoff has been reconciled. See
[worker prompts](references/worker-prompts.md) for prompt templates and safety
rules.

## Dependency Ready

A node may be `dependency-ready` only when a PR exists, scope is substantially
complete, the public contract is documented and stable, required local
tests/benchmarks passed or failures are scoped, no unaccepted material
regression remains, an internal review/fix loop completed, and remaining work
cannot change downstream APIs/formats/semantics/evidence.

`dependency-ready` does not mean mergeable. Because speculation is off by
default, it unblocks descendants only after explicit user-approved speculative
execution; otherwise descendants wait for merge.

## Completion And Failure Handling

Continue until every selected node is `merged`, intentionally deferred to a
linked owner, or `blocked` by external state with an exact next action. Pause at
`review-scope-reset` only under an explicit hard review policy or a
coordinator-confirmed recurring material scope failure, never advisory counts
or provider unavailability alone.

Pause and report rather than guessing when the DAG has an unsafe ambiguous edge,
a policy/branch-protection gate requires unavailable human action, credentials
or GitHub state cannot be verified, a shared contract lacks an owner, broad
restacking would risk unrelated work, or `openrouter/stealth/ox-alpha` is
unavailable/mismatched. Before reporting, terminate or harvest all child workers
and persist the blocker, owner, and next action.

## Final Report

Report:

- graph nodes and final states;
- PRs/branches/exact heads and merge SHAs;
- tests, benchmarks, latest-head CI, and review evidence per node;
- proof that coordinator and every child used
  `openrouter/stealth/ox-alpha`, plus transport/thinking details;
- dependency/sync events and any `review-scope-reset` state;
- worktree/local branch/remote branch cleanup status;
- deferred blockers, owner, and exact next action;
- durable graph-state location and confirmation that no child Pi process was
  left running.
