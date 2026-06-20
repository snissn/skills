# snissn/gomap Tracker Extension

Use this extension when the target repository is `snissn/gomap`.

## Intent

Preserve the original #1646-style tracker behavior for gomap while keeping the main skill repo-neutral.

## Tracker Shape

- Use the #1646-style issue structure for durable multi-PR implementation trackers.
- Keep the issue body authoritative, buildoutable, and useful as a work log.
- Separate generic column-store work from vector-search-specific work when relevant.
- Keep product goals, substrate work, experiments, and deferred follow-ups explicitly separated.

## Labels

Prefer existing gomap labels when present:

- `enhancement`
- `performance`
- `treedb`
- `tracking`

Run `gh label list --repo snissn/gomap` before using labels. Do not create missing labels unless the user asks.

## Benchmark Requirements

For TreeDB, vector, column-store, storage, cache, decode, query, or materialization work, require:

- exact command;
- hardware/context;
- commit or branch;
- dataset shape;
- measured boundary, including setup/search/decode/doc-fetch timing where relevant;
- `ns/op`;
- `ops/sec`;
- `B/op`;
- `allocs/op`;
- relevant counters such as rows/s, queries/s, bytes read, cache hits/misses, candidates/search, edges/search, docs fetched, storage/rebuild overhead, or index/build time.

Benchmark evidence must compare before vs after for each claimed optimization or hot-path/storage change using identical commands, fixture size, hardware, and environment.

For TreeDB scaling/flush/checkpoint trackers, require explicit north-star gates and path-proof counters. Example gates include effective CPU use during the target phase, worker busy ratio, fallback reason totals, ops/span, checkpoint stage wall time, write+checkpoint throughput, storage footprint, reopen/GC safety, and any issue-specific target. A TreeDB optimization milestone is not complete merely because it avoids regression; it must move the declared gate or create/link a blocker issue for the measured next limiter.

For TreeDB parallel-saturation work, require an early root-cause classification matrix before architectural fixes: distinguish weak worker substrate, insufficient work shape/ops-per-span, serial reducer/publish/append fan-in, checkpoint coordination/flushMu waiting, external sync/I/O limits, and benchmark noise. Include at least one isolation harness or focused profile when the production 10MM shape cannot distinguish substrate capacity from workload shape.

## PR Requirements

- Require PR start and close phases.
- Require focused tests plus broader affected tests.
- Require iterative Codex, Copilot, and CodeRabbit reviews until findings are fixed or explicitly rejected with rationale, but only after the PR is mature enough to avoid review-credit churn: coherent code, focused tests, required benchmark evidence or rationale, current PR body/status evidence, no known local blockers, and latest-head CI running or green.
- Latest-head CI is required for mergeability evidence; stale green checks do not count.
- If CI is backed up, include stale non-head run cancellation guidance.
