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

Each mutable branch and overlapping path surface has one writer. Back that
ownership with a short fenced lease stored on a dedicated remote Git ref, for
example `refs/heads/coordination/lease-<issue>`. A lease record contains the
issue, branch, owner, random owner token, UTC expiry, monotonically increasing
generation, and expected branch head.

Acquire or transfer the lease with an atomic compare-and-swap against the
previous lease-ref object ID. With command-line Git, push the new lease commit
using:

```sh
git push origin <new-lease-commit>:<lease-ref> \
  --force-with-lease=<lease-ref>:<expected-old-lease-commit>
```

For a previously absent ref, use an empty expected value. A provider API is
acceptable only when it offers the same expected-old-object precondition. If
the compare-and-swap loses, stop; fetch and reconcile rather than retrying over
the winner.

Every remote branch mutation requires the active owner token and generation in
the handoff log, plus a force-with-lease check against the expected branch
head. Immediately before merge, refetch and verify the lease token, generation,
expiry, candidate head, and default-branch head. Abort on any mismatch. Release
ownership by atomically advancing the lease ref to a record with the next
generation, `owner_token: null`, and `status: released`; do not merely wait for
expiry.

### Lease liveness

Default to a 30-minute lease and do not exceed 60 minutes merely for
convenience. Renew only while the owner is actively making branch writes. Each
renewal must use compare-and-swap, verify the expected remote branch head, and
record a fresh UTC expiry. A known long calculation may use a longer lease only
when its protected process and next checkpoint are named in the handoff record.

Before a planned pause, model or machine switch, or end of session, push the
latest coherent non-decisive checkpoint, publish its exact head, and release
the lease. Do not leave a lease held around an idle stable checkpoint. Local
process listings, worktree timestamps, and chat presence are advisory only:
never seize an unexpired lease from them. Before expiry, takeover requires an
explicit released or transferred lease record.

After expiry, fetch the lease ref and candidate branch again. Take ownership
only with compare-and-swap against the expired lease object and only when the
branch still equals its recorded expected head. If either ref moved, stop and
reconcile the new state. Record the takeover as a new generation; expiry does
not authorize rewriting or discarding the prior owner's commits.

### Collision recovery

When two agents discover overlapping branches or path ownership, the loser of
the lease compare-and-swap becomes read-only and publishes one exact collision
handoff. The winning owner must inventory both pushed heads before continuing.
It must either reconcile the sibling's applicable scientific or qualified
engineering evidence, or explicitly transfer ownership and name why the
sibling is inapplicable. Do not silently choose one branch, repeat a completed
qualification campaign, or discard a stronger theorem to make integration
easier.

Reconcile scientific bytes by semantic diff and renewed review at the effective
policy boundary. Reconcile execution-only qualification by proving it still
implements the winning scientific identity, then rerun only the affected tier.
Publish the selected head and disposition before requesting another review.

Never transfer authority through uncommitted files. Commit and push every
coherent non-decisive change before switching machines or agents.

## Handoff record

Put this record in the owning issue or PR:

```text
repo: owner/name
issue: number
role: constructor | reviewer | integrator
constructor: stable agent identity
integrator: stable agent identity
machine: stable machine label
branch: issue-scoped branch
base: full commit SHA
head: full pushed commit SHA
owned_paths: repository-relative paths or patterns
scientific_paths: repository-relative paths or patterns
engineering_paths: repository-relative paths or patterns
profile: diagnostic | analytic | promotion
authority: exact authority label
scientific_digest: SHA-256 or null
source_bindings: exact repository path and Git blob pairs, or []
validation: exact commands and outcomes bound to head
ci: status and head, or not-run
review: status and reviewed digest/head, or not-requested
status: constructing | review-ready | repairing | integration-ready | merged | blocked
blocker: concrete blocker or null
next_action: one bounded action
lease_ref: dedicated remote Git ref
lease_generation: positive integer
lease_token: random owner token, or null when released
lease_status: held | released
lease_renewed_at: UTC timestamp
lease_expires_at: UTC timestamp, or null when released
```

For `promotion`, `scientific_paths`, `scientific_digest`, and exact
`source_bindings` are mandatory and nonempty; the digest must bind the claim
classification and source bindings. For `analytic`, record scientific paths and
the digest used for review, and include exact source bindings whenever the
claim depends on external sources. A `diagnostic` may use a null digest and an
empty source list. Always separate engineering paths from the scientific
surface and name the integrator explicitly.

Do not write “complete” when only construction is complete. Use
`integration-ready` and name the remaining CI, review, merge, or parent gate.

## Integrator intake

1. Fetch live GitHub issue, PR, branch, CI, reviews, and default-branch head.
2. Verify the handoff head and a released, explicitly transferred, or safely
   expired lease; inspect dirty local paths before checkout.
3. Atomically acquire the fenced lease and record the new token and generation.
4. Recompute the scoped scientific digest and source bindings.
5. Compare default-branch drift with scientific and owned paths.
6. Classify every post-review change as scientific or engineering-only.
7. Apply repository review-stop and exact-head policies without requesting
   redundant review.
8. Choose a merge method that preserves any provenance topology promised by
   the candidate.
9. Revalidate the fenced lease and both remote heads immediately before merge.
10. Verify mainline bytes and disposition after merge, then atomically release
    the lease.

## Parent acceptance

Parent acceptance is synthesis, not a replay campaign. Build a concise matrix
of exact child theorem or obstruction, assumptions/authority, recovery or
inactive limit, remaining provenance gap, parent success condition, and final
classification. Import scoped digests and source hashes. Do not recreate child
derivations or rerun all inherited validators unless the parent explicitly
depends on their live execution.
