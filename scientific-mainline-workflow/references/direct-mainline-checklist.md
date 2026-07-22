# Direct Mainline Checklist

Direct commits to `main` are appropriate for this workflow only when the user or
repository has explicitly chosen them over a PR loop.

Use [the evidence scope ladder](evidence-scope-ladder.md) before defining the
candidate. Mainline integration certifies the selected scoped checkpoint; it
does not silently promote SHOULD or COULD work into a broader theorem.

## Before editing

- Read `AGENTS.md`.
- Fetch or sync the remote.
- Record local and remote `main` SHAs.
- Inspect dirty and untracked paths.
- Identify live scientific executions and source-hashed artifacts.
- Read the active issue, parent tracker, and latest steering comments.
- Decide whether the active step is analytic, execution-bearing, execution-only
  engineering, or exposition.
- Declare the checkpoint's evidence, quantifier, and stability levels.
- Separate NEED, SHOULD, and COULD burdens.
- Name the prepared domain and how nonemptiness will be established.
- Record effective assumptions and explicit deferrals.
- Name the single load-bearing question and stop rule.
- Create an issue-scoped feature branch and isolated worktree for mutable
  scientific construction. Keep the main checkout as an integration surface.
- Leave live frozen executions and their source-hashed artifacts untouched
  unless their disposition is explicitly in scope.

## Mutable branch cadence

- Commit and push each coherent derivation, analytic note, audit, source
  inventory, or non-decisive engineering utility.
- If a packet or script will emit a pass/fail scientific decision, keep its
  predicates, tolerances, comparator code, fixtures, runner, and source bindings
  uncommitted until adversarial review accepts those exact mutable bytes. Their
  first commit is the joint freeze commit with the review record.
- Mark every pre-freeze scientific artifact mutable, non-authoritative, and
  incapable of emitting a protocol verdict.
- Bind design reviews to exact pushed commits for non-decisive analytic work or
  deterministic working-tree manifests for decision-bearing candidates.
- Treat every scientific revision as a new candidate SHA requiring renewed
  review.
- Do not leave source or provenance untracked through a context switch, long
  calculation, review request, or end of session.
- Write generated matrices, caches, logs, and resumable outputs to a bound
  external scratch location rather than the source tree.
- Move nonblocking strengthening to SHOULD or COULD rather than expanding the
  active issue after its NEED burden is clear.

## Before freeze and mainline integration

- Construction is no longer a first draft.
- The evidence, quantifier, and stability levels are still the reviewed levels.
- The NEED set is explicit and unchanged after review.
- The successful domain is proved nonempty at the declared level.
- Effective assumptions and nonclaims are visible in the candidate.
- SHOULD and COULD items are recorded as nonblocking deferrals unless formally
  promoted.
- A non-decisive analytic candidate has a clean worktree and pushed exact commit.
- A decision-bearing candidate remains uncommitted, is bound by an exact
  working-tree manifest, and has not appeared in any earlier commit.
- The mutable design review resolved every blocking NEED finding.
- Substantive local validation completed before final exact-byte acceptance.
- Validation is proportional to the NEED set rather than to every possible
  stronger theorem.
- A deterministic candidate manifest records the reviewed base, exact path set,
  file SHA-256 values, and manifest hash.
- Independent review says `ACCEPT` for the exact base, changed-path set,
  candidate manifest, selected evidence, quantifier, and stability levels, NEED
  set, and validation evidence being integrated.
- The current candidate bytes still match the accepted manifest; any scientific
  change received renewed review.
- Every contradiction, circularity, vacuity, protected-boundary violation, and
  failed NEED finding was repaired before freeze/integration.
- No scientific byte changed after the accepted review; if one did, renewed
  review accepted the revised candidate.
- Dedicated and inherited validators pass when their hypotheses are consumed by
  the NEED claim.
- Exact formulas were independently recomputed where practical and load-bearing.
- Builder and validator do not share an unreviewed hard-coded expected table,
  dependency allowlist, or sign convention.
- Load-bearing maps, inverses, reactions, and source bindings are explicit
  formulas or executable symbolic data at the level required by the claim, not
  prose placeholders.
- Large generated NEED registries are backed by a reviewed template theorem and
  exact expansion check rather than repetitive row-by-row prose.
- Representation-invariance and semantic-sensitivity checks pass for the NEED
  predicates.
- Unimplemented SHOULD and COULD items are not required to have mutations or
  validators.
- Schema, serializer, and exact-type round trips pass where relevant.
- `git diff --check` passes.
- Markdown math and links pass.
- Source hashes are current.
- Exact validation commands, exit statuses, decisive counts, and artifact hashes
  are captured for the issue disposition.
- The changed-file list is exactly the intended artifact set.
- No unrelated user work or live artifact is included.
- If a steering note was applied, the issue comment or closure is already part
  of the plan rather than an afterthought.
- The stop rule is satisfied; no post-gate depth work was added merely because it
  was attractive.

## Freeze, integrate, and push

1. Create the freeze commit with the reviewed definition, decision code when
   applicable, source bindings, review record, evidence level, quantifier level,
   stability level, NEED set, effective assumptions, and deferrals. For a
   decision-bearing candidate, verify this is the first commit containing those
   files.
2. Reconfirm `main` has not moved.
3. If it moved, determine whether frozen inputs, theorem dependencies, any NEED
   premise, source hashes, or reviewed paths changed; renew review when they did.
4. Integrate only the reviewed files and verify their hashes or semantic diff
   against the accepted candidate.
5. If history is squashed or transplanted, verify every scientific file hash
   against the accepted manifest.
6. Rerun every validation affected by the synchronized base.
7. Inspect the mainline commit diff, source bindings, evidence scope, and hashes.
8. Push normally to `main` and verify the remote head.
9. Retain the pushed mutable branch as non-authoritative development provenance
   according to repository retention policy.

Never:

- force-push;
- reset destructively;
- rewrite frozen history;
- commit a decisive first draft directly to main and review it afterward;
- confuse a mutable feature-branch commit with a frozen candidate or verdict;
- split one scientific disposition into authorization/status/review-of-review
  commits;
- use a PR loop merely to obtain code-centric review for direct-main theorem
  work;
- push code that changes a live frozen execution's scientific identity;
- block an E0-E2 checkpoint on unpromoted global regularity, all-configuration
  stability, exhaustive diagnostics, or deeper-theory derivation;
- present a scoped witness or effective model as a global theorem.

## After push

- Comment the active issue with commit, artifacts, validations, evidence level,
  quantifier level, stability level, NEED set, effective assumptions, deferrals,
  and exact disposition.
- Close only if the issue's pass or stop rule is satisfied.
- Update the parent dependency graph when the result changes readiness.
- Refresh all related issues for steering notes.
- Select the highest-priority newly unblocked NEED task.
- Do not automatically activate SHOULD or COULD work after a valid checkpoint;
  stop when the steering contract requires it.

## When a decisive execution follows

The freeze commit precedes execution. Inspect and record hashes first. Run the
qualified frozen decision exactly as authorized, persist comparator rows
atomically, and separate engineering status, execution validity, protocol
verdict, and scientific inference. The first real comparator start begins the
trial. A later crash consumes a partial trial; only durable completed rows are
scientific evidence. Fix execution-only defects normally, but do not infer
replay authority from the fix itself.
