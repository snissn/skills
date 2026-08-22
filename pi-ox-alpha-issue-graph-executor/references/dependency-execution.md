# Dependency Execution Model

Represent the selected issues and PRs as a DAG:

```text
node = GitHub issue, ticket, or PR
edge A -> B = A must merge before B can be mergeable or merged
```

## Edge Sources

Use signals in this order:

1. Explicit user-provided dependencies.
2. Issue/tracker language: `depends on`, `blocked by`, `after`, `requires`,
   `foundation for`, or `follow-up to`.
3. PR stack notes, predecessor links, and base-branch relationships.
4. Parent tracker milestone order when it expresses a real dependency.
5. User list order as a weak hint only.
6. Shared contract/conflict risk that makes parallel implementation unsafe:
   public APIs, on-disk formats, schemas, migrations, benchmark semantics,
   persistent state, or shared hot-loop helpers.

Ask only when weak evidence conflicts or would suppress obvious safe
parallelism. Prefer a temporary foundation/design edge over letting workers
invent incompatible contracts.

## Node States

| State | Meaning | May Unblock Speculative Descendants | May Merge |
| --- | --- | --- | --- |
| `pending` | Not started. | No | No |
| `running` | Coordinator or child Pi is working. | No | No |
| `dependency-ready` | Contract is stable enough for explicitly authorized speculative work. | Yes, with user opt-in | No |
| `fix-needed` | Review, tests, CI, or performance found a blocker. | No new descendants unless the blocker is proven local/non-contract | No |
| `review-scope-reset` | PR-lifetime review cap was reached and owner scope/claim disposition is required. | No | No |
| `mergeable-candidate` | Implementation lane recommends readiness; coordinator gates remain. | No by default | Only after final coordinator gate |
| `merged` | Coordinator merged the PR. | Yes | Complete |
| `blocked` | Waiting for policy, decision, predecessor, conflict, CI, credentials, or external state. | No | No |

On `review-scope-reset`, do not request another AI review or start descendants.
Record the effective repository review rule, lifetime request/finding counts,
thread dispositions, owner, and required decision. Exit only after the scoped
artifact is accepted, narrowed, split, deferred, rejected, or explicitly
allowed to resume under repository policy.

## Conflict And Contract Table

Record for each node:

- paths/modules likely changed;
- public API, schema, format, migration, benchmark, and behavior contracts;
- predecessors and the exact snapshot/base SHA;
- `contract_owner` for shared decisions;
- whether execution is `local`, `pi-worker`, `parallel-independent`,
  `conflict-serialized`, or explicitly `speculative`;
- tests, benchmarks, review policy, and merge gate;
- requested and actual worker provider/model/thinking.

One writer owns a branch/worktree. One named contract owner resolves a shared
contract before parallel workers continue.

## Sync Windows

Do not continuously rebase downstream lanes. Sync at:

1. Initial snapshot (or first explicit speculative start).
2. Predecessor public-contract change.
3. Predecessor merge.
4. Pre-final-review.
5. Conflict or stale-test trigger.

Record:

```text
Predecessor #A changed:
- old head: <sha>
- new head/merge: <sha>
- contract delta: ...
- affected descendant files/claims: ...
- required action: update/rebase/rerun/review/docs/etc.
```

## Parallelism Rules

- Keep Pi-worker depth at one; workers may not spawn workers.
- Default to one child, use two only for independent isolated lanes, and require
  explicit user opt-in above two.
- Preserve coordinator capacity for GitHub state, integration, final review,
  and merge decisions.
- Serialize shared public APIs, formats, schemas, migrations, benchmark
  interpretation, authentication/authorization, persistent-state rules, and
  frequently conflicting files.
- Stop a worker whose base SHA, ownership boundary, or predecessor contract is
  stale.
- A worker waiting on hosted CI does not justify another worker for the same
  node; the coordinator polls CI and uses the lane for useful independent work.

## Merge Gate

A node can be declared mergeable only when:

- all predecessors are merged;
- the branch is updated onto the intended final base;
- exact required tests/benchmarks were rerun after that update;
- no unaccepted material performance regression or missed optimization gate
  remains;
- PR scope/body/comments match the exact latest head and final predecessor
  facts;
- exact-head CI is acceptable under repository policy;
- requested changes and material review findings are fixed or explicitly
  rejected with rationale, and threads are resolved;
- required Codex state is clean according to
  `github-pr-mergeable/scripts/codex_review_gate.py`, or the effective local
  policy records its permitted bounded alternative;
- the coordinator's independent final review passes;
- repository policy and user authorization permit merge.

Independent nodes may merge in any order after their own gates pass. Dependent
nodes merge topologically.

## Manifest Shape

Use a parent-issue state comment when possible; otherwise persist a local YAML
or JSON manifest with equivalent fields:

```yaml
repo: owner/name
parent: issue-or-url
base_ref: origin/main
mode: execute-and-merge
merge_authorized: true
merge_scope: selected-graph-only
max_active_pi_workers: 1
max_worker_depth: 1
model_lock:
  provider: openrouter
  model: stealth/ox-alpha
  fallback_allowed: false
coordinator:
  provider: openrouter
  model: stealth/ox-alpha
  thinking: ...
  pi_session_id: ...
worker_transport:
  preferred: bundled-script|subagent-extension|local
  transport_fallback: ...
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
    contract_surface: ...
    conflict_surface: ...
    contract_owner: ...
    execution_mode: local|pi-worker|parallel-independent|conflict-serialized|speculative
    worktree: ...
    branch: ...
    base_sha: ...
    pr: ...
    head_sha: ...
    worker_run_dir: ...
    requested_provider: openrouter
    requested_model: stealth/ox-alpha
    requested_thinking: ...
    actual_provider: ...
    actual_model: ...
    actual_thinking: ...
    model_route_verified: true|false
    model_fallback: forbidden
    review_policy: ...
    review_budget: {max_total_requests: ..., max_finding_heads: ...}
    tests: ...
    benchmarks: ...
    blockers: ...
    exact_next_action: ...
sync_log: []
merge_log: []
```

Live GitHub and git state override stale manifest prose. Reconcile exact heads,
PRs, merges, checks, and worker processes at the start of every invocation.
