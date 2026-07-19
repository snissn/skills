# Direct Mainline Checklist

Direct commits to `main` are appropriate for this workflow only when the user
or repository has explicitly chosen them over a PR loop.

## Before editing

- Read `AGENTS.md`.
- Fetch or sync the remote.
- Record local and remote `main` SHAs.
- Inspect dirty and untracked paths.
- Identify live scientific executions and source-hashed artifacts.
- Read the active issue, parent tracker, and latest steering comments.
- Decide whether the active step is analytic, execution-bearing, execution-only
  engineering, or exposition.
- Name the single load-bearing question and separate blockers, parallel
  controls, polish, and deferred extensions.
- Use an isolated worktree if the main checkout is dirty or context-specific.
- Leave live frozen executions and their source-hashed artifacts untouched
  unless their disposition is explicitly in scope.

## Before committing

- Construction is no longer a first draft.
- The mutable design review resolved every scientific blocker.
- Substantive local validation completed before final exact-byte acceptance.
- A deterministic candidate manifest records the reviewed base, exact path set,
  file SHA-256 values, and manifest hash.
- Independent review says `ACCEPT` for the exact base, changed-path set, and
  candidate manifest and validation evidence being integrated.
- The current candidate bytes still match the accepted manifest; any
  scientific change received renewed review.
- Every blocking finding was repaired before freeze/integration.
- No scientific byte changed after the accepted review; if one did, renewed
  review accepted the revised candidate.
- Dedicated and inherited validators pass.
- Exact formulas were independently recomputed where practical.
- Builder and validator do not share an unreviewed hard-coded expected table,
  dependency allowlist, or sign convention.
- Load-bearing maps, inverses, reactions, and source bindings are explicit
  formulas or executable symbolic data, not prose placeholders.
- Large generated registries are backed by a reviewed template theorem and
  exact expansion check rather than repetitive row-by-row prose.
- Representation-invariance and semantic-sensitivity checks pass.
- Schema, serializer, and exact-type round trips pass where relevant.
- `git diff --check` passes.
- Markdown math and links pass.
- Source hashes are current.
- Exact validation commands, exit statuses, decisive counts, and artifact
  hashes are captured for the issue disposition.
- The changed-file list is exactly the intended artifact set.
- No unrelated user work or live artifact is included.
- If a steering note was applied, the issue comment or closure is already part
  of the plan rather than an afterthought.

## Commit and push

1. Reconfirm `main` has not moved.
2. If it moved, determine whether frozen inputs, dependencies, source hashes,
   or reviewed paths changed; renew review when they did.
3. Integrate only the reviewed files and verify their hashes or semantic diff
   against the accepted candidate.
4. Rerun every validation affected by the synchronized base.
5. Commit one coherent scientific result.
6. Inspect the commit diff, source bindings, and hashes.
7. Push normally to `main`.
8. Verify the remote head equals the pushed commit.

Never:

- force-push;
- reset destructively;
- rewrite frozen history;
- commit a decisive first draft and review it afterward;
- split one scientific disposition into authorization/status/review-of-review
  commits;
- use a PR loop merely to obtain code-centric review for direct-main theorem
  work;
- push code that changes a live frozen execution's scientific identity.

## After push

- Comment the active issue with commit, artifacts, validations, and exact
  disposition.
- Close only if the issue's pass or stop rule is satisfied.
- Update the parent dependency graph when the result changes readiness.
- Refresh all related issues for steering notes.
- Select the highest-priority newly unblocked task.

## When a decisive execution follows

The freeze commit precedes execution. Inspect and record hashes first. Run the
qualified frozen decision exactly as authorized, persist comparator rows
atomically, and separate engineering status, execution validity, protocol
verdict, and scientific inference. The first real comparator start begins the
trial. A later crash consumes a partial trial; only durable completed rows are
scientific evidence. Fix execution-only defects normally, but do not infer
replay authority from the fix itself.
