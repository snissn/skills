# Dependency Execution Model

This reference defines the graph scheduling model for `/skill:orca-issue-graph-executor`.

## Graph Construction

Represent issues as a DAG:

```text
node = GitHub issue/ticket
edge A -> B = A must be merged before B can be mergeable/merged
```

Edge sources, in priority order:

1. Explicit user-provided dependencies.
2. Issue body or tracker language: `depends on`, `blocked by`, `after`, `requires`, `foundation for`, `follow-up to`.
3. PR stack notes or linked predecessor PRs.
4. Parent tracker milestone ordering when it expresses a real dependency.
5. User-provided list order only as a weak hint.
6. Conflict/contract risk that would cause high churn if parallelized: shared on-disk formats, public APIs, benchmark harnesses, hot-loop helpers, or migrations.

Ask for clarification if a weak hint would prevent obvious safe parallelism or if inferred edges conflict. Prefer adding a temporary design/foundation edge over parallelizing siblings that need the same unsettled contract.

## Conflict And Contract Risk Pass

Before dispatching managers, record a risk table for every node:

| Field | Meaning |
| --- | --- |
| `contract_surface` | APIs, on-disk formats, docs, benchmark meanings, public behavior |
| `conflict_surface` | files/modules likely to overlap with other nodes |
| `execution_mode` | `parallel`, `speculative`, `conflict-serialized`, or `design-gate` |
| `contract_owner` | issue responsible for settling shared contract, if any |

Use `design-gate` when several issues need the same unsettled format/API/helper decision. The gate can be a short predecessor PR, a dedicated issue, or an explicit coordinator-approved design note. Do not let multiple managers independently invent incompatible versions of the same format or helper API.

## Layering

Compute topological layers:

```text
L0 = nodes with no predecessors
L1 = nodes whose predecessors are all in earlier layers
...
```

Start all nodes in a layer that have no unready predecessor, subject to max parallelism. Descendants may start before predecessor merge only when all direct predecessors are `dependency-ready`.

## Flexible Scheduling Modes

Use the least parallel scheduling mode that still saves useful wall time:

| Mode | Use when | Start rule |
| --- | --- | --- |
| `strict-serial` | Every issue depends on merged facts or shared files churn heavily. | Start a dependent only after predecessors merge. |
| `layer-parallel` | Multiple nodes are independent and low-conflict. | Start ready topological-layer nodes up to `max_parallel_managers`. |
| `pipelined` | A mostly serial chain can overlap finalization with the next implementation. | Start one or more successors after predecessors reach `dependency-ready`, but keep them blocked before final review/merge. |
| `adaptive` | The graph mixes independent roots and high-overlap chains. | Use layer parallelism for independent nodes and bounded pipelining for chains. |

Recommended conservative pipeline defaults:

```yaml
scheduling_mode: pipelined
max_parallel_managers: 2
max_speculative_successors_per_chain: 1
max_speculative_depth: 1
dependency_ready_starts_allowed: true
```

These defaults allow exactly the common pattern: one predecessor PR is in CI/review/final polish while one direct successor starts implementation from a dependency-ready contract snapshot. Increase speculative depth or successor count only when contract churn risk is low and the manifest records why.

## Node States

| State | Meaning | May unblock descendants? | May be mergeable? |
| --- | --- | --- | --- |
| `pending` | Not started. | No | No |
| `running` | Manager is implementing/reviewing. | No | No |
| `dependency-ready` | Public contract is stable enough for descendants to start speculative work. | Yes | No |
| `fix-needed` | Coordinator/review found blockers, including unaccepted material performance regressions. | No new descendants unless already safe; existing descendants may need sync. | No |
| `mergeable-candidate` | Manager believes PR is mergeable, but graph gates may still block. | Yes | Only if predecessors merged and final revalidation passes |
| `merged` | Coordinator merged PR. | Yes | Yes, completed |
| `blocked` | Waiting for decision, predecessor, CI, or conflicts. | No | No |

## Dependency-Ready Checklist

A predecessor may be marked `dependency-ready` when all are true:

