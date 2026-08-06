# Scientific mainline review fallback policy

This file supplements the repository root `AGENTS.md` for
`scientific-mainline-workflow/`.

When GitHub `@codex review` is unavailable because of quota, usage-limit,
review-limit, rate-limit, capacity, or service errors, record
`CODEX_REVIEW_UNAVAILABLE_QUOTA` against the exact candidate head. The quota
response is not a review result and must not be described as clean or failed
science.

For an internal scientific review gate that does not explicitly mandate the
GitHub-hosted Codex service, use one of these exact-head substitutes:

1. preferred: an independent, read-only GPT-5.6 Pro subagent with no constructor
   role and no candidate write access;
2. fallback: a local clean-room GPT-5.6 Pro review after candidate freeze, in a
   separate adversarial phase or isolated worktree with candidate writes
   disabled.

The reviewer must inspect the actual theorem, action, state space, source
bindings, validators, controls, recovery maps, and claim boundaries at the exact
head or deterministic byte manifest. The durable record must identify reviewer
mode, model, base/head or manifest, reviewed paths, checks, findings,
dispositions, final `ACCEPT` or `REJECT`, and
`candidate_edits_by_reviewer: false`. It must also retain:

```text
codex_unavailability_evidence:
  response_url:
  bot_login:
  timestamp:
  exact_candidate_head:
  normalized_reason:
```

A local same-agent fallback is labeled `LOCAL_GPT56_REVIEW` and is accepted only
as an internal repository review. It is not independent human review, external
peer review, or hosted Codex review. A constructor's narrative self-review does
not satisfy the gate.

Any scientific edit invalidates the review. The fallback does not waive freeze,
current-main synchronization, CI, execution qualification, branch protection,
unresolved review threads, human-approval requirements, or the repository's
claim and evidence boundaries. Do not re-trigger Codex repeatedly after one
exact-head quota response unless a stricter rule requires one bounded retry.
