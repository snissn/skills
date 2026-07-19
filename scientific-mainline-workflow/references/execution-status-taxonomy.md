# Execution Status Taxonomy

Use this taxonomy whenever a scientific validator, runner, or decisive packet
produces a disposition.

## Required layers

Every execution-bearing report must separate:

1. `engineering_status`
2. `execution_validity`
3. `protocol_verdict`
4. `scientific_inference`

Do not collapse these layers into one pass/fail field.

## Meanings

### `engineering_status`

Whether the runner and its surrounding execution plumbing are qualified:

- schema and serializer support exact scalar types;
- atomic persistence is correct;
- representation-only changes are invariant;
- semantic mutations are detected;
- CLI, logging, and exception handling do not corrupt scientific values.

This is an engineering judgment, not a scientific result.

### `execution_validity`

Whether the qualified runner completed the declared comparator set without an
implementation or infrastructure defect.

Typical statuses:

- `VALID`
- `INVALID EXECUTION`

An execution can be invalid even if some rows persisted.

### `protocol_verdict`

The immutable result of the frozen scientific decision rule, available only for
a valid execution.

Typical statuses:

- `PASS <stage>`
- `FAIL <stage> REALIZATION`
- `INCONCLUSIVE`

Never use an engineering defect as a protocol verdict.

### `scientific_inference`

The scoped meaning of the valid protocol verdict.

This field states exactly what was established and what was not inferred.

## Invalid execution rule

Use:

`ENGINEERING DEFECT — NO SCIENTIFIC VERDICT`

when a representation, plumbing, or implementation defect prevents a valid
scientific execution.

Examples:

- serializer cannot encode an exact symbolic type;
- comparator state was not durably persisted;
- the runner crashed before the declared comparator set was validly run;
- a comparator implementation is later shown not to encode the frozen
  predicate.

Do not convert these into failed scientific comparators.

## Trial-consumption rule

A scientific trial begins when the first real scientific comparator starts
under the frozen qualified runner.

- A pre-comparator defect consumes no scientific trial.
- A crash after the first comparator starts consumes a partial trial, even when
  the in-progress comparator does not complete or persist.
- Scientific evidence consists only of comparator rows that completed and were
  durably persisted.
- Declaring the overall execution invalid does not erase durable rows or turn a
  started trial back into an unused trial.
- A corrected execution must use a new artifact and explicitly record the
  defect and replay authorization.
- Correcting execution-only software does not itself authorize replay.
- Never replay merely to improve a scientific outcome.

## Software qualification rule

The scientific identity and execution software have different lifecycles:

- freeze the scientific definition after adversarial review;
- keep execution-only software mutable until it is demonstrably qualified;
- use synthetic, non-decisive tests for schemas, serializers, comparator
  orchestration, atomic persistence, fault handling, collision refusal, and
  repeatability;
- bind the qualified runner hashes before the real scientific execution;
- prove with a focused semantic diff that engineering repairs did not alter a
  scientific input, value, comparator, tolerance, decision rule, or inference.

These engineering tests consume no scientific trial. Do not create a new
architecture packet for ordinary qualification defects.

## Analytic work

Purely analytic packets, integration theorems, scoped failures, and design
reviews do not need this taxonomy unless they also run a decisive scientific
validator.

Do not build a fake execution wrapper for an analytic theorem merely to emit
these fields.
