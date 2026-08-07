---
name: scientific-portfolio-governance
description: Coordinate independent scientific agents with one issue-scoped branch and writer per decision, lightweight path-overlap checks, explicit owner priorities, merged-predecessor gates, proportional exact-candidate review, and minimal disruption from unrelated mainline merges. Use when several agents need to work concurrently or when stale scheduling metadata must be reconciled.
---

# Lightweight Scientific Workstream Coordination

## Purpose

Keep independent scientific work safe without turning coordination into a second project. The owner chooses priorities. GitHub issues define scientific contracts, issue-scoped branches carry mutable work, PRs carry bounded candidates, and `main` carries merged authority.

A checked-in portfolio board, slot pool, class taxonomy, activation PR, schema migration, or workflow-generated scheduler is not required.

## Core rules

1. One bounded decision per branch and PR by default.
2. One writer per branch.
3. Search for the same decision and overlapping owned paths before writing.
4. Disjoint work may proceed in parallel.
5. Push coherent nonauthoritative WIP frequently.
6. No workflow may generate or push scientific or governance authority.
7. Use assurance proportional to the claim; bind review and CI to the candidate being merged.
8. Scientific edits after review require renewed review.
9. A declared downstream scientific dependency requires its exact merged predecessor.
10. No successor activates automatically.

## Starting work

Explicit owner authorization or a clear issue assignment is sufficient. Create or resume `work/issue-<number>-<slug>` and leave a concise issue comment containing status, branch, one decision, owned paths, and exact predecessors.

Do not require a mainline governance commit merely to start, pause, resume, review, or hand off work.

## Concurrency

The conflict test is scientific and path-local:

- same branch;
- same decision surface;
- overlapping owned paths; or
- a consumed source or dependency being modified concurrently.

Shared Lean, CI, review, or workflow infrastructure is not by itself a conflict. There is no default global slot cap. The owner may set a practical concurrency limit explicitly.

## Mainline synchronization

A mainline advance does not pause unrelated branches. Before merge, inspect current-main drift:

- disjoint changes with unchanged consumed sources do not require a ceremony-only rebase or renewed scientific review;
- overlapping paths or changed source/dependency bytes require synchronization and affected revalidation or review; and
- bounded results should merge periodically to limit divergence.

## Handoffs

A handoff preserves the exact remote branch and head, WIP status, changed paths, sources, calculations, open findings, and next step. It transfers the single writer role and no other authority.

## Review and merge

Keep scientific construction, qualification engineering, and parent synthesis separate when they are distinct decisions. Hosted Codex quota may use the repository-approved exact-candidate GPT-5.6 Pro fallback. Git mergeability alone is not scientific acceptance.

## Stale coordination metadata

When issue text, old boards, or comments disagree, do not globally halt unrelated work. Resolve the affected lane from live branch, PR, and merge facts plus the owner's current instruction. Archive or correct stale scheduling metadata separately; never rewrite scientific history to make coordination prose agree.

See `references/workstream-marker.md` for an optional issue-comment marker.
