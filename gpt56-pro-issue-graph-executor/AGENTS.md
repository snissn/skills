# GPT-5.6 Pro issue-graph review fallback policy

This file supplements the repository root `AGENTS.md` for
`gpt56-pro-issue-graph-executor/`.

In `execute-and-merge` mode, a GitHub `@codex review` quota, usage-limit,
review-limit, rate-limit, capacity, or service-unavailable response does not
block forever and does not count as a clean review. Record it as
`CODEX_REVIEW_UNAVAILABLE_QUOTA` against the exact PR head.

When effective target-repository policy requires an internal exact-head review
but does not explicitly require GitHub-hosted Codex itself, the GPT-5.6 Pro
coordinator may satisfy the gate by:

1. an internal read-only subagent review (`INTERNAL_SUBAGENT_REVIEW`) with no
   construction role; or
2. when a separate subagent cannot run, a same-agent mock subagent review
   (`LOCAL_MOCK_SUBAGENT_REVIEW`) after holding the candidate bytes fixed, in
   a separate adversarial phase or isolated worktree with writes disabled.

Both are acceptable internal fallbacks. Follow
[the shared contract](../github-pr-mergeable/references/internal-review-fallback.md)
and this harness's permitted model routing; record the actual reviewer model.

The fallback record must include exact base/head or manifest, reviewer mode and
model, reviewed paths and contract, tests and checks inspected, every finding
and disposition, explicit `ACCEPT` or `REJECT`, and confirmation that no
candidate bytes were edited. Its quota evidence must be structured as:

```text
codex_unavailability_evidence:
  response_url:
  bot_login:
  timestamp:
  exact_candidate_head:
  normalized_reason:
```

Label a same-agent review `LOCAL_MOCK_SUBAGENT_REVIEW`; it performs actual
source inspection and is not independent or hosted Codex review.

The coordinator may merge after a qualifying fallback only when all other
merge gates pass, including current base, latest-head CI or an explicitly
permitted CI-unavailability disposition, tests, benchmarks, performance,
security, scientific acceptance, required human or external review,
unresolved-thread inventory, branch protection, expected-head merge,
predecessor authority, and target-repository policy. Any later scientific or
review-relevant edit invalidates the fallback.

Do not repeatedly trigger `@codex review` after one exact-head quota response
unless a stricter target-repository rule requires one bounded retry. Existing
Codex findings or unresolved threads from a review that did run remain blocking.
