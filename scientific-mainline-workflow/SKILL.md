---
name: scientific-mainline-workflow
description: Execute and govern theorem, model-integration, physics, manuscript-claim, or other scientific repository work using pushed issue-scoped feature branches for mutable pre-freeze construction and reviewed freeze integration to main without PR churn when authorized. Use for durable scientific iteration, exact-candidate adversarial review, local validation, frozen executions, scoped dispositions and inference, issue-graph progression, and strict separation of engineering defects from scientific results.
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

When this workflow is authorized, use a dedicated feature branch as the durable
mutable staging surface; do not open a PR merely for code-centric review.
Commit and push coherent non-decisive pre-freeze work there, obtain scientific
review and validation, then integrate only the accepted frozen artifact onto
synchronized `main`. When a packet or script will emit a pass/fail scientific
decision, keep its decision-bearing definition, predicates, tolerances,
comparator code, fixtures, and source bindings uncommitted until adversarial
review accepts those exact mutable bytes. Their first commit is the joint freeze
commit containing the reviewed definition, decision code, and review record.

## Non-Goals

Do not use this workflow to replace theorem review with CI volume or PR
ceremony, treat implementation defects as scientific evidence, restate frozen
scope in governance packets, deepen a narrow certificate past the active exit
gate, or import analogous/deprecated work as authority rather than idea input.

## Core Operating Rule

Apply this discipline:

> Construct mutably on a dedicated feature branch. Commit and push coherent
> non-decisive iterations as non-authoritative provenance. Review exact candidate
> bytes. For a decision-bearing candidate, review the uncommitted definition and
> decision code and make their first commit the joint freeze commit. Repair
> before freeze. Validate locally. Integrate only the reviewed freeze onto
> synchronized `main`. Execute a frozen decision only when a substantive
> comparator requires it. Report engineering status, execution validity,
> protocol verdict, and scientific inference separately.

Direct-to-main removes PR ceremony, not scientific scrutiny.

Treat commits, freeze, and authority as distinct:

- a pushed mutable-branch commit is durable development provenance;
- a reviewed freeze commit binds the scientific identity;
- mainline integration and a reviewed tag confer checkpoint authority; and
- a qualified frozen execution may produce a protocol verdict.

The reviewed scientific disposition—not a PR and not an arbitrary intermediate
commit—is the unit of mainline integration. The feature branch must be the
first durable surface on which the candidate becomes inspectable.

For execution-bearing work, apply the companion rule:

> Freeze the science once. Keep execution software mutable until it is
> qualified. Debug ordinary code normally. Start the scientific trial only
> when the first real comparator starts under the frozen qualified runner.

Software qualification is not architecture governance. A serializer, schema,
atomic-write, CLI, logging, exception-handling, or deterministic-orchestration
repair does not create a new scientific candidate when a focused semantic diff
shows that no scientific input, value, comparator, tolerance, decision rule, or
inference changed.

Use the smallest honest cadence at each layer:

- on the mutable feature branch, commit and push every coherent derivation,
  analytic note, audit, source inventory, or non-decisive utility;
- keep files that define a pass/fail scientific decision uncommitted until their
  exact mutable bytes pass adversarial review, then commit them first in the
  joint freeze commit;
- do not leave source or provenance untracked through a context switch, long
  calculation, review request, or end of session;
- mark pre-freeze artifacts as mutable and non-authoritative with a null
  protocol verdict;
- on `main`, integrate one reviewed analytic freeze/result or the smallest
  freeze/result pair required for a genuine execution; and
- keep execution-only repairs visibly separate from scientific definitions and
  outcomes; do not manufacture authorization or review-of-review commits.

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
rules, analytic-versus-execution classification, feature branch and worktree,
mainline-integration authority, any protected live execution, intended path
set, reviewer ownership, and local acceptance checks.

If direct-main authority or a protected scientific scope boundary is unclear, ask before committing. Ordinary technical choices inside an authorized scientific identity do not require repeated approval.

## Composition And Review Precedence

When this workflow is composed with `github-pr-mergeable`, an issue-graph executor, or an automated reviewer:

- repository-local scientific proportionality and review-stop rules govern review cadence;
- inspect those rules from the scientific worktree or exact candidate head, not only the coordinator checkout;
- use PR tooling for final integration inventory, CI, and thread disposition, not to add an unbounded code-review loop after the scientific gate is satisfied;
- an exact-head Codex clean artifact is required only when effective repository/workstream policy requires it;
- a repair commit does not reset a repository-wide review-round cap.

Absent a repository-specific cap, a non-execution analytic candidate gets one independent review and one batched repair by default. After two finding-bearing candidate heads, stop and reassess the claim, authority, or artifact split before any further review. Continue only for a concrete finding that changes the scientific claim or with explicit project-owner authorization.

