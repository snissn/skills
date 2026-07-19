#!/usr/bin/env python3
"""Create a deterministic exact-byte manifest for scientific review."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import subprocess
import sys
from pathlib import Path


def git(repo: Path, *args: str, check: bool = True) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    if check:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {message}")
    return None


def git_blob(repo: Path, revision: str, path: str) -> str | None:
    return git(repo, "rev-parse", "--verify", f"{revision}:{path}", check=False)


def resolve_candidate(repo: Path, raw_path: str) -> tuple[str, Path]:
    supplied = Path(raw_path)
    absolute = supplied if supplied.is_absolute() else repo / supplied
    if absolute.is_symlink():
        raise ValueError(f"refusing symlink candidate: {raw_path}")
    resolved = absolute.resolve(strict=True)
    try:
        relative = resolved.relative_to(repo)
    except ValueError as exc:
        raise ValueError(f"candidate is outside repository: {raw_path}") from exc
    if not resolved.is_file():
        raise ValueError(f"candidate is not a regular file: {raw_path}")
    return relative.as_posix(), resolved


def build_manifest(repo_arg: str, base_arg: str, paths: list[str]) -> dict:
    requested_repo = Path(repo_arg).expanduser().resolve(strict=True)
    root = Path(git(requested_repo, "rev-parse", "--show-toplevel")).resolve()
    head = git(root, "rev-parse", "HEAD")
    base = git(root, "rev-parse", "--verify", f"{base_arg}^{{commit}}")

    resolved_paths: dict[str, Path] = {}
    for raw_path in paths:
        relative, absolute = resolve_candidate(root, raw_path)
        if relative in resolved_paths:
            raise ValueError(f"duplicate candidate path: {relative}")
        resolved_paths[relative] = absolute

    entries = []
    for relative in sorted(resolved_paths):
        absolute = resolved_paths[relative]
        data = absolute.read_bytes()
        mode = stat.S_IMODE(absolute.stat().st_mode)
        entries.append(
            {
                "path": relative,
                "bytes": len(data),
                "mode": f"{mode:04o}",
                "sha256": hashlib.sha256(data).hexdigest(),
                "base_blob": git_blob(root, base, relative),
                "head_blob": git_blob(root, head, relative),
            }
        )

    payload = {
        "schema": "scientific-candidate-manifest/v1",
        "base_sha": base,
        "head_sha": head,
        "files": entries,
    }
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return {
        **payload,
        "manifest_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bind a scientific candidate to its base, path set, and bytes."
    )
    parser.add_argument("--repo", default=".", help="Repository worktree path.")
    parser.add_argument(
        "--base",
        default="HEAD",
        help="Candidate base revision, resolved to a commit SHA.",
    )
    parser.add_argument(
        "--path",
        action="append",
        required=True,
        dest="paths",
        help="Candidate file path; repeat for every reviewed artifact.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = build_manifest(args.repo, args.base, args.paths)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"candidate_manifest: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
