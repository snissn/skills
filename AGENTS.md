# Skills repository policy

## Scientific portfolio skills

Any skill that opens, resumes, reviews, merges, or project-manages scientific
issues or pull requests must preserve these invariants:

1. read a repository-owned portfolio board when one exists;
2. enforce its active scientific and maintenance workstream limits;
3. use an explicit status taxonomy with blocked, parked, deferred, superseded,
   and completed states that do not authorize implementation;
4. keep one scientific identity and decision surface per PR by default;
5. prohibit workflow-generated scientific candidate revisions;
6. bind PR descriptions, manifests, review, CI, and merge to one exact head;
7. renew scientific review after every scientific edit;
8. continue review-fix work after the default repair round only for a
   claim-changing scientific or evidence-path finding; and
9. activate descendants only from merged positive predecessor authority.

Use `scientific-portfolio-governance` for portfolio reconciliation and compose
it with `scientific-mainline-workflow` and `gpt56-pro-issue-graph-executor` when
the target repository contains a scientific portfolio board or the user asks
for multi-lane scientific project management.

## GitHub Codex quota fallback

A GitHub `@codex review` quota, usage-limit, review-limit, rate-limit, capacity,
or service-unavailable response is evidence that the hosted review did not run.
It is never a clean review and never a finding-bearing review. Record it as
`CODEX_REVIEW_UNAVAILABLE_QUOTA` with the exact candidate head, response URL,
bot login, timestamp, and normalized reason.

When effective repository policy requires an internal exact-head review but
does not explicitly require the GitHub-hosted Codex service itself, GPT-5.6 Pro
agents may satisfy the review gate with either:

1. an independent, read-only GPT-5.6 Pro subagent that had no construction role;
   or
2. when no separate subagent is available, a documented local clean-room
   GPT-5.6 Pro review performed after the candidate is frozen, in a separate
   adversarial review phase or isolated worktree with candidate writes disabled.

The fallback review must identify the reviewer mode and model, exact base and
head or deterministic manifest, reviewed paths and load-bearing claims, checks,
all finding dispositions, an explicit `ACCEPT` or `REJECT`, and confirmation
that the reviewer did not edit candidate bytes. Label a same-agent fallback
`LOCAL_GPT56_REVIEW`; do not call it an independent human or hosted Codex
review.

One exact-head quota response is sufficient unless a stricter local policy
requires one bounded retry. Do not spam `@codex review`. Any later scientific
edit invalidates the fallback review. The fallback does not waive CI, branch
protection, unresolved threads, required human review, or a repository rule
that explicitly mandates GitHub-hosted Codex.

Every skill that classifies PR review state or mergeability must honor this
fallback and must never translate a quota response into a Codex pass.

Do not add a second competing status schema to another skill. Repository-local
policy may narrow the default limits and statuses, and wins when it is stricter.
