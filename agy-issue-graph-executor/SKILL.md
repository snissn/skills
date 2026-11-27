---
name: agy-issue-graph-executor
description: "Execute GitHub issue graphs toward agreed outcomes in Antigravity (AGY/Gemini) with accepted decisions, ticket revisions, artifacts, and merged PRs. Uses AGY native subagents, background tasks, provisional dependent work, conservative concurrency, and current-head PR gates. Use for graph execution, not requests to review or edit this skill."
---

# Antigravity (AGY) Issue Graph Executor

Use this skill when the user asks Antigravity (`agy` CLI, App, or IDE) to execute a dependency graph of GitHub issues, tickets, or PRs and drive them to completion. This is the Antigravity-native counterpart to `codex-issue-graph-executor` and shares its durable execution, cleanup, CI-watching, and CI-capacity contracts so policies do not drift across harnesses.

Do not invoke Codex, Orca, Pi, or Muse APIs here. Use Antigravity's native `define_subagent`, `invoke_subagent`, `send_message`, `manage_subagents`, background `run_command` + `manage_task`, `schedule`, and (for structured read-only fan-out) `run_workflow`. The current session remains the graph coordinator and sole owner of integration and merge-authority allocation.

For a graph execution request, invocation means `execute-and-merge`: inspect live state, delegate safe independent work, deliver and verify each node's intended output, drive PRs through readiness gates, and merge in topological order after gates pass. A plan, report, or ticket revision completes a node only when it is that node's accepted deliverable; it does not complete an unmet parent product outcome. Do not stop at an opened PR or ordinary pending CI/review; follow **Critical-Path Finalization And Monitoring** until the gate resolves. Do not ask for separate merge approval unless the user explicitly narrowed the request to planning or no-merge execution.

## Default Authorization

- Merge authorization is granted by default for PRs in the selected graph.
- Always start dependent nodes provisionally as soon as their predecessors have usable recorded contract snapshots and decision dependencies/conditional eligibility are satisfied. Do not wait for predecessor PR CI, review, or merge, and do not ask the user to opt into work-ahead. Respect the execution budget and actual repository restrictions; record concrete blockers rather than asking again.
- Authorization is scoped to the target repo, parent tracker, child issues, and PRs created or explicitly adopted during this execution.
- Within that scope, the coordinator may revise the remaining graph and create or adopt necessary nodes as evidence changes, preserving agreed acceptance criteria, guardrails, ownership, and history without repeated permission.
- **Proactive asynchronous flake repair is authorized by default within the same repository:** whenever CI exposes an unrelated flaky test or noisy CI gate with no active repair PR/owner, the coordinator is authorized to adopt or open one focused flake-repair issue, dispatch an asynchronous background `graph-worker` in a disjoint worktree off `origin/main`, open a focused maintenance PR, and drive it through normal review, CI, and authorized merge gates without asking for separate permission or blocking the primary product PR.
- Execution includes reclaiming released local worktrees, verified disposable outputs, and graph-owned Go build caches under [Disk Cleanup](../codex-issue-graph-executor/references/disk-cleanup.md). Editing this skill does not authorize disk cleanup.
- The coordinator may merge after all gates pass; workers may not merge unless explicitly delegated for a specific PR. Never merge unrelated non-flake PRs outside the selected graph, bypass required human approval/branch protection, merge with stale/missing/red/inconclusive latest-head CI (absent documented no-CI policy), or merge with unresolved requested changes, material review findings, missing required evidence, or unaccepted material performance regressions.
- If a hard blocker prevents completion, persist the blocker, owner, and next action in durable graph state before reporting.

## Antigravity Harness Contract And Model Routing

Resolve routine choices and finish authorized work; clarify only consequential unknowns while keeping independent work moving. User direction overrides skill defaults. Treat new user messages as steering and propagate corrections to affected workers via `send_message`.

### Native Tools And Lifecycle

