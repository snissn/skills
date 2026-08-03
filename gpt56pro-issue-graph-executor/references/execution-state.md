# Durable Execution State And Idempotent Resume

This reference defines the state record used by
`gpt56pro-issue-graph-executor`. Its purpose is to make a later GPT-5.6 Pro call
able to continue immediately without opening duplicate issues, branches, or PRs
and without depending on conversational memory.

## Canonical Marker

Store graph state in the parent issue under this marker:

```text
<!-- gpt56pro-issue-graph-executor:state:v1 -->
```

Prefer updating one marker comment. When comment editing is unavailable, append
a new marker comment with an incremented `generation` and the previous comment
URL or ID in `supersedes`. The highest valid generation is authoritative.

Do not put secrets, credential-bearing URLs, private keys, access tokens, or raw
user data in the state block.

## Reconciliation Order

At the beginning of every invocation:

1. Read the newest valid state block.
2. Fetch the parent issue and every recorded child issue.
3. Fetch every recorded PR, exact head, base, draft state, checks, reviews, and
   unresolved threads.
4. Search for issue-linked branches/PRs that the manifest missed.
5. Inspect recorded local worktrees when they exist.
6. Resolve conflicts in favor of live GitHub for remote state and in favor of
   the local filesystem only for unpushed files/artifacts.
7. Update stale fields and write a new generation before starting new work.

Never infer that a closed PR merged. Verify its merged state and merge commit.
Never infer that a local branch was pushed. Verify the remote ref or PR head.

## Node States

| State | Meaning | May start descendants? | May merge? |
| --- | --- | --- | --- |
| `pending` | Known node, not yet eligible or selected. | No | No |
| `ready` | All required predecessors are merged and lane may start. | No | No |
| `active` | Coordinator is implementing or fixing the lane in this call. | No | No |
| `checkpointed` | Coherent remote or artifact-backed milestone exists for a future call. | No, unless separately dependency-ready | No |
| `dependency-ready` | Consumed public contract is stable and locally evidenced; final CI/review/merge may remain. | Yes, within pipeline limits | No |
| `fix-needed` | Test, CI, review, performance, or contract blocker requires changes. | Only when blocker is explicitly local/non-contract | No |
| `review-ready` | Mature exact head may request or consume final review. | Yes when also dependency-ready | No |
| `ci-wait` | Exact head is otherwise mature and only current CI is outstanding. | Yes when contract is stable | No |
| `mergeable` | All graph, exact-head, review, test, and evidence gates pass. | Yes | Yes |
| `merged` | PR merge verified and merge commit recorded. | Yes | Completed |
| `blocked` | External or contract-blocking state prevents progress. | No | No |
| `deferred` | Explicitly outside the active execution scope with revisit trigger. | No | No |

A lane can carry secondary flags such as `dependency_ready: true` while its
primary state is `review-ready` or `ci-wait`.

## Blocker Classification

Use one value:

- `none`
- `local_non_contract`
- `contract_blocking`
- `test_blocking`
- `ci_blocking`
- `review_blocking`
- `performance_blocking`
- `persistence_blocking`
- `security_blocking`
- `external_tooling`
- `external_decision`
- `unknown`

Only `local_non_contract` permits a direct descendant to begin from a
`dependency-ready` snapshot before merge, and only when its consumed contract is
unchanged.

## Recommended State Schema

