# Hosted CI capacity

Use this when concurrent graph PRs, repeated pushes, or long CI queues make
hosted-runner demand relevant. This is an operational aid, not another merge
gate, a reason to serialize independent construction, or authority to take over
an unrelated CI project.

## Identify the constraint

1. Inspect the **current** workflow files and their actual `push`,
   `pull_request`, `merge_group`, manual and scheduled triggers; include matrix
   rows, `needs`, job conditions, existing concurrency groups and required
   aggregate/ruleset checks. A single PR update may produce separate push and PR
   runs, and a draft or non-PR branch may still run push workflows. Include
   default-branch work and relevant other PRs in a bounded read-only sample.
2. Bind evidence to repo, event, branch/PR, workflow, run ID, attempt, head SHA
   and job ID. Inspect job creation, runner assignment/start, completion and
   step durations. Job creation-to-start is a **wait proxy**, not necessarily
   runnable queue time: check dependencies, approvals, concurrency groups and
   event processing first. Distinguish queue, runner occupation, workflow
   elapsed time, critical path and billing. Never infer the configured account
   limit or cause of a queue from timing alone; other repositories and runner
   pools may share the account's capacity.
3. With Python 3.10+ and authenticated `gh`, inspect a small, explicit set of
   run IDs without mutating GitHub:

   ```sh
   python3 "${SKILLS_ROOT:-${HOME}/.codex/skills}/codex-issue-graph-executor/scripts/ci_capacity.py" \
     --repo OWNER/REPO --run-id RUN_ID --run-id OTHER_RUN_ID --show-steps
   ```

   It reads all job pages for each current attempt, rechecks attempt/head
   identity, and emits JSON. A partial rerun may expose only jobs in that
   attempt; inspect earlier attempts separately for complete lineage. The
   default label filter is `macos`; use
   `--label windows`, `--label linux`, or `--label ''` for all jobs. Empty or
   missing labels are counted as unknown and are excluded by a nonempty filter.
   `creation_to_start_seconds` is null without a runner assignment or while
   the job is queued; `age_since_creation_seconds` is only an age for a queued job,
   not proof it was eligible for a runner. Completed step times diagnose which
   phase consumed time, but do not split compilation, downloads and analysis
   occurring inside the same command. Missing timestamps remain null. The
   sample is not an account-wide inventory or a savings estimate.
4. Inspect logs and the source for a slow command before choosing caching,
   sharding or tooling changes. Preserve test commands and coverage; compare
   cold/warm behavior, actual cache restore/save and hit rates, trust and
   invalidation, CPU/memory, and runner time on comparable candidates. A faster
   setup step does not establish a faster vet/test command, and cached test
   results do not replace required current-candidate execution.

## Reduce starts before speeding up jobs

For a CI-demand change, map each expensive lane to its purpose: PR correctness,
post-merge integration, routine benchmark, or pinned evidence/release. Find
same-candidate push/PR overlap, but compare the actual tested ref and assertions
before treating two runs as interchangeable. Prefer one ordinary PR route over
an unrestricted branch push plus PR route for the same purpose. Keep full
default-branch integration and deliberate manual or pinned qualification. Move
heavy routine benchmarks off ordinary pushes where a cheap PR smoke protects the
changed path; do not make the smoke stand in for scale or latency qualification.

Scope costly platform jobs by their actual inputs, including transitive shared
code, build metadata, harness changes and CI configuration, not package prefixes
alone. For required checks, keep a stable aggregate and validate why each omitted
job is inapplicable; uncertain impact takes the full path. Don't silently drop a
unique platform check just because another workflow also requests that OS.

Record intended behavior for a relevant PR, an unrelated PR, a rapid replacement
head, parallel PRs/forks, and main/manual/merge-group runs that must survive.
Test the event and impact cases, then verify actual hosted admissions and latest
head coverage. Review live branch protection/rulesets before changing check names;
GitHub Actions configuration belongs in workflow files, and does not by itself
require an admin setting change. Report avoided job starts, runner time and
observed wall time separately; label anything not yet verified on GitHub.

## Reduce obsolete work safely

**Local pre-push gate, draft discipline, and review-window batching:** before
every PR push, verify formatting (`gofmt -l` clean for Go), static checks
(`go vet`/linters), affected package tests, and doc-contract checks when
docs/specs changed so hosted runners are never burned on avoidable format or
compile failures. Keep incomplete WIP iterations in Draft PRs (which run
lightweight preflight checks in tiered CI setups) and avoid pushing unreviewed
WIP branches that trigger unrestricted `push:` workflows. While an external
review such as `@codex review` is actively pending, hold non-urgent follow-up
pushes and base rebases unless fixing a blocking compile/format bug, then land
review fixes + base sync in one push. Use surgical PR CI for normal changes and
apply `[ci full]` / `ci:full` (where supported) for high-risk
OS/mmap/durability/format edits or post-sprint qualification.

Batch compatible local repairs and evidence with the next necessary push. Keep
durable checkpoints and dependency-ready snapshots available when needed, and
do not hold a mature critical-path candidate waiting for runner capacity. If
the current graph owns an older run and its cancellation is permitted, the
readiness owner may cancel it only after checking all of the following:

