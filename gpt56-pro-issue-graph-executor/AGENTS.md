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

1. spawning an independent read-only GPT-5.6 Pro review subagent with no
   construction role; or
2. if no separate subagent is available, running a local clean-room GPT-5.6 Pro
   review after freezing the candidate, in a separate adversarial review phase
   or isolated worktree with candidate writes disabled.

The fallback record must include exact base/head or manifest, reviewer mode and
model, reviewed paths and contract, tests and checks inspected, every finding
and disposition, explicit `ACCEPT` or `REJECT`, confirmation that no candidate
bytes were edited, and the Codex quota evidence URL. Label a same-agent review
`LOCAL_GPT56_REVIEW`; do not call it independent or hosted Codex review.

The coordinator may merge after a qualifying fallback only when all other merge
gates pass: current base, latest-head CI or an explicitly permitted CI
unavailability disposition, tests, benchmarks, unresolved-thread inventory,
branch protection, expected-head merge, predecessor authority, and target-repo
policy. Any later scientific or review-relevant edit invalidates the fallback.

Do not repeatedly trigger `@codex review` after one exact-head quota response
unless a stricter target-repository rule requires one bounded retry. Existing
Codex findings or unresolved threads from a review that did run remain blocking.
