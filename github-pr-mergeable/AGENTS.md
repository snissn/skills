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

## Internal substitute review

When effective repository policy requires an internal exact-head review but
does not explicitly require the GitHub-hosted Codex service itself, the merge
review gate may be satisfied by:

1. `INTERNAL_SUBAGENT_REVIEW`: an independent, read-only internal subagent
   with no construction role; or
2. `LOCAL_MOCK_SUBAGENT_REVIEW`: when no separate subagent can run, an actual
   same-agent reviewer pass in a distinct adversarial phase or isolated
   worktree, with candidate writes disabled.

Both are acceptable fallbacks under the default internal review gate. Follow
[the shared fallback contract](references/internal-review-fallback.md) for
the exact candidate, actual model, inspected paths and claims, checks, findings,
`ACCEPT` or `REJECT`, no candidate edits, and unavailability evidence. Use the
permitted model route; GPT-5.6 Pro is not a universal fallback requirement.
Label a mock review as same-agent, not independent, human, or hosted review.

## Merge gate

A qualifying internal fallback may replace only the unavailable hosted Codex
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
