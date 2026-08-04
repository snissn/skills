---
name: "github-pr-mergeable"
description: "Drive one or more GitHub pull requests through mergeable readiness, and merge only when repo policy and user authorization permit: deep review, test/benchmark coverage, PR description quality, latest-head CI, AI review resolution, and optional merge execution."
---

# GitHub PR Mergeable Loop

Use this skill when the user asks to make PRs mergeable, stabilize PRs, resolve reviews, get CI green, prepare a PR stack for review, or ensure Codex-required review and optional reviewer feedback are handled.

Default assumption: make eligible PRs mergeable. Merge execution is allowed only when repo policy permits it and the user has authorized merge execution, either explicitly in the current request or through a repo/workstream rule that clearly delegates it. If repo policy requires human approval, prohibits self-merge, or says agents must not merge, stop at mergeable evidence and hand off.

## Policy Audit First

Before merge-related action, inspect repo-local policy when available:

- `AGENTS.md`;
- `CONTRIBUTING.md`;
- PR templates;
- branch protection or merge policy docs;
- tracker issues or roadmap docs named by the user.

Repo-local rules override this skill. If policy and user instructions conflict, follow the stricter/no-merge interpretation unless the user explicitly authorizes a documented exception.

Audit policy from the actual checkout/worktree for **each** adopted PR, not only the coordinator's current directory. Enumerate every tracked `AGENTS.md` at the PR head (for example, `git ls-tree -r --name-only <head> | grep -E '(^|/)AGENTS\.md$'` or the recursive GitHub tree API), map changed paths to all root and nested policy files whose directory scope contains them, and read those exact-head bytes. Include an `AGENTS.md` added or modified by the PR. Record any review-round cap, proportionality rule, scientific acceptance path, or stop condition before requesting a reviewer. A repository-local review stop is merge policy, not an optional suggestion.

## Operating Modes

- `readiness-only`: make the PR or stack objectively mergeable, but do not merge.
- `mergeable-with-human-approval`: make the PR or stack mergeable and clearly state that human approval/merge is required.
- `coordinator-merge`: make and merge PRs only when repo policy allows agent/coordinator merge and the user has authorized it.

If the mode is ambiguous, default to `readiness-only`.

## Definition Of Mergeable

A PR is mergeable only when current evidence proves:

- latest PR head has no merge conflicts;
- latest-head CI is passing or explicitly non-blocking with a documented reason;
- code has had an internal deep review for correctness, drift, complexity, and tests;
- tests cover the behavior changed by the PR;
- performance-sensitive changes include relevant benchmark evidence in the PR body or a PR comment, do **not** show an unaccepted material regression, and meet any explicit improvement/saturation gate unless the PR is explicitly instrumentation/safety-only or a linked blocker/waiver is recorded;
- Codex review, when required by the effective repository/workstream policy, has been requested only after the PR is mature enough to avoid review-credit churn, and after meaningful pushes where available;
- when Codex remains required, the latest-head review has completed cleanly as either an explicit no-findings issue comment or an approved/clean review tied to the exact head SHA, with no unresolved Codex threads, or Codex is explicitly unavailable after a documented bounded retry window and the user/repo policy permits proceeding without it;
- when repository-local proportionality or scientific stop rules replace the default Codex gate, the PR records that policy, the bounded review disposition, and the acceptance evidence required by that policy; every existing thread is still fixed or explicitly rejected with rationale;
- optional reviewers such as CodeRabbit and Copilot have either produced no usable response, are rate-limited/unavailable, or had every actual finding/check/thread resolved; optional acknowledgement reactions alone do not block mergeability;
- AI review findings are fixed or explicitly rejected with rationale;
- review threads are commented on and marked resolved where the platform supports resolution;
- PR description accurately states scope, tests, benchmarks, risks, and remaining caveats.

Do not use stale green checks, stale reviews, or older benchmark numbers as proof for the latest head.

## Performance Regression Gate

For any PR that touches a hot path, storage/read/write path, cache, search, decode, query, serialization, materialization, benchmark harness, or persistent format, a material local regression is a **blocking mergeability failure** by default.

A regression includes worse `ns/op`, `ops/sec`, `B/op`, `allocs/op`, rebuild/storage overhead, latency sub-timers, or domain counters caused by the PR’s own code. When evidence shows a regression:

1. Mark the PR **not mergeable / performance-blocked** in the handoff or PR comment.
2. Profile and optimize the changed path before mergeability can be claimed; remove avoidable extra work, allocations, copies, I/O, locks, scans, or setup inside the measured boundary.
3. Rerun the identical before/after benchmark matrix on the latest head and update the PR evidence.
4. Claim mergeability only if the regression is eliminated, or if the remaining regression is proven correctness-required/unavoidable, minimized, explicitly documented with impact and profiles, and accepted by the coordinator/user.

Do not normalize regressions as “expected overhead” without this investigation and explicit acceptance.

## Insufficient Improvement Gate

For optimization PRs with explicit improvement, saturation, latency, throughput, allocation, or counter targets, **no regression is not enough**.

