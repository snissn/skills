---
name: scientific-mainline-workflow
description: Execute and govern theorem, model-integration, physics, manuscript-claim, or other scientific repository work by committing and pushing directly to main without PR or code-review churn when that workflow is authorized. Use for mutable pre-freeze construction, independent adversarial review bound to exact candidate bytes, local exact or quantitative validation, frozen scientific executions, scoped dispositions and inference, GitHub issue-graph progression, and strict separation of execution-only engineering defects from scientific results.
---

# Scientific Mainline Workflow

## Purpose

Apply this workflow to scientific repository work whose primary artifact is one
or more of:

- a theorem, obstruction, provider, model, or architecture definition;
- an exact or quantitatively controlled proof packet;
- a scientific validator or decision runner;
- an adversarial scientific review;
- a durable disposition in a dependency-tracked research program;
- a manuscript or synthesis change that alters a maintained scientific claim.

Do not use it to bypass a repository's required PR policy, to merge ordinary
software changes without review, or to treat prose assertions as proofs.

When this workflow is authorized, do not open a PR merely as a staging surface
and do not wait for code-centric automated review. Obtain the scientific review
and validation locally, then integrate the accepted artifact directly onto
synchronized `main`.

## Non-Goals

Do not use this workflow to replace theorem review with CI volume or PR
ceremony, treat implementation defects as scientific evidence, restate frozen
scope in governance packets, deepen a narrow certificate past the active exit
gate, or import analogous/deprecated work as authority rather than idea input.

## Core Operating Rule

Apply this discipline:

> Construct mutably. Review independently. Repair before freeze. Validate
> locally. Commit one coherent result directly to synchronized `main`.
> Execute a frozen decision only when a substantive scientific comparator
> requires it. Report engineering status, execution validity, protocol
> verdict, and scientific inference separately.

Direct-to-main removes PR ceremony, not scientific scrutiny.

Treat the reviewed scientific disposition—not a PR and not an arbitrary
intermediate commit—as the unit of integration. The direct-main commit records
an already reviewed result; it must not be the first durable surface on which
the candidate becomes inspectable.

For execution-bearing work, apply the companion rule:

> Freeze the science once. Keep execution software mutable until it is
> qualified. Debug ordinary code normally. Start the scientific trial only
> when the first real comparator starts under the frozen qualified runner.

Software qualification is not architecture governance. A serializer, schema,
atomic-write, CLI, logging, exception-handling, or deterministic-orchestration
repair does not create a new scientific candidate when a focused semantic diff
shows that no scientific input, value, comparator, tolerance, decision rule, or
inference changed.

Use the smallest honest commit cadence:

- an analytic theorem or integration result normally needs one reviewed result
  commit;
- an execution-bearing result normally needs one reviewed freeze commit and one
  later result/disposition commit;
- execution-only repairs may use ordinary engineering commits, but they must
  remain visibly separate from scientific definitions and outcomes;
- do not manufacture authorization, inspection, or review-of-review commits.

Use the governing GitHub issue and maintained repository artifacts as the
durable coordination surface. A PR is not required to make internal review
visible: bind the review to exact candidate bytes, record the disposition in
the issue or a maintained review artifact, and integrate the accepted result
directly. Do not replace a missing scientific audit with a code-centric PR
review, and do not add both unless repository policy independently requires
the PR.

## Inputs Needed

Before acting, establish the repository and current `main`, local instructions,
goal and dependency graph, frozen inputs and claim boundaries, active issue exit
rules, analytic-versus-execution classification, direct-main authority, any
protected live execution, intended path set, reviewer ownership, and local
acceptance checks.

If direct-main authority or a protected scientific scope boundary is unclear,
ask before committing. Ordinary technical choices inside an authorized
scientific identity do not require repeated approval.

See [the status taxonomy](references/execution-status-taxonomy.md) for the
required execution/disposition separation.

## Critical-Path Discipline