- **Define typed, depth-1 subagents structurally** with `define_subagent` at session start (or before first delegation), setting `EnableSubagentTools=false` on every worker/reviewer role so depth-1 is harness-enforced:
  - `graph-worker`: `EnableWriteTools=true`, `EnableSubagentTools=false` (implementation, provisional descendant, PR finalization, or disk cleanup).
  - `graph-reviewer`: `EnableWriteTools=false`, `EnableSubagentTools=false` (read-only adversarial review, ticket readiness review, or high-risk adviser; note that read-only subagents may lack network/shell writes, so pass exact diffs, paths, and raw command evidence directly in the prompt).
- **Invoke and supervise:** use `invoke_subagent(TypeName=..., Role=..., Prompt=..., Model=..., Workspace=...)`. Each call starts asynchronously with clean context and returns a `conversationId`.
- **Reactive wakeup (no polling loops):** subagents and background commands notify the coordinator automatically upon completion or message arrival. Never use shell `sleep` loops to poll workers or CI.
- **Reuse idle workers:** `send_message(Recipient=<conversationId>, Message=...)` automatically re-awakens an idle AGY subagent with its full prior context preserved—use it for fix loops, sync-window handoffs, and steering. Never use `send_message` to communicate with the user.
- **Release workers:** use `manage_subagents(Action="list"|"kill", ...)` to inspect or permanently terminate workers. Always harvest or kill every live child before finishing a run.
- **Built-in `research` caveat:** AGY's built-in `research` subagent runs in a read-only sandbox with **no network access**. Use it for codebase/diff exploration, not `gh` GitHub API inventory (perform live `gh` inventory locally in the coordinator or via a shell-capable worker).
- **Dynamic workflows & orchestrators:** for bounded multi-item read-only fan-out (e.g., auditing a retirement inventory across many files), `run_workflow` with `parallel(...)` and JSON schemas is allowed within the concurrency budget (read the built-in `run-workflow` skill first). Never call `swarm` unprompted—only when the user explicitly invoked `/swarm`.
- **Nested `AGENTS.md` discovery (critical in AGY):** Antigravity walks *up* from CWD to the repo root and **never down** into subdirectories (opening repo root does not auto-load `TreeDB/AGENTS.md`). For every adopted node, always run `git ls-tree -r --name-only <head> | grep -E '(^|/)AGENTS\.md$'` in that PR's worktree/head and read every applicable policy file explicitly.

### Model Routing (`invoke_subagent` Model Tiers)

AGY's `invoke_subagent` accepts `Model` tiers (`inherit`, `pro`, `flash`, `flash_lite`), not raw model IDs or per-subagent reasoning effort flags. `Model="inherit"` inherits the coordinator's active session model (e.g., `Gemini 4 Neon (XHigh)`). Keep the coordinator on the user's selected session model; never spawn a replacement coordinator or edit global settings.

| Role | `TypeName` | Preferred `Model` tier | Use for |
| --- | --- | --- | --- |
| Coordinator & final gate | current session | session model | DAG, live GitHub inventory, integration, blockers, merge-authority decisions. |
| Complex implementation or specialist | `graph-worker` / `graph-reviewer` | `inherit` (or `pro`) | Ambiguous multi-file work, architecture, persistence/concurrency, security, or disputed evidence. |
| Routine implementation | `graph-worker` | `inherit` (or `pro`) | Bounded issue with clear contract, focused tests, and fix loop. |
| PR finalization owner | `graph-worker` | `inherit` (or `pro`) | One mature PR's mutable review/CI repair loop when useful parallel work exists. |
| Independent review or adviser | `graph-reviewer` | `inherit` (or `pro`) | Fresh-context read-only review of mature candidates, disputed findings, or bounded architecture questions. |
| Disk cleanup | `graph-worker` | `inherit` or `flash` | Bounded batch of coordinator-allowlisted released worktrees, scratch, and graph Go caches. |
| Codebase-only research | `research` | `flash` or `inherit` | Offline codebase/symbol exploration when it saves coordinator wall time (no `gh`/network). |

Record requested tier and observable session model in graph state; never invent model IDs, capacity, or flags the harness lacks. If delegation fails or hits capacity/quota errors, execute locally and record the actual route.

### Workspace & Worktree Strategy (`Workspace` Parameter)

**Important AGY behavior:** `manage_subagents(Action="kill")` automatically deletes harness-created `Workspace="share"` and `Workspace="branch"` directories.