If latest-head evidence is neutral or misses the stated gate:

1. Mark the PR **not mergeable / gate-blocked** unless the issue is explicitly instrumentation-only or safety-only.
2. Profile the latest head to identify the next limiter and decide whether the same PR should continue iterating.
3. If the PR cannot reasonably meet the gate, update the tracker/PR with the measured blocker and open or link a follow-up issue that blocks downstream/final-gate completion.
4. Include a root-cause classification for the miss before choosing the next action: weak substrate, insufficient work shape, serial fan-in, coordination/locking, external sync/I/O, or benchmark noise.
5. Claim mergeability only after the gate passes, the PR is explicitly re-scoped, or the coordinator/user records an explicit waiver with evidence and impact.

Do not close performance stacks by documenting "insufficient improvement" as the default outcome. The default loop is iterate, fix, or mutate the graph with a real blocker.

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

For Codex review state, use the bundled classifier instead of inspecting only
the pull-request `reviews` array:

```sh
python "${CODEX_HOME:-${HOME}/.codex}/skills/github-pr-mergeable/scripts/codex_review_gate.py" \
  --repo <OWNER>/<REPO> --pr <PR> --check
```

The classifier inventories paginated issue comments, formal reviews, and review threads. Exit `0` means the Codex-specific gate is clean; exit `2` means its JSON result names the pending request, findings, unresolved threads, retry exhaustion, or PR-lifetime churn stop. A churn-stop result is an action boundary, not permission to ignore threads. If repository policy supplies a bounded alternative scientific acceptance path, evaluate and record that path separately. CI and the other merge gates remain separate.

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

Benchmark comments/descriptions should include domain-appropriate metrics. For Go/Rust microbenchmarks this often includes:

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

Use markdown tables. Always include `ops/sec` when reporting `ns/op`. For other domains, use metrics that match the claimed improvement, such as wall time, per-unit latency, p95/p99, memory footprint, bundle size, browser responsiveness, GPU/CPU utilization, or per-stage timing.

Do not optimize unrelated upstream cost inside every PR, but do not accept local regressions from the PR’s own code. If performance drops after review fixes, identify the change that caused it, whether it was correctness-required, and whether local CPU/memcopy/allocation overhead can be removed. A PR with an unexplained or avoidable material regression is not mergeable even if CI and AI reviews are green. A PR with insufficient improvement against its explicit optimization gate is likewise not mergeable until it iterates, re-scopes, or links a blocker/waiver as described above.

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

## Cross-Head Review Churn Breaker

Review budgets apply across the lifetime of the PR, not only to one head SHA. A repair commit does not erase earlier finding-bearing review rounds.

Before every new Codex request:

1. inventory total PR-lifetime review requests, distinct finding-bearing heads, and review threads;
2. apply any lower repository-local review-round cap;
3. classify findings as claim/contract blockers, implementation defects inside the declared scope, claim/authority mismatches, nonblocking hardening, or incorrect findings;
4. batch all current fixes and audit sibling invariants before asking for another review.

Absent a lower repository rule, stop automatically after either **three finding-bearing heads** or **six total Codex requests** across the PR. Run the classifier with `--max-finding-heads` and `--max-total-requests` when local policy specifies lower limits. When it reports `review_churn_blocked`, or reports unresolved findings with `review_churn_exhausted=true`:

- disposition the current threads, but do not request another review;
- transition the PR to an architecture/claim/scope reset;
- prefer rejecting an incorrect finding, narrowing emitted authority, splitting the PR, or deferring nonblocking hardening over expanding the implementation for every counterexample;
- update the PR/tracker with the stop reason and next decision;
- obtain explicit project-owner authorization before using `--allow-after-churn`.

A clean exact-head result remains terminal even when the historical budget was exceeded. The churn breaker prevents another request; it does not permit unresolved findings to be ignored.

## Mature PR Before AI Review

Do not request Codex, Copilot, CodeRabbit, or other review-credit-consuming AI reviewers merely because a PR exists. Codex is the required final AI reviewer by default only when repository/workstream policy does not define a different proportional review or scientific acceptance gate; CodeRabbit and Copilot are optional unless repo policy makes their checks required. First make the PR mature enough that the requested review is likely to inspect the intended final shape:

- coherent code for the scoped issue is pushed;
- focused tests and required benchmarks have run, or the PR body states why a required benchmark is not yet applicable;
- the PR body or status comment includes current scope, tests, benchmark evidence, known risks, and non-goals;
- internal deep review has found no known blocking correctness, performance, CI, or scope issues;
- latest-head CI is running or already green for the head that should be reviewed.

If a later meaningful push changes code, benchmarks, or review-relevant behavior, restore this maturity gate before re-requesting AI review. Do not churn AI review credits across half-formed intermediate heads, speculative stack propagation, or PRs with known local blockers.

## AI Review Loop

After meaningful pushes, after the maturity gate above is satisfied, and before final mergeable claim, request reviews from configured AI reviewers.

