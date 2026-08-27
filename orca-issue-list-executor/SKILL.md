---
name: orca-issue-list-executor
description: Execute an ordered list of GitHub issues/tickets using Orca Pi subagent managers. Use when the user wants tasks completed, reviewed, made mergeable, merged by default after gates pass, and then the next dependency issue started.
---

# Orca Issue List Executor

Use this skill when the user asks to execute a dependency-ordered list of issues using Orca subagents, especially when each issue must be driven through manager planning, implementation, review, mergeability, coordinator final review, merge, and then the next issue.

This skill composes:

- `/skill:orca-subagent-manager` for one xhigh manager per issue/task and manager-owned execution/review/fix loops.
- `/skill:github-pr-mergeable` for PR readiness, CI, AI reviews, PR body quality, and latest-head evidence.

## Operating Contract

The coordinator running this skill owns the **sequence**. Each issue manager owns the **issue implementation**.

Required sequence invariant:

```text
for each issue in dependency order:
  spawn xhigh manager
  manager plans and dispatches subagents
  manager executes implementation/review/fix loop
  manager makes PR mergeable
  coordinator performs independent final review
  if coordinator finds issues: send back to manager and repeat
  if final review passes and user has not opted out: merge PR
  update base refs / dependency state
  start next issue
```

Do not start the next dependent issue until the previous issue is merged, unless the user explicitly permits speculative/parallel work.

## Preconditions

Before executing the list:

1. Confirm the ordered issue list and dependency constraints.
2. Confirm whether the user has explicitly opted out of merging. Default assumption is merge authorization exists for PRs that pass all gates.
3. Identify repo selector, current Orca worktree, base branch, and current coordinator terminal handle.
4. Ensure `orca`, `pi`, `gh`, and git are available.
5. Read local `AGENTS.md` and any repo-specific instructions.
6. Prefer a clean coordinator worktree; never overwrite unrelated user edits.
7. For a long tracker/foundation stack, create a local execution manifest with: parent tracker, ordered issues, dependency mode, merge intent/opt-out status, current base SHA, cross-issue invariants, required evidence, and known non-goals. Update it after every merge.

## Retained Evidence Nodes

- Apply the canonical Retained Evidence Velocity policy linked from `/skill:github-pr-mergeable`.
- Where dependency policy permits, execute `product -> reviewed/landed harness or schema -> artifact-only evidence`. Focused pre-review MUST cover provenance, concurrency/isolation, fail-closed validation, and wording; freeze exact runtime and harness subtree/blob identities before expensive collection.
- Prefer a dedicated high-capacity runner with persistent build cache and durable artifact storage. Otherwise record `INFRASTRUCTURE_UNAVAILABLE: <runner|cache|storage>: <reason>` and the actual fallback; never invent infrastructure.
- Classify candidate failures separately from proven unrelated CI flakes, rerun only affected gates, and require current-head merge gates. Artifact-only descendants preserve evidence only under exact runtime/harness subtree and implementation-blob identity; product or harness drift invalidates affected evidence.

## Merge Authorization Rule

Default assumption: the user wants PRs merged after they pass all mergeable/final-review gates. Managers must not merge unless the coordinator explicitly delegates merge authority. The coordinator may merge only when:

- the user has not explicitly opted out of merging for this sequence or PR;
- the manager says the PR is mergeable under `/skill:github-pr-mergeable`;
- no unaccepted material performance regression remains for performance-sensitive or storage/read/write-path work;
- performance/scaling PRs meet their explicit improvement/saturation gates, or a linked blocker/explicit waiver is recorded; no-regression alone is not enough for optimization scope;
- the coordinator independently verifies mergeability and passes final review;
- latest-head CI/reviews/evidence are current;
- the PR branch is still the intended head.

If the user explicitly opts out, report “mergeable, not merged by request.”

## Thinking-Level Policy

