---
name: gh-tracker-issue
description: Create or update GitHub tracker issues in the snissn/gomap #1646-style format. Use when Codex is asked to open, draft, model, revise, or review a GitHub issue that should act as an implementation tracker with goals, scope boundaries, milestones, checklists, tests, performance evidence, PR process, AI review requirements, CI/backlog handling, and completion criteria.
---

# GitHub Tracker Issue

Use this skill for durable GitHub issues that are meant to coordinate multi-PR engineering work, not for small bug reports or one-off tasks.

## Workflow

1. Inspect the reference issue or tracker named by the user, usually with `gh issue view <number> --repo <owner>/<repo> --json number,title,body,url,state,labels`.
2. Identify the exact workstream, current evidence, non-goals, milestone order, and expected proof.
3. Read [references/tracker-issue-template.md](references/tracker-issue-template.md) for the reusable structure.
4. Draft the issue body with concrete, current facts. Do not overstate what the code proves.
5. Include checkbox milestones that can serve as a work log.
6. Include start-phase and close-phase requirements for every PR.
7. Include required tests and relevant benchmarks for each milestone; performance milestones must require a before/after comparison against the pre-change baseline, not only a current benchmark snapshot, and must treat material regressions as blocking until optimized or explicitly accepted.
8. Include AI review and CI process requirements when the workstream requires mergeable PRs.
9. Create or update the GitHub issue with `gh issue create` or `gh issue edit`.
10. Return the issue URL and the main scope boundaries.

## Rules

- Keep the issue body authoritative and buildoutable.
- Separate product goals from substrate work and experiments.
- Separate generic column-store work from vector-search-specific work when relevant.
- State non-goals explicitly to avoid drift.
- Require benchmark tables to report `ops/sec` in addition to `ns/op` when throughput matters.
- Require performance evidence to compare **before vs after** for each claimed optimization or hot-path/storage change, including baseline commit/branch, candidate commit/branch, delta/ratio, and whether the comparison used identical commands, fixture size, hardware, and environment. Do not accept a current-only benchmark as proof of improvement.
- Require exact commands, hardware/context, `B/op`, `allocs/op`, and setup/search/decode/doc-fetch timing boundaries for performance work.
- State a performance regression gate: material regressions in `ns/op`, `ops/sec`, `B/op`, `allocs/op`, storage/rebuild overhead, or relevant counters are not acceptable by default; the PR must profile and optimize before merge, or document that the remaining minimized regression is correctness-required and explicitly accepted by the coordinator/user.
- Require PR start and close phases: augment tests/benchmarks first, implement, then re-review and update evidence.
- Require iterative Codex, Copilot, and CodeRabbit review requests until reviews pass or are explicitly resolved when the user wants mergeable PRs.
- If GitHub CI is backed up, include a directive to cancel stale non-head runs and keep only latest-head CI for active PRs.
- Never mark aspirational work as already proven. Use “current evidence,” “target,” and “completion criteria” distinctly.

## When Creating The Issue

Prefer a temp body file and `--body-file` for long issues:

```sh
gh issue create \
  --repo snissn/gomap \
  --title "<tracker title>" \
  --label enhancement \
  --label performance \
  --label treedb \
  --label tracking \
  --body-file /tmp/<issue-body>.md
```

Adjust labels to match the repo and workstream. Do not add labels that do not exist unless the user asked for label management.
