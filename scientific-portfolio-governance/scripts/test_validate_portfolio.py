#!/usr/bin/env python3
"""Regression tests for scientific portfolio schema v2."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_portfolio.py"
REFERENCES = ROOT / "references"
EXAMPLE = REFERENCES / "example-portfolio.json"
STRICT = REFERENCES / "strict-portfolio.json"
MODULAR = REFERENCES / "modular-portfolio.json"


class PortfolioValidatorTests(unittest.TestCase):
    def run_validator(self, board: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(board), *extra],
            check=False,
            text=True,
            capture_output=True,
        )

    def mutated_board(self, mutate: Callable[[dict[str, Any]], None]) -> Path:
        data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        mutate(data)
        temp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False)
        with temp:
            json.dump(data, temp, indent=2)
            temp.write("\n")
        path = Path(temp.name)
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def assert_rejected(self, board: Path, message: str, *extra: str) -> None:
        result = self.run_validator(board, *extra)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr + result.stdout)

    def test_inline_strict_and_modular_fixtures_pass(self) -> None:
        for board in (EXAMPLE, STRICT, MODULAR):
            with self.subTest(board=board.name):
                result = self.run_validator(board)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('"status": "PASS"', result.stdout)

    def test_theorem_formalization_cannot_use_maintenance_pool(self) -> None:
        board = self.mutated_board(lambda d: d["workstreams"][1].update(**{"class": "maintenance", "slot_group": "maintenance"}))
        self.assert_rejected(board, "maintenance may not mutate governed authority")

    def test_qualification_cannot_mutate_source(self) -> None:
        board = self.mutated_board(lambda d: d["workstreams"][2].update(governed_authority_bytes_mutable=True))
        self.assert_rejected(board, "qualification may not mutate governed authority")

    def test_qualification_input_must_be_immutable(self) -> None:
        board = self.mutated_board(lambda d: d["workstreams"][2]["frozen_inputs"][0].update(mutable=True))
        self.assert_rejected(board, "must be immutable")

    def test_maintenance_cannot_enable_theorem_writes(self) -> None:
        board = self.mutated_board(lambda d: d["workstreams"][3].update(theorem_writes_allowed=True))
        self.assert_rejected(board, "maintenance may not mutate governed authority")

    def test_authority_surface_has_one_writer(self) -> None:
        board = self.mutated_board(lambda d: d["workstreams"][1].update(authority_surface=d["workstreams"][0]["authority_surface"]))
        self.assert_rejected(board, "has multiple active writers")

    def test_qualified_surface_has_one_qualifier(self) -> None:
        def add_duplicate(data: dict[str, Any]) -> None:
            other = json.loads(json.dumps(data["workstreams"][2]))
            other["id"] = "duplicate-qualifier"
            other["owner"] = "issue-50"
            other["issues"] = [50]
            other["concurrency_key"] = "qualification:duplicate"
            other["owned_paths"] = ["qualification/duplicate/"]
            data["workstreams"].append(other)

        board = self.mutated_board(add_duplicate)
        self.assert_rejected(board, "has multiple active qualifiers")

    def test_issue_cannot_have_two_owners(self) -> None:
        board = self.mutated_board(lambda d: d["nonactive_workstreams"][0].update(issues=[1]))
        self.assert_rejected(board, "issue 1 is owned by both")

    def test_board_cannot_raise_default_authority_limit(self) -> None:
        board = self.mutated_board(lambda d: d["limits"].update(active_authority_writing_workstreams=4))
        self.assert_rejected(board, "board limit exceeds default maximum")

    def test_cli_maximum_cannot_weaken_default(self) -> None:
        self.assert_rejected(EXAMPLE, "command-line maximum may only narrow default", "--max-authority", "4")

    def test_legacy_schema_is_rejected(self) -> None:
        board = self.mutated_board(lambda d: d.update(schema_version=1))
        self.assert_rejected(board, "schema_version must be 2")


if __name__ == "__main__":
    unittest.main()
