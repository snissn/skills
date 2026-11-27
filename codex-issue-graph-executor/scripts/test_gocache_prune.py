#!/usr/bin/env python3
"""Unit tests for gocache_prune.py."""

from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import gocache_prune


def _make_entry(path: Path, size: int, mtime: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)
    os.utime(path, (mtime, mtime))


class GoCachePruneTest(unittest.TestCase):
    def test_under_cap_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "agent-go-build"
            root.mkdir()
            (root / "trim.txt").write_text("1700000000")
            now = 2_000_000_000.0
            _make_entry(root / "00" / "aaaa-d", 1024, now - 10_000)
            res = gocache_prune.prune_cache(
                root,
                max_gb=1.0,
                target_gb=0.5,
                min_age_seconds=7200,
                emergency_free_gb=0.0,
                emergency_min_age_seconds=900,
                dry_run=False,
                now=now,
            )
            self.assertFalse(res["triggered"])
            self.assertEqual(res["deleted_entries"], 0)
            self.assertTrue((root / "00" / "aaaa-d").exists())

    def test_lru_evicts_oldest_first_and_protects_recent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "agent-go-build"
            root.mkdir()
            (root / "trim.txt").write_text("1700000000")
            (root / "fuzz").mkdir()
            (root / "fuzz" / "corpus").write_bytes(b"z" * 4096)

            now = 2_000_000_000.0
            mib = 1024 * 1024
            old_big = root / "0a" / "1111-d"
            old_small = root / "0b" / "2222-a"
            mid_dir = root / "0c" / "3333-d"
            mid_dir.mkdir(parents=True)
            mid_exec = mid_dir / "pkg.test"
            recent = root / "ff" / "9999-d"

            _make_entry(old_big, 4 * mib, now - 20_000)
            _make_entry(old_small, 1 * mib, now - 20_000)
            _make_entry(mid_exec, 3 * mib, now - 10_000)
            os.utime(mid_dir, (now - 10_000, now - 10_000))
            _make_entry(recent, 4 * mib, now - 300)  # < 2h -> protected

            # Total = 12 MiB; cap = 8 MiB -> target = 6 MiB.
            # Oldest (now - 20000) tie-breaks largest first: deletes old_big (4 MiB) -> 8 MiB,
            # then old_small (1 MiB) -> 7 MiB, then mid_dir (3 MiB) -> 4 MiB <= 6 MiB.
            # Recent (4 MiB) and trim.txt and fuzz/ stay untouched.
            res = gocache_prune.prune_cache(
                root,
                max_gb=8.0 / 1024.0,
                target_gb=6.0 / 1024.0,
                min_age_seconds=7200,
                emergency_free_gb=0.0,
                emergency_min_age_seconds=900,
                dry_run=False,
                now=now,
            )
            self.assertTrue(res["triggered"])
            self.assertEqual(res["deleted_entries"], 3)
            self.assertEqual(res["after_bytes"], 4 * mib)
            self.assertFalse(old_big.exists())
            self.assertFalse(old_small.exists())
            self.assertFalse(mid_dir.exists())
            self.assertTrue(recent.exists())
            self.assertTrue((root / "trim.txt").exists())
            self.assertTrue((root / "fuzz" / "corpus").exists())

    def test_dry_run_does_not_delete(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "agent-go-build"
            root.mkdir()
            (root / "trim.txt").write_text("1")
            now = time.time()
            mib = 1024 * 1024
            f = root / "01" / "abcd-d"
            _make_entry(f, 4 * mib, now - 20_000)
            res = gocache_prune.prune_cache(
                root,
                max_gb=2.0 / 1024.0,
                target_gb=1.0 / 1024.0,
                min_age_seconds=7200,
                emergency_free_gb=0.0,
                emergency_min_age_seconds=900,
                dry_run=True,
                now=now,
            )
            self.assertTrue(res["dry_run"])
            self.assertEqual(res["deleted_entries"], 1)
            self.assertTrue(f.exists())

    def test_emergency_disk_pressure_lowers_min_age(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "agent-go-build"
            root.mkdir()
            (root / "trim.txt").write_text("1")
            now = 2_000_000_000.0
            mib = 1024 * 1024
            semi_recent = root / "10" / "aaaa-d"
            active = root / "11" / "bbbb-d"
            _make_entry(semi_recent, 4 * mib, now - 3600)  # 1h old (< 2h, > 15m)
            _make_entry(active, 4 * mib, now - 120)        # 2m old (< 15m -> protected)

            with mock.patch.object(gocache_prune, "_free_bytes", return_value=5 * (1024**3)):
                res = gocache_prune.prune_cache(
                    root,
                    max_gb=10.0,
                    target_gb=5.0 / 1024.0,
                    min_age_seconds=7200,
                    emergency_free_gb=15.0,
                    emergency_min_age_seconds=900,
                    dry_run=False,
                    now=now,
                )
            self.assertTrue(res["disk_pressure"])
            self.assertEqual(res["effective_min_age_seconds"], 900)
            self.assertFalse(semi_recent.exists())
            self.assertTrue(active.exists())

    def test_refuses_non_cache_directory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            not_cache = Path(td) / "my-project"
            not_cache.mkdir()
            (not_cache / "main.go").write_text("package main\n")
            with self.assertRaises(SystemExit):
                gocache_prune.prune_cache(
                    not_cache,
                    max_gb=1.0,
                    target_gb=0.5,
                    min_age_seconds=7200,
                    emergency_free_gb=0.0,
                    emergency_min_age_seconds=900,
                    dry_run=True,
                )


if __name__ == "__main__":
    unittest.main()
