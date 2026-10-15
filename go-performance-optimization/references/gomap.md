# Gomap Allocation Reuse

Use this reference for material Go allocation work in `snissn/gomap`. Existing
repository arenas are the default for eligible bulk or common-lifetime storage.
Inventory the intended base's maintained mechanisms and their consumers before
proposing a heap-allocating helper, replacement pool, or new arena. Reuse the
strongest suitable seam; a different choice needs a documented lifetime/API mismatch
or measured public-path reason and protected ownership/retention controls. Do not
force an arena into a workload whose maintained path already avoids the cost.

Source starting points below are navigation hints; verify their current symbols,
contracts, and tests at the actual base rather than treating this list as authority:

- `TreeDB/batch/batch.go`: `Batch.arenaChunks`, chunked key/value copies,
  `Acquire`, `Reset`, and retention-limited arena reset/release.
- `TreeDB/caching/db.go`: batch `copyArena`/pointer-value storage, arena leases,
  memtable/view ownership, transfer and release. Check
  `TreeDB/caching/batch_arena_ownership_test.go` and related arena-budget tests;
  batch reset must preserve earlier borrowed writes and active readers.
- `TreeDB/internal/memtable/hash_sorted.go` and `btree.go`: chunked `hashArena`
  and `btreeArena`; hash-sorted reset waits for asynchronous indexing before
  reusing memory. Check each mode's actual borrowing and reset contract.
- `TreeDB/internal/valuelog/writer.go`: bounded append-buffer reuse and scratch
  retention. Preserve pending write consumers and the persistent value-log
  contract; resetting transient memory does not retire stored value segments.

Put the selected mechanism, reuse/exception rationale, actual public activation,
`B/op` plus `allocs/op`, and relevant retained/peak-memory and lifetime checks in
the owning issue/PR's existing evidence. Bulk storage may lower object count while
leaving allocated bytes unchanged. Preserve explicit private grants and publication,
snapshot, rollback, and last-consumer boundaries wherever applicable. A compact
source-linked finding is sufficient; no separate arena report or universal new
allocator is required.
