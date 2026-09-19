---
name: muse-issue-graph-executor
description: Execute a GitHub issue dependency graph to completion in Muse — dispatch bounded workers in topological order, enforce evidence and merge gates, report node states.
---

# Muse Issue Graph Executor

Use when the user asks to execute a dependency graph of GitHub issues or PRs
and drive it to completion. Pair with `gh-issue-planner`, which owns ticket
structure (standalone vs tracker, milestones, gates); this skill owns
execution only. This session is the coordinator and sole owner of integration
decisions. Workers are single-depth children and never decide merges.

Invocation means **implement to green plus PRs** unless the user requests
readiness-only or explicitly authorizes merge-and-close execution. Inspect live
state, delegate safe independent nodes, open/update PRs, run review/fix loops,
and — only with explicit user authorization — merge eligible nodes in
topological order. A request to plan or sketch is never authorization to push,
merge, or close.

## Modes And Write Boundary

- **Readiness-only:** inventory live state, validate the DAG, classify nodes,
  report exact next actions. No branches, PRs, or code changes.
- **Execute (default):** implement nodes, open/update PRs, run tests and
  required evidence. Push only branches the graph created or explicitly
  adopted; never push or merge on a bare completion — that still needs the
  user's explicit merge authorization for this graph.
- **Execute-and-merge:** as above, plus merge topologically mergeable nodes
  and close their issues, only after the user explicitly authorized merging
  for this graph. Repository branch protection and user restrictions always win.

## Harness Contract

- Delegate with `muse.subagent_spawn` (one bounded batch per wave); use
  `muse.subagent_status` / `muse.subagent_wait` to supervise and
  `muse.subagent_cancel` to stop stalled workers. For wide same-kind fan-out,
  prefer one `muse.workflow` run with a bounded parallel request array instead
  of many ad-hoc spawns.
- Workers start with limited context. Every assignment is self-contained: base
  SHA, scope, non-goals, policy chain, required evidence, stop conditions,
  time box, handoff format, and the depth-one rule (no descendant spawns).
- Keep one writer per branch, worktree, and contract/conflict surface. Name a
  `contract_owner` before parallel work touches shared APIs, formats,
  migrations, or benchmark semantics.
- Read-only inventory and broad codebase mapping stay inline or go to one
  bounded research child; never assign exploration to an implementation worker.
- A finished child result is a claim, not accepted work: verify against real
  git/PR/CI state before updating the graph. Before the final response,
  harvest or cancel every live child and persist graph state.

## Conservative Execution Budget

Default to **one active implementation worker**; the coordinator does
inventory, DAG updates, diagnosis, integration, review, and merges locally.
Raise to **two workers** only for independent ready nodes with disjoint
contract/conflict surfaces and a clear elapsed-time benefit. Never run three
or more unless the user explicitly opts into high concurrency for this graph.
Time-box implementation milestones to roughly 25 minutes without visible
progress; steer once, then cancel, preserve the worktree, and continue locally
or defer the node. Disable speculative descendants by default: start a node
only after all direct predecessors merged, unless the user approved
speculative execution for it.

## Node Classification

For every node record: `contract_surface`, `conflict_surface`,
`contract_owner`, execution mode, branch/worktree, required evidence, and exact
next action. A node is `dependency-ready` only when its PR exists, scope is
substantially complete, the public contract is stable, required local
tests/benchmarks pass, no unaccepted material regression remains, and
remaining work cannot change downstream APIs, formats, or evidence semantics.
`dependency-ready` is not mergeable; descendants still wait for the merge
unless speculative execution was approved.

## Merge Gates (Execute-And-Merge Only)

Never merge with stale/missing/red required latest-head CI, unresolved review
threads or requested changes, missing required evidence, or an unaccepted
material performance regression (runtime, throughput, latency, allocations,
memory, storage/recovery cost, or relevant domain counters). Each
performance-sensitive node needs identical before/after evidence (baseline and
candidate commit, delta, same fixture/hardware/environment); a current-only
benchmark never proves an improvement. Optimization nodes that miss their
stated improvement gate stay incomplete even when CI is green. Do not merge
unrelated nearby PRs.

## Workflow

1. Load policy: repo `AGENTS.md`, `CONTRIBUTING.md`, PR templates, and any
   parent-tracker gates. Repo-local rules override this skill.
2. Inventory live state locally: issue/PR title, state, branch, base/head SHA,
   links, CI, reviews, threads, existing worktrees. Live GitHub state wins over
   notes.
3. Build and validate the DAG from explicit dependencies, issue language, and
   PR stack relationships. Detect cycles; pause on ambiguous unsafe edges.
4. Persist graph state: prefer one parent-issue comment marked
   `<!-- issue-graph-executor:state:v1 -->`; without a parent or remote
   access, use a local manifest file and report the fallback.
5. Prepare isolated lanes: one branch/worktree per node from the recorded SHA;
   verify clean ownership before dispatch.
6. Dispatch ready nodes in one bounded batch with self-contained assignments.
7. Run the coordinator loop: local integration work while workers run,
   milestone supervision, prompt cancellation of stalled jobs, independent
   verification of every claimed change.
8. Mature each PR: review findings fixed, focused plus affected-broader tests,
   required performance evidence, PR body current, no known local blocker.
9. Merge topologically on authorization: after each merge, update descendants
   to the final base, rerun required checks, then reconsider mergeability.
10. Clean up safely: cancel leftover children; remove merged worktrees or
    branches only when no descendant, recovery, or provenance need remains.
11. Report: node states, PRs/branches/exact heads and merge SHAs, tests and
    evidence per node, deferred blockers with owner and next action, graph
    state location, and confirmation no child job was left running.
