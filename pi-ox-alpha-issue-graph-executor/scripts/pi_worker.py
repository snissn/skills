#!/usr/bin/env python3
"""Launch one model-locked Pi issue-graph worker.

The worker runs as a detached `pi --mode json --print --no-session` process
hard-pinned to OpenRouter `stealth/ox-alpha`. Its JSON event stream and stderr
remain in a run directory for coordinator reconciliation. This helper does not
interpret Git or GitHub state; the parent Pi coordinator remains responsible
for both.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import time
from typing import Any

SESSION_ENV_KEYS = (
    "PI_SESSION_ID",
    "PI_SESSION_FILE",
    "PI_PROVIDER",
    "PI_MODEL",
    "PI_REASONING_LEVEL",
)
DEFAULT_TOOLS = "read,bash,edit,write,grep,find,ls"
REQUIRED_PROVIDER = "openrouter"
REQUIRED_MODEL = "stealth/ox-alpha"
REQUIRED_ROUTE = f"{REQUIRED_PROVIDER}/{REQUIRED_MODEL}"
TERMINAL_STOP_REASONS = {"error", "aborted"}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_meta(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "meta.json"
    if not path.is_file():
        raise SystemExit(f"missing worker metadata: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid worker metadata {path}: {exc}") from exc


def text_from_message(message: dict[str, Any]) -> str:
    parts = message.get("content")
    if not isinstance(parts, list):
        return ""
    return "\n".join(
        part.get("text", "")
        for part in parts
        if isinstance(part, dict) and part.get("type") == "text" and isinstance(part.get("text"), str)
    ).strip()


def inspect_events(events_path: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "event_count": 0,
        "agent_end": False,
        "last_event_type": None,
        "final_text": "",
        "stop_reason": None,
        "error_message": None,
        "actual_provider": None,
        "actual_model": None,
        "actual_thinking": None,
    }
    if not events_path.is_file():
        return summary

    try:
        with events_path.open("r", encoding="utf-8", errors="replace") as stream:
            for raw_line in stream:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(event, dict):
                    continue
                summary["event_count"] += 1
                summary["last_event_type"] = event.get("type")
                if event.get("type") == "agent_end":
                    summary["agent_end"] = True
                if event.get("type") != "message_end":
                    continue
                message = event.get("message")
                if not isinstance(message, dict) or message.get("role") != "assistant":
                    continue
                text = text_from_message(message)
                if text:
                    summary["final_text"] = text
                summary["stop_reason"] = message.get("stopReason")
                summary["error_message"] = message.get("errorMessage")
                summary["actual_provider"] = message.get("provider")
                summary["actual_model"] = message.get("model")
                summary["actual_thinking"] = message.get("reasoningLevel") or message.get("thinkingLevel")
    except OSError as exc:
        summary["read_error"] = str(exc)
    return summary


def process_status(pid: int) -> tuple[bool, str]:
    if pid <= 0:
        return False, ""
    try:
        proc = subprocess.run(
            ["ps", "-p", str(pid), "-o", "stat=", "-o", "command="],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        try:
            os.kill(pid, 0)
            return True, ""
        except OSError:
            return False, ""
    output = proc.stdout.strip()
    if proc.returncode != 0 or not output:
        return False, ""
    stat, _, command = output.partition(" ")
    return not stat.startswith("Z"), command.strip()


def worker_status(run_dir: Path) -> dict[str, Any]:
    meta = load_meta(run_dir)
    pid = int(meta.get("pid") or 0)
    alive, process_command = process_status(pid)
    events = inspect_events(run_dir / "events.jsonl")
    stop_reason = events.get("stop_reason")
    route_observed = bool(events.get("actual_provider") or events.get("actual_model"))
    route_verified = (
        events.get("actual_provider") == REQUIRED_PROVIDER
        and events.get("actual_model") == REQUIRED_MODEL
    )
    route_violation = route_observed and not route_verified

    if route_violation or (events.get("agent_end") and not route_verified):
        state = "model-violation"
    elif events.get("agent_end") and (stop_reason in TERMINAL_STOP_REASONS or events.get("error_message")):
        state = "failed"
    elif events.get("agent_end"):
        state = "completed"
    elif alive:
        state = "running"
    else:
        state = "exited-incomplete"

    stderr_path = run_dir / "stderr.log"
    stderr_bytes = stderr_path.stat().st_size if stderr_path.exists() else 0
    return {
        "state": state,
        "run_dir": str(run_dir),
        "pid": pid,
        "process_alive": alive,
        "process_command": process_command,
        "started_at": meta.get("started_at"),
        "cwd": meta.get("cwd"),
        "prompt_file": meta.get("prompt_file"),
        "requested_provider": meta.get("requested_provider"),
        "requested_model": meta.get("requested_model"),
        "requested_thinking": meta.get("requested_thinking"),
        "required_route": REQUIRED_ROUTE,
        "model_route_verified": route_verified,
        "stderr_bytes": stderr_bytes,
        **events,
    }


def require_coordinator_route() -> None:
    provider = os.environ.get("PI_PROVIDER", "").strip()
    model = os.environ.get("PI_MODEL", "").strip()
    if provider != REQUIRED_PROVIDER or model != REQUIRED_MODEL:
        observed = f"{provider or '(unset)'}/{model or '(unset)'}"
        raise SystemExit(
            f"coordinator model lock violation: required {REQUIRED_ROUTE}, got {observed}"
        )


def build_command(args: argparse.Namespace) -> list[str]:
    if args.model != REQUIRED_ROUTE:
        raise SystemExit(
            f"model lock violation: required {REQUIRED_ROUTE}, got {args.model or '(none)'}"
        )
    pi = shutil.which(args.pi_binary)
    if not pi:
        raise SystemExit(f"Pi executable not found: {args.pi_binary}")

    skill_dir = Path(__file__).resolve().parents[1]
    worker_system = skill_dir / "references" / "pi-worker-system.md"
    if not worker_system.is_file():
        raise SystemExit(f"missing worker system prompt: {worker_system}")

    command = [
        pi,
        "--mode",
        "json",
        "--print",
        "--no-session",
        "--no-extensions",
        "--no-prompt-templates",
        "--no-skills",
        "--no-themes",
        "--no-approve",
        "--tools",
        args.tools,
        "--append-system-prompt",
        str(worker_system),
    ]

    skills: list[Path] = []
    if not args.no_default_skills:
        skills.append(skill_dir)
        mergeable_skill = skill_dir.parent / "github-pr-mergeable"
        if mergeable_skill.is_dir():
            skills.append(mergeable_skill)
    skills.extend(Path(value).expanduser().resolve() for value in args.skill)
    for skill in skills:
        if not skill.exists():
            raise SystemExit(f"explicit skill does not exist: {skill}")
        command.extend(["--skill", str(skill)])

    command.extend(["--model", REQUIRED_ROUTE])
    if args.thinking:
        command.extend(["--thinking", args.thinking])

    command.extend(
        [
            f"@{Path(args.prompt_file).expanduser().resolve()}",
            "Execute the delegated issue-graph task and return the required coordinator handoff.",
        ]
    )
    return command


def start_worker(args: argparse.Namespace) -> int:
    require_coordinator_route()
    run_dir = Path(args.run_dir).expanduser().resolve()
    cwd = Path(args.cwd).expanduser().resolve()
    prompt_file = Path(args.prompt_file).expanduser().resolve()

    if not cwd.is_dir():
        raise SystemExit(f"worker cwd is not a directory: {cwd}")
    if not prompt_file.is_file():
        raise SystemExit(f"worker prompt is not a file: {prompt_file}")
    if (run_dir / "meta.json").exists():
        raise SystemExit(f"run directory already contains meta.json: {run_dir}")

    command = build_command(args)
    if args.dry_run:
        print(json.dumps({"cwd": str(cwd), "command": command, "shell": shlex.join(command)}, indent=2))
        return 0

    run_dir.mkdir(parents=True, exist_ok=True)
    events_path = run_dir / "events.jsonl"
    stderr_path = run_dir / "stderr.log"
    env = os.environ.copy()
    for key in SESSION_ENV_KEYS:
        env.pop(key, None)
    env["PI_OX_ALPHA_ISSUE_GRAPH_WORKER"] = "1"

    with events_path.open("ab", buffering=0) as stdout, stderr_path.open("ab", buffering=0) as stderr:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
            close_fds=True,
        )

    meta = {
        "schema_version": 1,
        "started_at": utc_now(),
        "pid": process.pid,
        "process_group": process.pid,
        "cwd": str(cwd),
        "prompt_file": str(prompt_file),
        "events_file": str(events_path),
        "stderr_file": str(stderr_path),
        "coordinator_provider": os.environ.get("PI_PROVIDER"),
        "coordinator_model": os.environ.get("PI_MODEL"),
        "requested_provider": REQUIRED_PROVIDER,
        "requested_model": REQUIRED_MODEL,
        "requested_thinking": args.thinking,
        "command": command,
    }
    atomic_write_json(run_dir / "meta.json", meta)
    print(json.dumps({"state": "started", "run_dir": str(run_dir), "pid": process.pid}, indent=2))
    return 0


def status_worker(args: argparse.Namespace) -> int:
    status = worker_status(Path(args.run_dir).expanduser().resolve())
    if not args.include_final_text:
        status.pop("final_text", None)
    print(json.dumps(status, indent=2))
    return 0


def wait_worker(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).expanduser().resolve()
    deadline = time.monotonic() + args.timeout if args.timeout > 0 else None
    while True:
        status = worker_status(run_dir)
        if status["state"] != "running":
            if not args.include_final_text:
                status.pop("final_text", None)
            print(json.dumps(status, indent=2))
            return 0 if status["state"] == "completed" else 2
        if deadline is not None and time.monotonic() >= deadline:
            status.pop("final_text", None)
            status["wait_timed_out"] = True
            print(json.dumps(status, indent=2))
            return 124
        time.sleep(args.poll_interval)


def result_worker(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).expanduser().resolve()
    status = worker_status(run_dir)
    final_text = status.get("final_text") or ""
    if final_text:
        print(final_text)
    else:
        stderr_path = run_dir / "stderr.log"
        stderr = stderr_path.read_text(encoding="utf-8", errors="replace").strip() if stderr_path.exists() else ""
        print(stderr or f"worker has no final response (state={status['state']})", file=sys.stderr)
    return 0 if status["state"] == "completed" and final_text else 2


def stop_worker(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).expanduser().resolve()
    meta = load_meta(run_dir)
    status = worker_status(run_dir)
    if not status["process_alive"]:
        print(json.dumps({"state": status["state"], "stopped": False, "reason": "worker process is not running"}, indent=2))
        return 0

    pid = int(meta.get("pid") or 0)
    process_command = str(status.get("process_command") or "")
    prompt_file = str(meta.get("prompt_file") or "")
    if not args.force and prompt_file not in process_command:
        raise SystemExit(
            "refusing to signal a process whose command does not match worker metadata; "
            "inspect it and pass --force only if it is the recorded worker"
        )

    pgid = int(meta.get("process_group") or pid)
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        pass

    deadline = time.monotonic() + args.grace_seconds
    while time.monotonic() < deadline:
        alive, _ = process_status(pid)
        if not alive:
            break
        time.sleep(0.2)
    else:
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    meta["stop_requested_at"] = utc_now()
    atomic_write_json(run_dir / "meta.json", meta)
    final = worker_status(run_dir)
    print(json.dumps({"state": final["state"], "stopped": True, "pid": pid}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="start one detached Pi worker")
    start.add_argument("--run-dir", required=True, help="new artifact directory for this worker")
    start.add_argument("--cwd", required=True, help="absolute or relative isolated worktree path")
    start.add_argument("--prompt-file", required=True, help="worker assignment markdown file")
    start.add_argument(
        "--model",
        default=REQUIRED_ROUTE,
        choices=(REQUIRED_ROUTE,),
        help=f"fixed Pi route; only {REQUIRED_ROUTE} is allowed",
    )
    start.add_argument(
        "--thinking",
        default=os.environ.get("PI_REASONING_LEVEL", "medium"),
        choices=("off", "minimal", "low", "medium", "high", "xhigh", "max"),
    )
    start.add_argument("--tools", default=DEFAULT_TOOLS, help="comma-separated Pi worker tool allowlist")
    start.add_argument("--skill", action="append", default=[], help="additional explicit skill path (repeatable)")
    start.add_argument("--no-default-skills", action="store_true", help="do not load graph/mergeable skills")
    start.add_argument("--pi-binary", default="pi", help="Pi executable name or path")
    start.add_argument("--dry-run", action="store_true", help="validate and print the command without launching")
    start.set_defaults(func=start_worker)

    status = subparsers.add_parser("status", help="report process and event-stream status")
    status.add_argument("--run-dir", required=True)
    status.add_argument("--include-final-text", action="store_true")
    status.set_defaults(func=status_worker)

    wait = subparsers.add_parser("wait", help="wait for a worker to stop running")
    wait.add_argument("--run-dir", required=True)
    wait.add_argument("--timeout", type=float, default=0, help="seconds; zero means no timeout")
    wait.add_argument("--poll-interval", type=float, default=2.0)
    wait.add_argument("--include-final-text", action="store_true")
    wait.set_defaults(func=wait_worker)

    result = subparsers.add_parser("result", help="print the final assistant handoff")
    result.add_argument("--run-dir", required=True)
    result.set_defaults(func=result_worker)

    stop = subparsers.add_parser("stop", help="terminate a running worker process group")
    stop.add_argument("--run-dir", required=True)
    stop.add_argument("--grace-seconds", type=float, default=5.0)
    stop.add_argument("--force", action="store_true")
    stop.set_defaults(func=stop_worker)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
