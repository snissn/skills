#!/usr/bin/env python3
"""Integration checks using synthetic disposable Git repositories only."""

import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("create_worktree.py")
spec = importlib.util.spec_from_file_location("worktree_helper", SCRIPT)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def git(repo, *args, input=None):
    return subprocess.check_output(
        ["git", "-C", os.fspath(repo), *args], input=input, stderr=subprocess.PIPE,
        env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"),
    )


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class WorktreeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cow-worktree-test-")
        self.root = Path(self.tmp.name).resolve()
        self.repo = self.root / "source with spaces"
        self.repo.mkdir()
        git(self.repo, "init", "--quiet")
        git(self.repo, "config", "user.name", "Disposable Test")
        git(self.repo, "config", "user.email", "test@example.invalid")
        (self.repo / ".gitignore").write_text("scratch/\n")
        (self.repo / "readme.txt").write_text("pinned contents\n")
        (self.repo / "payload.bin").write_bytes(os.urandom(16384))
        (self.repo / "run.sh").write_text("#!/bin/sh\nexit 0\n")
        (self.repo / "run.sh").chmod(0o755)
        (self.repo / "link").symlink_to("readme.txt")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "--quiet", "-m", "fixture")
        self.base = git(self.repo, "rev-parse", "HEAD").decode().strip()
        self.external = None

    def tearDown(self):
        # Every repository, branch and mutation here is a synthetic fixture.
        listing = git(self.repo, "worktree", "list", "--porcelain").decode()
        for line in listing.splitlines():
            if line.startswith("worktree "):
                path = line[9:]
                if Path(path).resolve() != self.repo:
                    git(self.repo, "worktree", "remove", "--force", path)
        if self.external:
            self.external.cleanup()
        self.tmp.cleanup()

    def create(self, name="feature", **kwargs):
        return helper.create_worktree(
            self.repo, self.root / name, "codex/" + name,
            kwargs.pop("base", self.base), **kwargs,
        )

    def assert_checkout(self, result, expected=None):
        target = Path(result["worktree"])
        self.assertEqual(git(target, "rev-parse", "HEAD").decode().strip(), expected or self.base)
        self.assertEqual(git(target, "status", "--porcelain=v1", "--untracked-files=all"), b"")
        self.assertEqual(git(target, "symbolic-ref", "--short", "HEAD").decode().strip(), result["branch"])
        return target

    def test_cli_native_registration_separate_index_and_special_files(self):
        result = json.loads(subprocess.check_output([
            sys.executable, os.fspath(SCRIPT), "--repo", os.fspath(self.repo),
            "--path", os.fspath(self.root / "CLI with spaces"),
            "--branch", "codex/issue-123", "--base", self.base,
        ]))
        target = self.assert_checkout(result)
        if sys.platform == "darwin":
            self.assertEqual(result["mode"], "cow")
        self.assertTrue((target / ".git").is_file())
        self.assertEqual(os.readlink(target / "link"), "readme.txt")
        self.assertTrue((target / "run.sh").stat().st_mode & 0o111)
        self.assertNotEqual((target / "payload.bin").stat().st_ino, (self.repo / "payload.bin").stat().st_ino)
        source_index = self.repo / ".git/index"
        before = digest(source_index)
        (target / "readme.txt").write_text("agent change\n")
        git(target, "add", "readme.txt")
        self.assertEqual(digest(source_index), before)
        self.assertIn(os.fsencode(target), git(self.repo, "worktree", "list", "--porcelain"))

    def test_in_place_writes_are_independent_in_both_directions(self):
        result = self.create()
        target = self.assert_checkout(result)
        original = digest(self.repo / "payload.bin")
        with (target / "payload.bin").open("r+b") as f:
            f.write(b"agent mutation")
        self.assertEqual(digest(self.repo / "payload.bin"), original)
        target_hash = digest(target / "payload.bin")
        with (self.repo / "payload.bin").open("r+b") as f:
            f.write(b"seed mutation")
        self.assertEqual(digest(target / "payload.bin"), target_hash)
        self.assertEqual((target / "payload.bin").stat().st_nlink, 1)

    def test_untracked_and_ignored_outputs_are_not_inherited(self):
        (self.repo / "scratch").mkdir()
        (self.repo / "scratch/db.bin").write_bytes(b"disposable benchmark")
        (self.repo / "unique-untracked.txt").write_text("unique source work")
        target = self.assert_checkout(self.create())
        self.assertFalse((target / "scratch").exists())
        self.assertFalse((target / "unique-untracked.txt").exists())
        self.assertTrue((self.repo / "unique-untracked.txt").exists())

    @unittest.skipUnless(shutil.which("git-lfs"), "Git LFS unavailable")
    def test_git_lfs_materialized_files_are_clean_in_both_modes(self):
        for key, value in [
            ("filter.lfs.clean", "git-lfs clean -- %f"),
            ("filter.lfs.smudge", "git-lfs smudge -- %f"),
            ("filter.lfs.process", "git-lfs filter-process"),
            ("filter.lfs.required", "true"),
        ]:
            git(self.repo, "config", key, value)
        (self.repo / ".gitattributes").write_text("*.bin filter=lfs diff=lfs merge=lfs -text\n")
        original_hash = digest(self.repo / "payload.bin")
        git(self.repo, "add", ".gitattributes", "payload.bin")
        git(self.repo, "commit", "--quiet", "-m", "LFS fixture")
        self.base = git(self.repo, "rev-parse", "HEAD").decode().strip()
        self.assertTrue(git(self.repo, "show", self.base + ":payload.bin").startswith(b"version https://git-lfs"))
        for mode in ("auto", "git"):
            target = self.assert_checkout(self.create("lfs-" + mode, mode=mode))
            self.assertEqual(digest(target / "payload.bin"), original_hash)
            self.assertEqual(git(target, "write-tree"), git(self.repo, "write-tree"))

    def test_existing_destination_and_dangling_symlink_are_preserved(self):
        existing = self.root / "existing"
        existing.mkdir()
        (existing / "unique").write_text("keep")
        before = git(self.repo, "show-ref")
        with self.assertRaises(helper.SetupError):
            self.create("existing")
        dangling = self.root / "dangling"
        dangling.symlink_to(self.root / "missing")
        with self.assertRaises(helper.SetupError):
            self.create("dangling")
        self.assertEqual((existing / "unique").read_text(), "keep")
        self.assertTrue(dangling.is_symlink())
        self.assertEqual(git(self.repo, "show-ref"), before)

    def test_existing_branch_is_not_reset(self):
        git(self.repo, "branch", "codex/existing")
        before = git(self.repo, "show-ref")
        with self.assertRaises(helper.SetupError):
            self.create("existing")
        self.assertFalse((self.root / "existing").exists())
        self.assertEqual(git(self.repo, "show-ref"), before)

    def test_requested_base_is_used_when_seed_head_differs(self):
        (self.repo / "readme.txt").write_text("newer contents\n")
        git(self.repo, "commit", "--quiet", "-am", "newer")
        source_head = git(self.repo, "rev-parse", "HEAD")
        result = self.create(base=self.base)
        target = self.assert_checkout(result)
        self.assertEqual(result["mode"], "git")
        self.assertEqual((target / "readme.txt").read_text(), "pinned contents\n")
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), source_head)

    def test_dirty_seed_falls_back_without_reverting_source_work(self):
        (self.repo / "readme.txt").write_text("unique dirty source\n")
        git(self.repo, "add", "readme.txt")
        before = git(self.repo, "status", "--porcelain=v1")
        result = self.create()
        target = self.assert_checkout(result)
        self.assertEqual(result["mode"], "git")
        self.assertEqual((target / "readme.txt").read_text(), "pinned contents\n")
        self.assertEqual(git(self.repo, "status", "--porcelain=v1"), before)
        self.assertEqual((self.repo / "readme.txt").read_text(), "unique dirty source\n")

    def test_missing_seed_and_explicit_git_mode_fall_back(self):
        for name, options in [("missing", {"seed": self.root / "missing-seed"}), ("ordinary", {"mode": "git"})]:
            result = self.create(name, **options)
            self.assert_checkout(result)
            self.assertEqual(result["mode"], "git")
            self.assertEqual(result["cloned_files"], 0)

    @unittest.skipUnless(sys.platform == "darwin", "requires native clone path")
    def test_partial_clone_failure_falls_back_to_complete_clean_checkout(self):
        original = helper.clone_file
        calls = 0
        def fail_after_one(source, target):
            nonlocal calls
            calls += 1
            if calls > 1:
                raise OSError(errno.ENOTSUP, "injected unsupported clone")
            original(source, target)
        with patch.object(helper, "clone_file", side_effect=fail_after_one):
            result = self.create()
        target = self.assert_checkout(result)
        self.assertEqual(result["mode"], "git")
        self.assertEqual(digest(target / "payload.bin"), digest(self.repo / "payload.bin"))

    @unittest.skipUnless(sys.platform == "darwin", "requires native clone path")
    def test_seed_mutation_during_copy_is_detected_and_preserved(self):
        original = helper.copy_tracked
        def change_seed(seed, target, files):
            result = original(seed, target, files)
            (seed / "readme.txt").write_text("concurrent source change\n")
            return result
        with patch.object(helper, "copy_tracked", side_effect=change_seed):
            result = self.create()
        target = self.assert_checkout(result)
        self.assertEqual(result["mode"], "git")
        self.assertEqual((target / "readme.txt").read_text(), "pinned contents\n")
        self.assertEqual((self.repo / "readme.txt").read_text(), "concurrent source change\n")

    @unittest.skipUnless(sys.platform == "darwin", "requires native clone path")
    def test_seed_file_type_change_does_not_modify_symlink_target(self):
        outside = self.root / "unrelated.txt"
        outside.write_text("preserve unrelated file\n")
        before = outside.stat()
        original = helper.clone_file
        def replace_seed_file(source, target):
            if source.name == "payload.bin":
                source.unlink()
                source.symlink_to(outside)
            original(source, target)
        with patch.object(helper, "clone_file", side_effect=replace_seed_file):
            result = self.create()
        target = self.assert_checkout(result)
        self.assertEqual(result["mode"], "git")
        self.assertFalse((target / "payload.bin").is_symlink())
        self.assertTrue((self.repo / "payload.bin").is_symlink())
        self.assertEqual(outside.stat().st_ctime_ns, before.st_ctime_ns)
        self.assertEqual(outside.stat().st_mode, before.st_mode)
        self.assertEqual(outside.read_text(), "preserve unrelated file\n")

    @unittest.skipUnless(sys.platform == "darwin", "requires native clone path")
    def test_disk_exhaustion_does_not_trigger_full_copy_fallback(self):
        original_git = helper.git
        calls = []
        def recorded_git(repo, *args, **kwargs):
            calls.append(args)
            return original_git(repo, *args, **kwargs)
        with patch.object(helper, "git", side_effect=recorded_git), \
             patch.object(helper, "clone_file", side_effect=OSError(errno.ENOSPC, "injected full disk")):
            with self.assertRaises(helper.StorageError):
                self.create()
        self.assertFalse(any(args[0] == "checkout-index" for args in calls))
        self.assertTrue((self.root / "feature/.git").is_file())
        self.assertEqual((self.repo / "readme.txt").read_text(), "pinned contents\n")

    @unittest.skipUnless(sys.platform == "darwin", "requires native clone path")
    def test_filter_disk_exhaustion_does_not_trigger_full_copy_fallback(self):
        original_git = helper.git
        calls = []
        def recorded_git(repo, *args, **kwargs):
            calls.append(args)
            if args[:2] == ("update-index", "--refresh"):
                raise helper.StorageError("injected filter storage exhaustion")
            return original_git(repo, *args, **kwargs)
        with patch.object(helper, "git", side_effect=recorded_git):
            with self.assertRaises(helper.StorageError):
                self.create()
        self.assertFalse(any(args[0] == "checkout-index" for args in calls))
        self.assertEqual(digest(self.root / "feature/payload.bin"), digest(self.repo / "payload.bin"))

    @unittest.skipUnless(sys.platform == "darwin", "requires native seed preflight")
    def test_seed_preflight_storage_failure_stops_before_creation(self):
        original_git = helper.git
        calls = []
        def recorded_git(repo, *args, **kwargs):
            calls.append(args)
            if args[0] == "status":
                raise helper.StorageError("injected seed filter storage exhaustion")
            return original_git(repo, *args, **kwargs)
        before = git(self.repo, "show-ref")
        with patch.object(helper, "git", side_effect=recorded_git):
            with self.assertRaises(helper.StorageError):
                self.create()
        self.assertFalse((self.root / "feature").exists())
        self.assertFalse(any(args[0] == "worktree" for args in calls))
        self.assertEqual(git(self.repo, "show-ref"), before)

    def test_git_diagnostics_are_bounded(self):
        error = helper.brief_error(("error line\n" * 10000).encode())
        self.assertLess(len(error), 3501)
        self.assertIn("truncated", error)

    def test_linked_seed_can_be_deleted_without_losing_clone_data(self):
        seed_result = self.create("seed", mode="git")
        seed = self.assert_checkout(seed_result)
        result = self.create("from-linked", seed=seed)
        target = self.assert_checkout(result)
        expected = digest(target / "payload.bin")
        git(self.repo, "worktree", "remove", os.fspath(seed))
        self.assertFalse(seed.exists())
        self.assertEqual(digest(target / "payload.bin"), expected)
        self.assert_checkout(result)
        git(self.repo, "worktree", "remove", os.fspath(target))
        self.assertFalse(target.exists())
        self.assertNotIn(os.fsencode(target), git(self.repo, "worktree", "list", "--porcelain"))

    @unittest.skipUnless(Path("/Volumes/FlashDrive").is_dir(), "external test filesystem unavailable")
    def test_cross_filesystem_uses_ordinary_git(self):
        if self.repo.stat().st_dev == Path("/Volumes/FlashDrive").stat().st_dev:
            self.skipTest("fixture already on external filesystem")
        self.external = tempfile.TemporaryDirectory(prefix="cow-worktree-test-", dir="/Volumes/FlashDrive")
        result = helper.create_worktree(self.repo, Path(self.external.name) / "feature", "codex/external", self.base)
        self.assert_checkout(result)
        self.assertEqual(result["mode"], "git")

    def test_case_collision_is_rejected_before_creating_worktree(self):
        case_probe = self.root / "case-probe"
        case_probe.touch()
        if not (self.root / "CASE-PROBE").exists():
            self.skipTest("filesystem is case-sensitive")
        git(self.repo, "config", "core.ignorecase", "false")
        for name, data in [("Case.txt", b"upper\n"), ("case.txt", b"lower\n")]:
            oid = git(self.repo, "hash-object", "-w", "--stdin", input=data).strip().decode()
            git(self.repo, "update-index", "--add", "--cacheinfo", "100644," + oid + "," + name)
        git(self.repo, "commit", "--quiet", "-m", "case collision")
        base = git(self.repo, "rev-parse", "HEAD").decode().strip()
        refs = git(self.repo, "show-ref")
        with self.assertRaises(helper.SetupError):
            self.create("collision", base=base)
        self.assertFalse((self.root / "collision").exists())
        self.assertEqual(git(self.repo, "show-ref"), refs)

    def test_invalid_base_does_not_create_path_or_branch(self):
        before = git(self.repo, "show-ref")
        with self.assertRaises(helper.SetupError):
            self.create(base="missing-revision")
        self.assertFalse((self.root / "feature").exists())
        self.assertEqual(git(self.repo, "show-ref"), before)

    def test_unqualified_platform_uses_ordinary_git(self):
        with patch.object(helper.sys, "platform", "unqualified-platform"):
            result = self.create()
        self.assert_checkout(result)
        self.assertEqual(result["mode"], "git")

    def test_git_repository_environment_overrides_are_ignored(self):
        with patch.dict(os.environ, {"GIT_DIR": "/nonexistent/git-dir", "GIT_INDEX_FILE": "/nonexistent/index"}):
            result = self.create()
        self.assert_checkout(result)
        self.assertFalse(Path("/nonexistent/index").exists())

    @unittest.skipUnless(sys.platform == "darwin", "requires native clone path")
    def test_changed_worktree_head_is_retained_without_overwriting(self):
        original = helper.copy_tracked
        def change_head(seed, target, files):
            result = original(seed, target, files)
            (target / "readme.txt").write_text("new owner work\n")
            git(target, "commit", "--quiet", "-am", "new owner commit")
            return result
        with patch.object(helper, "copy_tracked", side_effect=change_head):
            with self.assertRaises(helper.OwnershipError):
                self.create()
        target = self.root / "feature"
        self.assertEqual((target / "readme.txt").read_text(), "new owner work\n")
        self.assertNotEqual(git(target, "rev-parse", "HEAD").decode().strip(), self.base)

    @unittest.skipUnless(sys.platform == "darwin", "requires native clone path")
    def test_replaced_destination_is_not_written_by_fallback(self):
        original = helper.copy_tracked
        def replace_destination(seed, target, files):
            result = original(seed, target, files)
            target.rename(target.with_name("owned-old"))
            target.mkdir()
            (target / "unique.txt").write_text("keep replacement\n")
            return result
        with patch.object(helper, "copy_tracked", side_effect=replace_destination):
            with self.assertRaises(helper.OwnershipError):
                self.create()
        target = self.root / "feature"
        self.assertEqual((target / "unique.txt").read_text(), "keep replacement\n")
        self.assertEqual(list(target.iterdir()), [target / "unique.txt"])
        # Repair the synthetic registration so tearDown removes its original tree.
        shutil.rmtree(target)
        target.with_name("owned-old").rename(target)


if __name__ == "__main__":
    unittest.main(verbosity=2)
