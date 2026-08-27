# Candidate Review Binding

Use this contract when an independent scientific review must authorize the
freeze and mainline integration of a mutable-branch candidate. Non-decisive
analytic candidates may be reviewed at an exact pushed commit. Decision-bearing
candidates must be reviewed as exact uncommitted bytes before their first joint
freeze commit.

Read [the evidence scope ladder](evidence-scope-ladder.md) before defining the
review burden. The reviewer must evaluate the checkpoint that was actually
selected, not silently replace it with a broader or more fundamental theorem.

## Review-scope declaration

Before generating the candidate manifest, record:

```text
Checkpoint name:
Evidence level: E0 / E1 / E2 / E3 / E4
Quantifier level: Q0 / Q1 / Q2 / Q3
Stability level: S0 / S1 / S2 / S3 / S4
Scientific inference:

NEED predicates:
- ...

SHOULD strengthening:
- ...

COULD extensions:
- ...

Prepared domain and nonemptiness evidence:
Effective assumptions:
Explicit deferrals:
Promotion authority:
Stop rule:
```

Only NEED predicates are integration blockers for the named checkpoint.
SHOULD and COULD items remain nonblocking unless the user, maintained steering
artifact, or a proved dependency explicitly promotes them.

The reviewer may still block a candidate for a contradiction, type error,
circular target injection, vacuous domain, hidden change to a protected
assumption, or an inference stronger than the selected evidence level.

## Candidate manifest

Generate a deterministic manifest from the explicit candidate path set:

```bash
python3 /home/mikers/.codex/skills/scientific-mainline-workflow/scripts/candidate_manifest.py \
  --repo /path/to/worktree \
  --base <candidate-base-sha> \
  --path path/to/definition.md \
  --path path/to/ledger.json \
  --path path/to/validator.py
```

The manifest binds:

- the candidate base commit;
- the worktree `HEAD`;
- the exact sorted path set;
- each file's byte count and SHA-256;
- the corresponding base and `HEAD` Git blob when present; and
- one hash of the canonical manifest payload.

For a non-decisive analytic candidate, generate it from a clean pushed
feature-branch commit. For a decision-bearing candidate, generate it from the
uncommitted working tree after confirming that its definition, predicates,
tolerances, comparator code, runner, fixtures, and source bindings have never
appeared in an earlier commit. In that case `head_sha` records the branch base,
the per-file SHA-256 values bind the mutable candidate bytes, and a missing or
different `head_blob` is expected. Mutable commits before that point are durable
development provenance, not scientific authority.

Pass the manifest, source paths, frozen inputs, review-scope declaration, and
acceptance predicates to the reviewer. The reviewer must return `ACCEPT`,
`BLOCK`, or a scoped failure bound to the manifest hash and candidate base.

## Proportional review rule

Review the candidate at its declared evidence level.

- **E0/Q0:** verify the witness is reproducible, correctly typed, nonvacuous,
  and not created by target injection. Do not demand a general theorem.
- **E1/Q1:** verify one coherent effective model, nonempty prepared domain,
  target mechanism, finite-horizon or equilibrium control, resource/error
  budget, and explicit assumptions. Do not demand global regularity.
- **E2/Q2:** verify uniformity over the declared operational domain, prospective
  observable/fault coverage, no hidden postselection, and charged error margins.
- **E3:** verify the broader equivalence, compositionality, or reusable interface
  actually claimed.
- **E4/Q3:** apply global/all-data burdens only when the candidate explicitly
  claims them.

Apply the declared stability level independently of E/Q:

- **S0:** verify existence of the selected solution or equilibrium.
- **S1:** verify survival through the declared finite observation horizon.
- **S2:** verify a nonempty collar remains in the selected regime through that
  horizon.
- **S3:** verify the claimed local energetic, spectral, or orbital stability on
  the correct reduced space and symmetry quotient.
- **S4:** verify the claimed all-data or all-time stability; lower-level
  existence or local control cannot satisfy an S4 claim.

A reviewer should report attractive strengthening separately. Preference for a
larger domain, stronger stability, broader fault alphabet, or deeper derivation
is not a blocking finding when the NEED claim does not consume it.

## Two-stage review

Use an early adversarial design review to find mathematical and semantic
problems while the candidate is cheap to change. Treat its acceptance as
provisional.

The design review should first audit the proposed burden itself:

- Is the evidence level appropriate to the program stage?
- Are the quantifiers stronger than the inference requires?
- Is a nonempty subset or finite horizon sufficient?
- Are effective assumptions stated rather than hidden?
- Have SHOULD or COULD items been promoted without authority?
- Does the stop rule prevent depth drift after the NEED gate is met?

After dedicated and inherited validation passes, regenerate the manifest and
ask an independent reviewer for the integration disposition on:

- the exact candidate bytes and base;
- the frozen inputs and source bindings;
- the selected evidence, quantifier, and stability levels;
- every NEED predicate;
- the prepared-domain nonemptiness evidence;
- the validation commands, outcomes, and decisive hashes;
- every previously blocking NEED finding;
- the issue exit gate, stop rule, deferrals, and forbidden inferences.

