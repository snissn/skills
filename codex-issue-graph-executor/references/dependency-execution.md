# Dependency Execution Model

Represent issues and PRs as a DAG:

```text
node = GitHub issue, ticket, or PR
edge A -> B = A must be merged before B can be mergeable/merged
```

Edges gate final mergeability, not provisional construction. Always start B
provisionally from A's recorded `dependency-ready` snapshot within the execution
budget; do not wait for A's CI/review/merge or ask for work-ahead opt-in.
Actual repository restrictions and scientific authority gates still apply.

## Edge Sources

Use dependency signals in this order:

1. Explicit user-provided dependencies.
2. Issue body or tracker language: `depends on`, `blocked by`, `after`,
   `requires`, `foundation for`, `follow-up to`.
3. PR stack notes, linked predecessor PRs, or base branch relationships.
4. Parent tracker milestone ordering when it expresses a real dependency.
5. User-provided list order only as a weak hint.
6. Conflict/contract risk that would cause churn if parallelized: storage
   formats, public APIs, benchmark harnesses, hot-loop helpers, or migrations.

Ask for clarification only when a weak hint would block obvious safe parallelism
or inferred edges conflict. Prefer a temporary design/foundation edge over
parallel managers inventing incompatible contracts.

## Node States

| State | Meaning | May Unblock Descendants | May Merge |
| --- | --- | --- | --- |
| `pending` | Not started. | No | No |
| `running` | Worker or coordinator is implementing or actively finalizing. | Provisionally once a recorded contract is `dependency-ready` | No |
| `dependency-ready` | Contract stable; provisional descendants start by default. | Yes, provisionally within the execution budget and repository restrictions | No |
| `fix-needed` | Review, CI, tests, or performance evidence found blockers. | Provisionally if the recorded descendant contract remains usable | No |
| `review-scope-reset` | An explicit hard review cap or coordinator-confirmed recurring material contract/architecture failure requires owner scope disposition. Advisory counts and provider exhaustion do not enter this state. | No | No |
| `mergeable-candidate` | Worker believes PR is ready, graph gates still apply. | Yes, provisionally by default | Only after predecessors merged and final revalidation passes |
| `merged` | Merge verified. | Eligible; scientific successor needs its own assignment | Completed |
| `blocked` | Waiting for a decision, conflict, or external state. Pending CI/review alone is ordinary finalization. | Provisionally if the blocker leaves the recorded descendant contract usable | No |

On `review-scope-reset`, do not request another AI review or start actual descendants of the affected node; independent nodes continue. Record the explicit hard policy or material-failure rationale, lifetime counts, thread dispositions, owner, and required decision. Exit after the artifact is accepted, narrowed, split, deferred, rejected, or explicitly authorized to resume. `review_churn_warning` is telemetry and does not change node state.

A failed benchmark or performance gate normally moves a candidate to
`fix-needed`; it does not make the issue `blocked`, completed, or intentionally
deferred. Those terminal dispositions require evidence that the issue premise
is false, the accepted objective is infeasible within its contract, a linked
successor owns the remaining work, or an external dependency prevents the next
causal test.

## Failed Candidate Intervention

When a coherent performance candidate fails a hard gate:

1. Revert or quarantine the failed product change when appropriate, but retain
   its exact base/head, raw artifacts, commands, and correctness results.
2. Separate the hard rejection reason from noise. Unchanged physical work,
   wrong-route counters, debt, or a contract failure is stronger evidence than
   a small single-run throughput delta.
3. Trace the actual measured workload end to end. Identify the caller-facing
   entrypoint, service or gateway admission, active coalescer, backend batch,
   physical sync, root publication, acknowledgement, and final drain. Verify
   activation with counters or one bounded event trace; do not infer it from a
   similarly named lower layer.
4. Recheck the issue premise against current main. Distinguish logical frames,
   physical syncs, publications, and deferred debt. If current code already
   satisfies part of the ticket, narrow or disposition that part before coding.
5. Prefer an existing knob, queue, coordinator, batch API, or test seam for one
   predeclared causal matrix. Freeze values, repetitions, promotion gates, and
   stop conditions before running it. Do not tune one yield, delay, or threshold
   per CI cycle.
6. If that probe identifies a viable mechanism, produce one completion packet:
   deterministic mechanism test, implementation, correctness/recovery tests,
   benchmark provenance, and the full performance matrix. Open a PR only after
   the local hard gates pass unless repository policy requires an earlier draft.
7. If the probe helps but the simplest mechanism violates another gate, try at
   most one evidence-motivated follow-on mechanism by default. If both fail,
   stop micro-tuning and make an explicit architecture, scope, or measured-no-go
   disposition. Further candidates require materially new evidence.

Record in durable graph state: retired mechanism, hard failure evidence, active
stack boundary, issue-premise changes, adviser input used or rejected, the next
experiment and stop conditions, and which independent node proceeds meanwhile.
Keep independent graph work moving while this diagnosis or a mature PR
finalizer runs.

## Graph Reassessment

