#!/usr/bin/env python3
"""Quiet, read-only GitHub CI notification watcher; never a merge gate.

Requires Python 3.10+ and an authenticated gh CLI. See references/ci-watcher.md.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone


QUERY = """
query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      state url headRefOid baseRefOid baseRefName isDraft mergeable reviewDecision
      commits(last: 1) { nodes { commit { oid statusCheckRollup {
        contexts(first: 100, after: $cursor) {
          pageInfo { hasNextPage endCursor }
          nodes {
            __typename
            ... on CheckRun {
              databaseId name status conclusion startedAt completedAt detailsUrl
              isRequired(pullRequestNumber: $number)
              checkSuite { workflowRun { databaseId runAttempt } }
            }
            ... on StatusContext { context state targetUrl isRequired(pullRequestNumber: $number) }
          }
        }
      } } } }
    }
  }
}
"""

BASE_QUERY = """
query($owner: String!, $name: String!, $ref: String!) {
  repository(owner: $owner, name: $name) {
    ref(qualifiedName: $ref) { target { oid } }
  }
}
"""


class WatchError(Exception):
    pass


def gh_json(args, deadline):
    timeout = 30 if deadline is None else min(30, deadline - time.monotonic())
    if timeout <= 0:
        raise TimeoutError
    try:
        result = subprocess.run(
            ["gh", "api", *args], capture_output=True, text=True, timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError from exc
        raise WatchError("GitHub request timed out; inspect API connectivity") from exc
    except OSError as exc:
        raise WatchError("Cannot execute gh; check installation and authentication") from exc
    if result.returncode:
        # Do not echo response bodies, tokens, or unbounded provider output.
        raise WatchError("gh api failed; inspect authentication, permissions, rate limits, or service state")
    try:
        data = json.loads(result.stdout)
    except ValueError as exc:
        raise WatchError("GitHub returned invalid JSON") from exc
    if isinstance(data, dict) and data.get("errors"):
        raise WatchError("GitHub GraphQL returned errors; snapshot is incomplete")
    return data


def read_pr(args, deadline):
    owner, name = args.repo.split("/")
    cursor = None
    checks = []
    identity = None
    while True:
        command = ["graphql", "-f", f"query={QUERY}", "-f", f"owner={owner}",
                   "-f", f"name={name}", "-F", f"number={args.pr}"]
        if cursor:
            command += ["-f", f"cursor={cursor}"]
        data = gh_json(command, deadline)
        try:
            pr = data["data"]["repository"]["pullRequest"]
            current = (pr["headRefOid"], pr["baseRefOid"], pr["baseRefName"],
                       pr["state"], pr["isDraft"], pr["reviewDecision"], pr["mergeable"])
            if identity is not None and current != identity:
                raise WatchError("PR changed during pagination; refresh its state")
            identity = current
            # Stop immediately for changed/closed PRs, even when checks are absent.
            if pr["headRefOid"] != args.head or pr["baseRefOid"] != args.base or pr["state"] != "OPEN":
                return {"pr": pr, "checks": []}
            commit = pr["commits"]["nodes"][-1]["commit"]
            if commit["oid"] != args.head:
                raise WatchError("PR commit snapshot does not match the pinned head")
            rollup = commit["statusCheckRollup"]
            if rollup is None:
                break
            page = rollup["contexts"]
            checks.extend(page["nodes"])
            if not page["pageInfo"]["hasNextPage"]:
                break
            next_cursor = page["pageInfo"]["endCursor"]
            if not next_cursor or next_cursor == cursor:
                raise WatchError("Invalid GitHub pagination cursor")
            cursor = next_cursor
        except (KeyError, TypeError, IndexError) as exc:
            raise WatchError("GitHub returned an incomplete PR/check snapshot") from exc

    # PR.baseRefOid can lag a moving branch. Read the repository ref separately;
    # do not accept its cached PR value as evidence of the current base target.
    data = gh_json(["graphql", "-f", f"query={BASE_QUERY}", "-f", f"owner={owner}",
                    "-f", f"name={name}", "-f", f"ref=refs/heads/{pr['baseRefName']}"], deadline)
    try:
        base_oid = data["data"]["repository"]["ref"]["target"]["oid"]
        if not isinstance(base_oid, str) or not re.fullmatch(r"[0-9a-f]{40}", base_oid):
            raise WatchError("GitHub returned an invalid live base branch target")
        pr["baseBranchOid"] = base_oid
    except (KeyError, TypeError) as exc:
        raise WatchError("Live base branch target unavailable; cannot verify base identity") from exc
    return {"pr": pr, "checks": checks}


def read_snapshot(args, deadline):
    snapshot = read_pr(args, deadline) if args.pr else {}
    snapshot["runs"] = []
    if args.pr and (snapshot["pr"]["headRefOid"] != args.head or
                    snapshot["pr"]["baseRefOid"] != args.base or snapshot["pr"]["state"] != "OPEN" or
                    snapshot["pr"]["baseBranchOid"] != args.base):
        return snapshot
    for run_id in args.run_id:
        run = gh_json([f"repos/{args.repo}/actions/runs/{run_id}"], deadline)
        if not isinstance(run, dict) or not all(key in run for key in
                ("id", "head_sha", "run_attempt", "status", "conclusion", "workflow_id")):
            raise WatchError("GitHub returned an incomplete workflow snapshot")
        if run["id"] != run_id:
            raise WatchError("Workflow run ID does not match the requested run")
        pages = gh_json([f"repos/{args.repo}/actions/runs/{run_id}/attempts/{run['run_attempt']}/jobs?per_page=100",
                         "--paginate", "--slurp"], deadline)
        try:
            run["jobs"] = [job for page in pages for job in page["jobs"]]
        except (KeyError, TypeError) as exc:
            raise WatchError("GitHub returned an incomplete workflow job snapshot") from exc
        snapshot["runs"].append(run)
    return snapshot


def check_execution(check):
    run = (check.get("checkSuite") or {}).get("workflowRun") or {}
    return (check.get("databaseId"), check.get("startedAt"), check.get("completedAt"),
            run.get("databaseId"), run.get("runAttempt"))


def acknowledged_advisories(args, snapshot, baseline=None):
    """IDs explicitly dispositioned by the owner, valid only for this execution."""
    previous = {item.get("databaseId"): item for item in (baseline or {}).get("checks", [])
                if item.get("__typename") == "CheckRun"}
    accepted = set()
    for check in snapshot.get("checks", []):
        check_id = check.get("databaseId")
        if (check.get("__typename") != "CheckRun" or check_id not in args.acknowledge_advisory_check_id or
                check["isRequired"] or check["name"] in args.require_check or
                check["status"] != "COMPLETED" or check.get("conclusion") != "FAILURE" or
                not check.get("completedAt")):
            continue
        if baseline is not None and (check_id not in previous or
                                     check_execution(check) != check_execution(previous[check_id])):
            continue
        accepted.add(check_id)
    return accepted


def evaluate(args, snapshot, baseline=None):
    """Return (event, exit code, details), or None while still pending."""
    pr = snapshot.get("pr")
    if pr:
        if pr["headRefOid"] != args.head or pr["baseRefOid"] != args.base:
            return "superseded", 3, {"head": pr["headRefOid"], "base": pr["baseRefOid"]}
        if baseline and pr["baseRefName"] != baseline["pr"]["baseRefName"]:
            return "superseded", 3, {"reason": "base branch changed"}
        if pr["state"] != "OPEN":
            return "pr_closed", 4, {"state": pr["state"]}
        if not pr.get("baseBranchOid"):
            raise WatchError("Live base branch target missing; cannot verify base identity")
        if pr["baseBranchOid"] != args.base:
            return "superseded", 3, {"reason": "live base branch advanced", "base": pr["baseBranchOid"],
                                      "pr_base": pr["baseRefOid"], "base_ref": pr["baseRefName"]}
        if pr["isDraft"] or pr["mergeable"] == "CONFLICTING" or pr["reviewDecision"] == "CHANGES_REQUESTED":
            return "intervention", 4, {"draft": pr["isDraft"], "mergeable": pr["mergeable"],
                                        "review_decision": pr["reviewDecision"]}
        if baseline and pr["reviewDecision"] != baseline["pr"]["reviewDecision"]:
            return "review_changed", 4, {"review_decision": pr["reviewDecision"]}

    ready = bool(args.run_id or snapshot.get("checks"))
    old_runs = {run["id"]: run for run in (baseline or {}).get("runs", [])}
    for run in snapshot.get("runs", []):
        if run["head_sha"] != args.head:
            return "superseded", 3, {"run_id": run["id"], "head": run["head_sha"]}
        old = old_runs.get(run["id"])
        if old and (run["run_attempt"] != old["run_attempt"] or run["workflow_id"] != old["workflow_id"]):
            return "superseded", 3, {"run_id": run["id"], "attempt": run["run_attempt"]}
        expected_attempt = args.run_attempt.get(run["id"])
        if expected_attempt is not None and run["run_attempt"] != expected_attempt:
            return "superseded", 3, {"run_id": run["id"], "attempt": run["run_attempt"]}
        for job in run.get("jobs", []):
            ready = ready and job["status"].lower() == "completed"
            conclusion = (job["conclusion"] or "").lower()
            matches = [item for item in snapshot.get("checks", []) if item.get("name") == job["name"]]
            required = any(item["isRequired"] or item["name"] in args.require_check for item in matches) if matches else None
            details = {"run_id": run["id"], "attempt": run["run_attempt"],
                       "job": job["name"], "job_id": job["id"], "conclusion": conclusion,
                       "scope": "explicit_workflow",
                       "required": required}
            if conclusion in {"failure", "timed_out", "startup_failure"}:
                return "failure", 1, details
            if conclusion == "cancelled":
                return "cancelled", 5, details
            if conclusion in {"action_required", "stale"}:
                return "intervention", 4, details
        status, conclusion = run["status"].lower(), (run["conclusion"] or "").lower()
        if conclusion == "cancelled":
            return "cancelled", 5, {"run_id": run["id"]}
        if conclusion in {"failure", "timed_out", "startup_failure"}:
            return "failure", 1, {"run_id": run["id"], "conclusion": conclusion}
        if status in {"waiting", "action_required"} or conclusion in {"action_required", "stale", "neutral", "skipped"}:
            return "intervention", 4, {"run_id": run["id"], "status": status, "conclusion": conclusion}
        if status == "completed" and conclusion != "success":
            return "intervention", 4, {"run_id": run["id"], "conclusion": conclusion}
        ready = ready and status == "completed" and conclusion == "success"

    names = set()
    acknowledged = acknowledged_advisories(args, snapshot, baseline)
    # Surface required failures ahead of advisory failures from the same snapshot.
    for check in sorted(snapshot.get("checks", []), key=lambda item:
                        not (item.get("isRequired") or item.get("name", item.get("context")) in args.require_check)):
        kind = check["__typename"]
        if kind == "CheckRun":
            name, status = check["name"], check["status"]
            conclusion = check.get("conclusion") or ""
            required = check["isRequired"] or name in args.require_check
            classification = {"check": name, "required": required,
                              "check_id": check.get("databaseId"),
                              "scope": "required" if required else "advisory",
                              "conclusion": conclusion}
            good = status == "COMPLETED" and (conclusion == "SUCCESS" or
                                              (not required and conclusion in {"NEUTRAL", "SKIPPED"}))
            if conclusion == "CANCELLED":
                return "cancelled", 5, classification
            if conclusion in {"FAILURE", "TIMED_OUT", "STARTUP_FAILURE"}:
                if check.get("databaseId") in acknowledged:
                    good = True
                else:
                    return "failure" if required else "advisory_failure", 1 if required else 4, classification
            elif check.get("databaseId") in args.acknowledge_advisory_check_id:
                return "intervention", 4, {**classification,
                    "reason": "acknowledgement no longer matches a completed advisory FAILURE"}
            if status == "WAITING" or conclusion in {"ACTION_REQUIRED", "STALE"} or (
                    required and conclusion in {"NEUTRAL", "SKIPPED"}):
                return "intervention", 4, classification
            if status == "COMPLETED" and not good:
                return "intervention", 4, classification
        elif kind == "StatusContext":
            name, state = check["context"], check["state"]
            if state in {"ERROR", "FAILURE"}:
                required = check["isRequired"] or name in args.require_check
                return "failure" if required else "advisory_failure", 1 if required else 4, {
                    "check": name, "state": state, "required": required,
                    "scope": "required" if required else "advisory"}
            good = state == "SUCCESS"
        else:
            raise WatchError("Unknown check type; snapshot is incomplete")
        names.add(name)
        ready = ready and good
    if set(args.require_check) - names:
        ready = False
    if ready:
        return "ci_success", 0, {"checks": len(snapshot.get("checks", [])),
                                 "run_ids": args.run_id, "merge_authorized": False,
                                 "acknowledged_advisory_check_ids": sorted(acknowledged)}
    return None


def emit(args, event, **details):
    print(json.dumps({"event": event, "repo": args.repo, "pr": args.pr,
                      "head": args.head, "base": args.base,
                      "time": datetime.now(timezone.utc).isoformat(), **details}), flush=True)


def observed_failures(snapshot, acknowledged=()):
    """Keep every observed failed check/job in the notification for diagnosis."""
    failures = []
    for check in snapshot.get("checks", []):
        state = check.get("conclusion") or check.get("state")
        if state in {"FAILURE", "ERROR", "TIMED_OUT", "STARTUP_FAILURE", "CANCELLED", "ACTION_REQUIRED", "STALE"}:
            failures.append({"check": check.get("name", check.get("context")), "state": state,
                             "required": check["isRequired"], "check_id": check.get("databaseId"),
                             "completed_at": check.get("completedAt"),
                             "acknowledged_advisory": check.get("databaseId") in acknowledged,
                             "url": check.get("detailsUrl", check.get("targetUrl"))})
    for run in snapshot.get("runs", []):
        for job in run.get("jobs", []):
            if job.get("conclusion") in {"failure", "timed_out", "startup_failure", "cancelled", "action_required", "stale"}:
                failures.append({"run_id": run["id"], "attempt": run["run_attempt"], "job_id": job["id"],
                                 "job": job["name"], "state": job["conclusion"], "url": job.get("html_url")})
    return failures


def notify_job_completions(args, snapshot, notified):
    """Emit optional progress only after the snapshot's terminal checks pass."""
    completed = []
    queued = set()
    for run in snapshot.get("runs", []):
        for job_id in args.notify_job_id.get(run["id"], []):
            jobs = [job for job in run.get("jobs", []) if job["id"] == job_id]
            if len(jobs) > 1:
                raise WatchError("Duplicate selected job identity in workflow snapshot")
            if not jobs:
                continue
            job = jobs[0]
            if (job.get("run_id", run["id"]) != run["id"] or
                    job.get("run_attempt", run["run_attempt"]) != run["run_attempt"]):
                raise WatchError("Selected job does not match its workflow run/attempt")
            key = (run["id"], run["run_attempt"], job_id)
            if job["status"].lower() != "completed" or key in notified or key in queued:
                continue
            if not job.get("conclusion") or not job.get("completed_at"):
                raise WatchError("Completed selected job is missing conclusion or completion time")
            completed.append((key, {"run_id": run["id"], "attempt": run["run_attempt"],
                "workflow_id": run["workflow_id"], "job_id": job_id, "job": job["name"],
                "conclusion": job["conclusion"].lower(), "started_at": job.get("started_at"),
                "completed_at": job["completed_at"], "url": job.get("html_url"),
                "scope": "explicit_workflow", "terminal": False, "merge_authorized": False}))
            queued.add(key)
    for key, details in completed:
        emit(args, "job_completed", **details)
        notified.add(key)


