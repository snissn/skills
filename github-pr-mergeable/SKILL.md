---
name: "github-pr-mergeable"
description: "Drive one or more GitHub pull requests through mergeable readiness and merge by default when coordinator-owned and gates pass: deep review, test/benchmark coverage, PR description quality, latest-head CI, AI review resolution, and optional merge execution."
---

# GitHub PR Mergeable Loop

Use this skill when the user asks to make PRs mergeable, stabilize PRs, resolve reviews, get CI green, prepare a PR stack for review, or ensure Codex/Copilot/CodeRabbit are passing. Default assumption: the user wants eligible PRs merged after they satisfy the mergeable gate, unless the user explicitly says **do not merge** or the agent is acting as a non-coordinator subagent.

## Definition Of Mergeable

A PR is mergeable only when current evidence proves:

- latest PR head has no merge conflicts;
- latest-head CI is passing or explicitly non-blocking with a documented reason;
- code has had an internal deep review for correctness, drift, complexity, and tests;
- tests cover the behavior changed by the PR;
- performance-sensitive changes include relevant benchmark evidence in the PR body or a PR comment, and do **not** show an unaccepted material regression;
- Codex, Copilot, and CodeRabbit reviews have been requested after meaningful pushes where available;
- AI review findings are fixed or explicitly rejected with rationale;
- review threads are commented on and marked resolved where the platform supports resolution;
- PR description accurately states scope, tests, benchmarks, risks, and remaining caveats.

Do not use stale green checks, stale reviews, or older benchmark numbers as proof for the latest head.

## Performance Regression Gate

For any PR that touches a hot path, storage/read/write path, cache, search, decode, query, serialization, materialization, benchmark harness, or persistent format, a material local regression is a **blocking mergeability failure** by default.

A regression includes worse `ns/op`, `ops/sec`, `B/op`, `allocs/op`, rebuild/storage overhead, latency sub-timers, or domain counters caused by the PR’s own code. When evidence shows a regression:

1. Mark the PR **not mergeable / performance-blocked** in the handoff or PR comment.
2. Profile and optimize the changed path before merging; remove avoidable extra work, allocations, copies, I/O, locks, scans, or setup inside the measured boundary.
3. Rerun the identical before/after benchmark matrix on the latest head and update the PR evidence.
4. Merge only if the regression is eliminated, or if the remaining regression is proven correctness-required/unavoidable, minimized, explicitly documented with impact and profiles, and accepted by the coordinator/user.

Do not normalize regressions as “expected overhead” without this investigation and explicit acceptance.

## Inventory First

For each PR, gather:

```sh
gh pr view <PR> --repo <OWNER>/<REPO> \
  --json number,title,url,state,headRefName,baseRefName,headRefOid,mergeStateStatus,isDraft,reviewDecision,statusCheckRollup,comments,reviews

gh pr checks <PR> --repo <OWNER>/<REPO>

gh run list --repo <OWNER>/<REPO> --branch <HEAD_BRANCH> --limit 20
```

Also inspect local branch state when working in a checkout:

```sh
git status --short
git branch --show-current
git log --oneline --decorate -n 8
```

If the worktree is dirty, preserve unrelated user edits. Use a detached worktree per PR or stack branch when that keeps changes auditable.

## Internal Deep Review

Before requesting external/AI review, do your own review:

- read the diff against the intended base;
- identify correctness risks, behavioral regressions, race/concurrency risks, persistence/reopen risks, and missing tests;
- verify public wording does not overstate what the code proves;
- check for unnecessary complexity, dead transitional code, duplicate abstractions, and drift from the tracker/issue;
- for performance-sensitive code, look for hot-loop allocations, extra memcopies, repeated setup/open/decode, broad locks, full-column/full-index scans, stale caches, or misleading benchmark labels.

If findings are real, fix them before treating the PR as review-ready.

## Tests

Every PR should have test evidence that matches its scope.

- Run focused tests for the changed package/path first.
- Run broader affected tests before final review.
- Add tests when coverage is missing; do not rely only on existing tests if the PR adds new behavior.
- For persistence/storage changes, include close/reopen and corruption/mismatch tests where relevant.
- For concurrency/cache/snapshot changes, include race or concurrent sanity tests where feasible.
- For public API changes, include end-to-end API tests, not just helper tests.

Report exact commands and outcomes in the PR body or comment.

## Benchmarks And Performance Evidence

If the PR touches a hot path, storage/read path, cache, search, decode, query, serialization, or materialization path, include benchmark evidence.

Benchmark comments/descriptions should include:

- exact command;
- hardware/context if known;
- commit or branch;
- dataset shape;
- what is timed and what is excluded;
- `ns/op`;
- `ops/sec`;
- `B/op`;
- `allocs/op`;
- relevant domain counters such as rows/s, queries/s, bytes read, cache hits/misses, candidates/search, edges/search, or docs fetched.

Use markdown tables. Always include `ops/sec` when reporting `ns/op`.

Do not optimize unrelated upstream cost inside every PR, but do not accept local regressions from the PR’s own code. If performance drops after review fixes, identify the change that caused it, whether it was correctness-required, and whether local CPU/memcopy/allocation overhead can be removed. A PR with an unexplained or avoidable material regression is not mergeable even if CI and AI reviews are green.

## CI Discipline

Use latest-head evidence only.

