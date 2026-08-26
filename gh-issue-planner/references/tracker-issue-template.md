# GitHub Tracker Issue Template

Use this as a structure guide. Keep sections that matter for the requested workstream and remove sections that do not.

## Contents

- [Title](#title)
- [Operating mode and graph preflight](#operating-mode-and-graph-preflight)
- [Body structure](#body-structure)
- [Quality checklist](#quality-checklist)

## Title

Use an action-oriented title:

```text
Land <capability/substrate> for <product/workstream>
```

Examples:

```text
Land browser WASM KZG optimization for no-local-helper uploads
Land shared cache invalidation for API read paths
```

## Operating Mode And Graph Preflight

Before using the body structure:

1. Confirm the request passed the skill's Issue Shape Preflight. A standalone issue must not use this template.
2. Confirm whether the request is inspect/review, structure sketch, local draft, or GitHub apply.
3. For umbrella or migration work, complete the preflight in [issue-graph-planning.md](issue-graph-planning.md).
4. Do not write to GitHub unless apply mode was explicitly requested.

## Body Structure

```markdown
## Goal

State the final concrete outcome. Include what “done” means.

## Why This Exists

Explain the observed gap, current bottleneck, or product mismatch. Use hard wording when the gap is real.

## Current Evidence

List current branches, PRs, commits, profiles, benchmark artifacts, issue links, and exact measured results.

Use tables for benchmark evidence:

| Benchmark | Baseline | Candidate | Delta | Notes |
| --- | ---: | ---: | ---: | --- |

Use the metrics that fit the workstream. Examples: wall time, per-unit latency, throughput, memory footprint, allocation count, storage footprint, rebuild time, browser responsiveness, or domain-specific counters.

## Current State

Describe how the code works today. Separate implementation facts from assumptions.

## Desired State

Describe the target architecture or workflow.

## Issue Graph And Gate Ownership

For umbrella work, keep a compact authoritative ledger. Omit this section for a standalone issue.

| Issue/node | Role | Depends on | Blocks | Authoritative gate | Current disposition |
| --- | --- | --- | --- | --- | --- |
| child or existing issue | substrate, experiment, integration, residual, evidence, or history | explicit blockers | explicit successors | one owned gate | create, retain, narrow, supersede, close, or defer |

State conditional edges and the evidence that activates them. Do not duplicate one completion gate across multiple issues.

## North-Star Gates

For performance or scaling trackers, define the gates that must pass before the tracker can close. Do not rely on merged child PRs alone.

| Gate | Current | Target | Required evidence | If the gate fails |
| --- | ---: | ---: | --- | --- |
| Example: effective CPU during target phase | current measured value | target threshold | exact benchmark/profile/counters | keep blocker open or create linked replacement child |

Rules:

- A final gate may decide not to change a default, but it may not claim the tracker goal is complete unless the north-star gates pass or explicit replacement blockers are linked and accepted.
- Current-only measurements are not proof of improvement.
- "No regression" is not enough for an optimization milestone unless that milestone is explicitly instrumentation-only or safety-only.

## Gate Classification And Accepted Gaps

Classify important metrics so reported values do not become accidental goals.

| Metric | Class | Current/baseline | Target or boundary | Decision source | Revisit trigger |
| --- | --- | ---: | ---: | --- | --- |
| example footprint | north-star, milestone exit, guardrail, observational, or accepted gap | current evidence | target, guardrail, or `n/a` | issue/user/decision link | format finalization, scale change, regression, or reprioritization |

Accepted gaps remain visible but do not block completion. A guardrail breach is separate from the already accepted baseline and must be handled explicitly.

## Root-Cause Classification Gate

For performance/saturation trackers, require an early evidence gate that classifies why the current path misses the north-star target before broad implementation starts.

| Candidate limiter | Evidence to collect | Action if confirmed |
| --- | --- | --- |
| insufficient work shape | ops/span, task size distribution, queue/frontier shape | coalescing/work-shaping milestone |
| weak parallel substrate | synthetic high-work saturation harness, worker busy/idle, CPU/wall | worker-kernel/task-balance milestone |
| serial fan-in | reducer/publish/append/commit stage wall and mutex/block profiles | fan-in polish milestone |
| checkpoint coordination | flushMu wait, active background wait, frontier/queue ownership | checkpoint coordinator/frontier milestone |
| external durability/I/O | backend sync/fsync/value-log sync timing with CPU idle | I/O-specific blocker or accepted external limit |
| benchmark/harness artifact | mismatched commands, stale baseline, noisy host | rerun/fix harness before implementation claims |

Do not choose an implementation lane by assumption when the evidence can distinguish these classes. The graph may branch or reorder after this classification; update child issues and edges rather than pushing a fixed stale plan.

## Scope

List what belongs in this issue.

## Non-Goals And Boundary

List what must not be implemented here.

## Execution Ordering And Blocking

Describe the intended order and what blocks later milestones. Identify conditional branches, their activation evidence, and the final evidence owner.

## Coordination

Identify adjacent PRs, issues, agents, branches, or modules and which files/areas each lane owns. Record in-flight work or correctness boundaries the tracker must not disturb.

## Test-First And Performance Classification

Classify every PR-bearing milestone before implementation. Do not infer that all PRs need the same benchmark matrix.

| Milestone/PR | Behavior or invariant first proved by | Test-first mode or exception | Performance class | Required performance evidence |
| --- | --- | --- | --- | --- |
| example | named failing test or contract suite | red-green-refactor, characterization, or explicit exception | not relevant, possible, sensitive, or objective | rationale, focused check, full before/after, or north-star gate |

Performance classes:

| Class | Default evidence |
| --- | --- |
| Not performance-relevant | Concise rationale; no ceremonial benchmark. |
| Possibly performance-relevant | Focused benchmark, allocation check, profile, or equivalent guardrail on the affected path. |
| Performance-sensitive | Identical before/after measurements for relevant throughput or latency, allocation efficiency, memory pressure, and domain counters. |
| Performance-objective | Performance-sensitive evidence plus a declared target, repeated measurements, profile-backed attribution when needed, and explicit failure action. |

Changes to hot paths, storage or wire layouts, encoding, concurrency, I/O, caching, query execution, ingestion, compaction, or bulk processing default to at least possibly performance-relevant unless the issue records a concrete rationale otherwise.

Hard numeric thresholds require a stable harness, fixture, repetition policy, and noise tolerance. If those do not exist yet, require reproducible human-reviewed evidence and make harness stabilization an owned prerequisite; do not invent precise automation gates.

## Branch And PR Policy

State the repo-specific policy discovered from `AGENTS.md`, `CONTRIBUTING.md`, PR templates, or equivalent files.

- [ ] Work must happen on a topic branch unless repo policy says otherwise.
- [ ] Direct pushes to protected/default branches are prohibited unless explicitly authorized by repo policy and the user.
- [ ] PRs must be mergeable before merge: latest-head CI, focused tests, benchmark evidence when relevant, and AI/code-review findings resolved or explicitly rejected with rationale.
- [ ] Codex, Copilot, CodeRabbit, or other review-credit-consuming AI reviews are requested only after the PR is mature enough to avoid review-credit churn: coherent code, focused tests, required benchmark evidence or rationale, current PR body/status evidence, no known local blockers, and latest-head CI running or green.
- [ ] Human approval or maintainer approval requirement is stated when required by repo policy.
- [ ] Self-merge policy is stated when relevant.

## Required PR Body Sections

- [ ] Linked tracker issue and milestone.
- [ ] Behavior or invariant under change.
- [ ] Start-phase failing-test evidence, including the expected failure reason, or an explicit test-first exception and alternative correctness evidence.
- [ ] Performance classification and metric rationale.
- [ ] Start-phase performance plan when the class requires one.
- [ ] Close-phase test evidence.
- [ ] Close-phase benchmark/profile evidence or the not-performance-relevant rationale.
- [ ] Performance regression assessment: any material regression is blocking until optimized away or explicitly accepted with evidence.
- [ ] Markdown benchmark table with domain-appropriate before/after metrics and relevant counters when the performance class requires it.
- [ ] Measurement boundary: what is timed and what is excluded.
- [ ] AI review status and unresolved thread summary.

## Per-PR Test And Performance Workflow

Start phase:

- [ ] Name the externally meaningful behavior, invariant, or regression being changed.
- [ ] Add or update the smallest appropriate test and run it before implementation to capture a failure for the intended reason.
- [ ] If a meaningful red test is impractical, document the allowed exception and the characterization, contract, review, or other evidence that bounds behavior.
- [ ] Classify performance relevance and select metrics that match the affected path.
- [ ] Review or augment the focused benchmark before implementation when the class requires performance evidence.
- [ ] Record baseline commands, environment, repetition policy, and artifact paths when applicable.

Implementation phase:

- [ ] Implement the smallest coherent change that makes the test pass.
- [ ] Refactor while the focused and affected suites remain green.
- [ ] Fix failures without weakening assertions, changing the intended behavior, or masking the original regression.
- [ ] Keep benchmarks scoped to the PR’s actual risk.

Close phase:

- [ ] Re-run focused tests.
- [ ] Re-run broader affected, race, recovery, reopen, or integration tests as the risk requires.
- [ ] Re-run the evidence required by the performance classification.
- [ ] For performance-sensitive or performance-objective work, compare identical before/after commands and report the relevant throughput or latency, `B/op`, `allocs/op`, peak/live memory, and domain counters; mark irrelevant axes `N/A` with rationale.
- [ ] Treat material regressions as blocking: profile, optimize, rerun, and do not merge unless eliminated or explicitly accepted as minimized/correctness-required.
- [ ] Request iterative AI reviews only after the PR is mature, then repeat after meaningful fixes until passing or intentionally resolved.

## CI Backlog Directive

- [ ] Cancel stale runs that are not for the current head of an active PR.
- [ ] Keep latest-head CI active for relevant PR branches.
- [ ] Do not use stale green checks from older heads as mergeability proof.

## Milestones

### M0. Baseline, Inventory, And Process

Purpose: establish facts before implementation.

- [ ] Inventory current code paths.
- [ ] Record baseline tests.
- [ ] Record baseline benchmarks when required by the milestone performance class.
- [ ] Identify ownership boundaries.

Required tests:

- [ ] Add focused test names here and identify the expected pre-implementation failure.

Required benchmarks:

- [ ] Add focused benchmark names and metrics here, or record the not-performance-relevant rationale.

### M1. First Implementation Seam

Purpose: create the smallest correct seam future PRs can build on.

- [ ] Add explicit option/status/contract.
- [ ] Fail closed on unsupported/mismatched state.
- [ ] Preserve existing behavior outside the selected path.

Milestone exit gate:

- [ ] The intended path/counter proves the seam is actually exercised, or this milestone is explicitly contract/instrumentation-only.
- [ ] If a required performance/scaling gate did not move, the issue is marked blocked/fix-needed and a measured next-bottleneck child is opened or linked before successors can claim readiness.

Required tests:

- [ ] Selection/status test.
- [ ] Fallback/error test.
- [ ] Compatibility test.

Required benchmarks:

- [ ] Benchmark the new seam only if it can affect hot paths.

### M2. Core Correctness Implementation

Purpose: implement the main behavior without broad optimization drift.

- [ ] Implement the real path through existing architecture.
- [ ] Avoid fake parallel formats or private sidecars unless explicitly scoped.
- [ ] Add direct validation and race/concurrency tests where relevant.

Required tests:

- [ ] Correctness parity test.
- [ ] Persistence/reopen test if durable state is involved.
- [ ] Mutation/staleness test if writes are involved.

Required benchmarks:

- [ ] Hot path benchmark.
- [ ] Allocation benchmark.
- [ ] Accounting counters if applicable.

### M3. Performance And Scaling Follow-Through

Purpose: remove measured local overhead introduced or exposed by the implementation.

- [ ] Profile the implementation.
- [ ] Rank bottlenecks by measured cost.
- [ ] Fix local overhead without weakening correctness.
- [ ] Defer unrelated broad tuning into follow-up tickets.

Milestone exit gate:

- [ ] The primary metric reaches the target threshold or improves by the tracker-defined minimum.
- [ ] Required counters prove the intended implementation path ran, not just a fallback/smoke path.
- [ ] An evidence reviewer has checked command identity, before/after baseline, counters, profiles, and that the PR/issue does not overclaim.
- [ ] If the gate fails, successors remain blocked until the PR is fixed or a replacement blocker is linked and accepted.

Required tests:

- [ ] Regression tests for optimized code paths.
- [ ] Race tests for shared/cache/session state.

Required benchmarks:

- [ ] Before/after benchmark table.
- [ ] CPU profile summary.
- [ ] Allocation profile summary.

### M4. Documentation, Demos, And Closeout

Purpose: leave the work understandable and auditable.

- [ ] Update docs or examples.
- [ ] Add commands for users/developers.
- [ ] Add final benchmark evidence.
- [ ] List remaining caveats.

Required tests:

- [ ] Docs/example command test if applicable.

Required benchmarks:

- [ ] Final representative benchmark table.

## Benchmarks And Evidence

Define the standard benchmark matrix. Include:

- [ ] Performance classification and why it applies.
- [ ] Exact command.
- [ ] Hardware/context.
- [ ] Dataset shape.
- [ ] Repetition count, summary statistic, and noise tolerance.
- [ ] What is timed.
- [ ] What is excluded from the timer.
- [ ] Runtime or latency metrics.
- [ ] Throughput metrics where relevant.
- [ ] Allocation efficiency (`B/op`, `allocs/op`) where relevant.
- [ ] Peak RSS, peak/live heap, retained heap, or another footprint metric where memory pressure is relevant.
- [ ] Relevant domain counters.
- [ ] Profile artifact paths when profiles are collected.

An instrumentation or benchmark-harness PR is judged on correctness, repeatability, attribution boundaries, and representativeness. It does not need to make the product faster merely because it emits performance data.

Regression gate: if the candidate is materially worse in runtime, throughput, latency, memory, allocations, storage/rebuild overhead, browser responsiveness, or relevant counters, the issue/PR remains incomplete until the team profiles and optimizes the changed path. A remaining regression needs explicit coordinator/user acceptance, a clear correctness or scope rationale, and updated evidence.

Insufficient-improvement gate: if the candidate is not materially worse but also does not meet the milestone's stated improvement/saturation target, the milestone is still incomplete for optimization work. The next action must be one of: fix and rerun, explicitly re-scope the milestone as instrumentation/safety only, or open/link a blocking follow-up for the newly measured bottleneck before downstream final-gate work proceeds.

## Tests

Group tests by behavior:

- [ ] Failing-test evidence or explicit test-first exception.
- [ ] Correctness.
- [ ] Persistence/reopen.
- [ ] Fallback/status.
- [ ] Mutation/staleness.
- [ ] Concurrency/race.
- [ ] Compatibility.
- [ ] No-document-fetch or hot-loop scope if relevant.

## Completion Criteria

State evidence required before closing the tracker:

- [ ] All milestone checkboxes complete or intentionally moved to linked follow-ups.
- [ ] Required tests pass.
- [ ] Required benchmarks are recorded.
- [ ] No unaccepted material performance regression remains.
- [ ] Accepted gaps are recorded as non-blocking with evidence and revisit triggers; any guardrail breach is resolved or explicitly accepted.
- [ ] Current evidence proves the goal, not just a subset.
- [ ] North-star gates are satisfied, or any failed gates have explicit user/coordinator acceptance plus linked replacement blockers that prevent false completion.
- [ ] PRs are mergeable under the repo policy: latest-head CI green, required tests pass, benchmark evidence is posted when relevant, and AI/code-review findings are passing, resolved, or explicitly rejected with rationale.
- [ ] Docs/examples are updated when user-facing behavior changed.

## Deferred Follow-Ups

List related work intentionally not included in this issue.
```

## Quality Checklist

Before creating or editing the issue, verify:

- [ ] The requested operating mode is explicit and no GitHub write exceeds it.
- [ ] Umbrella or migration work has a reviewed graph preflight.
- [ ] The issue distinguishes current state from desired state.
- [ ] The issue distinguishes implementation work from evidence work.
- [ ] Existing issues have explicit retain, narrow, supersede, close, or defer dispositions.
- [ ] Every blocking edge is explicit and every completion gate has one authoritative owner.
- [ ] North-stars, exit gates, guardrails, observational metrics, and accepted gaps are distinguished.
- [ ] Every PR-bearing milestone names its test-first behavior/invariant or a valid explicit exception.
- [ ] Every PR-bearing milestone classifies performance relevance and requests only context-appropriate evidence.
- [ ] Each milestone has checkboxes.
- [ ] Each milestone has tests.
- [ ] Performance-sensitive milestones have benchmark requirements.
- [ ] Non-goals are explicit.
- [ ] The issue avoids fake completion paths.
- [ ] The issue is useful as a work log after creation.
