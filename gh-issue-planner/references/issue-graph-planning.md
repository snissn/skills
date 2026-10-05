# GitHub Issue Graph Planning

Use this reference for umbrella trackers, dependency graphs, tracker migrations, supersession work, or requests to decide whether existing issues should be reused.

## Contents

- [Operating modes](#operating-modes)
- [Graph preflight](#graph-preflight)
- [Reuse versus net-new](#reuse-versus-net-new)
- [Node roles and gate ownership](#node-roles-and-gate-ownership)
- [Gate classification](#gate-classification)
- [Dependencies and conditional branches](#dependencies-and-conditional-branches)
- [Existing-issue dispositions](#existing-issue-dispositions)
- [Revising during execution](#revising-during-execution)
- [Apply sequence](#apply-sequence)
- [Maintenance](#maintenance)

## Operating Modes

Stay within the user's requested mode:

| Mode | Output | GitHub writes |
| --- | --- | --- |
| Inspect/review | live-state findings and recommendations | none |
| Graph sketch | proposed hierarchy, edges, roles, gates, and dispositions | none |
| Local draft | reviewable parent and child bodies or body files | none |
| Apply | created or edited issues plus verified links | directly authorized writes or necessary maintenance within authorized execution |

Do not infer apply authorization from a request to plan, synthesize, model, sketch, or review.
An executor may carry existing execution authorization into this skill for
necessary graph maintenance; preserve any narrower user restrictions.

## Graph Preflight

Complete SKILL.md's documentation/code preflight before selecting nodes or
edges. Then produce a compact graph preflight with:

1. The product outcome and final evidence owner.
2. A small hierarchy or dependency diagram.
3. A node ledger.
4. Existing-issue dispositions.
5. Gate classifications and ownership.
6. Conditional branches and their activation evidence.
7. Adjacent in-flight work and frozen boundaries.
8. The acceptance evidence and performance-relevance class for every executable
   node, including the test-first seam for implementation packets.
9. Canonical docs read at the intended base, the optimized production path to
   reuse, and doc/code conflicts or evidence gaps that affect sequencing.
10. Each performance-sensitive feature's allocation audit/budget and path proof,
    plus the owning node for affected documentation updates.

Use a ledger like this:

| Node | Role | Existing/new | Depends on | Blocks | Authoritative gate | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| umbrella | sequencing and acceptance | new | none | final gate | overall outcome | create |
| substrate | executable implementation | new | baseline | integration | substrate exit gate | create |
| legacy query issue | evidence/history | existing | none | none until reactivated | residual query gate | retain or narrow |

Keep the preflight approximate when the user requests a sketch. Do not fill it with issue-body boilerplate.

Every implementation packet should name the first behavior or invariant its PR
must drive from red to green, or an explicit allowed exception. Non-PR packets
name the evidence that accepts their assigned output. Classify each node as not
performance-relevant, possibly performance-relevant, performance-sensitive, or
performance-objective so benchmark requirements are deliberate rather than copied
uniformly across the graph.

Each executable node names its deliverable, target location, evidence, and acceptance
owner under SKILL.md's completion-packet rules. Implementation packets own production
callers/fallback, code, tests, docs, and performance evidence; an inquiry may instead
deliver an accepted decision or verified ticket revision. Record what completes that
packet without implying the parent outcome is achieved. Treat implementation phases
as one packet, not separate PRs or review cycles.

Apply SKILL.md's proportional reassessment guidance. For uncertain work, identify
the assumptions and meaningful decision boundaries; keep strategic review with
the parent rather than adding a ceremony to every child.

## Reuse Versus Net-New

Reuse an existing tracker when:

- its title, goal, metrics, and completion criteria still match the intended work;
- its history remains useful to implementers rather than obscuring the new plan;
- its dependency position is still correct; and
- updating it would not silently change an accepted decision or claim old evidence proves a new architecture.

Prefer a net-new execution graph when:

- the work changes from local optimization to a new substrate or architecture;
- existing titles or gates conflict with current accepted scope;
- historical experiments dominate the body and make ownership ambiguous;
- new dependency edges or final-gate ownership materially differ; or
- adjacent correctness or durability work requires a cleaner boundary.

The common default is hybrid:

- preserve existing issues as evidence, acceptance, or residual-work anchors;
- create a clean net-new implementation graph;
- add concise bidirectional links and dispositions; and
- close old issues only when their remaining scope is fully mapped or explicitly accepted as no longer required.

## Node Roles And Gate Ownership

Use only roles the work actually needs:

- **Umbrella:** owns sequencing, scope boundaries, and final acceptance.
- **Experiment/decision gate:** distinguishes implementation lanes; it does not claim the product outcome.
- **Substrate:** owns a reusable implementation seam.
- **Integration:** proves the substrate through production paths.
- **Residual optimization:** owns measured work left after shared architecture lands.
- **Evidence/final gate:** reruns the agreed representative matrix and owns the final claim.
- **Evidence/history anchor:** preserves prior experiments or benchmark attribution without blocking the new graph by default.

Roles describe purpose; deliverables describe outputs. An experiment can deliver a
report plus ticket revisions without a PR. Name one primary deliverable and include
required supporting outputs in its acceptance; use separate nodes only for separately
owned gates. A ticket revision must identify changed scope/edges, evidence, affected
owners, and remaining obligations, then verify the live result.

Assign every completion gate exactly one authoritative issue. Other issues may contribute evidence but must link to the owner rather than restating the same closure criterion.
Before execution, narrow or supersede any overlapping executable issue whose
scope or completion gate is already owned elsewhere.

## Gate Classification

Classify every reported metric explicitly:

| Class | Meaning | Closure behavior |
| --- | --- | --- |
| North-star | final product/performance outcome | blocks umbrella completion |
| Milestone exit | proves one executable slice achieved its purpose | blocks dependent nodes |
| Guardrail | limits regressions outside the optimization target | blocks only when its boundary is breached |
| Observational | reported for diagnosis or future planning | never blocks by itself |
| Accepted gap | measured shortfall explicitly accepted for this graph | does not block; revisit only on its trigger |

For an accepted gap, record:

- current value and units;
- baseline commit, artifact, date, and environment when available;
- who accepted it or the durable decision source;
- whether it remains a guardrail or is purely observational; and
- a concrete revisit trigger, such as a final-format milestone, material regression, scale change, or user reprioritization.

Do not create an optimization child solely because a metric is measurable. Acceptance of the current value is not permission for accidental unbounded regression; use a guardrail if that matters.

## Dependencies And Conditional Branches

- Draw only real blocking edges. A related issue is not automatically a dependency.
- Label decision/output dependencies separately from merge dependencies. Accepted
  non-PR outputs satisfy their own edges; product dependencies still require merged
  predecessor PRs. Preserve repository/scientific authority rules.
- Prefer an acyclic execution graph with one clearly identified final gate.
- Put measurement or contract work before irreversible format or architecture choices when evidence can select the path.
- A conditional child must state its eligibility evidence and failure action. Scientific successors also require owner direction/assignment and merged predecessor authority; evidence alone never activates them.
- Keep inactive conditional children out of the critical path.
- If evidence changes the graph, update the parent ledger and affected child bodies rather than continuing a stale plan.
- Avoid ticket explosion. A child should own a coherent, independently reviewable slice, not every function or anticipated PR.

For exploratory work, fully specify only the next useful inquiry and justified
implementation. Keep other mechanisms as conditional hypotheses in the parent until
selection requires a child. At meaningful evidence boundaries, revise the remaining
graph rather than executing a speculative implementation simply because it was listed.

## Existing-Issue Dispositions

Use one explicit disposition per existing issue:

- **Retain:** scope and gate remain active as written.
- **Narrow:** preserve the issue but remove or accept obsolete scope; record the new boundary.
- **Supersede:** a new issue owns future execution; retain the old issue as history with bidirectional links.
- **Close:** no required scope remains and durable evidence or acceptance supports closure.
- **Defer:** intentionally outside the active graph; record the revisit trigger.

Do not erase experiment history merely to make a body look clean. Prefer an authoritative current-state block or concise disposition comment. Do not close an issue as superseded until its remaining obligations are mapped to a live owner or explicitly accepted as no longer required.

## Revising During Execution

Within authorized execution, the coordinator may reorder, narrow, supersede,
create or explicitly adopt necessary nodes, and change their edges. Replace the
remaining graph when its structure misleads execution; reuse the dispositions
and reuse-versus-net-new rules above. Map new/adopted nodes to the parent outcome
before assigning work. Apply the same completion, ownership, and evidence rules
to replacements.

Preserve the agreed goal, acceptance criteria, guardrails, merged work, useful
in-flight work, experiment history, and unrelated owners' scope. Map each
remaining obligation to a live owner before retiring a node. Linking a follow-up
does not satisfy an unmet parent goal. Record a concise revision in the parent:
finding and evidence, affected nodes/edges, the revised plan, and preserved gates.

Replanning does not authorize a new goal/repository, weaker thresholds,
reopening accepted gaps without their revisit trigger or new direction, or
evading an explicit hard review cap through replacement issues/PRs. Scientific
successors still require their own owner direction/assignment and merged
predecessor authority; issue edits cannot generate scientific/governance authority.
Ask only for decisions outside existing authorization; continue independent
authorized work meanwhile. In read-only/planning modes, propose these revisions
without applying them.

## Apply Sequence

When GitHub writes are authorized directly or through execution scope:

1. Prepare and review parent and child bodies locally.
2. Create or update the parent with a temporary graph ledger if child URLs do not exist yet.
3. Create children with the parent URL, role, dependencies, and exit gate in each body.
4. Backfill the parent ledger with child URLs and exact edges.
5. Add concise disposition comments and reciprocal links to affected existing issues.
6. Verify titles, labels, states, links, and bodies from live GitHub.
7. Report the resulting graph, writes performed, accepted gaps, conditional nodes, and unresolved decisions.

Use quoted body files or safely replaced placeholders. Never rely on shell interpolation for Markdown containing backticks or dollar signs.

## Maintenance

- Keep the parent graph ledger authoritative for current node state and edges.
- Keep detailed implementation evidence in the owning child; summarize only decision-relevant results in the parent.
- After a merge, update the child first, then the parent ledger and any newly unblocked successors.
- When a gate moves, record the evidence and why the graph changed.
- Keep latest-head evidence distinct from historical baselines.
- When implementation changes a contract, optimized route, or usage recommendation,
  update its owning docs and affected child assumptions. Contract docs needed by
  descendants must land with their predecessor or as an explicit prerequisite.
- Do not let closed, stale, or merely related issues remain implicit blockers.

Before handoff, verify that the graph has one final evidence owner, every blocking edge is explicit, each existing issue has a disposition, accepted gaps are non-blocking, and no GitHub write exceeded the requested mode.
