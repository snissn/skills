# Evidence Scope Ladder

Use this reference before defining a scientific checkpoint. Its purpose is to
prevent an early-stage model, witness, or effective theory from inheriting the
proof burden of a global or fundamental completion.

## Core rule

> Select the smallest evidence level and weakest honest quantifier that supports
> the intended inference. Prove every NEED predicate at that level. Record SHOULD
> and COULD work as nonblocking unless it is explicitly promoted.

Scientific rigor is preserved by narrowing the claim, not by pretending that a
partial result is global. A scoped theorem or reproducible witness can be fully
valid without proving every configuration, every observable, or all-time
regularity.

## NEED, SHOULD, and COULD

### NEED

A NEED predicate is load-bearing for the named checkpoint. Failure of a NEED
predicate blocks the checkpoint.

Typical NEED predicates include:

- nonempty domain or explicit witness;
- the actual observable or mechanism named by the claim;
- absence of circular target injection;
- the minimum existence, stability, error, or resource control needed over the
  declared observation horizon;
- preservation of protected assumptions such as preparation independence;
- enough provenance and review to support the exact scoped inference.

### SHOULD

A SHOULD item strengthens robustness, portability, or reuse but is not required
for the checkpoint as presently named.

Examples:

- upgrading one witness to an open collar;
- uniformity over a larger parameter range;
- a second independent estimate;
- broader fault or observable coverage;
- limited release of an effective background;
- stronger stability than the selected experiment needs.

A SHOULD item becomes blocking only when:

1. the user or maintained steering artifact explicitly promotes it; or
2. a proved dependency shows that the NEED claim cannot be valid without it.

### COULD

A COULD item is a broader or deeper extension. It should be recorded in a
separate debt or future-work ledger and must not block the current checkpoint.

Examples:

- global regularity or all-time existence;
- stability of every admissible configuration;
- all observables or all fault modes;
- relativistic, gravitational, or microscopic completion;
- arbitrary instruments when a selected finite family is sufficient;
- uniqueness or minimality of the underlying theory.

## Evidence levels

### E0 — feasibility witness

Form:

> There exists one explicit configuration, solution, branch, trajectory, or
> numerical witness with the named property.

Minimum burden:

- the witness is reproducible and correctly typed;
- the domain is not vacuous;
- the target quantity is computed from the model rather than inserted;
- the claim is labeled as a witness, not a general theorem;
- known assumptions and failure modes are recorded.

E0 can be numerical, analytic, or mixed. It is appropriate for mechanism
discovery and early architecture selection.

### E1 — scoped effective model

Form:

> One declared effective law realizes the named mechanism on a nonempty finite
> family, open collar, or positive-measure prepared subset.

Minimum burden:

- one coherent physical or mathematical model identity;
- a nonempty prepared domain;
- finite-horizon existence or an equivalent equilibrium statement;
- the target observable or record on that domain;
- finite error/resource control appropriate to the claim;
- explicit effective assumptions and nonclaims.

E1 does not require all backgrounds to be dynamical, all coefficients to be
derived, or global stability.

### E2 — controlled operational domain

Form:

> Every preparation in one declared experimental or operational domain satisfies
> the named response, record, or statistical law within a controlled budget.

Minimum burden:

- a prospectively declared domain and observable/fault alphabet;
- uniform control on that domain for the required horizon;
- no postselection or hidden narrowing after evidence appears;
- all errors charged against the decision margin;
- the complete local outputs relevant to the operational claim.

E2 may remain finite, nonrelativistic, fixed-band, or fixed-background when those
assumptions are part of the declared model.

### E3 — broad equivalence or reusable theory

Form:

> A broad class of preparations, instruments, geometries, or parameter values is
> recovered by one reusable theory.

Typical added burdens:

- wider uniformity and compositionality;
- robust preparation and reset;
- larger instrument or observable families;
- stronger stability and resource bounds;
- controlled reduction maps across multiple regimes.

E3 is a legitimate Stage-2 strengthening but should not be the automatic burden
for the first physical model.

### E4 — global or fundamental completion

Form:

> The result holds for all admissible configurations, all relevant times, or a
> fundamental class without effective assumptions.

Typical burdens:

- global existence or regularity;
- all-data stability;
- complete release or derivation of backgrounds and constitutive coefficients;
- maximal observable closure;
- relativistic, gravitational, or microscopic completion;
- minimality, uniqueness, or empirical calibration when claimed.

E4 must be explicitly requested. Never infer it from the words “physical
model,” “closure,” or “complete” when the maintained claim is actually scoped.

## Quantifier ladder

Use the weakest quantifier that supports the inference:

| Level | Quantifier | Appropriate claim |
| --- | --- | --- |
| Q0 | there exists one witness | feasibility |
| Q1 | there exists a nonempty family, collar, or positive-measure subset | scoped model |
| Q2 | for every state in one declared prepared domain | operational closure |
| Q3 | for every admissible state or all time | global completion |

