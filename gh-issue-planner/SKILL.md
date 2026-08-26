---
name: gh-issue-planner
description: Inspect, plan, draft, create, update, reorganize, or review durable GitHub issues. Use for either a focused standalone engineering ticket or a multi-PR tracker and dependency graph, including deciding which shape fits and how existing issues should be reused or dispositioned.
---

# GitHub Issue Planner

Use this skill to choose and produce the smallest durable GitHub issue structure that fits the work: one focused issue or a multi-PR tracker graph.

## Operating Modes And Write Boundary

Match the user's requested mode and do not advance beyond it automatically:

- **Inspect/review:** read live issue state, classify the issue shape, and report findings; do not draft or write.
- **Structure sketch:** propose a standalone scope or tracker graph; do not write to GitHub.
- **Local draft:** prepare issue bodies or graph artifacts for review; do not write to GitHub.
- **Apply:** create or edit GitHub issues only when the user explicitly requests those writes.

For graph work, preserve the distinction between a clean execution graph and historical/evidence issues. A request to plan, synthesize, sketch, or review is not authorization to create or edit issues.

## Issue Shape Preflight

Before loading the tracker template or designing an issue graph, classify the requested work:

- **Standalone issue:** one repository, one coherent outcome, normally one PR, and no independently owned dependency or evidence gates.
- **Tracker:** multiple independently mergeable PRs, cross-repository sequencing, existing-issue reorganization, or multiple authoritative completion gates.

