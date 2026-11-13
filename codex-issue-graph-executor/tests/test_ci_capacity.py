"""Offline tests for the read-only CI timing inventory."""

import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("ci_capacity", Path(__file__).parents[1] / "scripts/ci_capacity.py")
capacity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capacity)
NOW = "2026-10-29T01:00:00Z"


class CapacityTests(unittest.TestCase):
    def test_distinguishes_job_creation_wait_execution_and_step_duration(self):
        job = {"id": 1, "labels": ["macos-latest"], "status": "completed", "runner_name": "hosted",
               "created_at": "2026-10-29T00:10:00Z", "started_at": "2026-10-29T00:40:00Z",
               "completed_at": "2026-10-29T00:55:00Z", "steps": [
                   {"name": "Vet", "started_at": "2026-10-29T00:41:00Z", "completed_at": "2026-10-29T00:53:00Z"}]}
        record = capacity.job_record(job, NOW, True)
        self.assertEqual(record["creation_to_start_seconds"], 1800)
        self.assertEqual(record["execution_seconds"], 900)
        self.assertEqual(record["steps"][0]["elapsed_seconds"], 720)
        self.assertIsNone(record["age_since_creation_seconds"])

    def test_queued_and_cancelled_without_runner_do_not_claim_execution(self):
        job = {"status": "queued", "runner_name": None, "created_at": "2026-10-29T00:30:00Z",
               "started_at": "2026-10-29T00:30:00Z", "completed_at": None}
        record = capacity.job_record(job, NOW, False)
        self.assertEqual(record["age_since_creation_seconds"], 1800)
        self.assertIsNone(record["started_at"])
        self.assertIsNone(record["creation_to_start_seconds"])
        self.assertIsNone(record["execution_seconds"])
        job["runner_name"] = "assigned but not started"
        record = capacity.job_record(job, NOW, False)
        self.assertEqual(record["age_since_creation_seconds"], 1800)
        self.assertIsNone(record["creation_to_start_seconds"])
        job["runner_name"] = None
        job.update(status="completed", conclusion="cancelled", completed_at=NOW)
        record = capacity.job_record(job, NOW, False)
        self.assertIsNone(record["age_since_creation_seconds"])
        self.assertIsNone(record["execution_seconds"])

    def test_paginated_attempt_filters_labels_and_counts_unknown(self):
        run = {"id": 10, "run_attempt": 2, "head_sha": "a" * 40}
        pages = [{"jobs": [{"id": 1, "labels": ["macOS-latest"]}, {"id": 2, "labels": []}]},
                 {"jobs": [{"id": 3, "labels": ["ubuntu-latest"]}]}]
        with patch.object(capacity, "gh_json", side_effect=[run, pages, copy.deepcopy(run)]) as api:
            result = capacity.inventory_run("owner/repo", 10, "macos", NOW, False)
        self.assertEqual(result["attempt"], 2)
        self.assertEqual(result["jobs_total"], 3)
        self.assertEqual(result["jobs_with_unknown_labels"], 1)
        self.assertEqual([j["id"] for j in result["jobs"]], [1])
        self.assertIn("/attempts/2/jobs?", api.call_args_list[1].args[0])
        self.assertEqual(api.call_args_list[1].args[1:], ("--paginate", "--slurp"))

    def test_changed_attempt_and_missing_pages_fail_closed(self):
        run = {"id": 10, "run_attempt": 1, "head_sha": "a" * 40}
        changed = {**run, "run_attempt": 2}
        with patch.object(capacity, "gh_json", side_effect=[run, [{"jobs": []}], changed]):
            with self.assertRaises(capacity.InventoryError):
                capacity.inventory_run("owner/repo", 10, "macos", NOW, False)
        with patch.object(capacity, "gh_json", side_effect=[run, []]):
            with self.assertRaises(capacity.InventoryError):
                capacity.inventory_run("owner/repo", 10, "macos", NOW, False)

    def test_bad_or_reversed_timestamps_do_not_invent_durations(self):
        self.assertIsNone(capacity.seconds_between("invalid", NOW))
        self.assertIsNone(capacity.seconds_between(NOW, "2026-10-29T00:59:00Z"))
        self.assertIsNone(capacity.seconds_between("2026-10-29T00:00:00", NOW))


if __name__ == "__main__":
    unittest.main()
