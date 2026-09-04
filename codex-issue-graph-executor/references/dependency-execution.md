# Dependency Execution Model

Represent issues and PRs as a DAG:

```text
node = GitHub issue, ticket, or PR
edge A -> B = A must be merged before B can be mergeable/merged
```

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
| `running` | Worker or coordinator is implementing/reviewing. | No | No |
| `dependency-ready` | Contract stable; speculation still requires user opt-in and repo permission. | Only with that authorization | No |
| `fix-needed` | Review, CI, tests, or performance evidence found blockers. | No, except authorized speculation | No |
| `review-scope-reset` | An explicit hard review cap or coordinator-confirmed recurring material contract/architecture failure requires owner scope disposition. Advisory counts and provider exhaustion do not enter this state. | No | No |
| `mergeable-candidate` | Worker believes PR is ready, graph gates still apply. | Only with authorized speculation | Only after predecessors merged and final revalidation passes |
| `merged` | Merge verified. | Eligible; scientific successor needs its own assignment | Completed |
| `blocked` | Waiting for decision, predecessor, CI, conflict, or external state. | No | No |

On `review-scope-reset`, do not request another AI review or start actual descendants of the affected node; independent nodes continue. Record the explicit hard policy or material-failure rationale, lifetime counts, thread dispositions, owner, and required decision. Exit after the artifact is accepted, narrowed, split, deferred, rejected, or explicitly authorized to resume. `review_churn_warning` is telemetry and does not change node state.

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
  assignments normally. Keep routine inventory and polling with the coordinator.
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

## Retained Evidence Gate

For retained performance evidence, order product, reviewed/landed harness or schema, then artifact-only evidence nodes where dependency policy permits. Complete focused provenance, concurrency/isolation, fail-closed validation, and wording review before freezing exact runtime and harness subtree/blob identities and starting expensive collection. Prefer a dedicated high-capacity runner, persistent build cache, and durable artifact storage; otherwise record typed `INFRASTRUCTURE_UNAVAILABLE` and the real fallback.

Classify proven unrelated CI flakes separately and rerun only affected gates while preserving current-head merge gates. Artifact-only descendants remain valid only under exact runtime/harness subtree and implementation-blob identity; product or harness drift invalidates affected evidence.

## Merge Gate

A node can be declared mergeable only when:

- no unaccepted material performance regression remains;
- all predecessors are merged;
- the branch is updated onto the intended final base;
- required tests/benchmarks were rerun after that update;
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
  requested_model: inherited
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
    agent_role: inventory|implementation|high-risk-specialist|readiness-review
    requested_model: gpt-6-astra|gpt-5.6-terra|gpt-5.6-luna|policy-required-reviewer
    requested_effort: low|medium|high|xhigh
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
