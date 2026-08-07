#!/usr/bin/env python3
"""Regression tests for scientific portfolio schema v2."""

from __future__ import annotations

import copy
import json
import shutil
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
MODULAR_ACTIVE = REFERENCES / "modular-portfolio.active.json"
MODULAR_NONACTIVE = REFERENCES / "modular-portfolio.nonactive.json"


class PortfolioValidatorTests(unittest.TestCase):
    """Exercise positive fixtures and fail-closed governance mutations."""

    def run_validator(
        self,
        board: Path,
        *extra: str,
    ) -> subprocess.CompletedProcess[str]:
        """Run the validator against one board."""
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(board), *extra],
            check=False,
            text=True,
            capture_output=True,
        )

    def mutated_board(
        self,
        mutate: Callable[[dict[str, Any]], None],
    ) -> Path:
        """Write one temporary mutation of the inline reference board."""
        data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        mutate(data)
        temp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            encoding="utf-8",
            delete=False,
        )
        with temp:
            json.dump(data, temp, indent=2)
            temp.write("\n")
        path = Path(temp.name)
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def assert_rejected(
        self,
        board: Path,
        message: str,
        *extra: str,
    ) -> None:
        """Assert that a board fails with a particular diagnostic."""
        result = self.run_validator(board, *extra)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr + result.stdout)

    def test_inline_strict_and_modular_fixtures_pass(self) -> None:
        """All maintained positive fixtures validate."""
        for board in (EXAMPLE, STRICT, MODULAR):
            with self.subTest(board=board.name):
                result = self.run_validator(board)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('"status": "PASS"', result.stdout)

    def test_repository_prefixed_modular_rosters_resolve(self) -> None:
        """A nested root board may use repository-prefixed roster paths."""
        with tempfile.TemporaryDirectory() as temp_name:
            repo = Path(temp_name) / "repo"
            nested = repo / "scientific-portfolio-governance" / "references"
            nested.mkdir(parents=True)
            root_data = json.loads(MODULAR.read_text(encoding="utf-8"))
            root_data["workstream_files"] = {
                "active": (
                    "scientific-portfolio-governance/references/"
                    "modular-portfolio.active.json"
                ),
                "nonactive": (
                    "scientific-portfolio-governance/references/"
                    "modular-portfolio.nonactive.json"
                ),
            }
            root_path = nested / "portfolio.json"
            root_path.write_text(
                json.dumps(root_data, indent=2) + "\n",
                encoding="utf-8",
            )
            shutil.copyfile(
                MODULAR_ACTIVE,
                nested / MODULAR_ACTIVE.name,
            )
            shutil.copyfile(
                MODULAR_NONACTIVE,
                nested / MODULAR_NONACTIVE.name,
            )
            result = self.run_validator(root_path)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_formalization_cannot_use_maintenance_pool(self) -> None:
        """Formalization remains formalization but cannot occupy maintenance."""
        board = self.mutated_board(
            lambda data: data["workstreams"][1].update(
                slot_group="maintenance",
            )
        )
        self.assert_rejected(board, "class/slot-group mismatch")

    def test_qualification_scientific_writes_are_rejected(self) -> None:
        """Qualification cannot enable scientific writes."""
        board = self.mutated_board(
            lambda data: data["workstreams"][2].update(
                scientific_writes_allowed=True,
            )
        )
        self.assert_rejected(
            board,
            "qualification may not mutate governed authority",
        )

    def test_qualification_theorem_writes_are_rejected(self) -> None:
        """Qualification cannot enable theorem writes."""
        board = self.mutated_board(
            lambda data: data["workstreams"][2].update(
                theorem_writes_allowed=True,
            )
        )
        self.assert_rejected(
            board,
            "qualification may not mutate governed authority",
        )

    def test_qualification_authority_mutation_is_rejected(self) -> None:
        """Qualification cannot mutate frozen governed bytes."""
        board = self.mutated_board(
            lambda data: data["workstreams"][2].update(
                governed_authority_bytes_mutable=True,
            )
        )
        self.assert_rejected(
            board,
            "qualification may not mutate governed authority",
        )

    def test_qualification_input_must_be_immutable(self) -> None:
        """Every frozen qualification input is immutable."""
        board = self.mutated_board(
            lambda data: data["workstreams"][2]["frozen_inputs"][0].update(
                mutable=True,
            )
        )
        self.assert_rejected(board, "must be immutable")

    def test_qualified_surfaces_bind_inputs_one_to_one(self) -> None:
        """Labels and canonical frozen identities have one-to-one cardinality."""
        board = self.mutated_board(
            lambda data: data["workstreams"][2]["qualified_surfaces"].append(
                "unbound-label"
            )
        )
        self.assert_rejected(
            board,
            "qualified surfaces must bind frozen inputs one-to-one",
        )

    def test_maintenance_scientific_writes_are_rejected(self) -> None:
        """Maintenance cannot enable scientific writes."""
        board = self.mutated_board(
            lambda data: data["workstreams"][3].update(
                scientific_writes_allowed=True,
            )
        )
        self.assert_rejected(
            board,
            "maintenance may not mutate governed authority",
        )

    def test_maintenance_theorem_writes_are_rejected(self) -> None:
        """Maintenance cannot enable theorem writes."""
        board = self.mutated_board(
            lambda data: data["workstreams"][3].update(
                theorem_writes_allowed=True,
            )
        )
        self.assert_rejected(
            board,
            "maintenance may not mutate governed authority",
        )

    def test_authority_surface_has_one_writer(self) -> None:
        """Two authority lanes cannot share an authority surface."""
        board = self.mutated_board(
            lambda data: data["workstreams"][1].update(
                authority_surface=data["workstreams"][0][
                    "authority_surface"
                ],
            )
        )
        self.assert_rejected(board, "has multiple active writers")

    def test_qualified_surface_has_one_qualifier(self) -> None:
        """Two qualification lanes cannot share a surface label."""
        def add_duplicate(data: dict[str, Any]) -> None:
            other = copy.deepcopy(data["workstreams"][2])
            other["id"] = "duplicate-qualifier"
            other["owner"] = "issue-50"
            other["issues"] = [50]
            other["concurrency_key"] = "qualification:duplicate"
            other["owned_paths"] = ["qualification/duplicate/"]
            data["workstreams"].append(other)

        board = self.mutated_board(add_duplicate)
        self.assert_rejected(board, "has multiple active qualifiers")

    def test_frozen_input_has_one_qualifier_even_with_new_label(self) -> None:
        """Changing a label cannot hide duplicate qualification of one input."""
        def add_duplicate(data: dict[str, Any]) -> None:
            other = copy.deepcopy(data["workstreams"][2])
            other["id"] = "duplicate-frozen-input"
            other["owner"] = "issue-51"
            other["issues"] = [51]
            other["concurrency_key"] = "qualification:duplicate-input"
            other["owned_paths"] = ["qualification/duplicate-input/"]
            other["qualified_surfaces"] = ["different-label"]
            data["workstreams"].append(other)

        board = self.mutated_board(add_duplicate)
        self.assert_rejected(board, "is qualified by both")

    def test_nested_owned_paths_are_rejected(self) -> None:
        """Ancestor and descendant paths are not path-disjoint."""
        board = self.mutated_board(
            lambda data: data["workstreams"][1].update(
                owned_paths=[
                    data["workstreams"][0]["owned_paths"][0] + "nested/"
                ],
            )
        )
        self.assert_rejected(board, "owned paths overlap")

    def test_issue_cannot_have_two_owners(self) -> None:
        """Issue ownership is globally unique."""
        board = self.mutated_board(
            lambda data: data["nonactive_workstreams"][0].update(
                issues=[1],
            )
        )
        self.assert_rejected(board, "issue 1 is owned by both")

    def test_board_cannot_raise_default_authority_limit(self) -> None:
        """A board may narrow but not exceed the reusable default limit."""
        board = self.mutated_board(
            lambda data: data["limits"].update(
                active_authority_writing_workstreams=4,
            )
        )
        self.assert_rejected(board, "board limit exceeds default maximum")

    def test_cli_maximum_cannot_weaken_default(self) -> None:
        """CLI overrides may only narrow reusable defaults."""
        self.assert_rejected(
            EXAMPLE,
            "command-line maximum may only narrow default",
            "--max-authority",
            "4",
        )

    def test_every_nonactive_status_is_required(self) -> None:
        """Boards retain blocked, parked, deferred, superseded, and completed."""
        board = self.mutated_board(
            lambda data: data["allowed_statuses"].remove("PARKED")
        )
        self.assert_rejected(
            board,
            "allowed status set must retain every nonactive state",
        )

    def test_legacy_schema_is_rejected(self) -> None:
        """Schema v1 cannot silently pass through the v2 validator."""
        board = self.mutated_board(
            lambda data: data.update(schema_version=1)
        )
        self.assert_rejected(board, "schema_version must be 2")


if __name__ == "__main__":
    unittest.main()