See [the status taxonomy](references/execution-status-taxonomy.md) for the
required execution/disposition separation.

## Critical-Path Discipline

Name the single load-bearing question. Separate blockers, parallel controls,
nonblocking strengthening, and deferred extensions. Select the smallest honest
theorem, construction, or obstruction that satisfies the exit gate; prefer
analytic reduction to brute-force certification when it proves the same
predicate. Stop deepening the artifact once the gate is met.

## Roles And Delegation

When delegation is authorized, separate constructor, independent reviewer, and
validation engineer roles; the primary agent owns integration and disposition.
The constructor must not be the sole reviewer. Bind review to the exact base,
candidate byte manifest, path set, frozen inputs, predicates, evidence standard,
stop rule, and forbidden changes. A non-decisive analytic candidate may bind a
pushed commit; a decision-bearing candidate must bind its uncommitted mutable
bytes before their first freeze commit. Use an adversarial mutable-stage review
and final exact-candidate acceptance. See [candidate review
binding](references/candidate-review-binding.md).

## Workflow

### 1. Refresh and orient

1. Sync or fetch the real repository state and verify current `main`.
2. Inspect dirty paths, worktrees, running processes, and active artifacts. Load policy from the actual scientific worktree/candidate head and record its review-round cap.
3. Read the active issue, parent tracker, recent steering comments, frozen definitions, ledgers, validators, reviews, and claim boundaries.
4. Build the smallest dependency map needed for the active question.
5. Keep the main checkout as an integration surface. Create or reuse one
   issue-scoped feature branch and isolated worktree for mutable construction.
6. Preserve unrelated user work; never absorb an existing dirty checkout into
   the candidate branch merely to make status clean.
7. Identify the load-bearing question, blockers, parallel controls, polish, and
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
  candidate before one coherent mainline freeze/result integration. Mutable
  feature-branch commits remain allowed and non-authoritative.
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

Keep equations, interfaces, fixtures, tolerances, code, and prose mutable on the
dedicated feature branch while the candidate is being designed and reviewed.
Commit and push each coherent non-decisive step. Use explicit status fields such
as:

```text
authority: MUTABLE_NONAUTHORITATIVE
engineering_status: DEVELOPMENT
execution_validity: NOT_A_SCIENTIFIC_EXECUTION
protocol_verdict: null
scientific_inference: none
```

These commits preserve work and enable exact review; they do not freeze a
candidate, authorize execution, or establish a scientific result. Generated
matrices, caches, and resumable run products should go to a bound external
scratch directory rather than becoming untracked source-tree debris.

Apply a stricter first-commit rule to decision-bearing artifacts. If a script or
packet can emit a pass/fail scientific decision, draft its scientific identity
uncommitted in the feature worktree: definition, state space, fixtures,
predicates, tolerances, initial boxes, comparators, decision surfaces, runner,
and source bindings. Review and revise those exact working-tree bytes until all
blocking findings close. Their first commit must be the joint freeze commit with
the review record. Ordinary derivations, source inventories, preservation
manifests, and utilities that cannot emit a scientific verdict remain eligible
for incremental commits and pushes.

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

- non-decisive mutable drafts may be revised through ordinary pushed branch
  commits before review acceptance and freeze;
- decision-bearing scientific files remain uncommitted until reviewed and enter
  history first in the joint freeze commit;
- every scientific edit creates a new candidate SHA and supersedes review of
  the prior mutable SHA;
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

Classify each finding before changing the candidate:

- **claim-changing scientific blocker:** fix before freeze and renew review within the review budget;
- **evidence-path engineering blocker:** fix if it can invalidate evidence for the declared claim;
- **claim/authority mismatch:** narrow the claim or emitted authority rather than expanding the validator by default;
- **nonblocking parser hardening, redundant mutation, unsupported-input behavior, or alternate representation:** defer or split once the claimed mathematics and a direct check are covered;
- **incorrect finding:** reject with rationale.

Resolve every blocking finding in the mutable draft. Batch sibling-invariant fixes before renewed review. Repeat only while a scientific blocker remains and the effective repository/PR-lifetime review budget permits it; do not freeze a merely promising draft, but do not deepen a scoped result merely to obtain a quiet automated reviewer.

The acceptance must identify the reviewed base, exact candidate-byte manifest,
and artifact set. For a non-decisive analytic candidate it may also identify a
pushed feature-branch commit. For a decision-bearing candidate it must identify
the uncommitted working-tree manifest that will be reproduced by the first
freeze commit. Any later change to a scientific definition, theorem statement,
formula, source binding, predicate, tolerance, control, or inference invalidates
that acceptance and requires renewed exact-byte review. A representation-only
or execution-only change may use a focused semantic review, but it must still
establish that the reviewed scientific values and decision surfaces are
unchanged.

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
evidence. For a non-decisive analytic candidate, use a clean pushed candidate
commit. For a decision-bearing candidate, use the uncommitted working-tree
bytes; if review or validation causes a scientific edit, revise them without
committing, regenerate the manifest, revalidate, and renew acceptance. Only
after acceptance may those decision-bearing files be committed for the first
time in the joint freeze commit.

