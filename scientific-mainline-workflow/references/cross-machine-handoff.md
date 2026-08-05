# Cross-Machine Scientific Handoff

GitHub is durable state. Local worktrees, chat context, and model memory are
caches.

## Roles

- The constructor owns scientific revisions on one issue-scoped branch.
- The independent reviewer reads exact candidate bytes and does not edit them.
- The integrator owns current-main comparison, final gate classification,
  merge method, merge, and parent acceptance.

GPT-5.6Pro may be the constructor and Codex the integrator. A constructor
handoff does not confer scientific acceptance.

## Single-writer rule

Each mutable branch and overlapping path surface has one writer. Record a
short advisory lease. Before taking over, verify the remote head and that the
previous writer released the lease or it expired. If live remote state differs
from the handoff, stop writes and reconcile first.

Never transfer authority through uncommitted files. Commit and push every
coherent non-decisive change before switching machines or agents.

## Handoff record

Put this record in the owning issue or PR:

```text
repo: owner/name
issue: number
role: constructor | reviewer | integrator
machine: stable machine label
branch: issue-scoped branch
base: full commit SHA
head: full pushed commit SHA
owned_paths: repository-relative paths or patterns
profile: diagnostic | analytic | promotion
authority: exact authority label
scientific_digest: SHA-256 or null
validation: exact commands and outcomes bound to head
ci: status and head, or not-run
review: status and reviewed digest/head, or not-requested
status: constructing | review-ready | repairing | integration-ready | merged | blocked
blocker: concrete blocker or null
next_action: one bounded action
lease: writer identity and UTC expiry, or released
```

Do not write “complete” when only construction is complete. Use
`integration-ready` and name the remaining CI, review, merge, or parent gate.

## Integrator intake

1. Fetch live GitHub issue, PR, branch, CI, reviews, and default-branch head.
2. Verify the handoff head and lease; inspect dirty local paths before checkout.
3. Recompute the scoped scientific digest and source bindings.
4. Compare default-branch drift with scientific and owned paths.
5. Classify every post-review change as scientific or engineering-only.
6. Apply repository review-stop and exact-head policies without requesting
   redundant review.
7. Choose a merge method that preserves any provenance topology promised by
   the candidate.
8. Verify mainline bytes and disposition after merge, then release the lease.

## Parent acceptance

Parent acceptance is synthesis, not a replay campaign. Build a concise matrix
of exact child theorem or obstruction, assumptions/authority, recovery or
inactive limit, remaining provenance gap, parent success condition, and final
classification. Import scoped digests and source hashes. Do not recreate child
derivations or rerun all inherited validators unless the parent explicitly
depends on their live execution.