- [ ] PR exists with branch and latest head SHA.
- [ ] Manager states implementation scope is substantially complete.
- [ ] Public contract surface is documented: APIs, formats, files, behavior, tests, benchmark expectations.
- [ ] Required local tests/benchmarks for that contract passed, or failures are unrelated and documented.
- [ ] No material performance regression remains unoptimized/unaccepted for the exposed contract.
- [ ] Manager completed at least one review/fix loop or explicit self-review.
- [ ] Remaining work is expected to be CI, review polish, docs wording, or non-contract-changing cleanup.
- [ ] Known risks and possible contract churn are listed.

Do not mark dependency-ready if unresolved review findings could change APIs, storage formats, public semantics, test harness shape, or benchmark interpretation used by descendants.

## Speculative Descendant Rules

A descendant started before predecessor merge must be treated as speculative:

- branch/PR title should make blocked status obvious when practical;
- PR can be draft or WIP;
- manager may implement and run local tests against a contract snapshot;
- manager must not claim final mergeability, request final AI review, or request merge;
- coordinator must not merge it;
- final rebase/revalidation after predecessor merge is mandatory.

For multiple predecessors, start the descendant only when all direct predecessors are dependency-ready, unless the user explicitly authorizes partial speculative work.

Before starting a speculative descendant, verify the pipeline window:

- running manager count is below `max_parallel_managers`;
- unmerged descendant count on that chain is below `max_speculative_successors_per_chain`;
- speculative distance from the nearest merged base is no greater than `max_speculative_depth`;
- predecessor handoff says public contract churn is unlikely;
- no open review, benchmark, or format findings are likely to invalidate the consumed contract.

If any check fails, leave the node `pending` or `blocked` and record the reason instead of starting it.

## Sync Windows

To minimize churn, do not continuously rebase or merge upstream changes into every descendant. Sync at these windows:

1. **Initial snapshot**: predecessor reaches dependency-ready.
2. **Contract change**: predecessor changes behavior/API/format relied on downstream.
3. **Predecessor merged**: descendant must update to final base.
4. **Pre-final-review**: before declaring descendant mergeable.
5. **Conflict/test trigger**: descendant tests fail due to stale predecessor assumptions.

Each sync should include a concise delta:

```text
Predecessor #A changed since snapshot:
- old head: <sha>
- new head/merge: <sha>
- contract changes: ...
- files likely affected downstream: ...
- required downstream actions: rebase/rerun/update docs/etc.
```

## Merge Gate

A node can be declared mergeable only when:

- no unaccepted material performance regression remains in runtime, throughput, allocations, storage/rebuild overhead, or relevant counters;
- all predecessors are `merged`;
- the branch is rebased/updated onto the final intended base;
- required tests/benchmarks were rerun after that update;
- PR body and comments no longer rely on speculative predecessor facts;
- latest-head CI and AI reviews are green/resolved, and AI reviews were requested only after the PR reached a mature reviewable head;
- coordinator final review passes.

Merge in topological order. If two nodes are independent, either may merge first after their own gates pass.

## Manifest Fields

Recommended execution manifest fields:

```yaml
repo: owner/name
base_ref: origin/main
merge_authorized: true|false|scope
scheduling_mode: strict-serial|layer-parallel|pipelined|adaptive
max_parallel_managers: N
max_speculative_successors_per_chain: N
max_speculative_depth: N
dependency_ready_starts_allowed: true|false
nodes:
  123:
    title: ...
    url: ...
    predecessors: [120, 121]
    successors: [130]
    layer: 2
    state: pending|running|dependency-ready|mergeable-candidate|merged|blocked|fix-needed
    manager_worktree: ...
    manager_terminal: ...
    branch: ...
    pr: ...
    head_sha: ...
    dependency_snapshot:
      predecessor: sha
    tests: ...
    benchmarks: ...
    blockers: ...
    contract_surface: ...
    conflict_surface: ...
    execution_mode: parallel|speculative|conflict-serialized|design-gate
    contract_owner: ...
approval_gate:
  graph_presented: true
  user_approved_execution: true|false
  notes: ...
sync_log:
  - time: ...
    from: 120
    to: 130
    reason: dependency-ready|contract-change|merged|pre-final-review
    summary: ...
merge_log:
  - issue: 120
    pr: ...
    merge_commit: ...
```
