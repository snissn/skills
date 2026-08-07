# Scientific portfolio governance policy

This file supplements the repository root `AGENTS.md` for
`scientific-portfolio-governance/`.

## Authority-write taxonomy

The skill and fixtures must classify work by governed writes:

- `science` and `formalization` share the authority-writing pool;
- `qualification` validates immutable authority and may not repair it;
- `maintenance` is non-authority engineering.

A theorem-bearing formalization may not be represented as maintenance. A
qualification lane may not enable scientific, theorem, source-authority,
classification, or governed-manifest writes.

Generic validators and examples must fail closed on those errors and on
multiple active writers or qualifiers for the same surface.

## Review fallback

Portfolio boards and status comments may record
`CODEX_REVIEW_UNAVAILABLE_QUOTA` when GitHub `@codex review` cannot run because
of quota, usage-limit, review-limit, rate-limit, capacity, or service errors.
That status is reviewer unavailability, not review success or scientific
failure.

A workstream may move from `REVIEW_OR_CI` to a merge-ready review disposition
only after an exact-head GPT-5.6 Pro fallback authorized by repository policy
returns `ACCEPT`:

- `INDEPENDENT_GPT56_SUBAGENT`; or
- `LOCAL_GPT56_REVIEW` when no separate subagent is available and a clean-room,
  read-only review phase is documented.

The board or owning PR must retain the quota evidence, exact candidate identity,
reviewer mode, findings disposition, and final `ACCEPT` or `REJECT`. All other
CI, branch-protection, predecessor, human/external-review, thread-resolution,
and merge gates remain in force. Any later governed edit returns the workstream
to review.
