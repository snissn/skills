# Worktree Creation With CoW Fallback

Use the bundled Python helper for new writable lanes. It uses native Git
registration and a separate branch/index, then prefers macOS `clonefile` for
tracked working files. File writes remain independent; hard links are never used.
The macOS backend is qualified here. Other platforms use ordinary Git checkout.

```bash
python3 <SKILL_DIR>/scripts/create_worktree.py \
  --repo /path/to/repo \
  --path /path/to/existing-parent/issue-123 \
  --branch codex/issue-123 \
  --base <EXACT_BASE_SHA> \
  --seed /path/to/clean-worktree
```

`--seed` defaults to `--repo`; `--mode auto` is the default. `--mode git` requests
ordinary `git worktree add` explicitly. The destination parent must exist and the
destination and local branch must be new. Existing worktrees stay under their
current owner; this helper never removes a destination or resets a branch.

## Seed And Base

- Pin the actual predecessor/base commit before creation. The seed must share
  the repository's Git common directory, have exactly that HEAD, and have no
  staged or unstaged tracked changes. A sparse seed or submodule checkout uses
  ordinary Git instead. Untracked/ignored seed files are excluded from the copy.
- Use a quiescent seed on the same filesystem as the destination. A shared APFS
  format alone is insufficient across volumes. Do not move, edit, delete, or
  reassign the seed or destination while setup runs. Keep the destination
  private until successful validation; do not start workers early.
- Reuse an eligible existing checkout when available. A prepared linked seed
  can help several large lanes at the same base; creating an extra full seed for
  one small lane can cost more than it saves. Gomap's source is small and its
  shared Go build/module cache is normally more useful; physics' large tracked
  inputs benefit more. Setup speed varied across local pilots; choose CoW for
  its storage savings.
- Copy tracked files only. Ignored caches, virtual environments, test/benchmark
  DBs, profiles, and generated datasets are not inherited. Shared persistent
  tool caches stay under their existing tooling and ownership rules.

## Validation And Fallback

Git creates the new worktree with `--no-checkout` on the CoW path. The helper
initializes its index from the pinned commit, clones the tracked files, checks
that the seed stayed clean at that commit, refreshes the new index through Git's
normal filters, and requires a clean checkout with the expected HEAD/branch.
The success JSON records `mode`, `worktree`, `branch`, `base_sha`, `seed`,
`fallback_reason`, `cloned_files`, and `cloned_bytes`. Save that result in existing
node notes and include it in the worker assignment.

A dirty, mismatched, unavailable, sparse, or cross-filesystem seed, unqualified
platform, or unsupported clone operation falls back to ordinary Git at the
requested commit. A partial clone can be overwritten only within the helper's
fresh private destination, before worker handoff. The helper uses Git checkout
filters, so Git LFS materialized files remain valid; LFS objects and filter
temporary files still need disk space and are not eliminated by CoW.

These conditions stop setup instead of forcing a fallback:

- An existing destination or branch, invalid base, or changed destination
  identity/HEAD/branch. Do not reset another owner's work.
- A target filesystem unable to represent case-colliding tracked paths. The
  tested physics snapshot contains `qm-foundations/README.md` and
  `qm-foundations/readme.md`; a full clean checkout requires a case-sensitive
  filesystem. Ordinary Git cannot preserve both on a case-insensitive volume.
- Disk/quota exhaustion. A full-copy retry consumes more storage. Record the
  incomplete path/branch, stop its consumers, and resolve storage or release it
  through the normal exact-path cleanup policy before retrying at a fresh path.

Errors return a nonzero exit and bounded diagnostics. Failed nonempty setup
paths are retained for inspection; success is required before assigning a lane.
Never force worktree removal or blanket Git cleanup to hide a setup failure.

Completed clones retain file data when a released linked seed is deleted; the
repository's primary/common Git store remains required. Protect only in-flight
copy consumers and other real seed users, then release disposable linked seeds
to the normal async cleanup owner. Measure free-space changes on each affected
filesystem: logical or summed clone sizes overstate physical reclaim.

Run the disposable integration checks after changing the helper:

```bash
python3 <SKILL_DIR>/scripts/test_create_worktree.py
```

The checks exercise isolation, native registration/indexes, pinned-base and dirty
seed fallback, ignored data exclusion, existing path/ref preservation, case
collisions, setup ownership changes, storage exhaustion, Git LFS when installed,
and exact worktree deletion/unregistration. Cross-volume fallback runs when a
second local test filesystem is available; ordinary Git remains the portable
fallback.
