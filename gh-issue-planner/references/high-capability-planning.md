# High-Capability Planning Advisory Pass

Use this reference only when the user requests Astra or another high-capability
planning advisor, or when a compact architecture pass is likely to remove
substantial implementation ambiguity. It supplements the ordinary preflight; it
does not authorize GitHub writes, code changes, extra agents, or a larger graph.

## Bounded Context Packet

The coordinator first supplies:

- the requested product outcome, explicit seams, non-goals, and operating mode;
- repository, intended base SHA, applicable `AGENTS.md` and contribution rules;
- canonical contract/guide sections and the observed production entry points;
- relevant current source, tests, benchmarks, and known optimized primitives;
- live candidate/overlapping issues with provisional dispositions; and
- the advisor's read-only boundary and one-synthesis-turn budget.

The advisor may inspect narrowly adjacent source or live issue state needed to
resolve the design. It must not edit code, write GitHub state, run an open-ended
benchmark campaign, or invent results. If source evidence cannot settle a choice,
name the uncertainty and put a bounded decision gate in the graph only when that
choice genuinely blocks implementation.

## Required Synthesis

Return one integrated proposal, not a stream of incremental observations:

1. **Planning thesis:** the smallest coherent graph, why each node boundary is
   independently reviewable, and which apparently separate seams should share a
   node because they have one contract or ownership surface.
2. **Fact boundary:** distinguish verified current behavior, inference, and open
   questions. Cite the base SHA and relevant paths/symbols.
3. **Graph:** node roles, directional dependencies, final evidence owner,
   existing-issue dispositions, and conflict-prone files that justify sequencing.
4. **Implementation blueprint for every executable node:**
   - externally visible behavior, invariants, non-goals, and failure semantics;
   - public entry point -> validation/selection -> optimized primitive -> result
     ownership/fetch call path, including fallback callers;
   - an edit map naming files, symbols, and the responsibility of each edit;
   - concise pseudocode for the consequential control/data-flow changes, API or
     schema fields, and validation rules—not a speculative full patch;
   - existing helpers and formats to reuse, plus duplicate paths or client-side
     workarounds that must not be introduced;
   - named test files/cases, fixtures, assertions, and the expected initial
     failure; include mutation, fallback, reopen, race, or path-selection proof
     only where the risk requires it;
   - performance class, measurement boundary, existing focused harness/command,
     path counters, allocation/copy risks, guardrails, and failure action;
   - contract, guide, example, and generated-source updates owned by the node;
   - dependencies, acceptance evidence, and implementation-order notes.
5. **Integration review:** cross-node API consistency, wire/SDK compatibility,
   ordering, likely merge conflicts, and the cheapest end-to-end proof.

Use tables for repeated file/symbol mappings. Put pseudocode only where it fixes
a design decision. Refer to shared policy once rather than copying generic PR/CI
boilerplate into every node.

## Mandatory Self-Critique And Revision

Before returning, attack the draft for:

- ticket explosion or nodes that do not own an independently useful outcome;
- a new sidecar, representation, route, harness, or client-side fusion when an
  existing production seam should be extended;
- missing public callers, fallback/error behavior, ownership/lifetime rules, or
  documentation and generated artifacts;
- tests that prove helpers but not public path selection or fail-closed behavior;
- performance claims without equivalent semantics, allocation accounting, or a
  bounded existing harness;
- speculative file/symbol names, hidden protocol/format changes, and assumptions
  that should instead be stated explicitly; and
- dependencies based on thematic similarity rather than an actual blocker or
  conflict-prone ownership surface.

Revise the proposal to resolve substantive findings. Return the corrected graph
and a short list of residual uncertainties; do not append an unreconciled review.

## Coordinator Verification And Readiness Gate

The coordinator remains responsible for live issue checks and all mutations.
Before drafting or applying issues, verify representative source paths/symbols,
existing-issue dispositions, and dependency claims at the intended base.

An issue is implementation-ready when a capable executor can begin with the
named red test and edit map without repeating architecture discovery. The
executor must still revalidate the assigned head and may adjust local mechanics;
the blueprint is a reviewed design aid, not proof that unimplemented pseudocode
compiles. Remove unsupported detail rather than making it falsely precise.
