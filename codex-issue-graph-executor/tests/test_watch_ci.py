"""Offline watcher behavior tests; no GitHub mutations or network calls."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("watch_ci", Path(__file__).parents[1] / "scripts/watch_ci.py")
w = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(w)
HEAD, BASE = "a" * 40, "b" * 40


def args(*extra):
    return w.parse_args(["--repo", "owner/repo", "--pr", "1", "--head", HEAD, "--base", BASE, *extra])


def check(name="build", status="IN_PROGRESS", conclusion=None, required=True):
    return {"__typename": "CheckRun", "name": name, "databaseId": 1, "status": status,
            "conclusion": conclusion, "isRequired": required,
            "startedAt": "2026-10-28T20:00:00Z",
            "completedAt": "2026-10-28T20:01:00Z" if status == "COMPLETED" else None,
            "checkSuite": {"workflowRun": None}}


def snapshot(*checks):
    return {"pr": {"headRefOid": HEAD, "baseRefOid": BASE, "baseBranchOid": BASE, "baseRefName": "main",
                   "state": "OPEN", "isDraft": False, "mergeable": "MERGEABLE",
                   "reviewDecision": "REVIEW_REQUIRED"}, "checks": list(checks), "runs": []}


def run(status="in_progress", conclusion=None, attempt=1, jobs=None):
    return {"id": 10, "head_sha": HEAD, "run_attempt": attempt, "status": status,
            "conclusion": conclusion, "workflow_id": 20, "jobs": jobs or []}


def response(pr, checks, more=False, cursor=None):
    pr = copy.deepcopy(pr)
    pr["commits"] = {"nodes": [{"commit": {"oid": HEAD, "statusCheckRollup": {
        "contexts": {"nodes": checks, "pageInfo": {"hasNextPage": more, "endCursor": cursor}}}}}]}
    return {"data": {"repository": {"pullRequest": pr}}}


def base_response(oid=BASE):
    return {"data": {"repository": {"ref": {"target": {"oid": oid}}}}}


def job(job_id=99, conclusion="success", run_id=10, attempt=1):
    return {"id": job_id, "name": f"job-{job_id}", "run_id": run_id, "run_attempt": attempt,
            "status": "completed", "conclusion": conclusion,
            "started_at": "2026-10-28T20:00:00Z", "completed_at": "2026-10-28T20:01:00Z",
            "html_url": f"https://github.com/owner/repo/actions/runs/{run_id}/job/{job_id}"}


class JobNotificationTests(unittest.TestCase):
    def watch(self, selected, states):
        output = io.StringIO()
        with patch.object(w, "read_snapshot", side_effect=states) as read, \
             patch.object(w.time, "sleep"), contextlib.redirect_stdout(output):
            code = w.watch(selected)
        return code, [json.loads(line) for line in output.getvalue().splitlines()], read.call_count

    def states(self, jobs=None, completed=False):
        state = snapshot(check(status="COMPLETED", conclusion="SUCCESS") if completed else check())
        state["runs"] = [run("completed" if completed else "in_progress",
                             "success" if completed else None, jobs=jobs)]
        return state

    def test_completion_once_while_workflow_continues_to_confirmed_success(self):
        selected = args("--run-id", "10", "--run-attempt", "10:1", "--notify-job-id", "10:99")
        pending = self.states()
        progress = self.states([job()])
        green = self.states([job()], completed=True)
        code, events, reads = self.watch(selected, [pending, progress, progress, green, green])
        self.assertEqual(code, 0)
        self.assertEqual(reads, 5)
        self.assertEqual([e["event"] for e in events], ["watching", "job_completed", "ci_success"])
        notification = events[1]
        self.assertEqual((notification["run_id"], notification["attempt"], notification["workflow_id"],
                          notification["job_id"], notification["conclusion"]), (10, 1, 20, 99, "success"))
        self.assertEqual((notification["head"], notification["base"]), (HEAD, BASE))
        self.assertFalse(notification["terminal"])
        self.assertFalse(notification["merge_authorized"])

    def test_repeatable_selection_is_exact_across_runs_and_jobs(self):
        selected = args("--run-id", "10", "--run-id", "11", "--notify-job-id", "10:99",
                        "--notify-job-id", "10:100", "--notify-job-id", "11:199")
        pending = self.states([job(), job(100), job(101)])
        other = run(jobs=[job(199, run_id=11)])
        other["id"] = 11
        pending["runs"].append(other)
        green = copy.deepcopy(pending)
        green["checks"] = [check(status="COMPLETED", conclusion="SUCCESS")]
        for item in green["runs"]:
            item.update(status="completed", conclusion="success")
        code, events, _ = self.watch(selected, [pending, pending, green, green])
        self.assertEqual(code, 0)
        self.assertEqual([(e["run_id"], e["job_id"]) for e in events if e["event"] == "job_completed"],
                         [(10, 99), (10, 100), (11, 199)])

    def test_early_success_does_not_hide_later_sibling_failure(self):
        selected = args("--run-id", "10", "--notify-job-id", "10:99")
        progress = self.states([job()])
        failed = self.states([job(), job(100, "failure")])
        code, events, reads = self.watch(selected, [progress, failed])
        self.assertEqual(code, 1)
        self.assertEqual(reads, 2)
        self.assertEqual([e["event"] for e in events], ["watching", "job_completed", "failure"])
        self.assertEqual(events[-1]["job_id"], 100)
        self.assertEqual(events[-1]["observed_failures"][0]["job_id"], 100)

    def test_terminal_failures_take_priority_over_same_snapshot_progress(self):
        selected = args("--run-id", "10", "--notify-job-id", "10:99")
        for kind in ["selected", "sibling", "required_check", "advisory_check"]:
            with self.subTest(kind=kind):
                state = self.states([job()])
                if kind == "selected":
                    state["runs"][0]["jobs"][0]["conclusion"] = "failure"
                elif kind == "sibling":
                    state["runs"][0]["jobs"].append(job(100, "failure"))
                else:
                    state["checks"].append(check("broken", "COMPLETED", "FAILURE", kind == "required_check"))
                code, events, _ = self.watch(selected, [state])
                self.assertIn(code, [1, 4])
                self.assertEqual(len(events), 2)
                self.assertIn(events[-1]["event"], ["failure", "advisory_failure"])

    def test_identity_changes_suppress_completion_and_end_watch(self):
        selected = args("--run-id", "10", "--notify-job-id", "10:99")
        pending = self.states()
        for field in ["head_sha", "run_attempt", "workflow_id", "baseBranchOid"]:
            with self.subTest(field=field):
                changed = self.states([job()])
                if field == "baseBranchOid":
                    changed["pr"][field] = "c" * 40
                else:
                    changed["runs"][0][field] = "c" * 40 if field == "head_sha" else 2
                code, events, _ = self.watch(selected, [pending, changed])
                self.assertEqual(code, 3)
                self.assertEqual([e["event"] for e in events], ["watching", "superseded"])

    def test_explicit_attempt_mismatch_never_notifies(self):
        state = self.states([job()])
        selected = args("--run-id", "10", "--run-attempt", "10:2", "--notify-job-id", "10:99")
        code, events, _ = self.watch(selected, [state])
        self.assertEqual(code, 3)
        self.assertEqual(events[-1]["event"], "superseded")

    def test_success_confirmation_has_priority_over_progress(self):
        selected = args("--run-id", "10", "--notify-job-id", "10:99")
        green = self.states([job()], completed=True)
        changed = copy.deepcopy(green)
        changed["pr"]["headRefOid"] = "c" * 40
        code, events, _ = self.watch(selected, [green, changed])
        self.assertEqual(code, 3)
        self.assertEqual([e["event"] for e in events], ["watching", "superseded"])

    def test_default_remains_quiet_with_completed_constituent_job(self):
        green = self.states([job()], completed=True)
        code, events, _ = self.watch(args("--run-id", "10"), [self.states([job()]), green, green])
        self.assertEqual(code, 0)
        self.assertEqual([e["event"] for e in events], ["watching", "ci_success"])
        self.assertNotIn("requested_job_notifications", events[0])

    def test_unselected_job_and_missing_target_do_not_invent_a_gate(self):
        green = self.states([job(100)], completed=True)
        green["runs"][0]["jobs"][0]["name"] = "job-99"  # Same name cannot substitute for exact ID.
        selected = args("--run-id", "10", "--notify-job-id", "10:99")
        code, events, _ = self.watch(selected, [green, green])
        self.assertEqual(code, 0)
        self.assertEqual([e["event"] for e in events], ["watching", "ci_success"])

    def test_incomplete_or_wrong_job_identity_fails_closed(self):
        selected = args("--run-id", "10", "--notify-job-id", "10:99")
        for field, value in [("run_id", 11), ("run_attempt", 2), ("completed_at", None), ("conclusion", None)]:
            with self.subTest(field=field):
                state = self.states([job()])
                state["runs"][0]["jobs"][0][field] = value
                code, events, _ = self.watch(selected, [state])
                self.assertEqual(code, 2)
                self.assertEqual([e["event"] for e in events], ["watching", "error"])

    def test_pending_job_then_duplicate_identity_are_not_notified(self):
        selected = args("--run-id", "10", "--notify-job-id", "10:99")
        pending = self.states([job()])
        pending["runs"][0]["jobs"][0].update(status="in_progress", conclusion=None, completed_at=None)
        duplicate = self.states([job(), job()])
        code, events, _ = self.watch(selected, [pending, duplicate])
        self.assertEqual(code, 2)
        self.assertEqual([e["event"] for e in events], ["watching", "error"])

    def test_neutral_completion_is_a_diagnostic_not_ci_acceptance(self):
        selected = args("--run-id", "10", "--notify-job-id", "10:99")
        state = self.states([job(conclusion="neutral")])
        code, events, _ = self.watch(selected, [state, w.WatchError("offline stop")])
        self.assertEqual(code, 2)
        self.assertEqual([e["event"] for e in events], ["watching", "job_completed", "error"])
        self.assertEqual(events[1]["conclusion"], "neutral")

    def test_selection_arguments_require_unique_positive_job_and_selected_run(self):
        for extra in [("--notify-job-id", "10:99"),
                      ("--run-id", "10", "--notify-job-id", "11:99"),
                      ("--run-id", "10", "--notify-job-id", "10:0"),
                      ("--run-id", "10", "--notify-job-id", "99"),
                      ("--run-id", "10", "--notify-job-id", "10:99", "--notify-job-id", "10:99")]:
            with self.subTest(extra=extra), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    args(*extra)


class WatchTests(unittest.TestCase):
    def test_pending_and_missing_checks_do_not_pass(self):
        self.assertIsNone(w.evaluate(args(), snapshot()))
        self.assertIsNone(w.evaluate(args(), snapshot(check())))
        self.assertIsNone(w.evaluate(args("--require-check", "not-yet-created"),
                                     snapshot(check(status="COMPLETED", conclusion="SUCCESS"))))

    def test_success_is_ci_notification_only(self):
        event, code, details = w.evaluate(args(), snapshot(check(status="COMPLETED", conclusion="SUCCESS")))
        self.assertEqual((event, code), ("ci_success", 0))
        self.assertFalse(details["merge_authorized"])

    def test_required_failure_wakes_before_other_jobs_complete(self):
        result = w.evaluate(args(), snapshot(check("other"), check("failed", "COMPLETED", "FAILURE")))
        self.assertEqual(result[:2], ("failure", 1))
        self.assertTrue(result[2]["required"])

    def test_advisory_failure_is_distinct_and_required_failure_wins(self):
        advisory = check("advice", "COMPLETED", "FAILURE", False)
        self.assertEqual(w.evaluate(args(), snapshot(advisory))[:2], ("advisory_failure", 4))
        required = check("build", "COMPLETED", "FAILURE")
        self.assertEqual(w.evaluate(args(), snapshot(advisory, required))[2]["check"], "build")

    def test_explicit_check_binding_and_legacy_status(self):
        advisory = check("advice", "COMPLETED", "FAILURE", False)
        self.assertEqual(w.evaluate(args("--require-check", "advice"), snapshot(advisory))[:2], ("failure", 1))
        legacy = {"__typename": "StatusContext", "context": "legacy", "state": "ERROR", "isRequired": True}
        self.assertEqual(w.evaluate(args(), snapshot(legacy))[:2], ("failure", 1))

    def test_cancellation_and_inconclusive_do_not_pass(self):
        for conclusion, event in [("CANCELLED", "cancelled"), ("SKIPPED", "intervention"),
                                  ("NEUTRAL", "intervention"), ("ACTION_REQUIRED", "intervention")]:
            with self.subTest(conclusion=conclusion):
                self.assertEqual(w.evaluate(args(), snapshot(check(status="COMPLETED", conclusion=conclusion)))[0], event)

    def test_advisory_skipped_and_neutral_do_not_block_success(self):
        for conclusion in ["SKIPPED", "NEUTRAL"]:
            with self.subTest(conclusion=conclusion):
                result = w.evaluate(args(), snapshot(check(status="COMPLETED", conclusion="SUCCESS"),
                    check("advisory", "COMPLETED", conclusion, False)))
                self.assertEqual(result[:2], ("ci_success", 0))
                required = args("--require-check", "advisory")
                self.assertEqual(w.evaluate(required, snapshot(check("advisory", "COMPLETED", conclusion, False)))[:2],
                                 ("intervention", 4))

    def test_head_base_and_base_branch_supersession(self):
        original = snapshot(check())
        for key, value in [("headRefOid", "c" * 40), ("baseRefOid", "c" * 40), ("baseRefName", "release")]:
            changed = copy.deepcopy(original)
            changed["pr"][key] = value
            self.assertEqual(w.evaluate(args(), changed, original)[:2], ("superseded", 3))

    def test_review_conflict_draft_and_close_wake(self):
        original = snapshot(check())
        for key, value, event in [("reviewDecision", "APPROVED", "review_changed"),
                                  ("reviewDecision", "CHANGES_REQUESTED", "intervention"),
                                  ("mergeable", "CONFLICTING", "intervention"),
                                  ("isDraft", True, "intervention"), ("state", "MERGED", "pr_closed")]:
            changed = copy.deepcopy(original)
            changed["pr"][key] = value
            self.assertEqual(w.evaluate(args(), changed, original)[0], event)

    def test_job_failure_wakes_while_workflow_in_progress(self):
        selected = args("--run-id", "10")
        state = snapshot(check())
        state["runs"] = [run(jobs=[{"id": 99, "name": "unit", "status": "completed", "conclusion": "failure"}])]
        result = w.evaluate(selected, state)
        self.assertEqual(result[:2], ("failure", 1))
        self.assertEqual(result[2]["job_id"], 99)

    def test_selected_workflow_job_failure_is_actionable_when_only_aggregate_is_required(self):
        selected = args("--run-id", "10")
        state = snapshot(check("aggregate"), check("unit", "COMPLETED", "FAILURE", False))
        state["runs"] = [run(jobs=[{"id": 99, "name": "unit", "status": "completed", "conclusion": "failure"}])]
        result = w.evaluate(selected, state)
        self.assertEqual(result[:2], ("failure", 1))
        self.assertEqual(result[2]["scope"], "explicit_workflow")
        self.assertIs(result[2]["required"], False)

    def test_run_attempt_and_head_binding(self):
        selected = args("--run-id", "10", "--run-attempt", "10:1")
        original = snapshot(check())
        original["runs"] = [run()]
        changed = copy.deepcopy(original)
        changed["runs"][0]["run_attempt"] = 2
        self.assertEqual(w.evaluate(selected, changed, original)[:2], ("superseded", 3))
        self.assertEqual(w.evaluate(selected, changed)[:2], ("superseded", 3))
        changed["runs"][0]["head_sha"] = "c" * 40
        self.assertEqual(w.evaluate(selected, changed)[:2], ("superseded", 3))

    def test_workflow_job_pages_and_attempt_endpoint(self):
        selected = w.parse_args(["--repo", "owner/repo", "--head", HEAD, "--run-id", "10"])
        selected_run = run()
        with patch.object(w, "gh_json", side_effect=[selected_run, [
                {"jobs": [{"id": 1, "name": "pending", "status": "in_progress", "conclusion": None}]},
                {"jobs": [{"id": 2, "name": "failed", "status": "completed", "conclusion": "failure"}]}]]) as api:
            state = w.read_snapshot(selected, None)
        self.assertIn("/attempts/1/jobs?", api.call_args_list[1].args[0][0])
        self.assertEqual(w.evaluate(selected, state)[:2], ("failure", 1))

    def test_multiple_failures_preserved_in_notification(self):
        state = snapshot(check("one", "COMPLETED", "FAILURE"), check("two", "COMPLETED", "FAILURE", False))
        self.assertEqual([item["check"] for item in w.observed_failures(state)], ["one", "two"])

    def test_acknowledged_advisory_waits_for_pending_then_reports_success_with_failure_retained(self):
        selected = args("--acknowledge-advisory-check-id", "1")
        failed = check("advisory", "COMPLETED", "FAILURE", False)
        pending = snapshot(failed, dict(check(), databaseId=2))
        green = snapshot(failed, dict(check(status="COMPLETED", conclusion="SUCCESS"), databaseId=2))
        self.assertIsNone(w.evaluate(selected, pending))
        self.assertEqual(w.evaluate(args(), pending)[:2], ("advisory_failure", 4))
        output = io.StringIO()
        with patch.object(w, "read_snapshot", side_effect=[pending, green, green]), \
             patch.object(w.time, "sleep"), contextlib.redirect_stdout(output):
            self.assertEqual(w.watch(selected), 0)
        event = json.loads(output.getvalue().splitlines()[-1])
        self.assertEqual(event["acknowledged_advisory_check_ids"], [1])
        self.assertEqual(event["observed_failures"][0]["check_id"], 1)
        self.assertTrue(event["observed_failures"][0]["acknowledged_advisory"])
        self.assertEqual(event["observed_failures"][0]["state"], "FAILURE")

    def test_advisory_acknowledgement_never_suppresses_a_different_id_or_required_check(self):
        selected = args("--acknowledge-advisory-check-id", "1")
        failed = check("advisory", "COMPLETED", "FAILURE", False)
        for changed, expected in [(dict(failed, databaseId=2), ("advisory_failure", 4)),
                                  (dict(failed, isRequired=True), ("failure", 1)),
                                  (dict(failed, conclusion="CANCELLED"), ("cancelled", 5)),
                                  (dict(failed, conclusion="TIMED_OUT"), ("advisory_failure", 4)),
                                  (dict(failed, status="IN_PROGRESS", conclusion=None), ("intervention", 4)),
                                  (dict(failed, conclusion="UNKNOWN"), ("intervention", 4))]:
            with self.subTest(check=changed):
                self.assertEqual(w.evaluate(selected, snapshot(changed))[:2], expected)
        explicitly_required = args("--acknowledge-advisory-check-id", "1", "--require-check", "advisory")
        self.assertEqual(w.evaluate(explicitly_required, snapshot(failed))[:2], ("failure", 1))

    def test_advisory_acknowledgement_does_not_survive_new_attempt_or_changed_execution(self):
        selected = args("--acknowledge-advisory-check-id", "1")
        failed = check("advisory", "COMPLETED", "FAILURE", False)
        failed["checkSuite"] = {"workflowRun": {"databaseId": 10, "runAttempt": 1}}
        original = snapshot(failed)
        for changed in [dict(failed, completedAt="2026-10-28T20:02:00Z"),
                        dict(failed, checkSuite={"workflowRun": {"databaseId": 10, "runAttempt": 2}}),
                        dict(failed, databaseId=2), dict(failed, completedAt=None)]:
            with self.subTest(check=changed):
                self.assertEqual(w.evaluate(selected, snapshot(changed), original)[:2], ("advisory_failure", 4))
        self.assertEqual(w.evaluate(selected, snapshot(dict(failed, isRequired=True)), original)[:2], ("failure", 1))

    def test_changed_advisory_attempt_during_success_confirmation_is_not_acknowledged(self):
        selected = args("--acknowledge-advisory-check-id", "1")
        failed = check("advisory", "COMPLETED", "FAILURE", False)
        original = snapshot(failed)
        changed = snapshot(dict(failed, completedAt="2026-10-28T20:02:00Z"))
        output = io.StringIO()
        with patch.object(w, "read_snapshot", side_effect=[original, changed]), contextlib.redirect_stdout(output):
            self.assertEqual(w.watch(selected), 4)
        event = json.loads(output.getvalue().splitlines()[-1])
        self.assertEqual(event["event"], "advisory_failure")
        self.assertEqual(event["acknowledged_advisory_check_ids"], [])
        self.assertFalse(event["observed_failures"][0]["acknowledged_advisory"])

    def test_selected_workflow_failure_cannot_be_acknowledged_as_advisory(self):
        selected = args("--run-id", "10", "--acknowledge-advisory-check-id", "1")
        state = snapshot(check("unit", "COMPLETED", "FAILURE", False))
        state["runs"] = [run(jobs=[{"id": 99, "name": "unit", "status": "completed", "conclusion": "failure"}])]
        self.assertEqual(w.evaluate(selected, state)[:2], ("failure", 1))

    def test_acknowledged_failure_is_retained_at_checkpoint(self):
        selected = args("--acknowledge-advisory-check-id", "1")
        pending = snapshot(check("advisory", "COMPLETED", "FAILURE", False), dict(check(), databaseId=2))
        output = io.StringIO()
        with patch.object(w, "read_snapshot", return_value=pending), patch.object(w.time, "sleep"), \
             patch.object(w.time, "monotonic", side_effect=[0, 51]), contextlib.redirect_stdout(output):
            self.assertEqual(w.watch(selected), 124)
        event = json.loads(output.getvalue().splitlines()[-1])
        self.assertEqual(event["acknowledged_advisory_check_ids"], [1])
        self.assertTrue(event["observed_failures"][0]["acknowledged_advisory"])

    def test_acknowledged_failure_is_retained_when_later_api_read_fails(self):
        selected = args("--acknowledge-advisory-check-id", "1")
        pending = snapshot(check("advisory", "COMPLETED", "FAILURE", False), dict(check(), databaseId=2))
        output = io.StringIO()
        with patch.object(w, "read_snapshot", side_effect=[pending, w.WatchError("API unavailable")]), \
             patch.object(w.time, "sleep"), contextlib.redirect_stdout(output):
            self.assertEqual(w.watch(selected), 2)
        event = json.loads(output.getvalue().splitlines()[-1])
        self.assertEqual(event["event"], "error")
        self.assertEqual(event["acknowledged_advisory_check_ids"], [1])
        self.assertTrue(event["observed_failures"][0]["acknowledged_advisory"])

    def test_changed_pr_stops_without_querying_old_runs(self):
        state = snapshot()
        state["pr"]["headRefOid"] = "c" * 40
        with patch.object(w, "read_pr", return_value=state), patch.object(w, "gh_json") as api:
            result = w.read_snapshot(args("--run-id", "10"), None)
        api.assert_not_called()
        self.assertEqual(w.evaluate(args(), result)[:2], ("superseded", 3))

    def test_pagination_includes_failure_on_later_page(self):
        pr = snapshot()["pr"]
        pages = [response(pr, [check()], True, "next"),
                 response(pr, [check("later", "COMPLETED", "FAILURE")]), base_response()]
        with patch.object(w, "gh_json", side_effect=pages) as api:
            result = w.read_pr(args(), None)
        self.assertEqual(api.call_count, 3)
        self.assertEqual(w.evaluate(args(), result)[:2], ("failure", 1))

    def test_live_base_advances_while_pr_base_oid_is_stale(self):
        pr = snapshot()["pr"]
        with patch.object(w, "gh_json", side_effect=[response(pr, [check()]), base_response("c" * 40)]) as api:
            result = w.read_snapshot(args("--run-id", "10"), None)
        self.assertEqual(api.call_count, 2)
        self.assertIn("ref=refs/heads/main", api.call_args.args[0])
        self.assertEqual(result["pr"]["baseRefOid"], BASE)
        self.assertEqual(w.evaluate(args(), result)[:2], ("superseded", 3))
        self.assertEqual(w.evaluate(args(), result)[2]["base"], "c" * 40)

    def test_unavailable_live_base_fails_closed(self):
        missing = {"data": {"repository": {"ref": None}}}
        with patch.object(w, "gh_json", side_effect=[response(snapshot()["pr"], [check()]), missing]):
            with self.assertRaises(w.WatchError):
                w.read_pr(args(), None)

    def test_changed_head_during_pagination_fails_closed(self):
        pr = snapshot()["pr"]
        changed = dict(pr, headRefOid="c" * 40)
        with patch.object(w, "gh_json", side_effect=[response(pr, [check()], True, "next"), response(changed, [])]):
            with self.assertRaises(w.WatchError):
                w.read_pr(args(), None)

    def test_success_confirmation_catches_changed_head(self):
        green = snapshot(check(status="COMPLETED", conclusion="SUCCESS"))
        changed = copy.deepcopy(green)
        changed["pr"]["headRefOid"] = "c" * 40
        output = io.StringIO()
        with patch.object(w, "read_snapshot", side_effect=[green, changed]), contextlib.redirect_stdout(output):
            code = w.watch(args())
        self.assertEqual(code, 3)
        self.assertNotIn('"event": "ci_success"', output.getvalue())

    def test_unchanged_polls_are_quiet_and_deadline_is_checkpoint(self):
        output = io.StringIO()
        with patch.object(w, "read_snapshot", return_value=snapshot(check())) as read, \
             patch.object(w.time, "sleep"), patch.object(w.time, "monotonic", side_effect=[0, 1, 51]), \
             contextlib.redirect_stdout(output):
            code = w.watch(args())
        self.assertEqual(code, 124)
        self.assertEqual(read.call_count, 2)
        self.assertEqual([json.loads(line)["event"] for line in output.getvalue().splitlines()], ["watching", "checkpoint"])

    def test_api_failure_and_timeout_never_pass(self):
        with patch.object(w.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "secret")):
            with self.assertRaises(w.WatchError) as error:
                w.gh_json(["graphql"], None)
        self.assertNotIn("secret", str(error.exception))
        with patch.object(w.subprocess, "run", side_effect=subprocess.TimeoutExpired("gh", 30)):
            with self.assertRaises(w.WatchError):
                w.gh_json(["graphql"], None)


if __name__ == "__main__":
    unittest.main()
