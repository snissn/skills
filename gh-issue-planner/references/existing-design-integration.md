# Existing Design And Integration Review

Use this review during documentation/code preflight for standalone features and
graph design. Complete it before selecting implementation slices or edges. Inspect
the affected architecture deeply enough to choose a sound integration point; bound
the search to the outcome and adjacent seams that could materially change the
design. Keep findings in the existing preflight and owning tickets.

## Recover The Existing Design

- Read canonical architecture and contracts, accepted design decisions, relevant
  issue discussions, and the history explaining consequential implementation
  choices. Follow their references to the current sources at the intended base.
  Distinguish accepted design, shipped behavior, experiments, and proposals.
- Trace the real caller through validation, selection/dispatch, shared primitives,
  state changes, result ownership, and fallback/error handling. Inspect lifecycle,
  cancellation, concurrency, persistence/recovery, and resource limits where
  relevant. Read representative consumers and tests so an apparent helper is
  understood in its actual contract.
- Search for other implementations of the same responsibility, including mature
  optimized paths, prior attempts, and adjacent modules. Identify why alternatives
  coexist and whether those reasons still apply. Follow enough callers to expose
  coupling and integration costs; a filename match or interface signature alone
  is insufficient.
- Bind findings to source paths/symbols, base SHA, contract sections, and existing
  correctness/performance evidence. Resolve material discrepancies or retain them
  as explicit uncertainties. Missing context calls for source recovery or a bounded
  inquiry before dependent design becomes implementation-ready.

## Coordinate With Landed And Ongoing Work

Inspect relevant live issues, PRs and their material comments/reviews, branches,
and repository coordination records. Record owners, current state/head, affected
paths, exposed contracts, and accepted or frozen boundaries. A local branch or
old issue snapshot alone does not establish current ownership or availability.

For each consequential overlap, decide whether to consume landed work, extend an
existing issue, depend on an in-flight contract, sequence overlapping edits, keep
lanes disjoint, or defer an incompatible proposal. Put that decision and its source
in the graph or owning issue. Reuse the issue that already owns the outcome when
its scope fits; preserve useful history and map remaining obligations when narrowing
or superseding it.

An in-flight implementation is a proposed dependency until its required acceptance
or merge gate passes. Name the exact contract the feature will consume, the owner
and readiness gate, and what happens if it changes. Provisional design may proceed
within repo policy. Do not silently duplicate unfinished work, assign another
writer to owned paths, take over a lane, or import a paused scientific mechanism.
Coordination must preserve existing work and its authority boundaries.

Use existing repository records for the coordination plan. Any needed owner
decision or handoff must be explicit; planning does not authorize contacting
others, editing their work, or changing live coordination state. Apply issue
changes only within the requested operating mode. Recheck relevant overlap and
contracts at implementation start and after changes that affect the chosen seam.

## Select The Strongest Suitable Seam

Compare credible existing candidates before choosing a new implementation. Judge
strength for the feature's actual semantics and workload:

- **Contract fit:** supported behavior, correctness, ownership, security,
  concurrency, failure handling, and compatibility requirements.
- **Maturity and robustness:** actual production consumers, tested invariants,
  recovery/edge-case coverage, maintained documentation, and clear ownership.
- **Performance:** representative public-path measurements, algorithmic scaling,
  allocations/copies, memory retention, and I/O or scheduling costs as applicable.
- **Integration and reuse:** reusable code and representations, affected callers,
  dependency direction, and the changes needed for a coherent shared contract.

Prefer the most developed, robust, performant seam that satisfies the required
contract. Code size, recency, an attractive abstraction, or an isolated benchmark
does not establish superiority. A fast path must preserve the declared semantics;
an unsupported internal shortcut can invalidate both robustness and the measurement.
Label missing or incomparable evidence honestly and assign a bounded decision gate
only when the uncertainty could change the choice.

For a consequential choice, use a compact comparison such as:

| Candidate and source | Consumers and contract fit | Robustness evidence | Performance evidence or gap | Reuse and required change | Decision and reason |
| --- | --- | --- | --- | --- | --- |
| Existing seam at base SHA | Relevant callers and constraints | Tests and lifecycle guarantees | Comparable workload or explicit unknown | Symbols/representations reused or revised | Select, extend, consolidate, or reject |

A short source-linked rationale suffices when one seam clearly fits. Do not invent
alternatives or measurements to fill a table.

Name the functions, types, formats, buffers, validation, persistence, scheduling,
and test/benchmark infrastructure to reuse where applicable. Reuse the actual
maintained implementation through a sound interface. Copying its logic into a new
module leaves two implementations to maintain. Require a concrete contract or
measured reason for new layers, conversions, parallel representations, sidecars,
or separate fast paths, and identify the shared primitives they still consume.
Maximize reuse while preserving dependency direction and ownership guarantees.

## Evaluate Seam Redesign With The Feature

Compare direct extension with consolidating or redesigning the affected seam.
Prefer those shared approaches when they satisfy the full outcome and guardrails.
A separate implementation needs a concrete requirement or evidence that an
appropriate shared seam cannot safely or efficiently meet the outcome. Strongly
favor a coherent redesign when repeated wrappers,
duplicated validation, incompatible data representations, lifecycle ownership,
legacy dispatch, or caller-specific exceptions would otherwise make integration
fragile or expensive. Include substantive API/data-flow changes when warranted;
cleanup should improve how the feature and existing consumers share the design.

Describe the resulting common contract, reused primitives, consumers to migrate,
obsolete paths/options to retire, and any compatibility transition required by
repo policy. Trace callers before removing a path. Protect affected existing
consumers as well as the new feature with relevant characterization, contract,
integration, lifecycle, and performance evidence. The shared public route must
exercise the resulting implementation.

Keep necessary redesign, caller migration, and cleanup in the feature's completion
packet, normally the same PR. A larger coherent refactor can be the simplest
maintainable solution. Split it only for an independently necessary outcome or
ownership boundary, with explicit consumed contracts and dependency gates. Do not
leave required integration cleanup to optional polish. Unrelated cleanup stays
outside the critical path. If keeping the current seam is
best, record the reason and proceed; there is no mandatory rewrite or deletion quota.

## Carry The Decision Into Executable Issues

The preflight and owning implementation packet must preserve:

- the selected seam, source identity, rationale, and consequential rejected options;
- the code to reuse and bounded edits/redesign, including existing consumer migration;
- the resulting public call path, selection/fallback behavior, and integration proof;
- related issues/PRs, owners, overlapping paths, consumed contracts, and readiness gates;
- correctness and performance guardrails for existing and feature-enabled behavior,
  affected documentation, and remaining decision-relevant evidence gaps.

Keep a shared architecture decision in the parent and put node-specific contracts
and edits in each child. A standalone issue carries the same relevant information
concisely without acquiring a graph or an extra audit artifact. An executor should
be able to start without repeating architecture discovery, while still checking
that its assigned base, contracts, and ownership match the plan.