Default assumption for ordinary code PRs without a contrary local rule: Codex should be requested and must complete on the latest head unless explicitly unavailable. For scientific/analytic work, apply repository proportionality and review-stop rules before this default. CodeRabbit and Copilot may be requested when useful, but they are opportunistic reviewers: rate limits, non-response, or acknowledgement-only reactions are documented and do not block mergeability unless repo policy or branch protection makes their check required.

Use the repo’s established commands when known. Common pattern:

```sh
gh pr comment <PR> --repo <OWNER>/<REPO> --body "@codex review"
gh pr comment <PR> --repo <OWNER>/<REPO> --body "@copilot review"
gh pr comment <PR> --repo <OWNER>/<REPO> --body "@coderabbitai review"
```

Before every Codex trigger, run `scripts/codex_review_gate.py`. Do not trigger
when it reports `clean`, `findings`, or `should_request=false`. A clean result
is terminal for the unchanged head; a later duplicate trigger does not make it
pending again. A later Codex findings review or unresolved Codex thread does
supersede the earlier clean result.

Default to one initial request and at most two retries for the same head, with at least ten minutes between triggers, subject to the stricter PR-lifetime churn budget above. After that, record Codex as unavailable instead of spamming the PR. A user may explicitly raise a cap, but may not bypass re-inventory, a repository-local stop rule, the cross-head churn reset, or the stop-on-clean rule without explicit authorization for that exception.

If one of those bots uses a different repo-specific trigger, follow the repo convention. If a bot is unavailable, say so explicitly and do not claim it passed.

For each AI review that produces comments, checks, review threads, or findings:

- read all findings, not just summaries;
- verify each suggested patch before applying;
- classify whether each finding affects the declared claim/contract and authority;
- fix real in-scope blockers with minimal, scoped changes;
- reject incorrect findings with a PR comment explaining why;
- narrow claims or defer nonblocking hardening instead of silently expanding scope;
- mark review threads resolved after fixing or explicitly dismissing;
- run a sibling-invariant/internal review over the whole batch;
- re-request at most once for the mature batch when both local and PR-lifetime review budgets permit it.

### Final AI Review Completion Gate

Before posting final mergeability evidence or merging, re-inventory each requested AI reviewer against the exact latest head SHA:

- When Codex is required by the effective policy, run the bundled classifier for the final decision; do not infer state from `reviews` alone. When a repository-local proportional scientific gate supersedes Codex, record the policy and its exact acceptance evidence instead.
- Codex commonly emits a clean result as an issue comment from
  `chatgpt-codex-connector[bot]` containing both `Codex Review: Didn't find any
  major issues` and `Reviewed commit: <sha>`. That exact-head comment is a
  completed clean artifact even when no formal review object exists. Stop
  requesting reviews for that head immediately.
- Codex emits findings as formal `COMMENTED` reviews and inline review threads.
  Any unresolved Codex thread blocks. If several artifacts exist for one head,
  the latest substantive Codex artifact wins; trigger comments are requests,
  not review artifacts.
- Match the `Reviewed commit` prefix or formal review `commit_id` to the full
  current head. Never use a clean artifact from an older head.
- If Codex acknowledged or started a latest-head review but the classifier has
  no exact-head artifact, treat it as **pending** until the bounded retry policy
  completes.
- Do not merge while a policy-required Codex latest-head review is pending, even if `mergeable=MERGEABLE`, `mergeStateStatus=CLEAN`, local validation passes, or earlier review threads have been resolved. Do not manufacture a Codex requirement when repository-local policy explicitly uses a bounded scientific acceptance path.
- CodeRabbit and Copilot are optional/conditional by default. If either returns a completed review, check, inline comment, or review thread, fix real findings or explicitly reject them with rationale and resolve threads. If either is rate-limited, unavailable, acknowledgement-only, or silent after a documented retry/window, record that disposition and proceed when the required gates are clean.
- If an optional reviewer has an active required status check under branch protection, treat that check as CI and wait for it or document why it is non-blocking. Do not treat a plain acknowledgement reaction from an optional reviewer as a pending merge blocker.
- A reaction alone is not a clean artifact. Require an explicit exact-head
  clean comment/review plus zero unresolved Codex threads.
- If an optional review completes after the PR was merged and reports real findings, open or push a follow-up fix PR and resolve the late threads.

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
- explicit improvement/saturation gate status for optimization PRs: pass, fail/fix-needed, re-scoped instrumentation/safety-only, linked blocker, or explicit waiver;
- CI status for latest head;
- AI review status for required Codex and optional CodeRabbit/Copilot dispositions;
- known caveats or intentionally deferred work;
- merge intent/status: mergeable handoff, pending human approval, merged by authorized coordinator, or intentionally not merged with reason.

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
7. Request/re-request AI reviews only after each PR has the mature, coherent latest head that reviewers should inspect.
8. Watch CI/reviews while doing non-conflicting work on the next bounded batch.

Merge only when the selected operating mode is `coordinator-merge`, repo policy permits it, and the user has authorized it. Otherwise, do not merge directly; hand off mergeable evidence to the coordinator or human reviewer.

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