def watch(args):
    started = time.monotonic()
    deadline = started + args.max_wait if args.max_wait else None
    baseline = None
    snapshot = {}
    notified_jobs = set()
    last_failure_metadata = {"acknowledged_advisory_check_ids": [], "observed_failures": []}
    emit(args, "watching", run_ids=args.run_id, run_attempts=args.run_attempt,
         requested_advisory_acknowledgement_ids=args.acknowledge_advisory_check_id,
         **({"requested_job_notifications": args.notify_job_id} if args.notify_job_id else {}))
    try:
        while True:
            snapshot = read_snapshot(args, deadline)
            result = evaluate(args, snapshot, baseline)
            acknowledged = acknowledged_advisories(args, snapshot, baseline)
            last_failure_metadata = {"acknowledged_advisory_check_ids": sorted(acknowledged),
                                     "observed_failures": observed_failures(snapshot, acknowledged)}
            acknowledgement_baseline = baseline
            if result:
                # A second read prevents reporting success from an already changed head,
                # cancelled/rerun workflow, or pagination race. Final merge gates still apply.
                if result[0] == "ci_success":
                    acknowledgement_baseline = baseline or snapshot
                    confirmation = read_snapshot(args, deadline)
                    result = evaluate(args, confirmation, acknowledgement_baseline)
                    snapshot = confirmation
                if result:
                    event, code, details = result
                    if event == "ci_success":
                        notify_job_completions(args, snapshot, notified_jobs)
                    acknowledged = acknowledged_advisories(args, snapshot, acknowledgement_baseline)
                    if "acknowledged_advisory_check_ids" not in details:
                        details["acknowledged_advisory_check_ids"] = sorted(acknowledged)
                    emit(args, event, **details, observed_failures=observed_failures(snapshot, acknowledged),
                         run_bindings=[{key: run[key] for key in ("id", "head_sha", "run_attempt", "workflow_id")}
                                       for run in snapshot.get("runs", [])])
                    return code
            notify_job_completions(args, snapshot, notified_jobs)
            baseline = baseline or snapshot
            remaining = args.poll_interval if deadline is None else deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError
            time.sleep(min(args.poll_interval, remaining))
    except TimeoutError:
        acknowledged = acknowledged_advisories(args, snapshot, baseline)
        emit(args, "checkpoint", reason="max_wait reached; CI remains unaccepted",
             acknowledged_advisory_check_ids=sorted(acknowledged),
             observed_failures=observed_failures(snapshot, acknowledged))
        return 124
    except (WatchError, KeyError, TypeError, ValueError) as exc:
        emit(args, "error", reason=str(exc), **last_failure_metadata)
        return 2
    except KeyboardInterrupt:
        emit(args, "watch_cancelled", reason="watcher interrupted; remote runs unchanged",
             **last_failure_metadata)
        return 130


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="OWNER/REPO, using gh's authenticated host")
    parser.add_argument("--pr", type=int)
    parser.add_argument("--head", required=True, help="Pinned full 40-character head SHA")
    parser.add_argument("--base", help="Pinned full base SHA; required with --pr")
    parser.add_argument("--run-id", type=int, action="append", default=[])
    parser.add_argument("--run-attempt", action="append", default=[], metavar="RUN_ID:ATTEMPT",
                        help="Pin an already recorded attempt, especially when resuming")
    parser.add_argument("--notify-job-id", action="append", default=[], metavar="RUN_ID:JOB_ID",
                        help="Emit once-only job completion progress without ending the watch; repeat as needed")
    parser.add_argument("--require-check", action="append", default=[], help="Expected check name; repeat as needed")
    parser.add_argument("--acknowledge-advisory-check-id", type=int, action="append", default=[], metavar="ID",
                        help="Exact CheckRun databaseId whose advisory FAILURE the owner already dispositioned")
    parser.add_argument("--poll-interval", type=float, default=60, help="Seconds between snapshots, minimum 15")
    parser.add_argument("--max-wait", type=float, default=50, help="Seconds until checkpoint exit; 0 waits until event")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        parser.error("--repo must be OWNER/REPO")
    if not args.pr and not args.run_id:
        parser.error("provide --pr and/or --run-id")
    if args.pr and not args.base:
        parser.error("--base is required with --pr")
    if args.base and not args.pr:
        parser.error("--base requires --pr; run-only mode cannot monitor a PR base")
    if args.require_check and not args.pr:
        parser.error("--require-check requires --pr")
    if args.acknowledge_advisory_check_id and not args.pr:
        parser.error("--acknowledge-advisory-check-id requires --pr")
    if any(check_id <= 0 for check_id in args.acknowledge_advisory_check_id):
        parser.error("acknowledged advisory check IDs must be positive")
    for sha in [args.head, args.base] if args.base else [args.head]:
        if not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
            parser.error("head/base bindings must be full 40-character SHAs")
    if not math.isfinite(args.poll_interval) or not math.isfinite(args.max_wait) or args.poll_interval < 15 or args.max_wait < 0:
        parser.error("poll interval must be >=15 seconds and max wait >=0")
    if (args.pr is not None and args.pr <= 0) or any(run <= 0 for run in args.run_id):
        parser.error("PR and run IDs must be positive")
    attempts = {}
    for binding in args.run_attempt:
        if not re.fullmatch(r"[1-9][0-9]*:[1-9][0-9]*", binding):
            parser.error("--run-attempt must be RUN_ID:ATTEMPT")
        run_id, attempt = map(int, binding.split(":"))
        if run_id not in args.run_id or run_id in attempts:
            parser.error("each --run-attempt must bind a distinct selected run")
        attempts[run_id] = attempt
    args.run_attempt = attempts
    notifications = {}
    for binding in args.notify_job_id:
        if not re.fullmatch(r"[1-9][0-9]*:[1-9][0-9]*", binding):
            parser.error("--notify-job-id must be RUN_ID:JOB_ID")
        run_id, job_id = map(int, binding.split(":"))
        if run_id not in args.run_id or job_id in notifications.get(run_id, []):
            parser.error("each --notify-job-id must bind a distinct job in a selected run")
        notifications.setdefault(run_id, []).append(job_id)
    args.notify_job_id = notifications
    args.head = args.head.lower()
    args.base = args.base.lower() if args.base else None
    return args


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    sys.exit(watch(parse_args()))