Before constructing, name the single load-bearing scientific question and
classify surrounding work as:

- a prerequisite that blocks the active exit gate;
- an independent control or audit that may proceed in parallel;
- nonblocking strengthening or exposition;
- a deferred provider, calibration, or deeper-theory question.

Select the smallest theorem, construction, or scoped obstruction that honestly
satisfies the active exit gate. Prefer analytic structure, symmetry, exact
reduction, or proof compression over brute-force certification when they prove
the same predicate without weakening it. Stop deepening the artifact once the
declared gate is met. Do not let desirable local polish displace an authorized
breadth-first program unless a dependency theorem makes that polish
load-bearing.

## Roles And Delegation

When delegation is authorized, use one bounded layer:

1. a constructor owns the mutable scientific artifact;
2. an independent reviewer attacks the construction;
3. a validation engineer is separate when substantive code or execution is
   involved;
4. the primary agent integrates the result and owns the final disposition.

The constructor must not be the sole reviewer of its own theorem. Subagents do
not decide the program disposition or recursively delegate unless explicitly
authorized.

Bind review to evidence rather than conversation state: give the reviewer the
exact base, changed paths, candidate artifacts, frozen inputs, acceptance
predicates, evidence standard, stop rule, and forbidden changes. The reviewer
must inspect the actual artifact and return a disposition bound to its identity;
a review of an earlier draft does not authorize a later scientific edit.

Use an adversarial design review while the draft is mutable and, when the result
is load-bearing, a final exact-candidate acceptance after validation. Review may
occur against an isolated worktree or manifest and does not need a PR. Do not
add a reviewer merely to review another review unless a concrete scientific
disagreement remains. Use [candidate review
binding](references/candidate-review-binding.md) for the exact-byte contract and
manifest tool. Treat subagent reports as evidence to integrate, not decisions
to concatenate.

## Workflow

### 1. Refresh and orient

1. Sync or fetch the real repository state and verify current `main`.
2. Inspect dirty paths, worktrees, running processes, and active artifacts.
3. Read the active issue, parent tracker, recent steering comments, frozen
   definitions, ledgers, validators, reviews, and claim boundaries.
4. Build the smallest dependency map needed for the active question.
5. Preserve unrelated user work and use an isolated worktree when appropriate.
6. Identify the load-bearing question, blockers, parallel controls, polish, and
   deferred extensions before assigning work.

During every planning round between substantive commits, refresh relevant
GitHub issues for steering notes. If a steering note is applied, leave a
thorough response and close only a steering-only issue whose requested action
is complete. Do not close active scientific issues merely because they were
read.

Treat a live frozen execution as protected state. Unless its disposition is
explicitly in scope, do not signal it, rewrite its sources or artifact, import
its modules from competing processes, or launch heavy work that materially
contends for its resources. Read-only telemetry and separately labelled,
non-decisive profiling are acceptable only when they cannot alter the live
trial.

### 2. Classify the work

Classify the proposed change as exactly one of:

- **Scientific definition:** changes ontology, state space, equations,
  fixtures, controls, predicates, tolerances, decision rules, or inference.
- **Scientific analytic result:** proves a theorem, obstruction, compatibility
  statement, or scoped failure without an outcome-bearing execution.
- **Scientific execution:** runs a frozen substantive comparator set.
- **Execution-only engineering:** changes serialization, atomic persistence,
  CLI behavior, logging, exception handling, deterministic orchestration, or
  report schemas without changing any scientific value or verdict.
- **Exposition:** clarifies maintained claims without changing frozen results.

Do not govern execution-only defects as scientific outcomes. Do not disguise a
scientific change as plumbing.

Apply a proportional gate:

- **Exposition with no claim change:** run source, link, formatting, and
  maintained-claim consistency checks. Use focused review when ambiguity is
  possible; do not manufacture a theorem audit for typography.
- **Execution-only engineering:** require a focused semantic diff,
  representation-invariance tests, exact-type/schema tests, and proof that no
  scientific value or decision surface changed. Do not create a new scientific
  identity.
