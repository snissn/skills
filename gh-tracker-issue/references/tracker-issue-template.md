# #1646-Style Tracker Issue Template

Use this as a structure guide. Keep sections that matter for the requested workstream and remove sections that do not.

## Title

Use an action-oriented title:

```text
Land <capability/substrate> for <product/workstream>
```

Examples:

```text
Land TreeDB column-store-native vector graph search
Land shared mmap-backed column-store views for native vector graph search
```

## Body Structure

```markdown
## Goal

State the final concrete outcome. Include what “done” means.

## Why This Exists

Explain the observed gap, current bottleneck, or product mismatch. Use hard wording when the gap is real.

## Current Evidence

List current branches, PRs, commits, profiles, benchmark artifacts, issue links, and exact measured results.

Use tables for benchmark evidence:

| Benchmark | Workers | ns/op | ops/sec | B/op | allocs/op |
| --- | ---: | ---: | ---: | ---: | ---: |

## Current State

Describe how the code works today. Separate implementation facts from assumptions.

## Desired State

Describe the target architecture or workflow.

## Scope

List what belongs in this issue.

## Non-Goals And Boundary

List what must not be implemented here.

## Execution Ordering And Blocking

Describe the intended order and what blocks later milestones.

## Coordination

Identify adjacent PRs, issues, agents, branches, or modules and which files/areas each lane owns.

## Required PR Body Sections

- [ ] Linked tracker issue and milestone.
- [ ] Start-phase test plan.
- [ ] Start-phase performance plan.
- [ ] Close-phase test evidence.
- [ ] Close-phase benchmark evidence.
- [ ] Performance regression assessment: any material regression is blocking until optimized away or explicitly accepted with evidence.
- [ ] Markdown benchmark table with `ns/op`, `ops/sec`, `B/op`, `allocs/op`, and relevant counters.
- [ ] Setup/decode/search/doc-fetch timing boundary.
- [ ] AI review status and unresolved thread summary.

## Per-PR Test And Performance Workflow

Start phase:

- [ ] Review and augment tests before implementation.
- [ ] Review and augment benchmarks before implementation.
- [ ] Record baseline commands and artifact paths.

Implementation phase:

- [ ] Implement tests before or alongside code.
- [ ] Fix failures without weakening scope.
- [ ] Keep benchmarks scoped to the PR’s actual risk.

Close phase:

- [ ] Re-run focused tests.
- [ ] Re-run relevant benchmarks.
- [ ] Compare before/after throughput and allocations.
- [ ] Treat material regressions as blocking: profile, optimize, rerun, and do not merge unless eliminated or explicitly accepted as minimized/correctness-required.
- [ ] Request iterative AI reviews until passing or intentionally resolved.

## CI Backlog Directive

- [ ] Cancel stale runs that are not for the current head of an active PR.
- [ ] Keep latest-head CI active for relevant PR branches.
- [ ] Do not use stale green checks from older heads as mergeability proof.

## Milestones

### M0. Baseline, Inventory, And Process

Purpose: establish facts before implementation.

- [ ] Inventory current code paths.
- [ ] Record baseline tests.
- [ ] Record baseline benchmarks.
- [ ] Identify ownership boundaries.

Required tests:

- [ ] Add focused test names here.

Required benchmarks:

- [ ] Add focused benchmark names and metrics here.

### M1. First Implementation Seam

Purpose: create the smallest correct seam future PRs can build on.

- [ ] Add explicit option/status/contract.
- [ ] Fail closed on unsupported/mismatched state.
- [ ] Preserve existing behavior outside the selected path.

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

- [ ] Exact command.
- [ ] Hardware/context.
- [ ] Dataset shape.
- [ ] What is timed.
- [ ] What is excluded from the timer.
- [ ] `ns/op`.
- [ ] `ops/sec`.
- [ ] `B/op`.
- [ ] `allocs/op`.
- [ ] Relevant domain counters.
- [ ] Profile artifact paths when profiles are collected.

Regression gate: if the candidate is materially worse in runtime, throughput, allocations, storage/rebuild overhead, or relevant counters, the issue/PR remains incomplete until the team profiles and optimizes the changed path. A remaining regression needs explicit coordinator/user acceptance, a clear correctness or scope rationale, and updated evidence.

## Tests

Group tests by behavior:

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
- [ ] Current evidence proves the goal, not just a subset.
- [ ] PRs are mergeable: latest-head CI green and AI reviews passing/resolved.
- [ ] Docs/examples are updated when user-facing behavior changed.

## Deferred Follow-Ups

List related work intentionally not included in this issue.
```

## Quality Checklist

Before creating or editing the issue, verify:

- [ ] The issue distinguishes current state from desired state.
- [ ] The issue distinguishes implementation work from evidence work.
- [ ] Each milestone has checkboxes.
- [ ] Each milestone has tests.
- [ ] Performance-sensitive milestones have benchmark requirements.
- [ ] Non-goals are explicit.
- [ ] The issue avoids fake completion paths.
- [ ] The issue is useful as a work log after creation.
