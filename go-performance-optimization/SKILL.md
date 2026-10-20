---
name: go-performance-optimization
description: Diagnose and optimize Go CPU, allocation, memory, and contention costs with representative public-path benchmarks and profiles. Use when Go runtime performance is material to an implementation or investigation, including proving fast-path activation and validating measured improvements.
---

# Go Performance Optimization

Optimize the user's actual workload and preserve its behavior. Use the repository's
toolchain, benchmark conventions, and acceptance policy. This skill supplies the
performance method; it does not authorize unrelated changes or replace PR gates.

For a pinned Go toolchain, verify the driver, resolved `GOROOT`/`GOTOOLDIR`
and `go tool compile -V` agree before a costly build. An absolute Go executable
does not override an inherited `GOROOT`; bind the intended root explicitly.
Retain setup failures separately and repair the environment before collecting
samples. An unexecuted benchmark is not a product regression or a gate rerun.

## Establish The Work And The Boundary

- Name the primary outcome and guardrails: latency/throughput, bytes and objects
  allocated, retained/peak memory, contention, or relevant domain work. Distinguish
  agreed targets from observations; do not invent a universal zero-allocation goal.
- Distinguish product requirements from chosen work-accounting limits. Record each
  consequential counter's origin, unit, and charged phases; do not infer a latency
  or useful-progress guarantee from the count alone. If fixed work defeats a
  selected quota, reassess the model explicitly: bound variable and fixed work
  separately when justified, report the full total, and preserve the original
  product gate or record its authorized revision. Changing units or excluding
  phases cannot silently pass the original gate.
- Inspect existing design, live adjacent work, and maintained primitives before
  choosing a fix. Trace the real public entry through dispatch, eligibility,
  optimized implementation, fallback, publication, and cleanup. Identify affected
  callers and ownership/lifetime contracts, including retry and failure paths.
- Define one operation, workload shape, lifecycle state, concurrency, and visibility
  or durability contract. Separate setup, warmup, steady work, flush/checkpoint, and
  teardown explicitly. Buffered acceptance, visible publication, and durable
  completion are different boundaries; keep the selected contract identical across
  comparisons and report deferred work. Do not improve timing by moving required
  work beyond the boundary or silently changing its amortization.
- Prove activation under the actual public configuration. A passing helper test or
  equivalent output can hide fallback. Prefer an existing selector, transaction
  statistic, or artifact; avoid mutable global hooks or production instrumentation
  solely for tests. Cover representative enabled and excluded configurations and
  state transitions that change routing. Verify configured mode together with
  actual flush/publication behavior; do not assume relaxed/buffered acceptance
  means no visibility flush.

For a planning request, capture the evidence gaps and smallest useful experiment;
do not launch a benchmark campaign merely to draft an issue.

## Diagnose Before Choosing The Fix

Read [Profiling And Measurement](references/profiling-and-measurement.md) when
collecting or interpreting evidence; it contains adaptable commands and traps.

1. Establish a comparable public-path baseline, plus an original/pre-project anchor
   when the claim needs one. Preserve the raw output and exact measurement inputs.
2. Choose a short profile that can distinguish the suspected cause: CPU for active
   execution; allocation bytes/objects for churn; live heap for retention; mutex,
   block, or trace for waiting and scheduling. Low CPU utilization with high elapsed
   time calls for a waiting/I/O investigation, not just CPU micro-optimization.
3. Rank a few concrete costs by absolute contribution, frequency, and the critical
   path. Follow high cumulative stacks to their actual flat costs. Treat GC as a
   possible consequence of churn or retained state. Form one causal hypothesis and
   the smallest change or counterfactual that can discriminate it.
4. Prefer removing repeated work, changing an unsuitable representation, consolidating
   a shared seam, or fixing dispatch over tuning a small leaf cost. Estimate the
   public ceiling from the measured affected fraction before pursuing a local win.
   A structural change still owns its callers, format/docs changes, and failure
   behavior; profile rank alone is not justification for a broad rewrite.

Do not add overlapping cumulative percentages, sum successive speedup percentages,
or present helper savings as public gains. For interacting changes, measure the
combined candidate against the baseline. Measure an incremental counterfactual only
when individual attribution matters, keeping mandatory fallback/copy work intact.

Reconsider the algorithm and integration boundary after two coherent attempts
fail to advance the public metric, or when helper wins disappear end to end.
Compare the current approach with reuse of an existing bulk/ordered operation,
less repeated work or materialization, and a different representation where
appropriate. Estimate which can move the measured dominant cost before coding.
Choose one bounded discriminating experiment, with a failure action; do not keep
tuning constants or growing lifetime/accounting helpers around a weak mechanism.
If instrumentation contradicts uninstrumented results, resolve the measurement
boundary/noise question with a predeclared control before selecting another fix.
An inconclusive control remains inconclusive; it does not require more repetitions
or waive the unresolved performance gate.
Carry consequential findings into the executing issue graph; a structural rewrite
still needs evidence and preserved behavior, not just a larger implementation.