- **Scientific analytic result:** require adversarial design review, local
  substantive validation, and final independent acceptance bound to the exact
  candidate before one coherent mainline commit.
- **Scientific execution:** review and commit the frozen definition first,
  qualify mutable execution software separately, execute the frozen decision
  once, and commit the durable result or disposition separately.
- **Post-freeze scientific change:** open a new scientific identity or explicit
  addendum; never smuggle the change through an engineering or exposition
  classification.

When classification is disputed, compare the proposed diff against the frozen
scientific identity: ontology, state space, Hamiltonian or evolution law,
fixtures, controls, predicates, tolerances, decision rule, and inference. A
change to any of these is scientific even when implemented in a file named
`runner`, `schema`, or `utility`.

### 3. Construct mutably

Keep equations, interfaces, fixtures, tolerances, code, and prose uncommitted
while the candidate is being designed and reviewed.

The draft must state:

- declared inputs and assumptions;
- exact state-space and type boundaries;
- theorem or decision predicates;
- domains, regularity, and conditioning;
- locality, gauge, symmetry, center, reaction, and conservation obligations;
- complete record or fault alphabet when measurement is involved;
- controls and semantic mutations;
- error terms and observation horizon for approximate claims;
- pass, scoped failure, invalid-execution, and no-go boundaries;
- non-goals and forbidden inferences.

Prefer one coherent artifact set over a ladder of authorization or
review-of-review documents.

Treat artifact mutability explicitly:

- mutable drafts may be rewritten freely before review acceptance and freeze;
- frozen definitions, frozen decision rules, and historical dispositions are
  immutable scientific provenance;
- later interpretation corrections belong in maintained synthesis files,
  addenda, or a new scientific identity;
- ordinary manuscript copy edits may touch a maintained exposition, but may
  not silently change the hypotheses or inference of a frozen theorem.

When the scientific definition becomes stable before its runner does, freeze
the scientific identity once and continue qualifying the execution-only
software as ordinary mutable engineering. Do not create architecture packets
or scientific dispositions for each runner defect. Before the real execution,
bind the final qualified runner hashes and prove by semantic diff and
representative tests that later engineering changes did not alter the frozen
scientific predicates.

### 4. Review adversarially before freeze

The independent reviewer must inspect the actual sources and formulas, not
only the constructor's summary. Review at the theorem's natural level:

- type and ontology consistency;
- exact algebra, signs, normalization, domains, and regularity;
- hidden assumptions, circular definitions, and vacuous domains;
- conditioning, postselection, and preparation dependence;
- locality, gauge invariance, reciprocal reaction, and retained complements;
- compactness versus boundedness;
- exact versus approximate proof type;
- numerical tolerance and floating-point policy;
- claim scope, failure inference, and family-no-go discipline;
- whether fixtures and controls can detect each semantic corruption;
- whether the proposed proof burden is proportional to the scientific claim.

For large generated registries or repeated finite cases, review the physical
or mathematical argument once per genuine template and require an exact
expansion or substitution theorem plus machine validation of every generated
row. Do not replace a missing template theorem with thousands of repetitive
prose checks, and do not treat a large mutation count as independent
mathematical evidence.

Resolve every blocking finding in the mutable draft. Repeat the design review
until no scientific blocker remains; do not freeze a merely promising draft.

The acceptance must identify the reviewed base and artifact set. Any later
change to a scientific definition, theorem statement, formula, source binding,
predicate, tolerance, control, or inference invalidates that acceptance and
requires renewed review. A representation-only or execution-only change may
use a focused semantic review, but it must still establish that the reviewed
scientific values and decision surfaces are unchanged.

Do not let construction and validation share an unexamined source of truth. A
validator that reproduces the builder's hard-coded allowlist, expected table,
sign convention, or formula can agree perfectly with a scientifically false
artifact. Derive expected results independently from frozen source data or
recompute the decisive mathematics by a second route. Treat schema validity,
keyword presence, deterministic byte equality, and builder/audit agreement as
necessary process checks only.