Reassess when evidence undermines the plan, not only when a candidate fails:

- Local improvements do not advance the representative parent outcome.
- Setup, publication, durability, or cleanup costs defeat the intended mechanism.
- A bottleneck, prerequisite, path-selection, or correctness assumption is false.
- A new safety finding changes the necessary work or ordering.

For abstract or materially uncertain work, also honor the tracker's named
reassessment boundaries even when tests and child exit gates pass. Keep direct,
well-understood work event-driven. The coordinator owns strategic reassessment;
workers surface consequential evidence without running a separate graph review
for every child.

Reuse available code, profiles, counters, tests, and review evidence. Investigate
only a bounded question that could change the next decision. Reassessment does
not itself require a new benchmark, reviewer, push, or wholesale replacement.
Keep a sound plan; revise only the affected remainder when it is inadequate.
Prioritize required structural/integration work over further local polishing.

Use `gh-issue-planner` to reorder, narrow, supersede, create/adopt necessary nodes,
or replace the remaining graph within existing authorization. Record the finding
and evidence, why the old plan is inadequate, changed nodes/edges, and preserved
gates in the parent. Preserve useful work and provenance; map remaining
obligations to live owners before retiring nodes. A linked follow-up cannot stand
in for an unmet parent acceptance gate.

Steer or stop affected provisional descendants when their assumed contracts
change; independent lanes continue. Preserve one writer per surface and the
default provisional start once a revised contract is usable. New/replacement
nodes retain the same ownership, review, final-base, CI, and evidence gates.
Replanning cannot reset an exhausted explicit hard review cap or bypass
`review-scope-reset` owner disposition. New goals/repos, weaker acceptance,
accepted-gap changes outside their triggers, and scientific authority still need
the applicable user/owner decision; scientific successors require their own
assignment and merged predecessor authority.

## Sync Windows

Do not continuously rebase downstream branches. Sync at:

1. Initial predecessor `dependency-ready` snapshot.
2. Predecessor contract change.
3. Predecessor merged.
4. Pre-final-review.
5. Conflict/test trigger.

Each sync should record:

```text
Predecessor #A changed since snapshot:
- old head: <sha>
- new head/merge: <sha>
- contract changes: ...
- files likely affected downstream: ...
- required downstream actions: rebase/rerun/update docs/etc.
```

## Parallelism Rules

- Keep agent depth at one. The coordinator owns all fan-out and follow-up
  routing.
- Apply SKILL.md's budget: one useful worker, at most two independent
  assignments normally. Do not create a worker solely to poll.
- Parallelize implementation only when workers have isolated worktrees and
  disjoint ownership boundaries and no shared contract decision remains.
- Serialize nodes that touch the same public API, storage format, migration,
  benchmark interpretation, hot-loop helper, or frequently conflicting files.
- Set the active worker count to the minimum of the runtime limit, the number of
  safely independent tasks, the skill budget, and the machine/repository resource limit. Preserve
  coordinator capacity.
- Stop or steer a worker when its base SHA, ownership boundary, or predecessor
  contract changes in a way that affects its assignment. Unrelated mainline
  changes alone do not invalidate a scientific lane.

## Finalization Ownership

An issue worker owns its total completion packet until a mature
`dependency-ready` PR or a real blocker. Finalize locally unless a delegated
direct-child finalizer enables concrete useful parallel work. The active owner
handles complete finding inventory, coherent repair batches, latest-head
CI/review and thread resolution; merge authority remains explicit. While
delegation is useful, the coordinator checks no more often than every 15 minutes
unless completion, a blocker or an ownership transfer occurs.

When no useful parallel work remains, apply SKILL.md's **Critical-Path
Finalization and Monitoring**: obtain a compact checkpoint, stop/release the delegated
owner, establish any in-flight command outcome, then reclaim local finalization
without repeating completed reviews/tests. Never keep two active readiness or
writer owners. If only external CI/review remains, continue monitoring with one
native watch/event mechanism or bounded polling/waits. Persist owner/head, gate
and next action, but do not end the turn just because the gate is still pending.
The delegated-owner polling cadence does not apply to external CI after transfer.
Keep output compact, reuse completed evidence, and proceed immediately when
the gate resolves; do not restart reviews/tests or duplicate monitors. Completion,
explicit pause, a genuine authority/input blocker or harness limit can end the
turn. All predecessor and evidence gates still apply.

If the same material blocker category survives two repair heads, stop before a
third and route one named question through the bounded GPT-6.1 Sol adviser.
Keep the same PR across base advancement; sync once pre-finalization or on a real
conflict/predecessor trigger. Replace it only when repo policy permits and either
its branch is genuinely irreparable or a recorded coordinator **Graph Reassessment**
supersedes its obsolete completion packet.


At each repair head, inventory every current review thread and failed gate
before editing. Batch compatible fixes, update tests and PR evidence together,
run proportional local checks, and push one coherent repair head. A serial
comment-by-comment push-and-wait loop is justified only when an earlier finding
changes the contract or makes the remaining fixes unknowable.

