#!/usr/bin/env python3
"""Focused tests for constructor-handoff graph-state invariants."""

from __future__ import annotations

import copy
import unittest

from validate_graph_state import validate


FULL_A = "a" * 40
FULL_B = "b" * 40
FULL_C = "c" * 40


def valid_handoff() -> dict[str, object]:
    return {
        "schema": "gpt56-pro-issue-graph-executor/v1",
        "repo": "owner/repo",
        "parent_issue": 1,
        "mode": "constructor-handoff",
        "base_branch": "main",
        "base_sha": FULL_A,
        "updated_at": "2026-08-05T00:00:00Z",
        "limits": {"max_active_lanes": 1, "max_heavy_processes": 1},
        "dispatchable_now": [],
        "review_or_ci_pending": [],
        "fix_needed": [],
        "blocked": [],
        "nodes": {
            "2": {
                "title": "Scientific constructor",
                "state": "integration-ready",
                "active_lane": False,
                "predecessors": [],
                "successors": [],
                "branch": "work/issue-2",
                "pr": 3,
                "base_sha": FULL_A,
                "head_sha": FULL_B,
                "merge_sha": None,
            }
        },
    }


class ConstructorHandoffTests(unittest.TestCase):
    def test_exact_unmerged_handoff_passes(self) -> None:
        self.assertEqual(validate(valid_handoff()).errors, [])

    def test_short_top_level_base_fails(self) -> None:
        data = valid_handoff()
        data["base_sha"] = "a" * 12
        self.assertTrue(any("exact" in error for error in validate(data).errors))

    def test_missing_node_base_fails(self) -> None:
        data = valid_handoff()
        del data["nodes"]["2"]["base_sha"]
        self.assertTrue(any("missing valid base_sha" in error for error in validate(data).errors))

    def test_merge_sha_fails_before_integrator_merge(self) -> None:
        data = copy.deepcopy(valid_handoff())
        data["nodes"]["2"]["merge_sha"] = FULL_C
        self.assertTrue(any("null merge_sha" in error for error in validate(data).errors))


if __name__ == "__main__":
    unittest.main()
