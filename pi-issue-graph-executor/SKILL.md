---
name: pi-issue-graph-executor
description: "Execute and merge dependency graphs of GitHub issues and PRs from the Pi coding-agent harness. Use conservative isolated Pi workers, one by default and two only for safe independent nodes; persist graph state, enforce exact-head review/CI/performance gates, and merge the selected graph in topological order."
---

# Pi Issue Graph Executor

Use this skill when the user asks Pi to execute a dependency graph of GitHub
issues, tickets, or PRs and drive it to completion. This is the Pi-native
counterpart to `codex-issue-graph-executor`: do not invoke Orca or Codex-native
subagent APIs. The current Pi session is the graph coordinator and sole owner of
final integration and merge decisions.

Invocation means **execute-and-merge** unless the user requests planning,
readiness-only, or no-merge execution. Inspect live state, implement or delegate
ready nodes, open/update PRs, run review/fix loops, and merge eligible nodes in
topological order. Do not stop after planning or opening PRs.

Read [dependency execution](references/dependency-execution.md) before creating
or updating the DAG/manifest. Read [worker prompts](references/worker-prompts.md)
before dispatching a child Pi worker.

## Harness Contract

- Pi core has no built-in subagents or background-bash facility. Never assume a
  worker tool exists.
- Prefer the bundled `scripts/pi_worker.py` for an isolated child Pi process. It
  disables extensions, adds a no-recursion worker system prompt, preserves
  JSONL/stderr artifacts, and accepts an explicit worktree, model, and thinking
  level.
- If a registered `subagent` extension is available, it may be used instead,
  but only with trusted user-level agent definitions, an explicit isolated
  `cwd`, and the same ownership/recursion limits. Project-local agents require
  explicit trust because they are repository-controlled prompts.
- If neither transport is safe or available, execute locally and record the
  fallback. Do not pretend delegation occurred.
- Child Pi processes are not durable autonomous services. Before replying to
  the user, harvest or stop every child and update durable graph state. Never
  claim work will continue after the response.
- Use `PI_PROVIDER`, `PI_MODEL`, `PI_REASONING_LEVEL`, and `PI_SESSION_ID` to
  identify the current coordinator. Use `pi --list-models` to verify child model
  availability rather than guessing.

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
human-approval rules always take precedence.

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
- After one model capacity/quota failure, fall back once to an available route
  or execute locally. Never cycle repeatedly through frontier models.

## Model Routing

Choose model and thinking separately. First inspect the live Pi model catalog.
Use these routes only when present and immediately available:

| Role | Preferred Pi route | Use for |
| --- | --- | --- |
| Coordinator/final gate | current Pi model and thinking | DAG ownership, integration, deep review, blockers, and merge decisions. Never spawn a replacement coordinator. |
| High-risk specialist | `openai-codex/gpt-5.6-sol`, `high` | One bounded persistence, concurrency, security, architecture, public-contract, or disputed benchmark question. |
| Implementation worker | `openai-codex/gpt-5.6-terra`, `medium` | One ready issue, focused tests, PR updates, and its fix loop. |
| Fast support worker | `openai-codex/gpt-5.6-luna`, `low` | Rare bounded mapping or CI-triage sidecar that genuinely saves time. |

Do not use `max` by default. Use `xhigh` for a child only for an exceptional,
written high-risk reason. Record requested and actual provider/model/thinking in
the manifest; if pinning cannot be verified, record the fallback and do not
claim it was pinned.

## Hard Invariants

- The coordinator owns the DAG, contract decisions, final review, and merges.
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
  immediately on an exact-head clean result. Apply lower repository review caps
  first and enforce PR-lifetime churn limits across repair SHAs.
- On `review_churn_blocked`, disposition current findings, transition to
  `review-scope-reset`, update durable state, and stop new review requests until
  the project owner authorizes a narrowed, split, deferred, or resumed path.
- Material regressions in runtime, throughput, latency, allocations, memory,
  storage/rebuild/checkpoint/recovery cost, or relevant domain counters block
  mergeability until optimized away or explicitly accepted with evidence.
- Optimization nodes that miss their stated improvement gate remain incomplete
  even when CI is green; iterate, re-scope explicitly, or add a linked blocker.
- Preserve unrelated user changes. Never use destructive git cleanup merely to
  simplify lane management.

## Workflow

1. **Load policy and capabilities.** Read repository policy and composing
   skills. Inspect `PI_*`, `pi --version`, `pi --list-models`, active tools, and
   whether `gh`/GitHub access is available. Record transport/model fallbacks.
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
   `<!-- pi-issue-graph-executor:state:v1 -->`. If no parent exists or remote
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
SKILL_DIR="${HOME}/.codex/skills/pi-issue-graph-executor"
RUN_DIR="$(mktemp -d /tmp/pi-issue-123-XXXXXX)"

python3 "$SKILL_DIR/scripts/pi_worker.py" start \
  --run-dir "$RUN_DIR" \
  --cwd "/absolute/path/to/issue-worktree" \
  --prompt-file "/absolute/path/to/worker-prompt.md" \
  --model openai-codex/gpt-5.6-terra \
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
linked owner, `blocked` by external state with an exact next action, or paused at
`review-scope-reset` under repository policy.

Pause and report rather than guessing when the DAG has an unsafe ambiguous edge,
a policy/branch-protection gate requires unavailable human action, credentials
or GitHub state cannot be verified, a shared contract lacks an owner, or broad
restacking would risk unrelated work. Before reporting, terminate or harvest all
child workers and persist the blocker, owner, and next action.

## Final Report

Report:

- graph nodes and final states;
- PRs/branches/exact heads and merge SHAs;
- tests, benchmarks, latest-head CI, and review evidence per node;
- coordinator and worker transport/model/thinking, including fallbacks;
- dependency/sync events and any `review-scope-reset` state;
- worktree/local branch/remote branch cleanup status;
- deferred blockers, owner, and exact next action;
- durable graph-state location and confirmation that no child Pi process was
  left running.
