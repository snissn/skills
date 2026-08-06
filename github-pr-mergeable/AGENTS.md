# GitHub PR mergeable review policy

This file supplements the repository root `AGENTS.md` for
`github-pr-mergeable/`.

## Quota classification

A latest-head response from the configured GitHub Codex bot that reports quota
exhaustion, usage limits, review limits, rate limits, capacity failure, or
service unavailability is:

```text
CODEX_REVIEW_UNAVAILABLE_QUOTA
```

It proves only that the hosted review did not run. It is not `clean`,
`approved`, `findings`, or a permanently pending request. Preserve the response
URL, bot login, timestamp, exact PR head, and normalized reason. One exact-head
quota response is sufficient unless effective repository policy requires one
bounded retry.

The bundled Codex classifier may still describe the request as pending or
exhausted because it is a hosted-artifact classifier. Supplement that output
with the recorded quota evidence rather than repeatedly triggering `@codex
review`.

## GPT-5.6 Pro substitute review

When effective repository policy requires an internal exact-head review but
does not explicitly require the GitHub-hosted Codex service itself, the merge
review gate may be satisfied by:

1. an independent, read-only GPT-5.6 Pro subagent with no construction role; or
2. when no separate subagent is available, one local clean-room GPT-5.6 Pro
   review after the candidate is frozen, performed in a distinct adversarial
   review phase or isolated worktree with candidate writes disabled.

The review record must contain:

```text
review_mode: INDEPENDENT_GPT56_SUBAGENT | LOCAL_GPT56_REVIEW
model: GPT-5.6 Pro
base_sha:
head_sha_or_manifest:
reviewed_paths:
load_bearing_contract:
checks_performed:
findings_and_dispositions:
disposition: ACCEPT | REJECT
candidate_edits_by_reviewer: false
codex_unavailability_evidence:
  response_url:
  bot_login:
  timestamp:
  exact_candidate_head:
  normalized_reason:
```

A same-agent local fallback must be labeled `LOCAL_GPT56_REVIEW`; it must not be
presented as independent, human, or hosted Codex review. A constructor summary,
ordinary self-review paragraph, test result, mutation count, or green CI run is
not a substitute review.

## Merge gate

A qualifying GPT-5.6 Pro fallback may replace only the unavailable hosted Codex
artifact. It does not waive:

- latest-head CI or an explicit permitted CI-unavailability disposition;
- branch protection;
- unresolved findings or threads from any Codex review that did run;
- required human or external review;
- exact-head synchronization and expected-head merge checks;
- performance, test, security, or scientific acceptance gates; or
- a repository rule that explicitly requires GitHub-hosted Codex itself.

Any later scientific or review-relevant code edit invalidates the fallback
review. A representation-only change also invalidates the prior fallback until
a new focused exact-head equivalence review is recorded with all required
evidence fields and `disposition: ACCEPT`. Never report quota evidence as a
Codex pass.
