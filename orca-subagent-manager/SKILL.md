---
name: orca-subagent-manager
description: "Coordinate Pi subagents inside Orca for multi-issue implementation work: spawn xhigh manager agents, split issues into subtasks, assign minimum appropriate thinking levels, run execution/review/fix loops, integrate final patches, and drive PRs to mergeable state using github-pr-mergeable."
---

# Orca Subagent Manager

Use this skill when a task should be delegated to multiple Pi agents in Orca-managed worktrees, especially for issue stacks that need planning, implementation, review, evidence, CI, and PR mergeability. The default topology is **one xhigh manager per issue/task**, with manager-owned execution/review loops for subtask chunks.

## Core Principles

- Create a **manager agent for each issue/task**. The manager runs with `pi --thinking xhigh` and owns planning, decomposition, subagent selection, review loop control, final integration, evidence, and mergeability.
- Split work into the **smallest mergeable subtask chunks** that have independent tests/evidence. A task may have one chunk if it is naturally small.
- Each subtask runs through: **plan -> execute -> review -> fix -> repeat until review passes -> manager integration**.
- The manager chooses the **minimum appropriate thinking level** for each subagent, not xhigh by default.
- Managers must keep work auditable: isolated worktrees, explicit branch/issue names, exact test and benchmark commands, PR body updates, and latest-head CI evidence.
- Managers must treat material performance regressions as blocking mergeability failures until the changed path is profiled and optimized, or the remaining minimized regression is explicitly accepted by the coordinator/user.
- Default user intent is to merge PRs after mergeable gates pass, but managers/subagents normally do not merge directly. The coordinator owns merge execution unless it explicitly delegates merge authority.

## Thinking-Level Policy

Managers must justify subagent thinking levels in the plan.

| Work type | Default thinking | Use when |
| --- | --- | --- |
| Mechanical grep/docs/rename/audit | `low` | Low ambiguity, easy verification, no architecture decisions. |
| Focused tests, small bug fixes, issue comments | `medium` | Local reasoning and ordinary code review needed. |
| Feature implementation in known package, benchmarks, persistence tests | `high` | Correctness/perf interactions are real but bounded. |
| Architecture, storage/lifetime/COW, concurrency, cross-issue design, final mergeability | `xhigh` | Broad design risk, irreversible API/format decisions, or final signoff. |

Use `xhigh` for managers, final integrators when scope is cross-cutting, and reviewers for storage/lifetime/persistence/perf-critical changes. Use lower levels for mechanical implementation to save budget.

## Orca Dispatch Patterns

### 1. Create a manager worktree and Pi session

```sh
orca worktree create \
  --repo id:<repo-id> \
  --name <issue>-manager \
  --parent-worktree active \
  --json

orca terminal create \
  --worktree path:<manager-worktree-path> \
  --title "Pi manager #<issue>" \
  --command "pi --thinking xhigh" \
  --json
```

If the manager must start from a specific branch or stack base, pass `--base-branch <ref>` to `orca worktree create`.

### 2. Prompt the manager

Use the manager prompt template in [references/prompts.md](references/prompts.md). Include:

- issue number/title and URL;
- dependency order and non-goals;
- expected deliverables and required evidence;
- instruction to create subtask chunks and assign thinking levels;
- instruction to use this skill and `/skill:github-pr-mergeable` before final signoff.

Send directly or through orchestration:

```sh
orca terminal send --terminal <manager-term> --text "<manager prompt>" --enter
```

or:

```sh
TASK=$(orca orchestration task-create --spec "<manager task>" --json | jq -r '.result.task.id')
orca orchestration dispatch --task "$TASK" --to <manager-term> --from "$ORCA_TERMINAL_HANDLE" --inject
```

### 3. Manager creates subtask worktrees

For each subtask, prefer a child branch/worktree off the manager branch when the subtask will produce code:

```sh
orca worktree create \
  --repo id:<repo-id> \
  --name <issue>-<chunk-slug> \
  --base-branch <manager-branch-or-current-head> \
  --parent-worktree path:<manager-worktree-path> \
  --json

orca terminal create \
  --worktree path:<subtask-worktree-path> \
  --title "Pi exec #<issue> <chunk>" \
  --command "pi --thinking <low|medium|high|xhigh>" \
  --json
```

Use a single subtask worktree when the issue only needs one implementation chunk. Use separate execution and review worktrees when parallel review is helpful.

## Required Manager Workflow