Require load-bearing maps, reactions, inverses, source bindings, and reductions
to be represented as exact formulas or executable symbolic data when the claim
depends on them. Prose such as "the exact inverse is declared" or "the reaction
is retained" is not a mathematical certificate.

Use [the scientific review checklist](references/scientific-review-checklist.md)
for the full audit.

### 5. Validate locally

Run all relevant checks before integration:

- dedicated theorem, ledger, schema, or decision validators;
- inherited dependency validators;
- exact symbolic recomputation or interval checks;
- independent derivation of expected values rather than a duplicate builder
  lookup table;
- representation-invariance tests;
- semantic-sensitivity or mutation tests;
- negative and matched controls;
- serializer round trips for exact scalar types;
- Python compilation or relevant language checks;
- `git diff --check`;
- Markdown math and link checks;
- source-hash and frozen-identity verification;
- changed-path and worktree-scope inspection.

Capture the exact commands, exit statuses, and decisive counts or hashes.
Prefer deterministic validators whose outputs can be reproduced from the
committed sources. A prose statement that checks were run is not equivalent to
validation evidence.

After substantive validation passes, generate the exact candidate manifest and
obtain the independent reviewer's final `ACCEPT` on those bytes and that
evidence. If review or validation causes a scientific edit, regenerate,
revalidate, and renew acceptance.

Every load-bearing predicate needs a mutation that would fail if its meaning
were corrupted. Include omissions, duplications, sign or orientation reversals,
nonpositive bounds, incomplete reactions, invalid support transport, false
dependency expansion, and changed inference boundaries when those predicates
are in scope. Do not accept a mutation suite that only perturbs serialization
or builder bytes.

Never use exact floating-point equality for a derived real result unless bit
identity is the theorem. Prefer exact arithmetic, symbolic identities, interval
enclosures, analytic bounds, or prospectively justified tolerances.

Validation counts are process evidence, not a substitute for theorem strength.

If the work is analytic only, do not build a ritual runner. If the work is
execution-bearing, qualify the runner with synthetic and semantic tests before
the scientific trial. Synthetic, non-decisive, fault-injection, schema,
serializer, persistence, and deterministic smoke tests do not consume the
scientific trial.

### 6. Integrate directly to main

Use direct-to-main only when it is authorized and:

- local `main` is synchronized with the intended remote head;
- the diff contains only the reviewed scientific artifact set;
- independent review is accepted;
- all required local validations pass;
- no active frozen execution is invalidated;
- no unrelated user changes are included.

Treat these as hard integration gates. If any gate is missing, keep the
candidate mutable and do not create a placeholder mainline commit.

Commit one coherent analytic result, or the smallest freeze/result pair needed
for a genuine execution. Avoid separate commits that merely authorize
implementation, restate unchanged scope, or review a review.

Immediately before integration, fetch the remote and compare the reviewed base
with current `main`. If `main` moved, integrate the new base, inspect the
resulting diff, and rerun every validation affected by the change. Do not push
a stale-base or non-fast-forward scientific commit merely because the draft
was already reviewed.

If the moved base overlaps a frozen input, source hash, theorem dependency, or
reviewed artifact, the earlier `ACCEPT` is no longer sufficient: refresh the
dependency audit and obtain renewed review. If the movement is provably
unrelated, transplant only the reviewed files and rerun the affected local
gates.

When construction occurred in an isolated worktree, transfer only the reviewed
artifact set onto synchronized `main`; do not merge unrelated worktree history
or temporary execution artifacts.

Push normally. Verify the remote head after the push. Never force-push,
destructively reset, or overwrite unrelated work.

See [the direct-mainline checklist](references/direct-mainline-checklist.md).

### 7. Execute only when scientifically necessary

An analytic theorem, obstruction, or compatibility decision does not need a
ritual runner.

