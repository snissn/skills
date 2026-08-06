#!/usr/bin/env python3
"""Regression tests for the scientific portfolio validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_portfolio.py"
EXAMPLE = ROOT / "references" / "example-portfolio.json"
STRICT = ROOT / "references" / "strict-portfolio.json"


class PortfolioValidatorTests(unittest.TestCase):
    def run_validator(
        self,
        board: Path,
        *extra: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(board), *extra],
            check=False,
            text=True,
            capture_output=True,
        )

    def mutated_board(self, mutate: Any) -> Path:
        data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        mutate(data)
        temp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            encoding="utf-8",
            delete=False,
        )
        with temp:
            json.dump(data, temp, indent=2, sort_keys=True)
            temp.write("\n")
        self.addCleanup(Path(temp.name).unlink, missing_ok=True)
        return Path(temp.name)

    def assert_rejected(self, board: Path, message: str, *extra: str) -> None:
        result = self.run_validator(board, *extra)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr + result.stdout)

    def test_default_and_strict_fixtures_pass(self) -> None:
        for board in (EXAMPLE, STRICT):
            with self.subTest(board=board.name):
                result = self.run_validator(board)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('"status": "PASS"', result.stdout)

    def test_board_cannot_raise_default_science_limit(self) -> None:
        board = self.mutated_board(
            lambda data: data["limits"].__setitem__(
                "active_scientific_workstreams",
                4,
            )
        )
        self.assert_rejected(
            board,
            "board science limit exceeds the default maximum",
        )

    def test_cli_maximum_cannot_weaken_default(self) -> None:
        self.assert_rejected(
            EXAMPLE,
            "command-line science maximum may only narrow the default",
            "--max-science",
            "4",
        )

    def test_allowed_active_status_cannot_be_made_nonoccupying(self) -> None:
        board = self.mutated_board(
            lambda data: data.__setitem__("occupying_statuses", ["ACTIVE"])
        )
        self.assert_rejected(
            board,
            "occupying statuses must preserve the default semantics",
        )

    def test_issue_cannot_have_two_workstream_owners(self) -> None:
        def duplicate_issue(data: dict[str, Any]) -> None:
            data["nonactive_workstreams"][0]["issues"] = data["workstreams"][0][
                "issues"
            ]

        board = self.mutated_board(duplicate_issue)
        self.assert_rejected(board, "issue 1 is owned by both")


if __name__ == "__main__":
    unittest.main()