1. **Inventory**
   - Read the issue body/comments and linked PRs/issues.
   - Read local `AGENTS.md` and relevant project docs/tests.
   - Check current branch, base, worktree cleanliness, and dependency state.

2. **Plan**
   - Produce a chunk table: subtask ID, scope, files/packages, dependencies, tests/benchmarks, evidence, reviewer, and thinking level.
   - Identify blockers and decision gates. Ask the coordinator/user before expanding scope or changing architecture.
   - For performance-sensitive work, define the benchmark matrix and the regression threshold/gate up front; default is zero unaccepted material regression.
   - Keep parent tracker boundaries explicit; do not absorb unrelated follow-ups.

3. **Dispatch execution**
   - Give each executor a bounded prompt with exact scope, non-goals, expected tests, branch/worktree rules, and reporting format.
   - Require executor commits or a patch summary plus exact commands run.
   - Executors should not request external review or claim mergeability.

4. **Review**
   - Assign a reviewer subagent with at least the implementation agent’s thinking level; use `high` or `xhigh` for persistence, GC, concurrency, benchmarks, and public API changes.
   - Reviewers must inspect the diff, tests, benchmarks, issue acceptance gates, and scope drift.
   - Reviewer output must be actionable: pass, blocking findings, non-blocking nits, missing evidence.

5. **Resolution loop**
   - Manager dispatches fixes for blocking review findings.
   - Repeat review until blockers are fixed or explicitly rejected with rationale.
   - Keep each iteration scoped; avoid using review fixes to sneak in new features.

6. **Manager integration**
   - Manager or a finalizer agent integrates accepted subtask changes into the manager branch.
   - Resolve conflicts, run focused and broad validation, update docs/issue comments/PR body, and ensure evidence is current.
   - If relevant benchmarks regress in runtime, throughput, allocations, storage/rebuild overhead, or counters, mark the PR performance-blocked, profile and optimize before mergeability, and rerun identical before/after evidence.
   - If subtask branches were used, merge/cherry-pick only reviewed commits. Preserve authorship when appropriate.

7. **Mergeable closeout**
   - Load and follow `/skill:github-pr-mergeable` or read the skill directly.
   - Ensure latest-head CI is green or explicitly non-blocking with evidence.
   - Request Codex, Copilot, and CodeRabbit reviews where available, resolve findings, and rerun after meaningful pushes.
   - Update PR body/comment with exact tests, benchmarks, counters, risks, and unresolved deferrals.
   - Do not merge directly unless the coordinator explicitly delegates merge authority.

## Review Standards

A subtask review passes only when:

- the diff is within the subtask scope;
- issue acceptance gates are mapped to code/tests/evidence;
- tests cover the behavior changed;
- performance-sensitive changes have benchmark or allocation evidence and no unaccepted material regression;
- storage/lifetime changes fail closed and include reopen/GC/concurrency tests where relevant;
- docs and issue/PR wording do not overclaim;
- any remaining performance regression is proven unavoidable/correctness-required, minimized, explicitly accepted, and documented with profiles/evidence;
- no private cache/lifecycle is introduced when a shared manager is required;
- fallback and unsupported paths remain safe.

## Coordinator Monitoring Commands

```sh
orca terminal list --json
orca terminal read --terminal <term> --limit 300 --json
orca terminal wait --terminal <term> --for tui-idle --timeout-ms 600000
orca orchestration inbox --terminal "$ORCA_TERMINAL_HANDLE" --full --json
orca orchestration task-list --json
```

Use `orca terminal send --interrupt` only when a subagent is clearly stuck or running the wrong task.

## Naming And Branch Conventions

- Manager worktree: `<issue>-manager`, branch like `snissn/<issue>-manager` or repo convention.
- Executor worktree: `<issue>-<chunk-slug>`.
- Reviewer terminal title: `Pi review #<issue> <chunk>`.
- Commit subjects should mention the issue or subtask gate when useful.
- PRs should remain reviewable: one issue PR unless the manager explicitly decides a stack is safer.

## When To Create Real GitHub Child Issues

Create or update GitHub tracker issues only when the subtask is durable beyond the current PR, has independent acceptance criteria, or needs product/backlog tracking. Use `/skill:gh-tracker-issue` for that. Otherwise, Orca orchestration tasks and manager checklists are enough.

## Final Report Format

Managers report back with:

- issue/PR handled and branch/worktrees created;
- subtask chunks completed and reviewers used;
- tests and benchmarks with exact commands;
- latest-head CI and AI review status;
- mergeability status;
- blockers, deferrals, and risks;
- cleanup instructions for temporary worktrees if any.