When a substantive scientific execution is required:

1. commit the reviewed definition, decision code, and review record as the
   freeze commit;
2. inspect and record the committed hashes without running the decision;
3. engineering-qualify the runner with synthetic non-scientific tests,
   including comparator-atomic persistence and fault injection before, during,
   and after comparators;
4. execute the frozen comparator set once;
5. persist each completed comparator atomically;
6. preserve partial evidence and crash provenance;
7. never retune the frozen identity after seeing a result.

Every decision report must separate:

- `engineering_status`;
- `execution_validity`;
- `protocol_verdict`;
- `scientific_inference`.

An implementation defect yields
`ENGINEERING DEFECT — NO SCIENTIFIC VERDICT`, not a failed realization. A
pre-comparator defect consumes no scientific trial. The trial begins when the
first real comparator starts. A crash after that point consumes a partial
trial, even if the in-progress comparator never persisted; the scientific
evidence consists only of comparator rows that completed and were durably
written. Calling the overall execution invalid does not erase those rows or
restore an unused trial.

Correcting an execution-only defect is ordinary engineering work, but the fix
does not by itself authorize a replay. Follow the frozen protocol's prospective
replay rule or obtain explicit replay authorization. Never rerun merely to
improve a scientific outcome.

### 8. Close the issue and progress the graph

After a valid analytic or executed disposition:

1. push the reviewed commit;
2. comment on the issue with the exact commit, reviewed base and artifact set,
   independent disposition, validation commands and outcomes, scientific
   disposition, inference boundary, and surviving obligations;
3. close the issue only when its exit or stop rule is satisfied;
4. refresh the parent tracker and all newly relevant issues;
5. repair dependency edges if the result exposed a real prerequisite;
6. select the highest-priority newly unblocked issue.

A failed selected realization is not a family no-go. Perform one bounded
architecture review and open a new scientific identity only when the repair
changes a load-bearing scientific choice. Do not reopen frozen dependencies
without a demonstrated contradiction.

The normal cadence is:

1. close the current issue only when its exit rule is actually satisfied;
2. spend a turn refreshing the parent graph and newly relevant issues;
3. repair graph edges if the new result exposed a real dependency;
4. choose the highest-priority newly unblocked issue;
5. repeat without reopening settled scope.

## Failure Handling

Stop and request a user-level decision only when work would change a protected
boundary such as:

- the frozen substrate or theorem identity;
- the program north star;
- actuality or ontology;
- protected preparation or measurement independence;
- a declared stage pass burden;
- a finite versus relativistic endpoint;
- a family-level closure rule.

Handle these without escalation:

- ordinary mathematical iteration before freeze;
- execution-only defects;
- serializer and exact-type support;
- proof-method changes;
- stronger equivalent lemmas;
- candidate replacement before freeze;
- scoped selected-realization failures;
- issue-graph repairs that preserve the authorized program.

If a candidate fails, preserve positive lemmas and exact obstructions. State
whether the failure is selected-provider, selected-realization, class-level,
or execution-invalid. Never use `KILL FAMILY` without a theorem covering the
declared class.

## Anti-Churn Rules

- Do not create a PR merely to obtain code-centric review of theorem work.
- Do not wait for automated code review after scientific review and local gates
  cover the artifact, or split direct-main work into PR-ready/merge-ready phases.
- Do not create authorization packets for obvious implementation or governance
  commits for ordinary runner qualification defects.
- Do not freeze drafts before adversarial review is complete.
- Do not build an execution harness for paperwork-only predicates.
- Do not count review/mutation volume as scientific depth.
- Do not deepen a narrow certificate past a breadth-first program gate.
- Use deprecated or analogous work as idea input, not authority.
- Do not let downstream failures retroactively weaken frozen results.

## Final Report Format

Use [report templates](references/report-templates.md) for the scoped
disposition, artifacts, commit, review and validation evidence, graph handoff,
surviving obligations, and execution status.