```yaml
schema: gpt56pro-issue-graph-executor/v1
generation: 4
supersedes: https://github.com/owner/repo/issues/4051#issuecomment-...
updated_at: 2026-08-03T18:00:00Z
mode: maximal-progress-and-merge
repo: snissn/gomap
parent_issue: 4051
base_branch: main
base_sha: <current-main-sha>
merge_authorized: true
active_lane_limit: 3
scheduling_mode: adaptive
speculative_depth_limit: 1
workspace:
  root: /tmp/gpt56pro-graphs/snissn-gomap-4051
  source_root: /path/to/gomap
  source_mode: existing-clone|git-clone|module-archive|connector-only
  source_identity: <commit-or-module-version>
  go_version: go1.26.0
  goos: linux
  goarch: amd64
  cgo_enabled: true
  goflags: -p=1
  gomaxprocs: 2
  shared_gomodcache: ...
  shared_gocache: ...
  baseline_build:
    status: pass|fail|not-run
    commands: []
    logs: []
    failure_class: none|dependency-acquisition|compiler|test|environment
contract_owners:
  capability_manifest: 4052
  bson_index_codec: 4061
nodes:
  "4052":
    title: Generate Mongo gateway capability metadata from the executable matrix
    url: https://github.com/snissn/gomap/issues/4052
    predecessors: []
    successors: [4053, 4054, 4055, 4057, 4060, 4062, 4067]
    layer: 0
    priority: critical-path
    state: merged
    dependency_ready: true
    blocker_classification: none
    branch: issue-4052/capability-manifest
    pr: https://github.com/snissn/gomap/pull/...
    base_sha: ...
    head_sha: ...
    merge_commit: ...
    worktree: /tmp/.../worktrees/4052
    dirty: false
    changed_files: []
    contract_surface: ...
    contract_snapshot_hash: sha256:...
    conflict_surface: ...
    test_first_witness: ...
    tests:
      - command: ...
        status: pass
        log: ...
    builds: []
    benchmarks: []
    ci:
      head_sha: ...
      status: green|red|pending|missing
      runs: []
    reviews:
      mature_head_requested: true|false
      status: clean|findings|pending|not-requested
      unresolved_threads: 0
    artifacts: []
    blockers: []
    descendants_safe_to_start: true
    exact_next_action: none
    resume_command: ...
    last_verified_at: ...
sync_log:
  - from: 4052
    to: 4053
    reason: predecessor-merged
    old_snapshot: ...
    new_snapshot: ...
    contract_delta: none
    required_actions: [rebase, rerun-focused-tests]
merge_log:
  - issue: 4052
    pr: ...
    merge_commit: ...
    exact_head: ...
    evidence: ...
processes:
  active: []
  confirmed_stopped_at: 2026-08-03T18:00:00Z
next_wave:
  ready: [4053, 4054, 4055]
  blocked: [4056, 4058, 4059, 4062, 4063, 4064, 4065, 4066]
  rationale: capability foundation merged; three independent gateway lanes fit budget
```

## Contract Snapshot Hash

A descendant needs a concise, stable description of what it consumes. Record a
hash over a small text artifact containing:

- predecessor issue and exact head SHA;
- public APIs, formats, generated files, command shapes, and semantics consumed;
- tests that define the contract;
- known risks and excluded behavior.

The hash is an identity aid, not a proof. If the predecessor changes, compare the
artifact and record the semantic delta rather than relying only on hash mismatch.

## Branch And PR Adoption

For each issue, search in this order:

1. PR explicitly linked from the issue or parent tracker.
2. Open PR whose body contains `Closes #N`, `Fixes #N`, `Parent: #P`, or the
   durable executor marker.
3. Remote branch following repository conventions and containing the issue
   number.
4. Recorded local worktree/branch.

If multiple candidates exist, do not create another branch. Determine which one
is authoritative from head freshness, issue comments, scope, and parent state.
Record duplicates as a blocker or close/supersede only with clear evidence.

## Checkpoint Quality Gate

A lane is checkpointed only when one of these is true:

### Remote checkpoint

- coherent commit exists on a remote branch;
- issue and parent are linked;
- draft PR exists for substantial work;
- PR body states current incomplete scope and failing/passing checks; and
- exact next action is recorded.

### Artifact-backed checkpoint

Use only when remote publication is impossible:

- local base and head identities are recorded;
- patch or bundle is saved outside the ephemeral worktree;
- SHA-256 checksum is recorded;
- `git apply` or restoration command is recorded;
- dirty files and untracked files are enumerated; and
- the state explicitly says `remote_persisted: false`.

A verbal summary without a remote commit or patch artifact is not a checkpoint.

## Resume Algorithm

A later invocation proceeds as follows:

1. Reconcile and merge any `mergeable` node first.
2. Repair `fix-needed` critical-path predecessors before starting lower-value
   work.
3. Resume the highest-unlock `active` or `checkpointed` lane from its exact
   remote head.
4. Finalize `review-ready` and `ci-wait` lanes while implementation proceeds in
   other independent lanes.
5. Start new `ready` nodes only when active-lane capacity remains.
6. After every merge, recalculate readiness and sync descendants at the defined
   window.
7. Before ending, publish a new state generation and verify `processes.active`
   is empty.

## Minimal Parent Comment Template

````markdown
<!-- gpt56pro-issue-graph-executor:state:v1 -->

```yaml
schema: gpt56pro-issue-graph-executor/v1
generation: 1
repo: owner/repo
parent_issue: 4051
mode: maximal-progress-and-merge
base_branch: main
base_sha: ...
nodes: {}
next_wave: {}
processes:
  active: []
```
````

Keep the machine-readable block complete. Put only a short human summary above
it when useful.
