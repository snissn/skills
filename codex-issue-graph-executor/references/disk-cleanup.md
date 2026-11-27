# Disk Cleanup After Graph Work

Use for bounded cleanup batches during graph execution, including authorized
execution hosts. Skill-editing and read-only requests do not authorize deletion.
Use existing graph notes and native filesystem/Git tools; no new scheduler or
cleanup service is required.

## Required Local Deletion

Remove eligible local worktrees, no-longer-needed checkouts, their per-lane
`TMPDIR`/`GOTMPDIR` scratch roots, and their disposable generated data as soon
as the last consumer releases them. Make that decision at stage completion,
supersession, candidate retirement, merge, or a stopped lane, and close/release
finished worker runtimes so harness-managed worktrees are also reclaimed
immediately. Carry out verified deletion in the same execution checkpoint,
including before merge when a later stage can proceed from durable evidence.
Apply the same release-and-reclaim rule on remote execution/benchmark hosts
(for example, deleting disposable benchmark DB directories like `treedb_data/`
immediately after reopen verification while preserving JSON, HTML, and profile
artifacts). Retain only required evidence or unique work, with its durable
location and concrete reason recorded. Use pushed source refs plus input
recipes, seeds, and hashes for reproducible data when those satisfy the
evidence contract. Keep an exact fixture or binary only when the contract
actually requires those bytes. Never delete protected or unreleased content to
meet this requirement.

Local worktree/output deletion proceeds independently of remote branch cleanup.
A protected remote ref, squash merge, or retained source ref is not a reason to
keep a clean released checkout. Verify required source commits are recoverable
from pushed refs or another explicitly accepted durable source binding. Report
local branch and remote-branch retention separately under the helper's policy.

## Scope And Release

- Inventory recorded run roots and attributable graph outputs: completed issue,
  baseline, review, and disposable clone/worktree directories; generated test or
  benchmark DBs and fixtures; binaries, test executables, build intermediates;
  temporary profiles/logs, downloads, and run-local caches. Prior-run leftovers
  are eligible only when ownership and release can still be verified.
- When allocating large paths, record their absolute paths, hosts, expected
  release events, and producer, consumer, and cleanup ownership in existing
  graph notes. At release, record estimated sizes and any retention reason.
  Require evidence of release even if the path is old, its name looks
  temporary, the PR merged, or the content can be regenerated.
- Release a path only after its writer/commands have stopped, descendants no
  longer consume it, and useful work and required evidence are preserved.
  At release, capture expected path/type and filesystem identity plus a
  contents/metadata inventory sufficient to detect replacement or additions;
  pass this snapshot with the allowlist. A pathname and size alone do not suffice.
  Preserve accepted and failed-candidate raw results, provenance, required
  non-reproducible inputs, scientific artifacts, and anything required for
  review/recovery. This does not require retaining the surrounding checkout,
  generated corpus, working DB, or run-local cache. A disposable
  working DB can go when the retained evidence and reproducible fixture suffice.
  Verify any required durable copy and its location before removing the local one.
- The coordinator gives one cleaner an exact allowlist and protected-path list.
  Do not reuse or reassign released paths until the cleaner finishes; resolve
  in-flight deletion before taking ownership back. No other worker/helper cleans
  the same paths. New candidates discovered by the cleaner need coordinator
  release before deletion, not a new user prompt for already authorized scope.
- Preserve primary checkouts, active/provisional worktrees, user files, real DBs,
  unrelated graph outputs, externally owned Go build caches, and shared
  persistent module/package caches. Add externally owned caches to the protected
  paths even if they sit under a task-looking directory. Separately isolated
  caches follow their recorded exception, owner, and normal release checks.
  Report large shared or unattributed candidates with sizes. Broader host
  cleanup requires explicit scope.

## Go Build Caches

- Go's built-in `DiskCache.Trim()` uses a 5-day idle TTL with **no byte cap**, so
  multi-worktree, `-race` (`100–350 MB` per `.a`), and cross-OS builds quickly
  grow a cache to `15–20+ GiB`, and ad-hoc per-worker caches multiply that bloat
  across `/tmp`. Standardize on **ONE persistent host-level shared agent
  `GOCACHE`** per `(execution host, user)` (macOS:
  `$HOME/Library/Caches/agent-go-build`; Linux/remote: high-capacity mount such
  as `/mnt/fast4tb/.cache/agent-go-build` or
  `${XDG_CACHE_HOME:-$HOME/.cache}/agent-go-build`), and pass `-trimpath` on
  `go build`, `go vet`, compile-only cross-OS checks, and `-trimpath`-safe
  `go test` invocations so all worktrees share compiled actions. Never create
  per-worker `/tmp/*-gocache` directories for routine work.
