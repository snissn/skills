# Lane Execution For GPT-5.6 Pro

This reference defines how one GPT-5.6 Pro invocation advances several independent issue nodes without subagents.

## Meaning Of Parallel

The harness has one reasoning coordinator. Parallelism comes from:

- isolated git worktrees and branches;
- several open implementation lanes with disjoint ownership;
- concurrent local build/test processes when the shell supports sessions;
- hosted CI and external review progressing while the coordinator works elsewhere;
- batched GitHub adapter reads and writes where supported.

Do not describe sequential reasoning as simultaneous work. Do not leave unobserved processes running after the invocation.

## Default Capacity

```text
active implementation lanes: 3
absolute normal maximum: 4
heavy local Go processes: 2
writer per contract/conflict surface: 1
```

Reduce capacity when:

- worktrees touch the same command dispatcher, manifest, schema, storage format, migration, authentication state, or heavily edited file;
- the machine is memory constrained;
- broad tests dominate CPU or disk;
- a predecessor contract is still changing;
- the coordinator cannot keep PR bodies, tests, and state current.

A fourth lane is appropriate when it is disjoint and low-collision, such as a harness/docs lane beside two implementation lanes and one review-fix lane.

## Ready-Node Scoring

Among nodes whose predecessors are merged, rank by:

1. **Graph multiplier:** number and criticality of successors unblocked.
2. **Final-gate ownership:** nodes that own release, security, durability, or evidence gates.
3. **Expected time to merge:** small coherent children before broad uncertain work.
4. **Conflict cost:** prefer disjoint nodes that preserve parallel capacity.
5. **Evidence availability:** prefer issues with explicit tests, baselines, and acceptance gates.
6. **Risk:** resolve a high-risk contract before descendants invent competing assumptions.

Use the score as a decision aid, not a fabricated numeric certainty.

## Contract And Conflict Table

Record one row per node:

| Field | Meaning |
| --- | --- |
| `contract_surface` | Public API, file format, error semantics, schema, benchmark contract, or behavior descendants consume. |
| `conflict_surface` | Files/modules likely to collide with sibling branches. |
| `contract_owner` | The issue that resolves shared decisions. |
| `execution_mode` | `parallel`, `conflict-serialized`, `design-gate`, or explicitly authorized `speculative`. |
| `local_target` | Packages, binary, test group, or benchmark required locally. |
| `performance_class` | Not relevant, possibly relevant, sensitive, or objective. |

Two nodes may be logically independent but still conflict-serialized because they edit the same generated capability table or central command switch. Keep implementation separate and merge/rebase them one at a time.

## Round-Robin Work Pattern

A productive three-lane round looks like:

```text
Lane A: add red test -> implement -> start focused tests
Lane B: add red test -> implement while A tests run
Lane C: inspect/resume PR -> fix review or implement -> start tests
Collect A/B/C test results
Publish coherent commits
Start or refresh hosted CI
Switch to another ready lane while CI/review runs
```

Rules:

- Start a local process only when its output can be inspected before the invocation ends.
- Use named shell sessions and separate artifact directories.
- Do not run multiple broad `go test ./...` jobs concurrently.
- Prefer focused package tests in parallel, followed by one broader affected suite after integration.
- Keep shared `GOMODCACHE` and `GOCACHE` when safe, but separate database directories, temp directories, benchmark output, and worktrees.
- A failed lane remains useful only if its exact failure and next action are published.

## Foundation Policy

A foundation node should normally merge before descendants start.

Mark a contract `dependency-ready` before merge only when all are true:

- its public contract is written and tested;
- no known review finding could change that contract;
- its PR is coherent and locally green;
- descendants can consume it from a pinned exact head;
- the user explicitly authorized speculative work.

Even then:

- descendant PRs remain draft;
- review and final performance evidence wait for the merged base;
- predecessor contract changes trigger immediate resynchronization;
- descendants never merge before predecessors.

The default for requests like “implement as much as possible” is still to finish graph-multiplier foundations quickly, then fan out after merge.

## Sync Windows

Synchronize a lane at:

1. initial creation/resume;
2. predecessor contract change;
3. predecessor merge;
4. sibling merge that touched its conflict surface;
5. pre-review;
6. pre-merge;
7. failing test or conflict evidence.

Record:

```text
old base/head:
new base/head:
contract changes:
files affected:
tests to rerun:
PR wording/evidence to update:
```

Do not continuously rebase every branch while another lane is changing.

## CI And Review As Capacity

An open PR waiting on CI or external review is not an active implementation lane unless the coordinator is currently investigating it.

Use freed capacity to:

- implement another ready node;
- improve tests or benchmark evidence on another mature PR;
- inventory newly unblocked nodes;
- update the parent ledger;
- run local deep review.

Return to the pending PR when a deliberate status check is due.

## Handoff Thresholds

Publish and hand off a lane when it reaches any durable milestone:

- red test and accepted implementation plan;
- coherent implementation with focused tests;
- draft PR with known failing gate;
- review-ready exact head;
- CI/review fix-needed;
- mergeable candidate;
- external blocker.

Do not preserve only local uncommitted work when the invocation ends. Prefer a remote issue branch and draft PR. A WIP commit is acceptable when the PR body clearly states what fails and why.

## Example Shape For `snissn/gomap#4051`

The live tracker controls; this example illustrates lane use.

### Initial round

```text
Lane A: #4052 capability manifest
Lane B: #4061 BSON key codec
Lane C: parent inventory, local gomap baseline, or mature existing PR fixes
```

`#4052` is a graph multiplier. Merge it as soon as its gates pass.

### After `#4052` merges

Possible three-lane round:

```text
Lane A: #4053 differential runner
Lane B: #4054 stats commands
Lane C: #4055 explain
```

If `#4061` remains active and is more critical than one of these, keep it as a lane and choose two gateway children. Do not exceed the worktree, conflict, and machine limits merely because more nodes are logically ready.

### Durable end of invocation

The parent state should identify:

```text
merged: #4052
active/draft: #4053, #4054, #4055
still running or ready: #4061
dispatchable after next merge: ...
exact PR heads and next actions: ...
```

The next invocation starts from that state, verifies live GitHub, and resumes.
