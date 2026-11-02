# Efficient Performance Experiments

Use this loop when an optimization's cause or benefit is uncertain. It complements
existing acceptance, authorization, and resource gates; it adds no approval step or
mandatory artifact. Known-cause repairs can proceed directly with relevant checks.
Optimize for accepted improvement or a useful decision per engineering and machine
time. Tests, prototypes, receipts, and reviews support those outcomes.

## Define A Decision Before Construction

Keep five short fields in the existing ticket or working checkpoint:

- **Observed cost:** source/workload identity, affected operation, and measured cost.
- **Hypothesis:** the cause and why changing it could move the public metric.
- **Intervention:** the smallest prototype or counterfactual using existing code.
- **Discriminator:** the observation separating the hypothesis from alternatives,
  expected direction, and worthwhile effect relative to observed noise.
- **Failure action:** what rejects the route, needs a different measurement, or
  triggers simplification, replacement, or deferral.

Use existing profiles and exact source routes first. Estimate the public ceiling
from affected work without adding overlapping cumulative percentages or treating
helper savings as an end-to-end prediction. Keep a short ranked set of unanswered
questions and favor cheap discriminators over speculative production implementations.
Overlap independent experiments when resources and contracts permit. Any
already-authorized helper gets a bounded unanswered question; reuse its answer
rather than repeating discovery.

## Climb The Evidence Ladder, Stop On Failure

1. **Route and fixture:** confirm the actual public configuration exercises the
   suspected path. Validate compilation, selectors, and the fixture at the unchanged
   baseline; distinguish an intended regression failure from a setup error before
   launching expensive work.
2. **Disposable prototype:** prefer a narrow source delta, test overlay, or existing
   configuration counterfactual. Reuse maintained APIs, ownership, decoders, and
   adapters. Avoid a new cache, public API, metric family, or control plane merely
   to test a hypothesis. Preserve the source, command, raw result, and conclusion.
3. **Mechanism and activation:** distinguish what works in a forced fixture from
   what activates naturally in the target workload. Zero activation rejects that
   route for this workload unless a concrete source finding justifies a revised
   hypothesis. Forced warmup or changed scheduling does not establish default use.
4. **Focused safety and ordinary cost:** check changed concurrency, lifetime,
   rollback, recovery, or durability risks before relying on the candidate. Measure
   relevant ordinary/fallback and cold/setup overhead; a favorable special case
   cannot hide a common-path regression.
5. **Early public comparison:** after focused safety, use a bounded uninstrumented
   A/B through the real entry. Microbenchmarks answer mechanism questions; profiles
   attribute costs. Neither substitutes for public throughput and latency evidence.
6. **Qualify the viable candidate:** expand risk-relevant validation and complete
   required review, CI, and representative qualification when the public result
   justifies it. A short diagnostic cannot replace a mandatory final gate.

A failed step redirects the idea rather than automatically earning a larger
campaign. A promising public result earns attention to unresolved regressions and
delivery; use unavoidable waits for independent exploration. Prototype success
is not acceptance.

## Use Experiment Waits Productively

A pending experiment is an opportunity to make progress on the next independent
question. Before an intentional wait, choose useful in-scope work and begin it
when safe; do not default to repeated polling or status-only updates.

- Start from the ranked questions and existing profiles/source. Select a different
  cause, an orthogonal mechanism, or an independent control with its own cheap
  discriminator and failure action. Do not assume the pending result is positive.
- Inspect the route, prepare a disposable prototype or fixture, and actually run
  its bounded mechanism/safety check when noncompeting resources are available.
  Independent experiment execution need not wait for the current run to finish.
- Protect the running experiment's pinned source, binary, configuration, fixtures,
  and database. Use isolated outputs and source ownership. Keep dependent promotion
  conditional until the result or required contract is known; label evidence by
  the candidate it actually tested.
- Keep the benchmark host exclusive. Source work against an existing local copy
  and tests on another host can overlap; a separate process, directory, or container
  on the same host does not prove CPU, memory, disk, or network isolation. Queue
  competing builds, tests, profile decoding, and artifact reads/transfers.
- Use the coordinator directly or existing authorized workers within their scope
  and concurrency limits. This loop creates no new delegation, execution, or
  spending authority and requires no additional scheduler or queue artifact.
- Collect the pending result promptly using bounded/event-driven checks. Re-rank
  questions, stop ideas its evidence invalidates, and prioritize the next critical
  action. If no safe useful overlap exists, wait; note the concrete constraint in
  the normal checkpoint rather than inventing work to fill capacity.

## Resolve Uncertainty Without Churn

Use the executing graph's reassessment boundary. Without one, reassess after two
coherent attempts without the named advance. Compare continuing, simplifying, and
replacing the approach; sunk implementation cost does not favor continuing.
An inconclusive result warrants another experiment only when a new discriminator
can resolve a named uncertainty. Do not repeat until results look favorable.

Retain failed attempts. Routine authorized fixture corrections can proceed within
the bounded assignment; preserve the original assertions and distinguish setup
failure from an exercised product failure. If an artifact consumer is faulty,
repair it and replay the unchanged artifact instead of rerunning an expensive
producer. Reuse valid checks and reviews; repeat for changed risks, failures,
source changes affecting their applicability, or required final gates.

## Keep Comparisons And Reporting Useful

Keep workload, operation mix, durability/ACK boundary, maintenance, runtime,
and resource caps equivalent across a pair; bind results to the respective baseline
and candidate source/binary identities. Prebuild outside timing. Use one measurement
owner per host; avoid competing
builds, heavy decoding, or unrelated I/O during timed work. Share trusted build
caches while isolating databases and outputs. Material baseline or physical-sync
service variation calls for a confound check before another algorithm change.

Choose samples for the question in advance and retain all of them. Reserve broad
repeatability campaigns for viable candidates, without shortening required gates.
Report throughput alongside material latency, allocation, residency, maintenance,
and per-operation tradeoffs; a higher mixed rate alone cannot accept a regression.

Keep one concise decision record linked to raw evidence and the owning ticket.
Update it when source, contract, verdict, or next consequential action changes;
batch routine status maintenance rather than duplicating reports and inventories.
Lead updates with paired public numbers, accepted/rejected/inconclusive outcomes,
tradeoffs, the remaining bottleneck, and the next discriminator. Say "no new accepted
improvement" when that is the result. A useful rejection advances the investigation;
it does not complete an unmet parent goal.
