#!/usr/bin/env python3
"""Live-safe mtime-LRU byte-capped pruner for a shared Go build cache (GOCACHE).

Go's built-in DiskCache.Trim() only evicts entries unused for 5 days and enforces
no byte limit, which lets multi-worktree / -race / cross-OS development grow a
cache to 15-20+ GiB within hours.

Because Go's DiskCache updates mtime on cache hits (at most once per 1h
mtimeInterval) and treats missing *-a / *-d entries as benign cache misses
(identically to Go's own trimSubdir), deleting entries whose mtime is older than
--min-age-seconds (default 7200s = 2h) oldest-first is safe even while other Go
builds are running concurrently.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

HEX_BUCKETS = frozenset(f"{i:02x}" for i in range(256))


@dataclass
class CacheEntry:
    path: Path
    size: int
    mtime: float
    is_dir: bool


def _resolve_default_cache_dir() -> Path:
    env_cache = os.environ.get("GOCACHE", "").strip()
    if env_cache and env_cache != "off":
        return Path(env_cache)
    out = subprocess.check_output(["go", "env", "GOCACHE"], text=True).strip()
    if not out or out == "off":
        raise SystemExit("Unable to resolve GOCACHE (got empty or 'off').")
    return Path(out)


def _validate_cache_dir(cache_dir: Path) -> None:
    if not cache_dir.is_absolute():
        raise SystemExit(f"Refusing non-absolute cache path: {cache_dir}")
    if cache_dir.is_symlink():
        raise SystemExit(f"Refusing symlink cache path: {cache_dir}")
    resolved = cache_dir.resolve()
    home = Path.home().resolve()
    if resolved in (Path("/"), home, Path("/tmp"), Path("/private/tmp"), Path("/var")):
        raise SystemExit(f"Refusing unsafe top-level directory as GOCACHE: {resolved}")
    if not cache_dir.exists():
        return
    if not cache_dir.is_dir():
        raise SystemExit(f"GOCACHE path is not a directory: {cache_dir}")

    # Verify the directory looks like a Go DiskCache (empty, has trim.txt/README,
    # or contains only expected Go cache items / hex buckets).
    entries = list(cache_dir.iterdir())
    if not entries:
        return
    has_marker = any(
        e.name in ("trim.txt", "README") or e.name in HEX_BUCKETS for e in entries
    )
    if not has_marker:
        raise SystemExit(
            f"Refusing directory that does not look like a Go build cache: {cache_dir}"
        )


def _dir_size_and_mtime(dir_path: Path) -> tuple[int, float]:
    total = 0
    latest_mtime = dir_path.lstat().st_mtime
    try:
        with os.scandir(dir_path) as it:
            for child in it:
                try:
                    st = child.stat(follow_symlinks=False)
                except OSError:
                    continue
                total += st.st_size
                if st.st_mtime > latest_mtime:
                    latest_mtime = st.st_mtime
    except OSError:
        pass
    return total, latest_mtime


def _scan_cache(cache_dir: Path) -> list[CacheEntry]:
    entries: list[CacheEntry] = []
    if not cache_dir.is_dir():
        return entries
    for bucket_name in sorted(HEX_BUCKETS):
        bucket = cache_dir / bucket_name
        if not bucket.is_dir() or bucket.is_symlink():
            continue
        try:
            with os.scandir(bucket) as it:
                for de in it:
                    name = de.name
                    if not (name.endswith("-a") or name.endswith("-d")):
                        continue
                    try:
                        st = de.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    p = Path(de.path)
                    if de.is_symlink():
                        continue
                    if de.is_dir(follow_symlinks=False):
                        sz, mt = _dir_size_and_mtime(p)
                        entries.append(CacheEntry(path=p, size=sz, mtime=mt, is_dir=True))
                    else:
                        entries.append(
                            CacheEntry(path=p, size=st.st_size, mtime=st.st_mtime, is_dir=False)
                        )
        except OSError:
            continue
    return entries


def _free_bytes(path: Path) -> int:
    probe = path if path.exists() else path.parent
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    st = os.statvfs(probe)
    return st.f_bavail * st.f_frsize


def _delete_entry(entry: CacheEntry) -> bool:
    try:
        if entry.is_dir:
            shutil.rmtree(entry.path)
        else:
            entry.path.unlink()
        return True
    except FileNotFoundError:
        return False
    except OSError:
        return False


def prune_cache(
    cache_dir: Path,
    *,
    max_gb: float,
    target_gb: float,
    min_age_seconds: int,
    emergency_free_gb: float,
    emergency_min_age_seconds: int,
    dry_run: bool,
    now: float | None = None,
) -> dict:
    _validate_cache_dir(cache_dir)
    if target_gb > max_gb:
        raise SystemExit("--target-gb must be <= --max-gb")

    now_ts = time.time() if now is None else now
    max_bytes = int(max_gb * (1024**3))
    target_bytes = int(target_gb * (1024**3))
    emergency_free_bytes = int(emergency_free_gb * (1024**3))

    free_before = _free_bytes(cache_dir)
    entries = _scan_cache(cache_dir)
    total_before = sum(e.size for e in entries)

    under_disk_pressure = emergency_free_bytes > 0 and free_before < emergency_free_bytes
    should_prune = total_before > max_bytes or (under_disk_pressure and total_before > target_bytes)

    deleted_count = 0
    deleted_bytes = 0
    effective_min_age = min_age_seconds
    remaining_bytes = total_before

    def _run_pass(age_floor: int) -> None:
        nonlocal deleted_count, deleted_bytes, remaining_bytes
        cutoff = now_ts - age_floor
        eligible = [e for e in entries if e.mtime < cutoff and e.path.exists()]
        # Evict oldest-mtime first; break ties by largest object first so
        # superseded 300MB -race archives shed before small metadata entries.
        eligible.sort(key=lambda e: (e.mtime, -e.size))
        for entry in eligible:
            if remaining_bytes <= target_bytes:
                break
            if dry_run:
                deleted_count += 1
                deleted_bytes += entry.size
                remaining_bytes -= entry.size
            else:
                # Recheck mtime right before unlink to guard against a concurrent hit.
                try:
                    st = entry.path.lstat()
                    if st.st_mtime >= cutoff:
                        continue
                except OSError:
                    continue
                if _delete_entry(entry):
                    deleted_count += 1
                    deleted_bytes += entry.size
                    remaining_bytes -= entry.size

    if should_prune:
        _run_pass(min_age_seconds)
        if (
            under_disk_pressure
            and remaining_bytes > target_bytes
            and emergency_min_age_seconds < min_age_seconds
        ):
            effective_min_age = emergency_min_age_seconds
            _run_pass(emergency_min_age_seconds)

    protected_bytes = sum(
        e.size for e in entries if (now_ts - e.mtime) < effective_min_age
    )
    free_after = _free_bytes(cache_dir)

    return {
        "cache_dir": str(cache_dir),
        "dry_run": dry_run,
        "triggered": should_prune,
        "disk_pressure": under_disk_pressure,
        "effective_min_age_seconds": effective_min_age,
        "entries_scanned": len(entries),
        "before_bytes": total_before,
        "after_bytes": remaining_bytes,
        "deleted_entries": deleted_count,
        "deleted_bytes": deleted_bytes,
        "protected_recent_bytes": protected_bytes,
        "free_before_bytes": free_before,
        "free_after_bytes": free_after,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Live-safe mtime-LRU byte-capped pruner for Go GOCACHE."
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Absolute path to GOCACHE directory (default: $GOCACHE or `go env GOCACHE`).",
    )
    parser.add_argument(
        "--max-gb",
        type=float,
        default=10.0,
        help="Trigger pruning when cache size exceeds this many GiB (default: 10.0).",
    )
    parser.add_argument(
        "--target-gb",
        type=float,
        default=6.0,
        help="Prune down to this many GiB when triggered (default: 6.0).",
    )
    parser.add_argument(
        "--min-age-seconds",
        type=int,
        default=7200,
        help="Never delete entries newer than this many seconds (default: 7200 = 2h).",
    )
    parser.add_argument(
        "--emergency-free-gb",
        type=float,
        default=15.0,
        help="If filesystem free space drops below this many GiB, prune toward --target-gb and allow --emergency-min-age-seconds (default: 15.0).",
    )
    parser.add_argument(
        "--emergency-min-age-seconds",
        type=int,
        default=900,
        help="Lower active-age floor used only under --emergency-free-gb pressure (default: 900 = 15m).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be pruned without deleting anything.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON summary.",
    )
    args = parser.parse_args(argv)

    cache_dir = args.cache_dir if args.cache_dir is not None else _resolve_default_cache_dir()
    result = prune_cache(
        cache_dir,
        max_gb=args.max_gb,
        target_gb=args.target_gb,
        min_age_seconds=args.min_age_seconds,
        emergency_free_gb=args.emergency_free_gb,
        emergency_min_age_seconds=args.emergency_min_age_seconds,
        dry_run=args.dry_run,
    )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        gib = 1024**3
        action = "DRY-RUN" if result["dry_run"] else ("PRUNED" if result["deleted_entries"] else "OK")
        print(
            f"[{action}] {result['cache_dir']}: "
            f"{result['before_bytes']/gib:.2f} GiB -> {result['after_bytes']/gib:.2f} GiB "
            f"(deleted {result['deleted_entries']} entries / {result['deleted_bytes']/gib:.2f} GiB; "
            f"protected <{result['effective_min_age_seconds']}s: {result['protected_recent_bytes']/gib:.2f} GiB; "
            f"disk free: {result['free_before_bytes']/gib:.1f} -> {result['free_after_bytes']/gib:.1f} GiB)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
