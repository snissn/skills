---
name: omp-issue-graph-executor
description: "Execute and merge dependency graphs of GitHub issues and PRs from the Oh My Pi (omp) coding harness on openrouter/stealth/ox-alpha. Delegate through native task/hub subagents conservatively - one implementation worker by default, hard ceiling of two without explicit opt-in - persist graph state, enforce exact-head review/CI/performance gates, and merge the selected graph in topological order."
---

# OMP Issue Graph Executor

Use this skill when the user asks this harness to execute a dependency graph of
GitHub issues, tickets, or PRs and drive it to completion. This is the OMP-native
counterpart to `codex-issue-graph-executor` and `pi-issue-graph-executor`: do
not launch child Codex or Pi processes, and do not use Orca commands. This
session is the graph coordinator and sole owner of final integration and merge
decisions. Bounded work is delegated through the native `task` tool and
coordinated over `hub`.

Invocation means **execute-and-merge** unless the user requests planning,
readiness-only, or no-merge execution. Inspect live state, delegate safe
independent nodes, open/update PRs, run review/fix loops, and merge eligible
nodes in topological order. Do not stop after planning or opening PRs.

Read [dependency execution](references/dependency-execution.md) before creating
or updating the DAG/manifest. Read [worker prompts](references/worker-prompts.md)
before dispatching any subagent.

## Harness Contract

- Delegation uses the built-in `task` tool (one `tasks[]` batch per wave);
  coordination uses `hub` (`send`, `wait`, `inbox`, `jobs`, `logs`, `cancel`).
  No helper scripts or detached child processes are needed.
- Subagents start blank with no conversation history. Every assignment must be
  self-contained: base SHA, scope, non-goals, evidence, stop conditions, time
  box, and handoff format.
