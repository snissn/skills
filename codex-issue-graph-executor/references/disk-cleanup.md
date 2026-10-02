# Disk Cleanup After Graph Work

Use for bounded cleanup batches during graph execution, including authorized
execution hosts. Skill-editing and read-only requests do not authorize deletion.
Use existing graph notes and native filesystem/Git tools; no new scheduler or
cleanup service is required.

## Scope And Release

- Inventory recorded run roots and attributable graph outputs: completed issue,
  baseline, review, and disposable clone/worktree directories; generated test or
  benchmark DBs and fixtures; binaries, test executables, build intermediates;
  temporary profiles/logs, downloads, and run-local caches. Prior-run leftovers
  are eligible only when ownership and release can still be verified.
- Record exact absolute paths and hosts, estimated sizes, retention reason, and
  producer/consumer state in existing graph notes. Age, a naming pattern, a
  merged PR, or regenerability alone does not prove a path is safe to delete.
- Release a path only after its writer/commands have stopped, descendants no
  longer consume it, and useful work and required evidence are preserved.
  At release, capture expected path/type and filesystem identity plus a
  contents/metadata inventory sufficient to detect replacement or additions;
  pass this snapshot with the allowlist. A pathname and size alone do not suffice.
  Preserve accepted and failed-candidate raw results, provenance, repro inputs,
  scientific artifacts, and anything required for review/recovery. A disposable
  working DB can go when the retained evidence and reproducible fixture suffice.
  Verify any required durable copy and its location before removing the local one.
- The coordinator gives one cleaner an exact allowlist and protected-path list.
  Do not reuse or reassign released paths until the cleaner finishes; resolve
  in-flight deletion before taking ownership back. No other worker/helper cleans
  the same paths. New candidates discovered by the cleaner need coordinator
  release before deletion, not a new user prompt for already authorized scope.
- Preserve primary checkouts, active/provisional worktrees, user files, real DBs,
  unrelated graph outputs, and shared persistent build/module/package caches.
  Broader cache/host cleanup requires explicit scope; report large unattributed
  or shared candidates with their sizes instead of deleting them.

## Reclaim And Verify

1. Measure candidate sizes and free space on each affected filesystem. Prefer
   the largest eligible batches; avoid broad home/root scans and scans of active
   benchmark datasets. Run at low resource priority where supported, and defer
   heavy scans/deletion during measurement windows that they could contaminate.
   Before starting a conflicting timed run, the coordinator obtains a cleaner
   pause/completion acknowledgement and verifies that in-flight I/O has stopped.
2. Immediately before each deletion, recheck path identity, symlink/mount
   boundaries, current owners/consumers and live processes, and protected-path
   overlap, including nested worktrees. Compare with the release snapshot,
   adjusted only for successful deletions this sole owner already performed in
   the same batch. Missing identity/content evidence or any other mismatch means
   retain the target. Skip changed, active, locked, unreadable, or uncertain
   targets; do not infer inactivity merely from an agent finishing.
3. For a worktree, verify registration, current HEAD, clean tracked state,
   untracked/ignored contents, and preservation of required commits on durable
   refs. Delete only separately allowlisted disposable generated contents, then
   use `git worktree remove <exact-path>` without force. If it refuses, retain and
   report the reason. Remove unregistered scratch directories only after their
   complete contents are attributable and disposable. Do not run blanket
   `git clean`, forced branch deletion, or global worktree pruning.
4. Delete only exact released files/directories, with path-safe native commands;
   do not turn a glob or recursive discovery into a deletion allowlist. A tracked
   binary/fixture outside a removable worktree is source content, not scratch.
   Branch removal stays with the coordinator unless separately delegated under
   `github-pr-mergeable` policy; the disk worker has no merge/push authority.
5. Verify removed paths are absent and removed worktrees unregistered; confirm
   protected paths remain and remeasure free space. Report removed paths, kept
   paths/reasons, and observed filesystem deltas separately from size estimates
   (hard links, snapshots, open files, and concurrent writes can change recovery).

## Completion And Pressure

Use one reusable bounded agent when useful execution can proceed in parallel
and the existing budget permits. Queue a batch instead of reserving an idle
cleanup slot; perform small cleanup locally. Recheck queued targets when assigned.
If disk pressure prevents the next build/test, prioritize released scratch,
briefly pause only affected producers, and resume after recovery. Do not weaken
retention rules to make space. If only protected/uncertain data remains, record
the storage blocker and concrete broader-cleanup candidates.

Collect the result before ending execution, or explicitly stop the worker and
record remaining cleanup with its exact next action. Persist removed/retained
paths and space observations in graph state. Cleanup does not require rerunning
product tests/reviews or generating another push solely because files were removed.