Every predicate load-bearing for the **declared scientific claim and authority** needs a mutation that would fail if its meaning were corrupted. This obligation does not extend to unsupported custom inputs, fields outside the claimed authority, or hypothetical future profiles. Prefer narrowing or explicitly rejecting unsupported modes over turning one validator into a universal certifier. Include omissions, duplications, sign or orientation reversals, nonpositive bounds, incomplete reactions, invalid support transport, false dependency expansion, and changed inference boundaries when those predicates are in scope. Do not accept a mutation suite that only perturbs serialization or builder bytes.

Never use exact floating-point equality for a derived real result unless bit
identity is the theorem. Prefer exact arithmetic, symbolic identities, interval
enclosures, analytic bounds, or prospectively justified tolerances.

Validation counts are process evidence, not a substitute for theorem strength.

If the work is analytic only, do not build a ritual runner. If the work is
execution-bearing, qualify the runner with synthetic and semantic tests before
the scientific trial. Synthetic, non-decisive, fault-injection, schema,
serializer, persistence, and deterministic smoke tests do not consume the
scientific trial.

### 6. Freeze and integrate to main

Use direct-to-main only when it is authorized and:

- local `main` is synchronized with the intended remote head;
- the diff contains only the reviewed scientific artifact set;
- independent review is accepted;
- all required local validations pass;
- no active frozen execution is invalidated;
- no unrelated user changes are included.

Treat these as hard integration gates. If any gate is missing, keep the work on
the mutable feature branch and continue normal commits for non-decisive
artifacts, but do not commit a reviewed-decision candidate early and do not
create a placeholder mainline commit.

Create one freeze commit containing the reviewed definition, decision code when
applicable, exact source bindings, and review record. For mainline integration,
either merge the reviewed freeze branch under repository history policy or
transplant/squash only the reviewed artifact set into one mainline freeze
commit. When commit identity changes, verify that every scientific file hash
matches the accepted manifest. Preserve the pushed mutable branch as
development provenance; its earlier commits do not become frozen authority.

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

When construction occurred in an isolated worktree, integrate only the reviewed
artifact set onto synchronized `main`; do not merge unrelated worktree history
or temporary execution artifacts. Do not delete the mutable branch until its
provenance and any external artifacts are durably recoverable.

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

Push the reviewed result, report its exact commit, artifacts, review,
validations, inference boundary, and surviving obligations, and close the issue
only when its exit or stop rule is satisfied. Refresh the parent graph, repair
real dependency edges, and choose the highest-priority newly unblocked issue.
A failed selected realization is not a family no-go; do not reopen frozen
dependencies without a demonstrated contradiction.

## Failure Handling

Request a user-level decision only when work would change a frozen identity,
program north star, ontology, protected independence assumption, declared pass
burden, endpoint regime, or family-level closure rule. Handle ordinary
pre-freeze iteration, proof-method changes, execution-only defects, candidate
replacement, scoped realization failures, and compatible graph repairs without
escalation. Preserve positive lemmas and exact obstructions; never claim a
family no-go without a theorem covering the declared class.

## Anti-Churn Rules

- Use the feature branch, not a late preservation lane, as the normal recovery
  surface for mutable scientific source and provenance.
- Commit and push coherent non-decisive mutable steps; do not accumulate a large
  untracked workbench in any checkout.
- Keep only the bounded decision-bearing candidate set uncommitted during exact
  adversarial review, and make its first commit the joint freeze commit.
- Keep `main` as the reviewed integration surface and merge only after freeze.
- Do not create a PR merely to obtain code-centric review of theorem work.
- Do not wait for automated code review after scientific review and local gates cover the artifact, or split direct-main work into PR-ready/merge-ready phases. If PR policy requires automated review, apply its PR-lifetime churn breaker and the lower repository scientific round cap.
- Do not create authorization packets for obvious implementation or governance
  commits for ordinary runner qualification defects.
- Do not freeze drafts before adversarial review is complete.
- Do not build an execution harness for paperwork-only predicates.
- Do not count review/mutation volume as scientific depth.
- A new candidate SHA does not reset a review-round cap. After the cap, stop at a claim/architecture/scope reset; do not post another review trigger without explicit authorization.
- Do not deepen a narrow certificate past a breadth-first program gate.
- Use deprecated or analogous work as idea input, not authority.
- Do not let downstream failures retroactively weaken frozen results.

## Final Report Format

Use [report templates](references/report-templates.md) for the scoped
disposition, artifacts, commit, review and validation evidence, graph handoff,
surviving obligations, and execution status.
