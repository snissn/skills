# Orca Issue List Executor Prompt Templates

## Issue Manager Dispatch Prompt

```text
You are the xhigh Pi manager for issue #<issue>: <title>.

Load and follow:
- /skill:orca-subagent-manager
- /skill:github-pr-mergeable

You are one issue manager in a dependency-ordered sequence. The coordinator will not start the next issue until your PR is mergeable, passes coordinator final review, and is merged.

Repo: snissn/gomap
Issue: <url>
Base ref: <base-ref>
Dependency state: <previous issues/PRs merged or blockers>
Priority/order: <position in sequence>
Non-goals / later issues: <non-goals>

Your requirements:
1. Read issue body/comments, linked PRs/issues, AGENTS.md, and relevant code/tests.
2. Produce a subtask plan before broad implementation. Include chunk scope, acceptance gates, tests/benchmarks, reviewer, and minimum thinking level for each executor/reviewer.
3. Dispatch/manage executors and reviewers through Orca according to /skill:orca-subagent-manager.
4. Run implementation -> review -> fix loops until subtask and issue review pass.
5. Open or update a PR for this issue only.
6. Drive the PR to mergeable state under /skill:github-pr-mergeable. Do not merge directly unless the coordinator explicitly delegates merge authority.
7. Treat material performance regressions as blocking: profile, optimize, rerun identical before/after evidence, and do not claim mergeability unless the regression is eliminated or explicitly accepted by the coordinator/user.
8. Do not request Codex, Copilot, CodeRabbit, or other review-credit-consuming AI reviews until the PR is mature: coherent code pushed, focused tests and required benchmarks run or explained, PR body/status evidence current, no known local blockers, and latest-head CI running or green.
9. Return a final handoff with PR URL/number, branch, latest head SHA, exact tests/benchmarks, performance regression status, CI status, AI review status, unresolved threads, risks, and deferrals.

Do not absorb work from later dependency issues unless the coordinator explicitly approves.
```

## Coordinator Final Review Findings Prompt

```text
Coordinator final review for issue #<issue> found blocking items. Please resolve these and return a fresh mergeability handoff.

Blocking findings:
<findings>

Required response:
- map each finding to a fix or explicit rejection rationale;
- update code/tests/docs/PR body as needed;
- rerun focused validation and any required benchmarks; if performance regressed, profile/optimize and rerun identical before/after benchmarks;
- re-request AI review if code changed meaningfully, but only after the PR is mature again and no known local blocker remains;
- provide latest PR head SHA, CI status, review status, and evidence.

Do not merge directly unless the coordinator explicitly delegates merge authority. Do not expand scope beyond these fixes without asking.
```

## Post-Merge Next Manager Prompt Addendum

```text
The previous dependency issue has merged.

Merged PR: <PR URL>
Merge commit: <sha>
Current base for your work: <base-ref or origin/main after fetch>

Before planning, verify the merged dependency state locally and from GitHub. Do not rely on stale branch assumptions.
```

## Pause / Blocker Report Template

```text
Sequence paused at issue #<issue>.

Blocker:
<exact blocker, including any material performance regression>

Evidence:
<commands, CI links, review findings, benchmark data, or decision needed>

Recommended next action:
<decision, retry, split issue, update tracker, or allow scope change>
```
