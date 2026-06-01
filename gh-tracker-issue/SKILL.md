---
name: gh-tracker-issue
description: Create or update durable GitHub tracker issues for multi-PR engineering work. Use when Codex is asked to open, draft, model, revise, or review a GitHub issue that should act as an implementation tracker with goals, scope boundaries, milestones, checklists, tests, performance evidence, branch/PR process, AI review requirements, CI/backlog handling, and completion criteria.
---

# GitHub Tracker Issue

Use this skill for durable GitHub issues that are meant to coordinate multi-PR engineering work, not for small bug reports or one-off tasks.

## Workflow

1. Identify the target repository with user input, `gh repo view`, or the current checkout.
2. Read repo-local governance before drafting when available: `AGENTS.md`, `CONTRIBUTING.md`, PR templates, branch policy docs, and workstream-specific roadmap files. Repo-local rules override this skill.
3. Inspect the reference issue or tracker named by the user, usually with `gh issue view <number> --repo <owner>/<repo> --json number,title,body,url,state,labels`.
4. Load a repo extension from [Repo Extensions](#repo-extensions) when one matches the repository; otherwise use the generic workflow.
5. Identify the exact workstream, current evidence, non-goals, milestone order, owner boundaries, and expected proof.
6. Read [references/tracker-issue-template.md](references/tracker-issue-template.md) for the reusable structure.
7. Draft the issue body with concrete, current facts. Do not overstate what the code proves.
8. Include checkbox milestones that can serve as a work log.
9. Include start-phase and close-phase requirements for every PR.
10. Include required tests and relevant benchmarks for each milestone. Performance milestones must require a before/after comparison against the pre-change baseline, not only a current benchmark snapshot, and must treat material regressions as blocking until optimized or explicitly accepted.
11. Include branch, PR, AI review, and CI process requirements when the workstream requires mergeable PRs.
12. Create or update the GitHub issue with `gh issue create` or `gh issue edit`.
13. Return the issue URL, repo, labels used, parent/child relationship if any, and main scope boundaries.

## Repo Extensions

Repo extensions preserve project-specific conventions without hardcoding them into the generic skill.

- For `snissn/gomap`, read [references/gomap.md](references/gomap.md) and preserve the legacy #1646-style tracker behavior.
- For `Polynomialstore/polystore`, read [references/polystore.md](references/polystore.md) before drafting tracker issues.
- If no extension matches, continue with the generic template and adapt metrics, labels, and PR policy from repo-local files.
- If adding a new repo-specific convention, add it as a reference file and keep this skill's main body generic.
- Prefer `gh label list --repo <owner>/<repo>` before creating issues.
- Only use labels that already exist unless the user has explicitly authorized label management.
- When label management is authorized, create narrowly scoped labels needed by the tracker before creating or updating issues. Use clear descriptions and stable colors; do not rename or delete existing labels unless explicitly requested.

## Rules

- Keep the issue body authoritative and buildoutable.
- Separate product goals from substrate work and experiments.
- State non-goals explicitly to avoid drift.
- Use benchmark metrics that match the domain. Throughput-sensitive work should include throughput; latency-sensitive work should include latency percentiles or per-unit timing; memory-sensitive work should include allocation or footprint metrics.
- Require performance evidence to compare **before vs after** for each claimed optimization or hot-path/storage change, including baseline commit/branch, candidate commit/branch, delta/ratio, and whether the comparison used identical commands, fixture size, hardware, and environment. Do not accept a current-only benchmark as proof of improvement.
- Require exact commands, hardware/context, benchmark boundaries, and domain counters for performance work.
- State a performance regression gate: material regressions in runtime, throughput, latency, memory, allocation, storage/rebuild overhead, or relevant counters are not acceptable by default; the PR must profile and optimize before mergeability can be claimed, or document that the remaining minimized regression is correctness-required and explicitly accepted by the coordinator/user.
- Require PR start and close phases: augment tests/benchmarks first, implement, then re-review and update evidence.
- Require iterative Codex, Copilot, and CodeRabbit review requests until reviews pass or are explicitly resolved when the user wants mergeable PRs, but only after each PR is mature enough to avoid review-credit churn: coherent code, focused tests, required benchmark evidence or rationale, current PR body/status evidence, no known local blockers, and latest-head CI running or green.
- If GitHub CI is backed up, include a directive to cancel stale non-head runs and keep only latest-head CI for active PRs.
- Never mark aspirational work as already proven. Use “current evidence,” “target,” and “completion criteria” distinctly.
- For umbrella work, create a parent tracker for sequencing and acceptance, then child issues for executable slices. Cross-link children from the umbrella and link the umbrella from every child.
- Every issue that requires PRs should state the branch policy and merge policy from the repo. If the repo requires topic branches, human approval, or no self-merge, include that explicitly.

## When Creating The Issue

Prefer a temp body file and `--body-file` for long issues:

```sh
gh issue create \
  --repo <owner>/<repo> \
  --title "<tracker title>" \
  --label enhancement \
  --label performance \
  --label tracking \
  --body-file /tmp/<issue-body>.md
```

If you generate issue bodies from a shell command, protect Markdown from shell expansion:

- Use single-quoted heredoc delimiters for every Markdown body: `<<'EOF'`, never `<<EOF`.
- Do not rely on shell interpolation inside Markdown bodies. Backticks in issue text will otherwise be executed as command substitutions, and `$...` may expand unexpectedly.
- For dynamic values such as newly created child issue URLs, create the issue bodies with quoted placeholders like `PARENT_ISSUE_URL`, then replace placeholders with a safe tool (`perl -0pi -e 's|PARENT_ISSUE_URL|...|g' /tmp/body.md`) or rewrite the issue with a second quoted heredoc after the values are known.
- Quote every heredoc in multi-issue scripts, including later `gh issue edit --body-file -` calls.

Adjust labels to match the repo and workstream. Do not add labels that do not exist unless the user authorized label management. When authorized, create missing labels first with `gh label create <name> --repo <owner>/<repo> --description <description> --color <hex>`.