Only this final exact-candidate `ACCEPT` authorizes the freeze and mainline
integration. Validation does not replace scientific review, and review does not
replace validation.

## Blocking and nonblocking findings

Return `BLOCK` only for the smallest concrete issue that prevents the declared
NEED claim, including:

- a failed NEED predicate;
- a mathematical contradiction or type inconsistency;
- a circular definition or target-table injection;
- a vacuous or unproved successful domain;
- a hidden preparation, conditioning, or protected-boundary change;
- an error/resource budget that does not support the inference;
- a validation path unable to detect corruption of a NEED predicate;
- claim language that exceeds the selected evidence level.

Record as nonblocking follow-up:

- unpromoted SHOULD strengthening;
- COULD extensions;
- global stability when local finite-horizon control suffices;
- release or derivation of an explicitly effective input;
- broader observables, faults, parameters, or instruments than the checkpoint
  declares;
- a more elegant or minimal architecture.

Nonblocking findings belong in the deferral ledger. They do not prevent
`ACCEPT`.

## Change rule

Any change to a scientific byte, formula, source binding, selected E/Q/S level,
NEED predicate, tolerance, control, prepared domain, or inference invalidates
the prior acceptance. For a non-decisive analytic candidate, commit and push the
revision on the mutable branch. For a decision-bearing candidate, revise the
uncommitted draft. In both cases regenerate the manifest and obtain a new
review.

Changing a SHOULD or COULD note without changing the scientific identity may
use a focused exposition review. Promoting a SHOULD or COULD item into NEED is a
scientific scope change and requires a new candidate identity or explicit
steering update.

A representation-only or execution-only repair may use a focused semantic
review, but the repair must still demonstrate that all scientific values and
decision surfaces are unchanged.

Artifact-only descendants may retain the accepted candidate evidence only when
their recorded runtime/scientific and harness/schema subtree identities plus
implementation blob provenance exactly match the accepted freeze. Any product,
scientific-runtime, or harness/schema drift invalidates affected evidence and
requires renewed review, freeze, and collection.

## Base-drift rule

Immediately before integration, fetch the remote and compare the accepted base
with current `main`.

- If candidate paths, frozen inputs, theorem dependencies, or any NEED premise
  changed, rebase or transplant the draft, rerun validation, regenerate the
  manifest, and obtain a renewed independent review.
- If the movement is demonstrably unrelated, preserve the accepted candidate
  file bytes, document the base-drift audit, rerun affected inherited checks,
  and bind the integration evidence to both manifests.

Do not infer that a clean textual merge proves scientific compatibility.

## Freeze and mainline verification

After creating the freeze commit and before mainline execution:

1. verify the committed path set is exactly the reviewed set;
2. verify every committed blob reproduces the accepted candidate SHA-256;
3. inspect the full commit diff;
4. rerun any check whose input is the committed tree rather than the mutable
   worktree;
5. confirm the remote has not advanced;
6. merge, squash, or transplant only under repository history policy;
7. if the commit identity changes, verify every scientific file hash against
   the accepted manifest;
8. push without force and verify remote `main` equals the integrated freeze.

Retain the pushed mutable branch as non-authoritative provenance. Its history
does not acquire scientific authority merely because its reviewed freeze was
integrated.

The manifest is provenance evidence, not a scientific theorem. Independent
formula derivation and substantive validation remain mandatory at the selected
level.

## Reviewer request template

```text
Review this scientific candidate for freeze and mainline integration.

Base: <sha>
Candidate branch and HEAD: <branch> <sha>
Candidate state: <pushed non-decisive commit / uncommitted decision-bearing draft>
Manifest: <sha256>
Candidate paths: <exact list>
Frozen inputs: <exact files and hashes>

Checkpoint: <name>
Evidence level: <E0-E4>
Quantifier level: <Q0-Q3>
Stability level: <S0-S4>
Scientific inference: <exact scoped claim>

NEED predicates:
- <blocking predicate>

SHOULD strengthening:
- <nonblocking item>

COULD extensions:
- <deferred item>

Prepared domain and nonemptiness evidence: <exact evidence>
Effective assumptions: <list>
Explicit deferrals: <list>
Promotion authority: <user/steering/dependency>
Stop rule: <rule>

Prior blocking NEED findings: <list and claimed resolutions>
Validation evidence: <commands and exact outcomes>

Inspect the actual files and recompute load-bearing mathematics independently.
Do not edit files or rely on the constructor summary. Review the declared
checkpoint, not a stronger replacement theorem.

Return ACCEPT, BLOCK, FAIL SELECTED REALIZATION, or CLASS-LEVEL OBSTRUCTION,
bound to the base and manifest. Block only on NEED predicates, contradictions,
vacuity, circularity, protected-boundary violations, or overclaim. Record SHOULD
and COULD observations as nonblocking deferrals. State the exact inference
boundary and surviving obligations.
```