## Reuse Existing Allocation Domains

For material allocation optimization, inventory the affected repository's arenas,
pools, batch buffers, caller-owned scratch, and direct-write APIs before choosing
storage. Record the strongest maintained mechanism, eligible payloads, owner and
last-consumer boundary, reset/release behavior, and retention limits. Reuse that
mechanism by default when its lifetime and concurrency contract fit; do not add a
replacement heap helper, pool, or arena around a cost already solved by that seam.
A different choice needs a documented contract mismatch or measured public-path
reason, with the applicable bytes, objects, latency, and retention tradeoffs.

Carry this choice into the plan and acceptance evidence. Planning may name the
bounded comparison still needed rather than invent results; implementation is not
allocation-complete without the reuse decision, lifetime controls, and applicable
public performance evidence. An arena-choice exception permits alternate storage;
it does not waive the measurement and acceptance rules below. For `snissn/gomap`, apply the
[existing-arena default](references/gomap.md) to eligible bulk/lifetime storage.

Bulk allocation can reduce objects without reducing bytes. Account for unused
capacity, peak/live backing storage, reset policy, and retained-memory bounds.
Reset or return storage only after its final alias, snapshot, pending write, and
asynchronous consumer release it. For shared/COW state, preserve explicit private
preparation and mutation authority, immutable rollback aliases, and candidate/seal
boundaries; arena residence alone does not grant exclusive ownership. Transient
buffer reuse never changes persistent value-log reachability or durability rules.

## Implement With Ownership And Risk In View

Use a meaningful public regression or activation check before implementation when
feasible. For a representation-only optimization without an observable behavioral
red, record that exception and use public activation/performance evidence plus
focused correctness and ownership controls; do not fabricate a failing assertion.

Audit changed hot-path allocations/copies by site and frequency: per item, batch,
request, goroutine, or setup. Separate required immutable output from temporary
work. Before reuse or pooling, establish who owns each buffer/object, who can retain
an alias, and when ownership ends. Small views may retain large backing storage;
fewer allocated bytes can increase residency. Do not turn a bounded temporary into
an unbounded cache or global pool. `sync.Pool` is opportunistic, not a lifetime or
correctness guarantee; preserve resets, size limits, isolation, and concurrent use.

Run focused checks for the changed risks before treating the changed implementation
as a performance candidate: repeated reuse and rollback, retained snapshots/candidates,
partial failure/retry, cancellation, or
concurrent consumers as applicable. Storage changes need relevant publication,
recovery, reopen, and corruption controls; performance tests alone do not protect
durability. Inventory real callers of a changed contract rather than patching only
initially failing fixtures. Test public behavior, not a copied eligibility predicate.

## Measure Early, Qualify The Stable Candidate

After focused correctness is sound, run a bounded **uninstrumented** public A/B
comparison early enough to redirect the approach. Alternate before/after runs on
the same quiet host; prebuild outside timing and keep workload, configuration,
toolchain, scheduler/concurrency, fixtures, and durability semantics equivalent.
Run diagnostic instrumentation separately. Serialize competing timed workloads and
avoid measurement I/O interference; disjoint source work or correctness tests need
not be globally serialized when they do not contaminate a measurement.

A few short pairs can show direction and reject a weak approach; label them
accordingly. Choose final repetition/duration and workload coverage for the claim
and noise, retain every planned sample, and use an appropriate statistical summary.
Do not rerun until significance appears. Investigate missed targets or material
regressions before declaring success; preserve explicit acceptance for unavoidable
residual costs. New behavior needs old-workload guardrails and feature-enabled
incremental/scaling evidence when no equivalent before case exists.

Once the candidate is coherent and viable, finish all affected tests, race,
integration, persistence, CI, and review gates required by risk and repository
policy. Run a broader check earlier when a changed risk requires it. Reuse unchanged
applicable evidence instead of restarting every campaign: after a test/docs-only
commit, show exact production and harness input equivalence and retain the original
measured source/binary identity. Product, build, configuration, or harness drift
requires affected evidence to be refreshed.

## Leave A Reviewable Result

Report the public operation and activation evidence, before/after source identities,
commands/environment, raw results, metrics with denominators, profile interpretation,
changed behavior, validation, and limitations. Include `ns/op` and derived operations/s
when useful, `B/op` and `allocs/op` for churn, and residency/peak data when lifetime
changed. Keep diagnostic profiles separate from uninstrumented acceptance numbers.

Bind retained evidence to exact source/build inputs, harness/overlays, binary hashes,
and raw artifacts; a branch name alone is insufficient. A component gain is scoped
to that component and workload, not final project acceptance. If an investigation
budget expires, record the finding, unresolved gate, and next bounded action.
Report actual useful work completed; repeated scans, empty polls, enqueued work, or
invented record counts cannot stand in for progress or completion.
