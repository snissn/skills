# Optional lightweight workstream marker

Post or update one issue comment when useful:

```text
<!-- scientific-workstream:v1 -->
status: ACTIVE | HALTED | REVIEW | COMPLETED
branch: work/issue-<number>-<slug>
head: <sha or pending>
decision: <one bounded decision>
owned_paths:
  - <repo-relative path>
predecessors:
  - <merge identity or none>
writer: one
next_action: <one sentence>
```

This is coordination metadata only. It creates no scientific authority and requires no repository commit.