- Concurrent batches have two prerequisites: every task MUST skip
  formatter/linter/test-suite validation mid-flight (validate once during
  integration), and cross-task contracts are stated in the batch `context`
  (# Goal / # Constraints / # Contract), not negotiated later.
- Task bodies use # Target / # Change / # Acceptance. Pass large payloads via
  `local://<path>` URIs, never inline blobs.
- Job results auto-deliver. A settled `hub jobs`/`hub wait` snapshot counts as
  delivery. `completed` means successful exit, not accepted work: verify
  claimed changes against real git/PR state before updating the graph.
- Read-only research runs on `scout`. Never assign exploration to an
  implementation agent.
- Subagents are not durable autonomous services. Before replying to the user,
  harvest results or `hub cancel` every live job, and update durable graph
  state. Never claim work continues after the response.

## Default Authorization

- Merge authorization is granted by default for PRs in the selected graph:
  scoped to the target repository, parent tracker, child issues, and PRs
  created or explicitly adopted during this execution.
- Workers may push and open/update PRs, but may not merge or request external
  AI reviews. The coordinator owns those actions.
- Repository policy, branch protection, and explicit user restrictions override
  this default.
- Never merge with stale/missing/red required latest-head CI, unresolved
  requested changes or review threads, missing required evidence, or an
  unaccepted material performance regression.
- Do not merge unrelated nearby PRs.
- On a hard blocker, update durable graph state with blocker, owner, and next
  action before reporting.

## Compose With

Load these skills when available:

- `github-pr-mergeable` for exact-head CI, internal review, AI-review state,
  performance evidence, merge execution, and cleanup. Run its bundled
  `scripts/codex_review_gate.py`; do not infer Codex completion from formal
  reviews alone.
- `gh-tracker-issue` when a durable parent tracker or dependency ledger needs
  creation or restructuring.
- `github:gh-fix-ci` for targeted GitHub Actions diagnosis.
- `github:gh-address-comments` for unresolved review-thread work.
- `scientific-mainline-workflow` when a node changes scientific authority,
  claims, theorem/model decisions, or provenance-bearing outputs.

Repository-local proportionality, review-stop, scientific acceptance, and
human-approval rules always take precedence. Verify helper availability at
startup and record any fallback in graph state.

## Conservative Execution Budget

Optimize completed graph nodes per usage window, not maximum fan-out. The
runtime permits many concurrent subagents; this skill does not use that headroom
by default.

- Default to **one active implementation worker**. The coordinator performs
  live inventory, DAG/state updates, straightforward diagnosis, CI polling,
  integration, final review, and merges locally.
- Raise to **two active workers** only for independent ready nodes in isolated
  worktrees with disjoint contract/conflict surfaces and a clear elapsed-time
  benefit. Two is the normal hard ceiling.
- Never run three or more workers unless the user explicitly opts into high
  concurrency for this graph.
- Keep one implementation worker per node and reuse its lane for fix loops. Do
  not launch implementer, benchmark, and reviewer agents for the same PR. An
  independent review agent runs only on a mature high-risk PR or a concrete
  disputed finding, and never concurrently with that PR's implementer.
- Do not delegate inventory, status polling, simple CI-log extraction, tracker
  edits, branch synchronization, or merge commands unless delegation saves
  meaningful elapsed time.
- Disable speculative descendants by default. Start a node only after all
  direct predecessors merge; record explicit user approval before speculative
  implementation.
- Do not duplicate broad tests or exact-head evidence; reviewers run only
  bounded checks tied to a concrete risk.
- Steer a drifting worker once with `hub send`; if it stays stalled past its
  time box, `hub cancel` its job, preserve the worktree, and continue locally
  or defer the node.
- Time-box read/review assignments to roughly 10 minutes and implementation
  milestones to roughly 25 minutes without visible progress. Harvest one
  concise handoff, then stop the worker.
- After one model capacity/quota failure, fall back once to an available route
  or execute locally; never cycle repeatedly through models. A hosted Codex
  quota failure during review is recorded as `CODEX_REVIEW_UNAVAILABLE_QUOTA`;
  it is not a clean result.

## Agent And Model Routing

All lanes run on the session model, `openrouter/stealth/ox-alpha`. The `task`
surface has no per-worker model parameter, so routing is expressed through
agent type. Record requested versus actual routing; never claim a model was
pinned when the surface cannot pin it.

| Role | Agent type | Use for |
| --- | --- | --- |
| Coordinator/final gate | this session (no subagent) | DAG ownership, contract decisions, integration, deep review, blockers, merges. Never spawn a replacement coordinator. |
| Implementation worker | `task` | One ready issue: implementation, focused tests, PR push/update, fix loop. |
| Inventory/research | `scout` | Read-only live-state passes or broad codebase mapping that genuinely saves coordinator time. |
| Independent review | `reviewer` / `security-reviewer` | Bounded quality/security pass on a mature high-risk PR or disputed finding. Read-only. |
| Mechanical support | `sonic` | Strictly mechanical bulk updates or data collection only. |

Workers stay at depth one. Every assignment states: you are a direct child, you
must not spawn subagents/descendants, must not merge, and must not request
external AI reviews.

## Hard Invariants

- The coordinator owns the DAG, contract decisions, final review, and merges.
- Workers are direct children and may not launch descendants.
- Keep one writer per branch/worktree and per contract/conflict surface. Assign
  a named `contract_owner` before parallel work touches shared APIs, formats,
  migrations, benchmark semantics, or hot-loop helpers. Sibling coordination
  goes through `hub`, not shared-file guesswork.
- A dependent PR cannot be called mergeable or merged until every predecessor
  is merged, its branch is updated to the final base, and required validation
  is rerun.
- Audit policy for every adopted node from that node's actual worktree or PR
  head. Enumerate root and nested `AGENTS.md`, including policy files added by
  the PR, and map changed paths to the applicable policy chain.
- Request AI reviews (Codex, Copilot, CodeRabbit, ...) only on mature PRs:
  coherent code pushed, tests/benchmarks run or justified, PR body current, no
  known local blocker, latest-head CI running or green. Before each review
  request, run the `github-pr-mergeable` classifier; stop on an exact-head
  clean result. Enforce PR-lifetime churn caps (default: 3 requests per exact
  head, 6 per PR, 3 finding-bearing heads; lower repo-local caps win). On
  `review_churn_blocked`, disposition current threads, move the node to
  `review-scope-reset`, update durable state, and stop new requests until the
  project owner authorizes resumption.
- Material regressions in runtime, throughput, latency, allocations, memory,
  storage/recovery cost, or relevant domain counters block mergeability until
  optimized away or explicitly accepted with evidence.
- Optimization nodes that miss their stated improvement gate remain incomplete
  even when CI is green.
- Preserve unrelated user changes; no destructive git cleanup merely to
  simplify lanes.

## Workflow

1. **Load policy and capabilities.** Read repository policy and composing
   skills. Confirm `gh`/GitHub access, available agent types, and review-gate
   scripts. Record transport/routing fallbacks.
2. **Inventory live state locally.** Gather each issue/PR title, URL, state,
   branch/base/head SHA, linked nodes, CI, reviews, threads, tests,
   benchmarks, and existing worktrees. Live GitHub state wins over old notes.
3. **Build and validate the DAG.** Explicit dependencies first, then issue
   language, PR stack/base relationships, tracker ordering, and shared
   contract risk. Detect cycles.
4. **Classify every node.** Record `contract_surface`, `conflict_surface`,
   `contract_owner`, execution mode, worktree/branch, agent role, required
   evidence, and exact next action.
5. **Persist graph state.** Prefer one parent-issue comment marked
   `<!-- omp-issue-graph-executor:state:v1 -->`. Without a parent or remote
   access, use a local manifest and report the fallback.
6. **Show a concise snapshot and continue.** Execute under default
   authorization; pause only for an ambiguous unsafe edge, plan-only mode, or a
   policy-required approval gate.
7. **Prepare isolated lanes.** One branch/worktree per node based on the
   recorded SHA. Verify clean ownership before dispatch.
8. **Dispatch bounded work.** Send ready nodes in one `tasks[]` batch using
   the worker-prompt templates: base SHA, scope, non-goals, policy chain,
   evidence, stop conditions, time box, handoff format, depth-one rule, and
   skip-validation-mid-flight rule.
9. **Run the coordinator loop.** While workers run, do local graph/CI/
   integration work. Check `hub jobs`/`hub logs` at milestones, steer via
   `hub send`, verify git/PR reality independently before accepting results,
   and `hub cancel` stalled jobs promptly.
10. **Mature each PR.** Internal deep review, fix findings, focused plus
    broader affected tests, performance evidence, exact-head-accurate PR body
    - all before external AI review.
11. **Apply merge gates.** Use `github-pr-mergeable` including the deterministic
    Codex classifier and repository review-stop rules. A worker's
    `mergeable-candidate` recommendation is never a final decision.
12. **Merge topologically.** After every predecessor merge, update affected
    descendants to the final base, rerun required checks, refresh PR facts,
    then consider them mergeable.
13. **Clean up safely.** Cancel leftover jobs; remove merged worktrees/branches
    only after no descendant, recovery, or provenance obligation needs them.
    Update durable state after every merge and before the final response.

## Dependency Ready

A node may be `dependency-ready` only when a PR exists, scope is substantially
complete, the public contract is documented and stable, required local
tests/benchmarks passed or failures are scoped, no unaccepted material
regression remains, a review/fix loop completed, and remaining work cannot
change downstream APIs/formats/semantics/evidence.

`dependency-ready` does not mean mergeable. Because speculation is off by
default, it unblocks descendants only after explicit user-approved speculative
execution; otherwise descendants wait for merge.

## Completion And Failure Handling

Continue until every selected node is `merged`, intentionally deferred to a
linked owner, `blocked` by external state with an exact next action, or paused
at `review-scope-reset` under repository policy.

Pause and report rather than guessing when the DAG has an unsafe ambiguous
edge, a policy gate requires unavailable human action, credentials or GitHub
state cannot be verified, a shared contract lacks an owner, or broad restacking
would risk unrelated work. Before reporting, harvest or cancel all child jobs
and persist the blocker, owner, and next action.

## Final Report

Report:

- graph nodes and final states;
- PRs/branches/exact heads and merge SHAs;
- tests, benchmarks, latest-head CI, and review evidence per node;
- coordinator and worker agent types with requested-versus-actual routing and
  any fallback;
- dependency/sync events and any `review-scope-reset` state;
- worktree/local branch/remote branch cleanup status;
- deferred blockers, owner, and exact next action;
- durable graph-state location and confirmation that no subagent job was left
  running.