- **Prefer live-safe mtime-LRU byte-capped pruning over nuclear `go clean -cache`:**
  Go's `DiskCache` updates `mtime` on cache hits (`1h` resolution) and treats
  missing `*-a`/`*-d` files as benign misses. At coordinator startup, wave/sprint
  boundaries, lane releases, disk-pressure checkpoints, and graph closeout, run:
  `python3 <SKILLS_ROOT>/codex-issue-graph-executor/scripts/gocache_prune.py --cache-dir "<SHARED_GOCACHE>" --max-gb 10 --target-gb 6 --min-age-seconds 7200`
  (use `--max-gb 8 --target-gb 5` on laptops with `< 50 GiB` free; `--max-gb 20
  --target-gb 12` on high-capacity hosts such as `/mnt/fast4tb`). Because entries
  newer than `2h` are never touched (lowered to `15m` only under `< 15 GiB`
  emergency disk pressure), this safely bounds disk usage even while concurrent
  builds run and preserves warm stdlib/`-race`/dependency artifacts across waves.
- **When full `go clean -cache` is used (isolated exceptions or orphaned legacy
  caches only):** never run `go clean -cache` while any Go process uses that
  cache. After verifying zero active consumers (and identity/release checks
  below), run `GOCACHE="<exact-absolute-path>" go clean -cache` from a neutral
  working directory (leaving `GOMODCACHE` intact), verify the hexadecimal buckets
  are empty, and remove disposable isolated/orphaned `/tmp/*-gocache` directories
  so dead bucket trees do not linger. Never delete the user's protected personal
  `GOCACHE` or shared `GOMODCACHE` without explicit authorization.
- Delete each lane's dedicated `TMPDIR`/`GOTMPDIR` root together with its
  released worktree so orphaned `go-build*` and `t.TempDir()`/`Benchmark*`
  directories are reclaimed immediately.

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
   Assess consumers that plausibly use the target, using exact producer/consumer
   releases, graph commands, and readable executable, open-file, or mapping
   evidence where useful. Universal host process-map readability is not required.
   An unreadable unrelated service does not by itself make a released target
   uncertain; record why available command, ancestry, start-time, or ownership
   evidence excludes a plausible connection. Retain the affected target if a
   relevant consumer remains active or cannot be ruled out, or if target identity
   or evidence preservation cannot be verified. Do not equate a release notice
   alone with proof of inactivity or escalate privileges merely to inspect
   unrelated processes.
3. For a worktree, verify registration, current HEAD, clean tracked state,
   untracked/ignored contents, and preservation of required commits on durable
   refs. Delete only separately allowlisted disposable generated contents, then
   use `git worktree remove <exact-path>` without force. If it refuses, retain and
   report the reason. Do not create a whole-worktree backup to bypass a refusal;
   identify the specific dirty work, consumer, or evidence requirement. Remove
   unregistered scratch directories only after their
   complete contents are attributable and disposable. Do not run blanket
   `git clean`, forced branch deletion, or global worktree pruning.
4. Delete only exact released files/directories, with path-safe native commands;
   do not turn a glob or recursive discovery into a deletion allowlist. A tracked
   binary/fixture outside a removable worktree is source content, not scratch.
   Branch removal stays with the coordinator unless separately delegated under
   `github-pr-mergeable` policy; the disk worker has no merge/push authority.
5. Verify removed paths are absent, removed worktrees unregistered, and cleaned
   build cache entries gone. Confirm protected paths remain and remeasure free
   space. Report removed paths, cleared caches, kept paths with reasons, and
   observed filesystem deltas separately from size estimates
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
paths and space observations in graph state. A queued deletion or a relocated
worktree is not a completed cleanup result. Retained paths need an explicit
retention requirement or a concrete blocker, rather than a default archive.
Cleanup does not require rerunning
product tests/reviews or generating another push solely because files were removed.