- **Default for graph lanes:** allocate explicit registered worktrees with `git worktree add` from the repository's Git common directory, invoke workers with `Workspace="inherit"`, and pass the exact worktree path, base/head SHAs, persistent host-shared `GOCACHE`/`GOMODCACHE`, and lane-local `TMPDIR` + `GOTMPDIR` in the prompt. This preserves branch names, allows seamless ownership handoffs, and keeps cleanup under [disk-cleanup.md](../codex-issue-graph-executor/references/disk-cleanup.md).
- **When to use `Workspace="share"`:** acceptable for disposable prototypes or self-contained slices whose commits are pushed (or merged/copied back) *before* killing the subagent. Never rely on a `share`/`branch` workspace surviving worker termination.

## Conservative Execution Budget

Optimize for verified progress toward the agreed parent outcome:

- Default to **one active subagent when useful coordinator work can proceed in parallel**, otherwise zero (work locally). The coordinator handles live GitHub inventory, DAG/state updates, straightforward diagnosis, integration, and merge-authority allocation.
- Raise to **two active subagents** only when two ready assignments are genuinely independent, use isolated worktrees for writes, have disjoint contract/conflict surfaces, and each saves substantial elapsed time. Two is the normal hard ceiling.
- Never run three or more concurrent subagents unless the user explicitly opts into high-concurrency execution for the current graph.
- Choose ready assignments by dependencies and conflict surfaces, not issue count; multiple workers may own disjoint slices of one node under a single integration/acceptance owner.
- Do not delegate inventory, status polling, simple CI log extraction, tracker edits, branch syncs, or bare merge commands.
- Start the highest-priority dependent node provisionally from recorded `dependency-ready` predecessor snapshots once decision/eligibility gates pass; separate reusable work from merge-identity-bound evidence.
- Do not duplicate evidence: if exact-head CI or a worker already ran a broad suite, reviewers run only bounded targeted checks.
- Time-box delegated read/review work to ~10 minutes and implementation checkpoints to ~25 minutes without visible progress (use `schedule` with `TimerCondition=<conversationId>` if waiting). Request one concise status via `send_message`; kill only when blocked, out of scope, or no longer useful.
- Do not wait indefinitely on model capacity or quota errors; after one capacity failure or ~2 minutes without starting useful work, stop the subagent and execute locally when possible.

### Bounded Read-Only Advisers

Use a fresh-context `graph-reviewer` (`Model="inherit"` or `"pro"`, `EnableWriteTools=false`, `EnableSubagentTools=false`, ~10 min budget) as a read-only adviser—not a shadow implementer—only on these triggers:

1. **Ticket-start risk:** architecture, persistence, concurrency, security, benchmark semantics, or a consequential unknown could change the design. Ask one concrete question.
2. **Stuck repair loop:** the same material blocker category survives two coherent repair batches/heads. Stop before a third micro-fix loop and provide both failed approaches plus raw evidence.
3. **Failed hard performance gate:** the first coherent performance candidate contradicts the proposed mechanism or suggests the wrong stack boundary. Provide workload entrypoint, active counters, logical-vs-physical counts, and raw artifacts.

The coordinator owns the decision and records whether the advice was adopted.

## Execution Policies (Shared Contracts)

Apply the shared contracts below verbatim; do not weaken gates or duplicate their prose:

