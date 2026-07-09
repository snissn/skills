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
| `dependency-ready` | Public contract is stable enough for speculative descendants. | Yes | No |
| `fix-needed` | Review, CI, tests, or performance evidence found blockers. | No new descendants unless safe | No |
| `mergeable-candidate` | Worker believes PR is ready, graph gates still apply. | Yes | Only after predecessors merged and final revalidation passes |
| `merged` | Coordinator merged PR. | Yes | Completed |
| `blocked` | Waiting for decision, predecessor, CI, conflict, or external state. | No | No |

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
- Prefer parallel inventory, exploration, test runs, CI triage, and independent
  review because their outputs are easy to reconcile.
- Parallelize implementation only when workers have isolated worktrees or
  disjoint ownership boundaries and no shared contract decision remains.
- Serialize nodes that touch the same public API, storage format, migration,
  benchmark interpretation, hot-loop helper, or frequently conflicting files.
- Set the active worker count to the minimum of the runtime limit, the number of
  safely independent tasks, and the machine/repository resource limit. Preserve
  coordinator capacity.
- Stop or steer a worker when its base SHA, ownership boundary, or predecessor
  contract becomes stale; do not let it continue accumulating speculative work.

## Merge Gate

A node can be declared mergeable only when:

- no unaccepted material performance regression remains;
- all predecessors are merged;
- the branch is updated onto the intended final base;
- required tests/benchmarks were rerun after that update;
- PR body and comments no longer rely on speculative predecessor facts;
- latest-head CI and review state are acceptable;
- AI reviews, if used, were requested only after the PR was mature;
- coordinator final review passes.

Independent nodes may merge in any order after their own gates pass.

## Manifest Fields

Use this shape for working notes or a temp manifest:

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
  requested_model: gpt-5.6-sol
  requested_effort: xhigh
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
    requested_model: gpt-5.6-luna|gpt-5.6-terra|gpt-5.6-sol
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
