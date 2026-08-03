# Durable State And Idempotent Resume

The graph executor must leave enough remote state that another GPT-5.6 Pro invocation can resume after local worktrees, shell sessions, and conversational context are gone.

## Authoritative State Location

Prefer one top-level comment on the parent tracker containing:

```text
<!-- gpt56-pro-issue-graph-executor:state:v1 -->
```

Update the existing marked comment rather than posting a new state comment every invocation.

Keep the parent comment concise. Detailed code/test evidence belongs in the child issue, PR body, or PR comments.

If the adapter cannot update comments, use this fallback order:

1. parent issue body section with the same marker;
2. committed graph-state artifact in an explicitly agreed repository path;
3. local state file, with the limitation reported clearly.

A local-only file is not sufficient for a normal handoff.

## State Schema

Use JSON for machine-readable validation. The comment may include prose followed by a fenced JSON block.

```json
{
  "schema": "gpt56-pro-issue-graph-executor/v1",
  "repo": "snissn/gomap",
  "parent_issue": 4051,
  "mode": "execute-and-merge",
  "base_branch": "main",
  "base_sha": "0123456789abcdef",
  "updated_at": "2026-08-03T18:00:00Z",
  "run": {
    "id": "20260803T180000Z-gpt56",
    "started_at": "2026-08-03T18:00:00Z",
    "lease_expires_at": "2026-08-03T22:00:00Z"
  },
  "limits": {
    "max_active_lanes": 3,
    "max_heavy_processes": 2
  },
  "dispatchable_now": [],
  "review_or_ci_pending": [],
  "fix_needed": [],
  "blocked": [],
  "nodes": {
    "4052": {
      "title": "Generate capability metadata",
      "state": "merged",
      "active_lane": false,
      "predecessors": [],
      "successors": [4053, 4054, 4055],
      "branch": "gpt56/issue-4052-capability-metadata",
      "pr": 4100,
      "base_sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "head_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "merge_sha": "cccccccccccccccccccccccccccccccccccccccc",
      "contract_surface": ["mongo capability manifest"],
      "conflict_surface": ["TreeDB/mongo_gateway compatibility docs"],
      "performance_class": "not-relevant",
      "tests": [
        {
          "command": "GOWORK=off go test ./TreeDB/mongo_gateway -count=1",
          "result": "pass",
          "head_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
      ],
      "ci": {
        "head_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "status": "success"
      },
      "review": {
        "head_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "status": "clean"
      },
      "blocker": null,
      "next_action": null
    },
    "4053": {
      "title": "Differential compatibility runner",
      "state": "testing",
      "active_lane": true,
      "predecessors": [4052],
      "successors": [],
      "branch": "gpt56/issue-4053-compat-diff",
      "pr": 4101,
      "base_sha": "cccccccccccccccccccccccccccccccccccccccc",
      "head_sha": "dddddddddddddddddddddddddddddddddddddddd",
      "merge_sha": null,
      "contract_surface": ["fixture and result schema"],
      "conflict_surface": ["compatibility manifest integration"],
      "performance_class": "not-relevant",
      "tests": [],
      "ci": {
        "head_sha": "dddddddddddddddddddddddddddddddddddddddd",
        "status": "pending"
      },
      "review": {
        "head_sha": "dddddddddddddddddddddddddddddddddddddddd",
        "status": "not-requested"
      },
      "blocker": null,
      "next_action": "Inspect focused test result, update PR body, and request review only if mature."
    }
  },
  "sync_log": [],
  "merge_log": []
}
```

Use issue numbers as string keys under `nodes`.

## Node States

| State | Meaning |
| --- | --- |
| `pending` | In graph, not dependency-ready. |
| `ready` | All predecessors merged and safe to start. |
| `running` | Active implementation in this invocation. |
| `testing` | Coherent implementation exists; local validation is active or needs collection. |
| `draft` | Remote branch/PR exists but implementation or evidence is incomplete. |
| `review-ready` | Mature head is eligible for review requests. |
| `review-pending` | Exact-head external review is outstanding. |
| `fix-needed` | Tests, CI, review, performance, conflict, or scope found required work. |
| `ci-pending` | Exact-head hosted CI is running. |
| `mergeable-candidate` | Local and remote gates appear satisfied; final coordinator check remains. |
| `merged` | PR merged; merge SHA recorded. |
| `blocked` | External or design blocker with owner and next action. |
| `deferred` | Explicitly moved to another issue/owner and non-blocking for this graph. |

