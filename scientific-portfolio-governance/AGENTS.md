# Scientific portfolio review fallback policy

This file supplements the repository root `AGENTS.md` for
`scientific-portfolio-governance/`.

Portfolio boards and status comments may record
`CODEX_REVIEW_UNAVAILABLE_QUOTA` when GitHub `@codex review` cannot run because
of quota, usage-limit, review-limit, rate-limit, capacity, or service errors.
That status is reviewer unavailability, not review success or scientific
failure.

A workstream may move from `REVIEW_OR_CI` to a merge-ready review disposition
only after an exact-head GPT-5.6 Pro fallback authorized by repository policy
returns `disposition: ACCEPT`:

- `INDEPENDENT_GPT56_SUBAGENT`; or
- `LOCAL_GPT56_REVIEW` when no separate subagent is available and a clean-room,
  read-only review phase is documented.

The board or owning PR must retain the complete Codex quota evidence, exact
candidate identity, reviewer mode, findings disposition, and final `ACCEPT` or
`REJECT`. A `REJECT` disposition remains non-mergeable. All other CI,
branch-protection, predecessor, human/external-review, thread-resolution, and
merge gates must also pass. Any later scientific edit returns the workstream to
review.