- Every issue manager: `pi --thinking xhigh`.
- Managers assign minimum appropriate thinking levels to their own executors/reviewers using `/skill:orca-subagent-manager`.
- Coordinator final review should be `xhigh` quality even if performed directly, because it gates merges and dependency progression.

## Issue Manager Spawn Pattern

For each issue, create an isolated manager worktree. Use latest `origin/main` or the appropriate post-merge base unless the issue is intentionally stacked.

```sh
orca worktree create \
  --repo id:<repo-id> \
  --name <issue>-manager \
  --base-branch <base-ref> \
  --parent-worktree active \
  --json

orca terminal create \
  --worktree path:<manager-worktree-path> \
  --title "Pi manager #<issue>" \
  --command "pi --thinking xhigh" \
  --json
```

Prompt the manager with the template in [references/prompts.md](references/prompts.md). Require the manager to load:

```text
/skill:orca-subagent-manager
/skill:github-pr-mergeable
```

## Per-Issue Coordinator Workflow

### 1. Dispatch manager

Before dispatch, re-read the parent tracker and the current issue from GitHub so the manager receives the latest contract, not a stale local summary.

Give the manager:

- issue number, title, URL, and priority;
- current dependency state, latest merged predecessor facts, and base ref;
- parent tracker invariants that must not be violated;
- explicit non-goals and linked follow-ups;
- required tests/benchmarks from the issue;
- required conformance/compatibility checks for generic substrate changes;
- instruction to produce a subtask plan before broad implementation;
- instruction to report PR URL, branch, latest head SHA, checks, AI review status, tests, benchmarks, and blockers.
- instruction not to request Codex, Copilot, CodeRabbit, or other review-credit-consuming AI reviews until the PR has coherent code, focused tests, required benchmark evidence or an explicit not-applicable rationale, an accurate PR body/status comment, no known local blockers, and latest-head CI running or green.

### 2. Monitor manager progress

Useful commands:

```sh
orca terminal read --terminal <manager-term> --limit 300 --json
orca terminal wait --terminal <manager-term> --for tui-idle --timeout-ms 600000
orca orchestration inbox --terminal "$ORCA_TERMINAL_HANDLE" --full --json
orca terminal list --json
```

If the manager stalls, first read output and ask for a status update. Interrupt only if the agent is clearly stuck/running the wrong task.

### 3. Receive manager handoff

The manager handoff must include:

- PR URL/number and branch;
- latest head SHA;
- summary of implemented scope and non-goals;
- statement of which tracker contracts/layers changed;
- conformance/fallback evidence for generic substrate changes;
- subagents/reviewers used;
- exact tests and benchmarks run;
- benchmark tables with required counters when relevant;
- explicit gate status for optimization work: pass, fail/fix-needed, re-scoped instrumentation/safety-only, linked blocker, or explicit waiver;
- latest-head CI status;
- Codex/Copilot/CodeRabbit status or unavailable notes;
- unresolved review threads, if any;
- known risks/deferrals.

Do not proceed to final review until this handoff is complete.

### 4. Coordinator final review

Independently verify:

- issue acceptance gates are satisfied or explicitly deferred with linked follow-ups;
- diff scope matches the issue and does not absorb later tasks;
- tests cover changed behavior;
- benchmark/allocation evidence is current and meaningful for performance-sensitive work;
- any material regression in runtime, throughput, allocations, storage/rebuild overhead, or relevant counters has been treated as blocking, optimized, rerun, and either eliminated or explicitly accepted by the coordinator/user with rationale;
- any insufficient improvement against the issue's explicit optimization gate has been treated as blocking, iterated on, re-scoped, or converted into a linked blocker/explicit waiver before claiming readiness;
- storage/lifetime/fallback paths fail closed and have reopen/GC/concurrency tests where relevant;
- PR body accurately states scope, tests, benchmarks, performance regression status, risks, CI, and AI review status;
- GitHub latest-head checks are green or explicitly non-blocking;
- AI review findings are fixed or explicitly resolved;
- no unresolved blocking review threads remain;
- branch is mergeable against intended base.