Every `for all`, `uniform`, `complete`, `arbitrary`, or `global` in a candidate
must be traced to a NEED predicate. Otherwise weaken it or move it to SHOULD or
COULD.

## Stability ladder

| Level | Meaning |
| --- | --- |
| S0 | one solution or equilibrium exists |
| S1 | the selected solution survives the declared finite horizon |
| S2 | a nonempty collar remains in the selected regime for that horizon |
| S3 | local energetic, spectral, or orbital stability |
| S4 | global all-data or all-time stability |

Do not require S4 for an E0 or E1 claim. For an early apparatus or field-model
checkpoint, S1 is often sufficient and S2 is usually a strong result. S3 may be
useful when the model is explicitly sold as a stable branch. S4 is a separate
program.

## Effective assumptions are allowed

A scoped Stage-2 or model-integration result may assume, when declared:

- a fixed background time or preferred foliation;
- a selected finite band or mode sector;
- fixed support, radial, coframe, boundary, or material data;
- phenomenological constitutive coefficients;
- a finite observation horizon;
- a selected source, preparation family, instrument family, or setting set;
- a controlled numerical discretization or finite-dimensional reduction.

The reviewer should ask whether the assumption invalidates the named inference,
not whether it has already been derived from a deeper theory. Derivation of an
effective input is a later checkpoint unless the current mechanism is circular
without it.

## Proportional validation

Validation follows the NEED set.

- E0: reproduce the witness, test target non-injection, and run decisive sanity
  controls.
- E1: validate the model identity, nonempty domain, target mechanism,
  finite-horizon/resource budget, and the declared local assumptions.
- E2: add uniform-domain, boundary, fault-alphabet, and margin checks.
- E3: add compositionality, wider parameter sweeps, and reusable interface tests.
- E4: use the global theorem or exhaustive decision machinery genuinely required
  by the claim.

Do not demand a semantic mutation for an unimplemented SHOULD or COULD item.
Do not build a large registry, runner, or exact-arithmetic apparatus when a
short analytic or reproducible numerical witness proves the same NEED
predicate.

## Reviewer blocking rule

A reviewer may return `BLOCK` for:

- a failed NEED predicate;
- a contradiction or type error;
- a circular definition or target-table injection;
- a vacuous or unproved nonempty domain;
- a hidden change to a protected assumption;
- an inference stronger than the selected evidence, quantifier, or stability
  level;
- a validation path that cannot detect corruption of a NEED predicate.

A reviewer should record, but not block on:

- unpromoted SHOULD strengthening;
- COULD extensions;
- preferences for a more elegant architecture;
- global stability when local finite-horizon control suffices;
- broader observable or fault coverage than the declared operational claim;
- derivation of an explicitly effective input from a deeper theory.

## Promotion and deferral

Every checkpoint should include:

```text
Evidence level: E0 / E1 / E2 / E3 / E4
Quantifier level: Q0 / Q1 / Q2 / Q3
Stability level: S0 / S1 / S2 / S3 / S4

NEED:
- ...

SHOULD:
- ...

COULD:
- ...

Effective assumptions:
- ...

Explicit deferrals:
- ...

Promotion authority:
- user / steering artifact / proved dependency

Stop rule:
- ...
```

A deferred item may be promoted in a later issue without weakening the earlier
scoped checkpoint. Downstream failure does not retroactively invalidate a valid
E0-E2 result unless it reveals a direct contradiction in that result.

## Anti-depth checks

Before starting a new proof obligation, ask:

1. Does the named checkpoint require this quantifier?
2. Does the next operational step consume this result?
3. Would a nonempty prepared subset be enough?
4. Would finite-horizon control be enough?
5. Is the fixed background an honest effective assumption?
6. Is this a scientific necessity or a preference for elegance/completeness?
7. Can the item be deferred without circularity or hidden postselection?
8. Are we trying to solve a global PDE problem to justify one finite experiment?

When the answer shows the obligation is nonblocking, move it to SHOULD or COULD
and proceed.

## Example: early physical apparatus checkpoint

A proportional E1/Q1/S1 checkpoint may NEED:

- one physical action or Hamiltonian;
- one nonempty prepared domain;
- a finite-energy current-bearing solution;
- the target apparatus response;
- finite-horizon persistence;
- reciprocal reaction for the active coupling;
- an explicit resource estimate and claim boundary.

It may SHOULD:

- prove an open robustness collar;
- release selected background modes;
- improve local stability and error bounds.

It may COULD:

- prove all-data global regularity;
- release every support and material variable;
- derive time, gravity, or microscopic coefficients;
- cover every instrument or fault.

Accepting the scoped result is not lowering rigor. It is matching rigor to the
claim and preserving later work as a clearly named extension.
