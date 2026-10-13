# Internal Review Fallback

When hosted AI review cannot run, or review delegation is unavailable, either
of these modes can satisfy the default internal review gate:

- `INTERNAL_SUBAGENT_REVIEW`: a real, read-only subagent reviews the exact
  candidate in fresh context, without a construction role. Prefer this mode
  when delegation is available.
- `LOCAL_MOCK_SUBAGENT_REVIEW`: the current agent performs a separate
  adversarial reviewer pass when a separate subagent cannot run. Hold the
  candidate bytes fixed, disable candidate writes during that pass, and inspect
  the actual sources, requirements, diff, and raw validation evidence as a
  reviewer would. This is an acceptable same-agent fallback; label it as a
  mock subagent review rather than independent or hosted review.

Both modes require actual review work, disposition of findings, and an explicit
`ACCEPT` or `REJECT` bound to the exact head or deterministic byte manifest.
A simulated reviewer role must not invent an agent invocation, checks, findings,
or acceptance. An implementation summary or green CI alone is not a reviewer
pass. Use the executor's permitted model routing and record the actual model;
these modes do not require GPT-5.6 Pro unless target-repository policy does.

## Review Record

Record the following in the existing PR, issue, or maintained review artifact:

```text
review_mode: INTERNAL_SUBAGENT_REVIEW | LOCAL_MOCK_SUBAGENT_REVIEW
reviewer: actual agent identity or same-agent reviewer role
model: actual model or unknown
base_sha:
head_sha_or_manifest:
reviewed_paths_and_claims:
checks_performed: source inspections and actual commands/results or cited evidence
findings_and_dispositions:
disposition: ACCEPT | REJECT
candidate_edits_by_reviewer: false
unavailability_evidence: reason, exact candidate, and available response URL/time
```

For hosted Codex quota, usage-limit, capacity, rate-limit, or service failures,
retain the bot response URL, login, timestamp, exact head, and normalized reason
as `CODEX_REVIEW_UNAVAILABLE_QUOTA`. One exact-head failure is enough to use the
fallback unless target policy requires a bounded retry. For a missing review
service or delegation capability, record that concrete limitation instead.

## Gate And Renewal

A qualifying fallback `ACCEPT` satisfies this skill's default internal review
requirement. Keep hosted unavailability and fallback acceptance as separate
facts; the hosted classifier need not report `clean` for a fallback to qualify.
Follow explicit target-repository requirements for a separately independent
reviewer, a named model, hosted-only review, or human approval.

The fallback does not waive CI, tests, benchmarks, branch protection, merge
authorization, predecessor authority, scientific acceptance/freeze rules, or
unresolved findings and threads from a review that actually ran. Later
scientific or review-relevant edits require renewed review of the new candidate;
a representation-only change needs a focused exact-candidate equivalence review
when target policy permits that narrower check.