Recommended inventory commands:

```sh
gh pr view <PR> --repo <OWNER>/<REPO> \
  --json number,title,url,state,headRefName,baseRefName,headRefOid,mergeStateStatus,isDraft,reviewDecision,statusCheckRollup,comments,reviews

gh pr checks <PR> --repo <OWNER>/<REPO>

git fetch origin
```

Use local review in the manager worktree or a clean review worktree. Do not trust stale CI or stale review comments.

### 5. Review/fix loop

If final review finds blockers, send them back to the same issue manager:

```sh
orca terminal send --terminal <manager-term> --text "<blocking findings and required fixes>" --enter
```

Require the manager to:

- fix or explicitly reject each finding with rationale;
- rerun required tests/benchmarks, including identical before/after benchmarks for any performance-sensitive fix, and verify improvement/saturation gates not only regression status;
- update PR body/comments;
- re-request AI review if meaningful code changed, but only after the PR is mature again and no known local blocker remains;
- return a fresh mergeability handoff.

Repeat coordinator final review until pass.

### 6. Merge and advance

When final review passes and the user has not explicitly opted out of merging:

```sh
gh pr merge <PR> --repo <OWNER>/<REPO> --merge --delete-branch
```

Adjust merge method to repo convention if needed. After merge:

- record merge commit and PR URL;
- fetch/update base refs;
- comment/update relevant tracker if required;
- tell any downstream managers their base changed, if they exist;
- apply `/skill:github-pr-mergeable` post-merge cleanup once no dependent work
  or recovery/provenance obligation needs the completed worktree or branch;
- start the next issue manager from the updated base.

If merge fails due to new conflicts/checks/reviews, send back to the manager and resume the review/fix loop.

## Dependency Handling

- Default: strictly serial. Next issue starts only after previous issue is merged.
- If an issue is a closeout/handoff task, ensure it consumes actual merged facts, not unmerged PR evidence.
- If a later issue is independent and user approves parallelism, mark it speculative and rebase/revalidate after dependencies merge.
- After every merge, make the next manager explicitly verify dependency state from GitHub and local `origin/main`.
- For foundation/substrate stacks, do not let a later type-specific or optimization issue bypass contracts established by earlier semantic, conformance, layout, lifetime, or fallback issues. If the current issue reveals a missing foundation, pause and update/create the foundation ticket before continuing.

## Failure / Blocker Handling

Pause and report if:

- benchmark evidence shows a material regression from the PR’s own changes and optimization/acceptance has not happened;
- benchmark evidence is neutral or insufficient against an explicit optimization gate and no fix loop, linked blocker, re-scope, or explicit waiver has been recorded;
- an issue needs a product decision not in scope;
- a generic substrate issue lacks conformance/fallback evidence for impacted non-reference paths;
- a performance PR lacks before/after evidence for the hot path it claims to improve;
- a proposed optimization bypasses previously established semantics, integrity, lifetime, or fallback contracts;
- CI is persistently failing for reasons unrelated to the PR;
- AI review bots are unavailable and repo policy requires them;
- the manager wants to expand scope into another issue;
- merge conflicts require broad restacking;
- benchmarks show a material regression with no acceptable explanation;
- an optimization sequence is drifting toward a documentation-only/insufficient closeout instead of iterating, opening blockers, or obtaining explicit user direction.

## Final Sequence Report

After the list is complete or paused, report:

- issues completed, PRs merged, merge commits;
- issues still pending and exact blockers;
- current base/head SHA and execution manifest path if one was used;
- tests/benchmarks by issue;
- conformance/fallback evidence by foundation issue where relevant;
- CI and AI review status by issue;
- follow-up issues/deferrals created or updated;
- Orca worktrees/terminals created and completed or deferred cleanup status.