Predecessor finalization starts provisional successor work by default. Start
the successor against the exact recorded predecessor snapshot while the
finalizer owns CI/review; no user opt-in or predecessor merge is needed.
Observe ownership, concurrency, and repository restrictions. Label it
provisional, do not claim mergeability, and inventory which outputs are:

- reusable after a tree/contract-equivalent merge;
- required to be resynced or rerun on the final base; or
- invalid until an actual merge identity exists (for example VCS-stamped
  binaries, candidate-bound provenance, and official retained-evidence runs).

For retained-evidence successors, work ahead on constructor review, immutable
input staging, environment/toolchain setup, hostile/preflight validation, and
an explicitly nonqualifying rehearsal when it materially reduces risk. Never
relabel a rehearsal as qualification evidence; refreeze and rerun every
merge-identity-bound stage after the predecessor merge.

## Retained Evidence Gate

For retained performance evidence, order product, reviewed/landed harness or schema, then artifact-only evidence nodes where dependency policy permits. Complete focused provenance, concurrency/isolation, fail-closed validation, and wording review before freezing exact runtime and harness subtree/blob identities and starting expensive collection. Prefer a dedicated high-capacity runner, persistent build cache, and durable artifact storage; otherwise record typed `INFRASTRUCTURE_UNAVAILABLE` and the real fallback.

Classify proven unrelated CI flakes separately and rerun only affected gates while preserving current-head merge gates. Artifact-only descendants remain valid only under exact runtime/harness subtree and implementation-blob identity; product or harness drift invalidates affected evidence.

## Merge Gate

Apply SKILL.md's post-push evidence discretion: assess the actual change and
reuse applicable evidence with its original SHA and rationale when policy
permits. A new SHA alone does not mandate another review or full validation run.

A node can be declared mergeable only when:

- no unaccepted material performance regression remains;
- all predecessors are merged;
- the branch is updated onto the intended final base;
- required test/benchmark evidence covers the final candidate, with justified
  reuse or affected/policy-required reruns;
- PR body and comments no longer rely on speculative predecessor facts;
- latest-head CI and review state are acceptable;
- when Codex is required and no policy-permitted replacement applies, the shared `github-pr-mergeable/scripts/codex_review_gate.py --check` classifier reports clean for the exact head; a clean Codex issue comment is sufficient, while any later unresolved Codex thread blocks;
- for hosted quota/service unavailability, apply SKILL.md's
  `CODEX_REVIEW_UNAVAILABLE_QUOTA` and policy-permitted independent fallback;
  never count an unavailable review as clean;
- when repository-local proportional scientific policy replaces Codex, the bounded review disposition and exact acceptance evidence required by that policy are recorded, and all existing threads are fixed or explicitly rejected;
- AI reviews, if used, were requested only after the PR was mature;
- coordinator final review passes.

Independent nodes may merge in any order after their own gates pass.

## Manifest Fields

Use only fields needed for resumable evidence; this example is not a required
checked-in schema, scheduler, roster, or scientific activation mechanism.
Record owner assignment for scientific nodes; never synthesize authority from
tracker status or predecessor completion. Use working notes or a temp manifest:

```yaml
repo: owner/name
base_ref: origin/main
mode: execute-and-merge
merge_authorized: true
merge_scope: selected graph only
max_parallel_agents: N
max_agent_depth: 1
coordinator:
  agent_role: graph-coordinator
  requested_model: gpt-6.1-sol
  requested_effort: inherited
  actual_model: ...
  actual_effort: ...
  routing_fallback: ...
durable_state:
  kind: parent-issue-comment|local-manifest
  location: ...
nodes:
  id:
    kind: issue|pr
    title: ...
    url: ...
    predecessors: []
    successors: []
    layer: 0
    state: pending
    agent: ...
    agent_role: inventory|implementation|high-risk-specialist|finalization|independent-review
    requested_model: gpt-6.1-sol
    requested_effort: low|medium|high|xhigh|max
    actual_model: ...
    actual_effort: ...
    routing_rationale: ...
    routing_fallback: ...
    worktree: ...
    branch: ...
    pr: ...
    head_sha: ...
    tests: ...
    benchmarks: ...
    blockers: ...
    review_policy: ...
    review_budget: {max_total_requests: ..., max_finding_heads: ...}
    review_stop_reason: ...
    review_resume_authorized_by: ...
    contract_surface: ...
    conflict_surface: ...
    execution_mode: parallel|speculative|conflict-serialized|design-gate
    contract_owner: ...
sync_log: []
merge_log: []
```

When this skill is invoked, `merge_authorized` defaults to `true` for the
selected graph. Record a narrower scope only when the user explicitly requests
plan-only or no-merge execution.

Routing defaults to `gpt-6.1-sol` for every delegated role. Record retained
coordinator, explicit user, or required reviewer-identity exceptions with their
actual model and rationale; never relabel another model or an external hosted
review as Sol. If actual routing is not observable, record it as unknown.
