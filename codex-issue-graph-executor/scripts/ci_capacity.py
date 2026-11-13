#!/usr/bin/env python3
"""Read-only, bounded GitHub Actions job timing inventory for selected runs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
import subprocess
import sys


class InventoryError(Exception):
    pass


def gh_json(*args):
    try:
        result = subprocess.run(["gh", "api", *args], capture_output=True,
                                text=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise InventoryError("GitHub request unavailable or timed out") from exc
    if result.returncode:
        raise InventoryError("gh api failed; check authentication, access and rate limits")
    try:
        return json.loads(result.stdout)
    except ValueError as exc:
        raise InventoryError("GitHub returned invalid JSON") from exc


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else None
    except ValueError:
        return None


def seconds_between(start, end):
    start, end = timestamp(start), timestamp(end)
    if start is None or end is None:
        return None
    elapsed = (end - start).total_seconds()
    return elapsed if elapsed >= 0 else None


def job_record(job, observed_at, show_steps):
    # GitHub can populate started_at for jobs that never received a runner.
    # Do not mistake those placeholders for actual execution or queue time.
    assigned = bool(job.get("runner_name"))
    pending = job.get("status") in ("queued", "waiting", "pending")
    started = job.get("started_at") if assigned and not pending else None
    completed = job.get("completed_at")
    record = {
        "id": job.get("id"), "name": job.get("name"),
        "url": job.get("html_url"), "labels": job.get("labels"),
        "status": job.get("status"), "conclusion": job.get("conclusion"),
        "runner": job.get("runner_name"), "created_at": job.get("created_at"),
        "started_at": started, "completed_at": completed,
        "creation_to_start_seconds": seconds_between(job.get("created_at"), started),
        "execution_seconds": seconds_between(started, completed),
        "age_since_creation_seconds": seconds_between(job.get("created_at"), observed_at)
        if pending else None,
    }
    if show_steps:
        record["steps"] = [{
            "name": step.get("name"), "status": step.get("status"),
            "conclusion": step.get("conclusion"), "started_at": step.get("started_at"),
            "completed_at": step.get("completed_at"),
            "elapsed_seconds": seconds_between(step.get("started_at"), step.get("completed_at")),
        } for step in job.get("steps", [])]
    return record


def inventory_run(repo, run_id, label, observed_at, show_steps):
    endpoint = f"repos/{repo}/actions/runs/{run_id}"
    run = gh_json(endpoint)
    if (not isinstance(run, dict) or run.get("id") != run_id or
            not isinstance(run.get("run_attempt"), int) or not run.get("head_sha")):
        raise InventoryError(f"Run {run_id} has incomplete identity")
    attempt = run["run_attempt"]
    pages = gh_json(f"{endpoint}/attempts/{attempt}/jobs?per_page=100", "--paginate", "--slurp")
    if not isinstance(pages, list) or not pages or any(not isinstance(page, dict) or
                                         not isinstance(page.get("jobs"), list) for page in pages):
        raise InventoryError(f"Run {run_id} has incomplete job pages")
    fresh = gh_json(endpoint)
    if not isinstance(fresh, dict) or (fresh.get("id"), fresh.get("head_sha"), fresh.get("run_attempt")) != (
            run_id, run["head_sha"], attempt):
        raise InventoryError(f"Run {run_id} changed identity or attempt during collection")
    jobs = [job for page in pages for job in page["jobs"]]
    if any(not isinstance(job, dict) for job in jobs):
        raise InventoryError(f"Run {run_id} returned a malformed job")
    unknown = sum(not isinstance(job.get("labels"), list) or not job["labels"] for job in jobs)
    selected = [job for job in jobs if not label or (isinstance(job.get("labels"), list) and any(
        label.casefold() in str(item).casefold() for item in job["labels"]))]
    return {
        "id": run_id, "url": run.get("html_url"), "workflow": run.get("name"),
        "event": run.get("event"), "branch": run.get("head_branch"),
        "head_sha": run["head_sha"], "attempt": attempt,
        "created_at": run.get("created_at"), "status_at_start": run.get("status"),
        "conclusion_at_start": run.get("conclusion"),
        "jobs_with_unknown_labels": unknown, "jobs_total": len(jobs),
        "jobs": [job_record(job, observed_at, show_steps) for job in selected],
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="GitHub owner/repository")
    parser.add_argument("--run-id", type=int, action="append", required=True,
                        help="Selected run ID; repeat for each run, maximum 20")
    parser.add_argument("--label", default="macos", help="Case-insensitive runner label substring; empty selects all")
    parser.add_argument("--show-steps", action="store_true", help="Include per-step timestamps and elapsed seconds")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        parser.error("--repo must be owner/repository")
    if len(args.run_id) > 20 or any(n <= 0 for n in args.run_id) or len(set(args.run_id)) != len(args.run_id):
        parser.error("--run-id values must be unique positive integers, at most 20")
    return args


def main(argv=None):
    args = parse_args(argv)
    observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        runs = [inventory_run(args.repo, run_id, args.label, observed_at, args.show_steps)
                for run_id in args.run_id]
    except InventoryError as exc:
        print(f"ci_capacity: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"repository": args.repo, "observed_at": observed_at,
                      "label_filter": args.label, "runs": runs}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