- If GitHub is backed up, cancel stale CI runs that are not for the current head of active PR branches when safe.
- In stacked/chained PRs, cancel stale runs for superseded intermediate heads after a batch propagation; keep only latest-head CI for active PR heads.
- Ensure the latest commit for each relevant PR has active or completed CI.
- Do not treat green checks from an older head as proof.
- If a check is flaky or external, document the retry/result and current status.

Useful commands:

```sh
gh run list --repo <OWNER>/<REPO> --branch <HEAD_BRANCH> --json databaseId,headSha,status,conclusion,displayTitle,workflowName,createdAt
gh run cancel <RUN_ID> --repo <OWNER>/<REPO>
gh run watch <RUN_ID> --repo <OWNER>/<REPO>
```

Cancel only stale/non-head runs unless the user explicitly authorizes broader cleanup. Do not cancel the only active CI for a PR head unless you are about to push or have already pushed a newer head.

## AI Review Loop

After meaningful pushes and before final mergeable claim, request reviews from configured AI reviewers.

Use the repo’s established commands when known. Common pattern:

```sh
gh pr comment <PR> --repo <OWNER>/<REPO> --body "@codex review"
gh pr comment <PR> --repo <OWNER>/<REPO> --body "@copilot review"
gh pr comment <PR> --repo <OWNER>/<REPO> --body "@coderabbitai review"
```

If one of those bots uses a different repo-specific trigger, follow the repo convention. If a bot is unavailable, say so explicitly and do not claim it passed.

For each AI review:

- read all findings, not just summaries;
- verify each suggested patch before applying;
- fix real issues with minimal, scoped changes;
- reject incorrect findings with a PR comment explaining why;
- mark review threads resolved after fixing or explicitly dismissing;
- re-request review after meaningful fixes until reviews are quiet/passing or intentionally resolved.

## Review Thread Resolution

Prefer GitHub review-thread APIs or the UI-equivalent through `gh api graphql` when needed. At minimum, inventory unresolved threads and ensure each has a clear disposition.

GraphQL inventory shape:

```graphql
query($owner:String!, $repo:String!, $number:Int!) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$number) {
      reviewThreads(first:100) {
        nodes {
          id
          isResolved
          path
          line
          comments(first:20) {
            nodes {
              author { login }
              body
              url
            }
          }
        }
      }
    }
  }
}
```

For unresolved AI threads:

- fix the code or document why no code change is appropriate;
- reply in the PR/thread with the disposition;
- resolve the thread if resolved by code or rationale.

Do not leave dangling AI review threads when claiming mergeable.

## PR Description / Comment Requirements

Ensure the PR body or a final status comment includes:

- what changed;
- linked issue/tracker;
- path identity and scope boundary;
- tests run with exact commands;
- benchmark table if relevant;
- CI status for latest head;
- AI review status for Codex, Copilot, and CodeRabbit;
- known caveats or intentionally deferred work;
- merge intent/status: merged by coordinator, pending merge, or intentionally not merged with reason.

For stacked PRs, also include base PR/branch, dependency order, and whether downstream PRs need rebasing after changes.

## Stacked PR Workflow

For a stack, work bottom-up for merge conflicts and CI, but keep wall time efficient:

- inventory the whole stack first;
- stabilize the lowest blocking PR;
- propagate fixes/rebases upward when necessary, but batch propagation instead of restacking after every tiny commit;
- while CI/reviews run on one PR, make non-conflicting progress on the next;
- after each base PR changes, re-check downstream mergeability and tests;
- keep each PR reviewable by avoiding unrelated cleanup.

Chained PRs need churn control. Avoid quadratic pain from repeatedly merging every base change into every descendant:

- Identify the dependency chain: `main -> PR A -> PR B -> PR C`, including branch names and head SHAs.
- Classify each change as stack-wide, local to one PR, or review-only/docs-only.
- For stack-wide fixes, batch related fixes on the lowest applicable PR, then merge/rebase upward once for the batch.
- For local fixes, keep them on the owning PR and do not churn unrelated downstream branches unless needed for conflicts, tests, or review.
- Limit the number of branches restacked at once. Prefer a small active window, such as the current base PR plus the next one or two dependent PRs, unless the user asks for full-stack propagation.
- Do not repeatedly trigger CI for every intermediate head if another propagation batch is imminent. Push a coherent batch, then let latest-head CI run.
- After propagation, cancel stale non-head CI runs for branches whose head changed.
- Preserve reviewability: if a propagation would turn a PR into a huge diff, consider splitting or pausing to ask whether to create a new chained PR.
- Keep PR descriptions updated with current base branch/PR, whether upstream changes were merged in, and whether downstream PRs still need propagation.

Preferred batch workflow:

1. Fix and test the lowest real blocker.
2. Run focused local validation.
3. Push that PR head.
4. If the fix affects descendants, merge/rebase it into a bounded downstream batch.
5. Push downstream batch heads.
6. Cancel stale non-head CI runs.
7. Request/re-request AI reviews only after each PR has the coherent latest head that reviewers should inspect.
8. Watch CI/reviews while doing non-conflicting work on the next bounded batch.

When acting as the coordinator and the user has not opted out, merge PRs after the Definition Of Mergeable is satisfied. When acting as a manager/subagent, do not merge directly unless the coordinator explicitly delegates that authority; hand off mergeable evidence to the coordinator.

## Final Response

When reporting back, provide:

- PRs made mergeable;
- PRs still blocked and the exact blocker;
- latest-head CI status;
- AI review status;
- tests/benchmarks run;
- any local branches/worktrees created;
- any risks that remain.

Keep it evidence-backed and do not overclaim.