- Refresh the live repository/branch/PR head, workflow, event, run ID/attempt,
  candidate SHA and ownership. The run is from a different, superseded head;
  the graph owns the branch and no other workstream relies on the run.
- An appropriate replacement run for the actual current candidate and event
  exists or is guaranteed by the verified trigger. It will supply all required
  checks, including synthetic merge or merge-group checks where applicable.
  A push run, PR run, and merge-group run are not interchangeable by assumption.
- No downstream decision, original failure, performance/recovery evidence,
  audit, release, deployment, protected/default-branch or other contract needs
  the old run to finish. Preserve already produced failures, logs, artifacts,
  run links and any source bindings required by the graph. When uncertain,
  leave it running. Do not cancel unrelated lanes or a healthy current run.
- Recheck immediately before cancellation; GitHub does not offer an atomic
  compare-head-and-cancel operation. If identity changes, stop and reassess.
  Afterward, verify the newest candidate still has its own pending or successful
  required checks. Cancellation is not success and is never a reason to erase a
  previously observed failure.

For an **authorized** CI workflow change, prefer automatic supersession for
disposable branch runs over repeated manual cancellation. Design concurrency
groups separately per workflow, event and branch or PR; protect default and
release branches, tags, merge groups, scheduled/manual runs, and required
historical evidence unless their owner explicitly accepts different semantics.
Do not rely on the display workflow name alone to avoid collisions. GitHub
groups are case-insensitive and event/dispatch order is not guaranteed: verify
that branch names cannot collide ignoring case, and verify the actual latest
head still has an appropriate run. A replacement can otherwise be displaced.

For example, **only after verifying** that `ci-lane/` branches are exclusively
disposable, no case-colliding refs exist, and all relevant protected branches
are recognized by `github.ref_protected`, an individual push-triggered workflow
could use its own unique prefix and this pattern:

```yaml
concurrency:
  group: root-ci-${{ github.event_name }}-${{ github.event_name == 'push' && github.ref_type == 'branch' && !github.ref_protected && startsWith(github.ref, 'refs/heads/ci-lane/') && github.ref || github.run_id }}
  cancel-in-progress: ${{ github.event_name == 'push' && github.ref_type == 'branch' && !github.ref_protected && startsWith(github.ref, 'refs/heads/ci-lane/') }}
```

Adapt the namespace and unique prefix to the actual repo; do not paste this as
an account-wide policy. Other events and protected refs receive unique run IDs,
including pending runs. Test same-branch repeated pushes, different branches
and workflows, case variants, protected/default branches, tags, fork/PR events,
manual and merge-group events, out-of-order triggering, and a final required
check on the actual latest candidate. Check repo policy and roll back if those
invariants fail. Workflow-level concurrency applies to all of its jobs, so
retain any evidence or job that must complete separately.

## Preserve coverage while reducing demand

Before moving, combining, skipping, or removing a platform job, identify its
real inputs and consumers, original platform/CGO/race/durability behavior,
check name/source and event candidate. Reuse existing CI-optimization tickets,
owners, planner, qualification and rollback rules. An unqualified filename
filter is not proof that a check is inapplicable. Workflow-level path or commit
filters can leave required checks pending, and conditional skipped jobs can
appear successful; a stable aggregate must fail closed for unexpected missing,
failed, canceled or skipped work and validate any authorized omission. Include
merge-group coverage and full fallback for unknown inputs when required. Avoid
duplicating an existing selection initiative.

After reducing waste, compare real remaining queue and occupied time with the
cost and trust model of more capacity. A host or plan limit should be reported
as unknown unless confirmed. Never route untrusted PR code to a persistent
self-hosted runner without an appropriate isolation/security design. Preserve
the repository's required current-head CI and review rules throughout.

Useful references: [GitHub concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency),
[required status check troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks),
and [Actions limits](https://docs.github.com/en/actions/reference/limits).

### Historical example: GoMap, 2026-10-29 UTC

At main `85af164b8c900046fa1d8c61f15ea69f982f386c`, a typical open-PR push
requested four macOS TreeDB jobs (PR event), two Root jobs and one
unified-bench job (push events). TreeDB canceled superseded PR runs; Root and
unified-bench had no workflow concurrency. Two Root macOS jobs from an earlier
[#5317 push](https://github.com/snissn/gomap/actions/runs/40793624918) remained
active for over five minutes after its next push. In the sampled
[#5242 TreeDB run](https://github.com/snissn/gomap/actions/runs/40795315430),
one macOS shard started about 45 minutes after job creation. Handoffs from
[#5317](https://github.com/snissn/gomap/actions/runs/40795541719) are consistent
with contention but do not prove the account limit. TreeDB's macOS vet ran with
`setup-go` cache disabled; its command included downloads and took about
726 seconds in one sampled job. Existing timing does not distinguish the cost
of compilation, downloads and vet analysis. GoMap's
[#5049](https://github.com/snissn/gomap/issues/5049) already owns a qualified
CI-impact initiative; do not bypass its domain and full-coverage gates.
