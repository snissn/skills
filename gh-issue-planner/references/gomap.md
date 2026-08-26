# snissn/gomap Tracker Extension

Use this extension when the target repository is `snissn/gomap`.

## Intent

Preserve the original #1646-style tracker behavior for gomap while keeping the main skill repo-neutral.

## Tracker Shape

- Use the #1646-style issue structure for durable multi-PR implementation trackers.
- Keep the issue body authoritative, buildoutable, and useful as a work log.
- Separate generic column-store work from vector-search-specific work when relevant.
- Keep product goals, substrate work, experiments, and deferred follow-ups explicitly separated.

## Graph Migration

- Preserve mature gomap issues as evidence/history anchors when their experiment ledgers remain useful.
- Prefer a net-new architecture or substrate graph when existing tickets are organized around local optimizations, stale attribution, or completion gates that no longer match the accepted goal.
- Add concise bidirectional `superseded by`, `consumed by`, `narrowed to`, or `deferred until` links instead of rewriting historical issue bodies into a different project.
- Keep benchmark-contract and final-evidence issues separate from implementation children when they own different claims.
- Make the parent graph ledger authoritative for current ordering; keep detailed benchmark and implementation evidence in the owning child.

## Accepted Gaps And Adjacent Durability Work

- Do not turn every TreeDB storage, load, query, allocation, or rebuild measurement into a north-star target. Classify it as a north-star, exit gate, guardrail, observational metric, or explicitly accepted gap.
- Record an accepted gap with the exact baseline, artifact or command, commit, environment, decision source, and revisit trigger. Keep reporting it, but do not leave it as an accidental completion blocker or create an optimization child solely for it.
- Treat a material unexplained regression against an accepted baseline separately from the already accepted gap.
- Before proposing on-disk, WAL, value-log, GC, checkpoint, manifest, or recovery changes, inspect adjacent in-flight work and state explicit ownership and non-goal boundaries.
- Accepted performance or footprint gaps never weaken correctness, persistence/reopen, recovery, reachability/GC, or durability requirements.

## Labels

Prefer existing gomap labels when present:

- `enhancement`
- `performance`
- `treedb`
- `tracking`

Run `gh label list --repo snissn/gomap` before using labels. Do not create missing labels unless the user asks.

## Benchmark Requirements

### Test-First Defaults

TreeDB implementation PRs use test-first development by default. Select the red test by the actual risk:

- bug fixes start with a focused regression test that fails for the reported behavior;
- durable or on-disk changes start with reopen, recovery, corruption/torn-tail, reachability/GC, or compatibility-contract tests as appropriate;
- query and collection changes start with result-parity, selection/fallback, mutation/staleness, no-document-fetch, or path-counter tests as appropriate;
- concurrency changes start with deterministic coordination/invariant tests plus race coverage where useful;
- architecture seams start with contract, selection, fallback, and generation/schema invalidation tests before substrate implementation.

Documentation-only, pure benchmark/instrumentation, exploratory, or adequately characterized mechanical-refactor work may use an explicit exception. Record why a meaningful red test is unavailable and what alternative correctness evidence applies. TreeDB's pre-alpha format policy permits intentional compatibility breaks, but it does not waive tests for the new format's reopen, durability, recovery, or GC invariants.

### Performance Relevance

Classify every TreeDB milestone or PR before implementation:

- **Not performance-relevant:** only with a concrete rationale.
- **Possibly performance-relevant:** require a focused benchmark, allocation check, profile, or path guardrail.
- **Performance-sensitive:** require identical before/after evidence on the relevant throughput/latency, allocation, memory-pressure, storage/rebuild, and domain-counter axes.
- **Performance-objective:** add a declared north-star or exit target, repeated measurements, and a failure action.

TreeDB hot-path, storage-layout, encoding, query, collection, ingestion, merge/compaction, checkpoint, value-log, concurrency, caching, and bulk-processing changes default to at least possibly performance-relevant. Query-ready storage, load/build, and OLAP execution changes are normally performance-sensitive or performance-objective.

For performance-relevant TreeDB, vector, column-store, storage, cache, decode, query, or materialization work, require:

- exact command;
- hardware/context;
- commit or branch;
- dataset shape;
- measured boundary, including setup/search/decode/doc-fetch timing where relevant;
- runtime or latency and throughput where relevant;
- `B/op` and `allocs/op` where allocation efficiency is relevant;
- peak RSS, peak/live heap, retained heap, or an equivalent measure where memory pressure is relevant;
- relevant counters such as rows/s, queries/s, bytes read, cache hits/misses, candidates/search, edges/search, docs fetched, storage/rebuild overhead, or index/build time.

Benchmark evidence must compare before vs after for each claimed optimization or hot-path/storage change using identical commands, fixture size, hardware, and environment.

If a metric is observational or an explicitly accepted gap, require faithful current reporting and any stated guardrail, but do not invent an improvement target.

Before imposing automated numeric performance gates, require a committed canonical workload and fixture, explicit durability/cache state, controlled temp/data placement, repetition and summary policy, noise tolerance, stable artifact schema, and an owned baseline. Use CI for stable, bounded smoke or regression checks and host-local canonical runs for expensive/noisy matrices. Until these guardrails exist, performance-sensitive PRs still require reproducible before/after evidence and reviewer judgment; lack of automation is not permission to omit measurement.

Do not require a PR to improve throughput, allocation efficiency, and peak memory simultaneously unless all three are declared objectives. Define the objective and guardrails, report tradeoffs, and treat an unexplained material regression on any relevant axis as blocking until optimized or explicitly accepted.

For TreeDB scaling/flush/checkpoint trackers, require explicit north-star gates and path-proof counters. Example gates include effective CPU use during the target phase, worker busy ratio, fallback reason totals, ops/span, checkpoint stage wall time, write+checkpoint throughput, storage footprint, reopen/GC safety, and any issue-specific target. A TreeDB optimization milestone is not complete merely because it avoids regression; it must move the declared gate or create/link a blocker issue for the measured next limiter.

For TreeDB parallel-saturation work, require an early root-cause classification matrix before architectural fixes: distinguish weak worker substrate, insufficient work shape/ops-per-span, serial reducer/publish/append fan-in, checkpoint coordination/flushMu waiting, external sync/I/O limits, and benchmark noise. Include at least one isolation harness or focused profile when the production 10MM shape cannot distinguish substrate capacity from workload shape.

## PR Requirements

- Require PR start, implementation, and close phases with red-test evidence or an explicit exception, green implementation evidence, and final affected-suite evidence.
- Require focused tests plus broader affected tests.
- Require iterative Codex, Copilot, and CodeRabbit reviews until findings are fixed or explicitly rejected with rationale, but only after the PR is mature enough to avoid review-credit churn: coherent code, focused tests, required benchmark evidence or rationale, current PR body/status evidence, no known local blockers, and latest-head CI running or green.
- Latest-head CI is required for mergeability evidence; stale green checks do not count.
- If CI is backed up, include stale non-head run cancellation guidance.