- **DAG, node states, sync windows, failed-candidate intervention, graph reassessment, retained evidence, merge gate, and manifest schema:** [dependency-execution.md](../codex-issue-graph-executor/references/dependency-execution.md).
- **Node deliverables:** apply [gh-issue-planner](../gh-issue-planner/SKILL.md#total-completion-packet) (`pr`, `issue-update`, `decision`, `artifact`). Do not manufacture a PR solely to represent an accepted non-code output. Negative inquiry findings complete an inquiry but never pass a product optimization gate.
- **Bug reproduction & RED/GREEN evidence:** before repairing a bug, observe and preserve baseline RED on the unfixed source with exact config/assertions/cleanup; demonstrate GREEN on the identical public path (including ACK/read-back, checkpoint, checked close, reopen/recovery, and error propagation for storage changes). Never fabricate RED or substitute legacy fixtures for COW proof. Keep reproduction, fix, and coverage in one integrated packet.
- **Simplification within the completion packet:** inspect existing code and candidate diff for reuse, duplication, redundant layers, and obsolete options; consolidate/remove verified unnecessary structure in the same PR while preserving the full outcome, behavior, and performance gates. Record consequential findings briefly in PR evidence.
- **Performance-sensitive & orthogonal workstreams:** follow [gh-issue-planner](../gh-issue-planner/SKILL.md#performance-sensitive-feature-contract), [orthogonal workstreams](../gh-issue-planner/SKILL.md#orthogonal-performance-workstreams), and [Go Performance Optimization](../go-performance-optimization/SKILL.md) + [efficient-experiments.md](../go-performance-optimization/references/efficient-experiments.md). Run focused changed-seam checks before bounded public A/B comparisons and short profiles, then exhaustive qualification on a viable candidate. Use experiment waits productively on noncompeting resources while maintaining exclusive measurement-host custody until runs, profiling, and artifact transfers finish.
- **Outcome & algorithm checkpoints:** for uncertain, architectural, or performance work, reassess after 2 coherent batches without moving the named public-path outcome, or ~45 minutes of active work without a strategic checkpoint (or immediately on user churn concern), applying [Graph Reassessment](../codex-issue-graph-executor/references/dependency-execution.md#graph-reassessment). Concrete known-solution work remains event-driven.
- **Integrated product feedback:** consolidate tightly coupled shared layers and callers onto one canonical integration candidate with one integration owner; run developmental public-capability checks early; batch common-cause failures rather than discovering migrations one CI shard at a time; carry maintained registration/naming inventories.
- **Parallel slices within a node:** split only genuinely independent work (e.g., causal review, reproduction narrowing, test design, disjoint client/harness prep) with explicit file/worktree ownership, one execution owner per expensive run, and one integration/acceptance owner for the combined packet.
- **Storage, persistent shared Go build cache, and live-safe LRU pruning:** use **one persistent host-level shared agent `GOCACHE`** per `(execution host, user)` (macOS: `$HOME/Library/Caches/agent-go-build`; Linux/remote: `/mnt/fast4tb/.cache/agent-go-build` or `${XDG_CACHE_HOME:-$HOME/.cache}/agent-go-build`; never allocate per-worker `/tmp/*-gocache` directories), reuse shared `GOMODCACHE`, pass `-trimpath` explicitly on `go build`, `go vet`, compile-only cross-OS checks, and `-trimpath`-safe `go test` commands (do not export global `GOFLAGS` if repo scripts assert `GOFLAGS=""`), keep both `TMPDIR` and `GOTMPDIR` plus datasets lane-local, cap laptop build concurrency (`-p=2` or `-p=3`) when `>= 2` local worktrees run on `<= 8`-core/`<= 16 GiB` hosts, and bound cache size live-safely via `../codex-issue-graph-executor/scripts/gocache_prune.py` (`--max-gb 10 --target-gb 6 --min-age-seconds 7200`, or `8/5` on laptops with `< 50 GiB` free) rather than wiping warm caches with `go clean -cache`. Reclaim released worktrees, lane scratch dirs, disposable DBs, and orphaned caches promptly under [disk-cleanup.md](../codex-issue-graph-executor/references/disk-cleanup.md). Delegate sizeable cleanup batches to one reusable `graph-worker` when useful graph work continues; finish small or final batches locally.
- **Checkpoint/evidence pushes & hosted CI capacity:** always pass the local pre-push gate (`gofmt -l`, `go vet`, affected package tests, and repo doc-contract checks when docs/specs change) *before* every push so hosted CI never burns runners on avoidable format/compile failures. Keep incomplete iterations in **Draft PRs**; hold non-urgent pushes and base rebases while `@codex review` is still pending so review fixes + base sync land in one push. Use surgical PR CI for ordinary changes and opt into `[ci full]` / `ci:full` (where supported by repo policy) when touching high-risk OS/mmap/durability/format internals or post-sprint qualification. Refresh live open-PR head mappings before using any repository-supported CI-skip on a non-PR checkpoint; cancel only confirmed-superseded owned runs under [ci-capacity.md](../codex-issue-graph-executor/references/ci-capacity.md).
- **Recurring CI flakes (proactive async repair):** whenever CI reports an unrelated flaky test or noisy gate, capture the failing run/job/attempt log excerpt *before* any rerun, check GitHub for an existing active owner/PR, and **immediately dispatch one asynchronous `graph-worker` on an isolated `git worktree add` lane off `origin/main`** (using the **Async CI Flake-Repair Worker** template in [references/worker-prompts.md](references/worker-prompts.md)) to complete the bounded `gh-issue-planner` → `agy-issue-graph-executor` → `github-pr-mergeable` repair loop under [recurring-ci-flakes.md](../github-pr-mergeable/references/recurring-ci-flakes.md). Do not merely queue `gh run rerun --failed` and sit idle while sibling shards finish; keep the flake PR disjoint from the primary PR so neither blocks the other.

## Critical-Path Finalization And Monitoring

- Keep finalization in the main coordinator session when it is the only critical-path work. Delegate a `graph-worker` finalizer only when concrete useful authorized work (such as a provisional successor, independent node, or proactive async flake repair) can run concurrently.
- When parallel work finishes and only delegated finalization remains, reclaim sole ownership once: request one compact checkpoint (`head`, findings, checks/retries, dirty files, in-flight commands, merge authority) via `send_message`, establish any in-flight command outcome, kill the finalizer with `manage_subagents`, and continue locally reusing all valid evidence. Never allow two concurrent readiness/writer owners.
- Ordinary pending CI or review is **not** a reason to stop or ask the user to say "resume". While waiting, advance the highest-value safe parallel work without manufacturing busywork: start an eligible provisional successor or independent node, **dispatch an async `graph-worker` off `origin/main` to causally fix any newly observed unrelated CI flake or noisy gate** (instead of idling until you can run `gh run rerun --failed`), or prepare the merge packet. If delegation is unavailable during a long CI wait, start the isolated flake diagnosis/repair locally while the background watcher monitors the primary PR.
- Start one quiet CI watcher for the sole readiness owner using `../codex-issue-graph-executor/scripts/watch_ci.py` as an **asynchronous AGY background task** (`run_command` with `WaitMsBeforeAsync=500`, `NotificationTimeoutSeconds=1800`, `--max-wait 3600`); see [ci-watcher.md](../codex-issue-graph-executor/references/ci-watcher.md#asynchronous-antigravity-agy-continuation). AGY automatically wakes the coordinator on watcher exit or notification timeout; inspect or cancel with `manage_task`. Use `schedule` (with `TimerCondition`) if a separate review-check timer is needed.
- Refresh only affected or policy-required gates after a push; a new SHA alone does not automatically invalidate unchanged evidence (never relabel old evidence as new-head CI or review). Before retrying failed CI, inspect failure logs, classify intersection with changed paths, reproduce locally when feasible, and retry failed jobs at most once before diagnosing repeats.
- Before any unavoidable session exit or turn stop on a genuine blocker/harness limit, persist a resumable checkpoint (repo, PR/issue URLs, branch/worktree, exact head/base, readiness owner, pending run/job IDs, review IDs/SHA bindings, evidence paths, retry counts, last observed state/time, next action).

## AI Review And Fallback Policy

- Audit effective repository policy at each PR's exact head first (including nested `AGENTS.md` files). Repository proportionality rules, scientific stop rules, and explicit reviewer requirements override skill defaults.
- **Maturity gate:** never request AI review until the PR is coherent, issue-complete (code, callers, tests, docs, required benchmarks/rationale), PR body is current, internal deep review found no known blockers, and latest-head CI is running or green.
- **Hard exact-head AI review convergence gate (Codex required; CodeRabbit conditional on quota):** run `../github-pr-mergeable/scripts/codex_review_gate.py --repo <OWNER>/<REPO> --pr <PR> --check` on the exact final head SHA before merging. Require:
  1. **Codex clean on exact final head** (explicit clean comment/review or `codex-review-state:v1` with `commit_sha == head`, `status == "completed"`, `has_any_findings == false`, `has_unresolved_findings == false` + `0` unresolved Codex threads; stop immediately on exact-head clean; respect the 3-request exact-head cap; record quota/capacity failures as `CODEX_REVIEW_UNAVAILABLE_QUOTA` and apply the internal fallback below unless the repo strictly requires hosted-only review).
  2. **CodeRabbit converged on exact final head (conditional on quota support):** wait if `coderabbit_state == "pending"`; allow merge if `coderabbit_state == "rate_limited"` (or `not_configured`) with `0` unresolved threads; **HARD BLOCK** if `unresolved_coderabbit_threads` (or `unresolved_other_threads`) is non-empty, even when the `CodeRabbit` GitHub check run reports `✓ success`!
  3. **Mandatory re-convergence after fixes:** after pushing fixes for ANY review findings, wait for fresh exact-head CI, fresh exact-head Codex clean (triggering `@codex review` if auto-review did not start), and fresh exact-head CodeRabbit `clean`/`rate_limited` with `0` unresolved threads across ALL reviewers before merging.
- **AGY internal review (primary when hosted Codex is not required, or fallback on `CODEX_REVIEW_UNAVAILABLE_QUOTA`):** run `INTERNAL_SUBAGENT_REVIEW` via a fresh-context `graph-reviewer` (`EnableWriteTools=false`, `EnableSubagentTools=false`, `Model="inherit"` or `"pro"`) inspecting the exact base/head diff, files, and raw validation evidence under [internal-review-fallback.md](../github-pr-mergeable/references/internal-review-fallback.md). Use `LOCAL_MOCK_SUBAGENT_REVIEW` only when delegation cannot run. Bind the review record to the exact candidate SHA/manifest with actual mode, model, reviewed paths/claims, checks, findings, `ACCEPT`/`REJECT`, and `candidate_edits_by_reviewer: false`. Later review-relevant edits invalidate prior acceptance.

## Compose With

- `gh-issue-planner`: durable trackers, ticket readiness reviews, and in-scope graph revisions (carry existing execution authorization into apply mode).
- `github-pr-mergeable`: PR readiness, exact-head review classification (`scripts/codex_review_gate.py`), thread disposition, and authorized merge execution.
- `go-performance-optimization`: Go public-path activation, allocation-domain reuse, profiling, and A/B measurement discipline.
- `scientific-mainline-workflow` & `scientific-portfolio-governance`: scientific branches, pre-freeze exact-byte review, merged-predecessor authority, and no automatic successor activation.
- `build-gomap` / `dot-laptop-to-111`: GoMap toolchain/build setup and SSH transport to host111/host185 when relevant.
- `run-workflow`: structured multi-agent Python workflows when bounded parallel read-only fan-out fits.

Verify helper skill/script availability at startup and record any fallback in graph state.

## Hard Invariants

- Coordinator owns the DAG, contract conflict resolution, and merge-authority allocation; workers never merge unless explicitly delegated per PR.
- Keep depth at 1 (`EnableSubagentTools=false`) and normal concurrency at 1 (hard ceiling 2 without explicit user opt-in).
- One writer per branch, worktree, and overlapping edit/conflict surface; resolve shared contract changes via one named `contract_owner`.
- `dependency-ready` unblocks provisional descendants by default, but no dependent PR is mergeable or merged until predecessors merge, required non-PR outputs are accepted, conditional eligibility holds, and final-base revalidation passes.
- Audit nested `AGENTS.md` from each PR's actual head/worktree, not only the coordinator checkout.
- Material performance regressions block mergeability unless explicitly accepted with evidence; failed performance candidates move to `fix-needed` for root-cause diagnosis rather than silent deferral.
- Never revert unrelated local user changes or run destructive git commands unless explicitly requested.
- Enter `review-scope-reset` only for an exhausted explicit hard review cap or coordinator-confirmed recurring material contract/architecture failure—never advisory churn counts or provider unavailability.
- Harvest or kill every live subagent and collect/verify disk cleanup before final reporting.

## Workflow

1. **Load policy & define subagent types:** read target repo root/nested `AGENTS.md`, contribution/PR docs, and applicable helper skills. Define `graph-worker` (`EnableWriteTools=true`, `EnableSubagentTools=false`) and `graph-reviewer` (`EnableWriteTools=false`, `EnableSubagentTools=false`) via `define_subagent` when delegation will be used.
2. **Inventory live GitHub state locally:** issues, PRs, branches, base/head SHAs, CI checks, reviews, unresolved threads, existing worktrees, and reusable host Go caches (`GOCACHE`, `GOMODCACHE`, Git common dir).
3. **Build & validate DAG:** infer edges per [dependency-execution.md](../codex-issue-graph-executor/references/dependency-execution.md), identify reassessment boundaries, and verify acyclicity.
4. **Record conflict/contract & routing table:** `contract_surface`, `conflict_surface`, `execution_mode`, `contract_owner`, `agent_role`, `requested_model` (`inherit`/`pro`/`flash`), `actual_model`, and slice ownership/worktree paths.
5. **Persist durable graph state:** update an existing parent-issue comment marked `<!-- issue-graph-executor:state -->` or `<!-- codex-issue-graph-executor:state -->` (preferring `<!-- issue-graph-executor:state -->` for new trackers); fall back to a local manifest if no parent/remote access exists. Track large generated paths with host, owner, and release events.
6. **Present concise graph snapshot & start immediately** (do not wait for plan approval in default `execute-and-merge` mode).
7. **Execute ready nodes & provisional descendants:** create isolated `git worktree add` lanes + private graph `GOCACHE`; delegate within the 1–2 worker budget using [references/worker-prompts.md](references/worker-prompts.md), or work locally when no useful parallel coordinator work exists.
8. **Track transitions & reassess at boundaries:** maintain `pending`, `running`, `dependency-ready`, `fix-needed`, `review-scope-reset`, `mergeable-candidate`, `merged`, `completed`, or `blocked`; apply **Failed Candidate Intervention** and **Graph Reassessment** as needed.
9. **Sync at defined sync windows** (initial snapshot, predecessor contract change, predecessor merge, pre-final-review, conflict/test trigger); advance existing PRs rather than replacing them unnecessarily.
10. **Finalize mature PRs:** run `github-pr-mergeable` locally (or via one delegated `graph-worker` finalizer only while parallel work runs); batch all findings into coherent repair heads; watch CI asynchronously via `watch_ci.py`; enforce exact-head review (`codex_review_gate.py` when required, or `graph-reviewer` `INTERNAL_SUBAGENT_REVIEW`).
11. **Merge in topological order:** recheck exact live head/base, required checks, approvals, threads, and predecessor merges; rebase/revalidate descendants after each merge.
12. **Clean up & verify:** kill/harvest all subagents, stop finished CI watchers, reclaim released worktrees/scratch/graph Go caches under [disk-cleanup.md](../codex-issue-graph-executor/references/disk-cleanup.md), and verify removal before reporting.

## Final Report

Lead with the outcome, summarize evidence, and link detailed state:

- Graph nodes, final states, and intended deliverables (separately stating whether the parent goal passed, inquiry completed, or optimization obligations remain).
- PRs merged (with merge SHAs) and issues updated/closed.
- Tests, benchmarks, CI, and review evidence per merge (confirming AI reviews ran only on mature heads, and recording hosted vs `INTERNAL_SUBAGENT_REVIEW`/`LOCAL_MOCK_SUBAGENT_REVIEW` mode and actual model).
- Agent routing used (coordinator session model, delegated roles/tiers, any fallback).
- Deferred/blocked nodes with blocker, owner, and next action.
- Per-node worktree, local branch, remote branch, disposable output, and Go build-cache cleanup status with observed free-space changes.
- Durable graph-state location and confirmation that no subagents or background watchers remain running.

Read [references/worker-prompts.md](references/worker-prompts.md) before dispatching workers. Read [../codex-issue-graph-executor/references/dependency-execution.md](../codex-issue-graph-executor/references/dependency-execution.md) when constructing or updating the DAG, manifest, sync log, or merge gate.