Route standalone work to the [Standalone Issue Workflow](#standalone-issue-workflow) and tracker work to the [Tracker Workflow](#tracker-workflow). In inspect/review mode, report:

- the fit decision and rationale;
- relevant existing-issue dispositions;
- coordination or ordering constraints; and
- the recommended standalone scope or tracker shape.

Do not create an umbrella, dependency graph, milestone ledger, or tracker-form issue for standalone work. Explicit invocation of this skill does not require forcing a standalone request into tracker form.

## Shared Workflow

1. Identify the requested operating mode and target repository with user input, `gh repo view`, or the current checkout.
2. Inspect any named reference issue and only the adjacent live state needed to classify the work. Use `gh issue view <number> --repo <owner>/<repo> --json number,title,body,url,state,labels` plus live linked state as needed. A new candidate without a reference issue is valid input.
3. Run the [Issue Shape Preflight](#issue-shape-preflight), then follow only the matching workflow below.

## Standalone Issue Workflow

Do not load the tracker template or design a dependency graph.

1. Read repo-local governance before drafting when available. Repo-local rules override this skill.
2. From concrete current evidence, define a concise title, problem, goal, scope, non-goals, acceptance criteria, risk-relevant tests or other proof, and related-issue or ordering constraints. Do not overstate what the code or linked evidence proves.
3. Reuse or update an existing issue when it already owns the outcome; otherwise recommend or draft one new issue.
4. Add only validation, performance evidence, branch, PR, review, or CI requirements that are relevant to this issue. Do not add tracker milestones or process boilerplate.
5. In apply mode, create or update the issue with `gh issue create` or `gh issue edit` after checking available labels.
6. Verify any write, then return the issue URL, disposition, scope boundaries, and coordination constraints.

## Tracker Workflow

1. Read repo-local governance before drafting when available: `AGENTS.md`, `CONTRIBUTING.md`, PR templates, branch policy docs, and workstream-specific roadmap files. Repo-local rules override this skill.
2. Load a repo extension from [Repo Extensions](#repo-extensions) when one matches the repository; otherwise use the generic workflow.
3. For umbrella, dependency-graph, reorganization, or supersession work, read [references/issue-graph-planning.md](references/issue-graph-planning.md) and produce the graph preflight before drafting issue bodies.
4. Classify each existing issue as retain, narrow, supersede, close, or defer. Assign every completion gate exactly one authoritative owner.
5. Identify the exact workstream, current evidence, non-goals, milestone order, owner boundaries, expected proof, and adjacent in-flight work that must not be disturbed.
6. Read [references/tracker-issue-template.md](references/tracker-issue-template.md) for the reusable issue structure.
7. Draft with concrete, current facts. Do not overstate what the code proves or convert every reported metric into an optimization target.
8. For every PR-bearing milestone, define the behavior or invariant that drives its test-first loop. Require a failing test before implementation, or an explicit exception with the alternative correctness evidence.
9. Classify each PR or milestone as **not performance-relevant**, **possibly performance-relevant**, **performance-sensitive**, or **performance-objective**. State the evidence required for that class and the metrics that match the affected path.
10. Include checkbox milestones that can serve as a work log, plus test-first start, implementation, and close phases for every PR.
11. Include required tests and context-relevant benchmarks for each milestone. Performance-sensitive and performance-objective milestones must require a before/after comparison against the pre-change baseline, not only a current benchmark snapshot, and must treat material regressions as blocking until optimized or explicitly accepted.
12. For performance-optimization trackers, define explicit **north-star gates** and per-milestone **exit gates** with current value, target value, required evidence, and the action if the gate fails. Classify non-target metrics as guardrails, observational metrics, or explicitly accepted gaps.
13. Include branch, PR, AI review, and CI process requirements when the workstream requires mergeable PRs.
14. In apply mode, create or update issues with `gh issue create` or `gh issue edit`, link every child to its parent, backfill the parent's graph ledger, and add concise disposition comments to superseded issues.
15. Verify the live graph after writes, then return issue URLs, repo, labels, edges, existing-issue dispositions, gate ownership, and main scope boundaries.

## Repo Extensions

Repo extensions preserve project-specific conventions without hardcoding them into the generic skill.

- For `snissn/gomap`, read [references/gomap.md](references/gomap.md) and preserve the legacy #1646-style tracker behavior.
- For `Polynomialstore/polystore`, read [references/polystore.md](references/polystore.md) before drafting tracker issues.
- For any umbrella, dependency graph, tracker migration, or supersession request, read [references/issue-graph-planning.md](references/issue-graph-planning.md).
- If no extension matches, continue with the generic template and adapt metrics, labels, and PR policy from repo-local files.
- If adding a new repo-specific convention, add it as a reference file and keep this skill's main body generic.
- Prefer `gh label list --repo <owner>/<repo>` before creating issues.
- Only use labels that already exist unless the user has explicitly authorized label management.
- When label management is authorized, create narrowly scoped labels needed by the tracker before creating or updating issues. Use clear descriptions and stable colors; do not rename or delete existing labels unless explicitly requested.

## Tracker Rules

- Keep the issue body authoritative and buildoutable.
- Separate product goals from substrate work and experiments.
- State non-goals explicitly to avoid drift.
- Keep the graph minimal: every child must own an executable slice, a decision gate, or final evidence. Do not create parallel issues that own the same completion gate.
- Distinguish the execution graph from evidence/history issues. Preserve useful history with cross-links and concise disposition comments instead of rewriting mature issue narratives into unrelated architecture.
- Make dependencies directional and explicit. Conditional children must name the evidence that activates them and remain non-blocking until that condition is met.
- Classify measured metrics as north-star gates, milestone exit gates, guardrails, observational metrics, or explicitly accepted gaps. An accepted gap must record its evidence basis and revisit trigger and must not remain an accidental completion blocker.
- Require test-first development for implementation PRs: name the behavior or invariant, add or update a test that fails for the intended reason, implement the smallest coherent change that makes it pass, and refactor while green. Do not treat post-hoc coverage as test-first evidence.
- Test-first does not mean unit-test-only. Use contract, characterization, integration, reopen/recovery, fault-injection, race, or end-to-end tests when those best express the risk.
- Allow explicit test-first exceptions for documentation-only work, pure instrumentation or benchmark changes, exploratory spikes, and mechanical refactors already bounded by adequate characterization tests. The tracker and PR must record why a meaningful red test is impractical and what alternative evidence protects behavior.
- Require every PR-bearing milestone to classify performance relevance. Changes touching hot paths, storage or wire layouts, encoding, concurrency, I/O, caching, query execution, ingestion, compaction, or bulk processing default to at least possibly performance-relevant unless the tracker records a concrete rationale otherwise.
- For possibly performance-relevant work, require a focused benchmark, allocation check, profile, or equivalent guardrail on the affected path. For performance-sensitive and performance-objective work, require identical before/after evidence on the relevant axes. A not-performance-relevant PR needs only a concise rationale, not ceremonial benchmarks.
- Select metrics by risk. Throughput and latency measure execution behavior; `B/op` and `allocs/op` measure allocation efficiency; peak RSS, peak/live heap, or retained heap measure memory pressure. Do not substitute allocation metrics for footprint evidence when memory residency is the risk.
- Do not require simultaneous improvement in every metric. Define the objective and guardrails, measure tradeoffs, and require explicit acceptance for a remaining material regression.
- Use hard numeric regression thresholds only when the harness, fixture, repetition policy, and noise tolerance are stable enough to support them. Until then, require reproducible human-reviewed evidence and a reliability plan rather than inventing a precise gate.
- Use benchmark metrics that match the domain. Throughput-sensitive work should include throughput; latency-sensitive work should include latency percentiles or per-unit timing; memory-sensitive work should include allocation or footprint metrics.
- Require performance evidence to compare **before vs after** for each claimed optimization or hot-path/storage change, including baseline commit/branch, candidate commit/branch, delta/ratio, and whether the comparison used identical commands, fixture size, hardware, and environment. Do not accept a current-only benchmark as proof of improvement.
- Require exact commands, hardware/context, benchmark boundaries, and domain counters for performance work.
- State a performance regression gate: material regressions in runtime, throughput, latency, memory, allocation, storage/rebuild overhead, or relevant counters are not acceptable by default; the PR must profile and optimize before mergeability can be claimed, or document that the remaining minimized regression is correctness-required and explicitly accepted by the coordinator/user.
- For optimization work, state an insufficient-improvement gate: if the claimed/north-star metric does not move by the tracker-defined threshold, the issue remains incomplete even when tests and CI pass. The PR or issue must either fix the gate, narrow itself to instrumentation-only, or open/link a blocking follow-up that owns the measured next bottleneck before downstream/final-gate work can claim completion. Default tracker behavior is iterative and thorough: do not close as "insufficient" unless the user explicitly stops or accepts an open-blocker outcome.
- Require per-milestone exit gates with numeric targets or explicit qualitative pass/fail evidence. Each gate should include: intended path/counter proof, before/after command identity, success threshold, and failure action.
- Require PR start, implementation, and close phases: establish and capture the red test first (or document the exception), implement to green, refactor while green, then rerun affected tests and context-required performance evidence.
- Require iterative Codex, Copilot, and CodeRabbit review requests until reviews pass or are explicitly resolved when the user wants mergeable PRs, but only after each PR is mature enough to avoid review-credit churn: coherent code, focused tests, required benchmark evidence or rationale, current PR body/status evidence, no known local blockers, and latest-head CI running or green.
- If GitHub CI is backed up, include a directive to cancel stale non-head runs and keep only latest-head CI for active PRs.
- Never mark aspirational work as already proven. Use “current evidence,” “target,” and “completion criteria” distinctly.
- For umbrella work in apply mode, create a parent tracker for sequencing and acceptance, then child issues for executable slices. Cross-link children from the umbrella and link the umbrella from every child.
- Every issue that requires PRs should state the branch policy and merge policy from the repo. If the repo requires topic branches, human approval, or no self-merge, include that explicitly.

## When Creating The Issue

Prefer a temp body file and `--body-file` for long issues:

```sh
gh issue create \
  --repo <owner>/<repo> \
  --title "<issue title>" \
  --body-file /tmp/<issue-body>.md
```

If you generate issue bodies from a shell command, protect Markdown from shell expansion:

- Use single-quoted heredoc delimiters for every Markdown body: `<<'EOF'`, never `<<EOF`.
- Do not rely on shell interpolation inside Markdown bodies. Backticks in issue text will otherwise be executed as command substitutions, and `$...` may expand unexpectedly.
- For dynamic values such as newly created child issue URLs, create the issue bodies with quoted placeholders like `PARENT_ISSUE_URL`, then replace placeholders with a safe tool (`perl -0pi -e 's|PARENT_ISSUE_URL|...|g' /tmp/body.md`) or rewrite the issue with a second quoted heredoc after the values are known.
- Quote every heredoc in multi-issue scripts, including later `gh issue edit --body-file -` calls.

Adjust labels to match the repo and workstream. Do not add labels that do not exist unless the user authorized label management. When authorized, create missing labels first with `gh label create <name> --repo <owner>/<repo> --description <description> --color <hex>`.