Do not use `running` merely because a PR is open. Set optional `active_lane`
explicitly when a node's state is ambiguous; the validator otherwise treats
`running` and `testing` as active.

## Run Lease

The run block prevents accidental simultaneous ownership but must not lock the graph forever.

- Use a descriptive run ID and a short lease, normally four hours.
- Refresh the lease when updating state during a long invocation.
- A later invocation may reclaim an expired lease after re-reading live state.
- A non-expired lease is advisory. If the user intentionally invokes another executor, reconcile rather than refusing automatically.
- Never use the lease to imply background work continues.

## Reconciliation Rules

On every invocation:

1. Fetch current default-branch SHA.
2. Fetch every child issue, linked PR, remote branch, latest PR head, CI status, reviews, and unresolved threads.
3. Compare live state to saved state.

Apply these rules:

| Saved/live condition | Reconciled action |
| --- | --- |
| Saved `merged`, PR not merged | Downgrade and investigate; never trust stale state. |
| PR merged live | Mark `merged`, record merge SHA, recompute descendants. |
| Issue closed with merged PR | Mark merged/completed. |
| Issue closed without merged implementation | Read disposition; mark deferred, blocked, or ready as evidence requires. |
| Open PR head differs from saved head | Update head and invalidate stale tests, CI, and reviews. |
| Remote branch exists, no PR | Resume branch; inspect before opening a PR. |
| Open owning PR exists on another branch | Adopt it; do not create a duplicate. |
| Saved `running`, no remote progress | Reclassify based on branch/PR; local work is presumed lost unless recoverable. |
| Predecessor changed contract | Mark descendants sync-required and invalidate affected evidence. |
| CI/review belongs to old head | Treat as stale. |
| Local worktree missing | Recreate from remote branch or PR head. |

Live GitHub wins over the state comment.

## Idempotent Branch And PR Discovery

For issue `N`:

1. Search open and closed PRs mentioning `#N`, `Closes #N`, the parent, or the canonical branch.
2. Search remote branches matching `issue-N`, `N-`, or the recorded branch.
3. Read the child issue for explicit branch/PR ownership.
4. Adopt one authoritative implementation line.
5. If several PRs conflict, stop new writes until one is retained and the others are explicitly superseded or treated as evidence.

Canonical new branch:

```text
gpt56/issue-N-short-slug
```

Do not rename a mature existing branch merely to fit the convention.

## Evidence Freshness

Every test, benchmark, CI, and review entry should record the head SHA it proves.

Invalidate evidence when:

- the PR head changes;
- a predecessor merge changes the base or consumed contract;
- conflict resolution changes code;
- generated files are refreshed;
- a relevant configuration or fixture changes.

Docs-only rebases may reuse focused evidence only when the diff is mechanically proven to leave the tested behavior unchanged and repository policy permits it. Latest-head CI and review requirements still apply.

## Child Handoff

Each active child PR or issue should state:

- current branch and PR;
- exact base and head;
- changed files or owned modules;
- completed behavior;
- failing or remaining behavior;
- exact tests and results;
- benchmark evidence or rationale;
- CI and review state;
- conflicts or predecessor assumptions;
- one exact next action.

Use the PR marker:

```text
<!-- gpt56-pro-issue-graph-executor:node:v1 -->
```

## End-Of-Invocation Update

The parent comment should have four concise views:

### Graph summary

```text
merged:
active/draft:
review or CI pending:
fix-needed:
blocked/deferred:
```

### Dispatchable now

Only nodes whose predecessors are merged and conflict surfaces are available.

### Critical next actions

Use imperative, exact actions:

```text
#4053: run <command> on head <sha>, fix <failure>, then update PR #...
#4054: inspect CI run ... for head ...
```

### Machine-readable JSON

Update the fenced JSON and validate it.

## Validator

Save the JSON portion to a file and run:

```sh
python3 scripts/validate_graph_state.py state.json
```

The validator checks:

- required top-level fields;
- recognized states;
- predecessor references;
- branch and PR uniqueness;
- DAG cycles;
- active-lane budget;
- dispatchability;
- merged-node evidence.

It does not replace live GitHub reconciliation.

## Handoff Quality Gate

Before ending:

- [ ] Every useful local change is on a remote branch or clearly reproducible.
- [ ] No duplicate PR was created.
- [ ] Exact heads are recorded.
- [ ] Stale test/CI/review evidence is removed or marked stale.
- [ ] Every blocker names owner and next action.
- [ ] Dispatchable nodes have merged predecessors.
- [ ] Active lanes fit the declared limit.
- [ ] The parent marked comment is updated rather than duplicated.
