#!/usr/bin/env python3
"""Validate a gpt56-pro-issue-graph-executor state document.

The input may be raw JSON or a Markdown parent-comment body containing the
executor marker and a fenced JSON block.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "gpt56-pro-issue-graph-executor/v1"
MARKER = "<!-- gpt56-pro-issue-graph-executor:state:v1 -->"

STATES = {
    "pending",
    "ready",
    "running",
    "testing",
    "draft",
    "review-ready",
    "review-pending",
    "fix-needed",
    "ci-pending",
    "mergeable-candidate",
    "merged",
    "blocked",
    "deferred",
}

ACTIVE_STATES = {"running", "testing"}
FULL_SHA_RE = re.compile(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}")


def is_full_sha(value: Any) -> bool:
    return isinstance(value, str) and FULL_SHA_RE.fullmatch(value) is not None


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def extract_data(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("{"):
        value = json.loads(stripped)
    else:
        if MARKER not in text:
            raise ValueError(f"Markdown input is missing marker: {MARKER}")
        matches = re.findall(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
        if not matches:
            raise ValueError("Markdown input has no fenced JSON object")
        value = json.loads(matches[-1])
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def as_issue_id(value: Any) -> str:
    if isinstance(value, bool):
        raise ValueError("boolean is not an issue id")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str) and value.isdigit():
        return str(int(value))
    raise ValueError(f"invalid issue id: {value!r}")


def validate(data: dict[str, Any]) -> Validation:
    v = Validation()

    for key in (
        "schema",
        "repo",
        "parent_issue",
        "mode",
        "base_branch",
        "base_sha",
        "updated_at",
        "limits",
        "nodes",
    ):
        if key not in data:
            v.error(f"missing top-level field: {key}")

    if data.get("schema") != SCHEMA:
        v.error(f"schema must be {SCHEMA!r}")

    repo = data.get("repo")
    if not isinstance(repo, str) or "/" not in repo:
        v.error("repo must be an owner/name string")

    try:
        as_issue_id(data.get("parent_issue"))
    except ValueError as exc:
        v.error(f"parent_issue: {exc}")

    mode = data.get("mode")
    if not isinstance(mode, str) or mode not in {
        "execute-and-merge",
        "readiness-only",
        "no-merge",
    }:
        v.error("mode must be execute-and-merge, readiness-only, or no-merge")

    base_sha = data.get("base_sha")
    if (
        not isinstance(base_sha, str)
        or re.fullmatch(r"[0-9a-fA-F]{7,64}", base_sha) is None
    ):
        v.error("base_sha must be a hexadecimal commit SHA or unambiguous prefix")

    limits = data.get("limits")
    if not isinstance(limits, dict):
        v.error("limits must be an object")
        limits = {}

    max_lanes = limits.get("max_active_lanes")
    if not isinstance(max_lanes, int) or isinstance(max_lanes, bool) or max_lanes < 1:
        v.error("limits.max_active_lanes must be a positive integer")
        max_lanes = 0

    max_heavy = limits.get("max_heavy_processes")
    if not isinstance(max_heavy, int) or isinstance(max_heavy, bool) or max_heavy < 1:
        v.error("limits.max_heavy_processes must be a positive integer")

    nodes = data.get("nodes")
    if not isinstance(nodes, dict):
        v.error("nodes must be an object keyed by issue number")
        return v

    normalized: dict[str, dict[str, Any]] = {}
    for raw_id, raw_node in nodes.items():
        try:
            node_id = as_issue_id(raw_id)
        except ValueError as exc:
            v.error(f"node key {raw_id!r}: {exc}")
            continue
        if node_id in normalized:
            v.error(f"duplicate normalized node id: {node_id}")
            continue
        if not isinstance(raw_node, dict):
            v.error(f"node {node_id} must be an object")
            continue
        normalized[node_id] = raw_node

    branch_owner: dict[str, str] = {}
    pr_owner: dict[int, str] = {}
    graph: dict[str, list[str]] = {node_id: [] for node_id in normalized}
    validated_predecessors: dict[str, list[str]] = {
        node_id: [] for node_id in normalized
    }
    active: list[str] = []

    for node_id, node in normalized.items():
        state = node.get("state")
        if not isinstance(state, str) or state not in STATES:
            v.error(f"node {node_id}: unrecognized state {state!r}")

        state_is_active = isinstance(state, str) and state in ACTIVE_STATES
        is_active = node.get("active_lane", state_is_active)
        if not isinstance(is_active, bool):
            v.error(f"node {node_id}: active_lane must be boolean when present")
        elif is_active:
            active.append(node_id)

        branch = node.get("branch")
        if branch is not None:
            if not isinstance(branch, str) or not branch:
                v.error(f"node {node_id}: branch must be a non-empty string or null")
            elif branch in branch_owner:
                v.error(
                    f"nodes {branch_owner[branch]} and {node_id} share branch {branch!r}"
                )
            else:
                branch_owner[branch] = node_id

        pr = node.get("pr")
        if pr is not None:
            if not isinstance(pr, int) or isinstance(pr, bool) or pr <= 0:
                v.error(f"node {node_id}: pr must be a positive integer or null")
            elif pr in pr_owner:
                v.error(f"nodes {pr_owner[pr]} and {node_id} share PR #{pr}")
            else:
                pr_owner[pr] = node_id

        predecessors = node.get("predecessors", [])
        if not isinstance(predecessors, list):
            v.error(f"node {node_id}: predecessors must be an array")
            predecessors = []

        for pred_raw in predecessors:
            try:
                pred = as_issue_id(pred_raw)
            except ValueError as exc:
                v.error(f"node {node_id}: predecessor {exc}")
                continue
            if pred not in normalized:
                v.error(
                    f"node {node_id}: predecessor {pred} is missing from nodes; "
                    "include completed/external graph nodes in state"
                )
                continue
            validated_predecessors[node_id].append(pred)
            graph[pred].append(node_id)

        for field in ("base_sha", "head_sha", "merge_sha"):
            value = node.get(field)
            if value is not None and not is_full_sha(value):
                v.error(
                    f"node {node_id}: {field} must be an exact 40- or "
                    "64-character hexadecimal commit SHA"
                )

        if state == "merged":
            if pr is None:
                v.error(f"node {node_id}: merged node missing pr")
            for field in ("head_sha", "merge_sha"):
                if not is_full_sha(node.get(field)):
                    v.error(
                        f"node {node_id}: merged node missing valid {field}"
                    )
        elif node.get("merge_sha") is not None:
            v.warn(f"node {node_id}: non-merged node has merge_sha")

        node_head = node.get("head_sha")
        for evidence_name in ("ci", "review"):
            evidence = node.get(evidence_name)
            if evidence is None:
                continue
            if not isinstance(evidence, dict):
                v.error(f"node {node_id}: {evidence_name} must be an object or null")
                continue
            evidence_head = evidence.get("head_sha")
            if not isinstance(evidence_head, str) or not evidence_head:
                v.error(
                    f"node {node_id}: {evidence_name} evidence must record head_sha"
                )
            elif not isinstance(node_head, str) or not node_head:
                v.error(
                    f"node {node_id}: {evidence_name} evidence exists but node head_sha is missing"
                )
            elif evidence_head != node_head:
                v.error(
                    f"node {node_id}: stale {evidence_name} evidence for {evidence_head}; "
                    f"current head is {node_head}"
                )

        tests = node.get("tests")
        if tests is not None:
            if not isinstance(tests, list):
                v.error(f"node {node_id}: tests must be an array when present")
            else:
                for index, test in enumerate(tests):
                    if not isinstance(test, dict):
                        v.error(f"node {node_id}: tests[{index}] must be an object")
                        continue
                    test_head = test.get("head_sha")
                    if not isinstance(test_head, str) or not test_head:
                        v.error(
                            f"node {node_id}: tests[{index}] must record head_sha"
                        )
                    elif not isinstance(node_head, str) or not node_head:
                        v.error(
                            f"node {node_id}: test evidence exists but node head_sha is missing"
                        )
                    elif test_head != node_head:
                        v.error(
                            f"node {node_id}: stale tests[{index}] evidence for {test_head}; "
                            f"current head is {node_head}"
                        )

    if max_lanes and len(active) > max_lanes:
        v.error(
            f"active lanes {active} exceed max_active_lanes={max_lanes}"
        )

    # Cycle detection over predecessor -> successor edges.
    color: dict[str, int] = {node_id: 0 for node_id in normalized}
    stack: list[str] = []

    def visit(node_id: str) -> None:
        color[node_id] = 1
        stack.append(node_id)
        for successor in graph[node_id]:
            if color[successor] == 0:
                visit(successor)
            elif color[successor] == 1:
                start = stack.index(successor)
                cycle = stack[start:] + [successor]
                v.error("dependency cycle: " + " -> ".join(cycle))
        stack.pop()
        color[node_id] = 2

    for node_id in normalized:
        if color[node_id] == 0:
            visit(node_id)

    for node_id, node in normalized.items():
        if node.get("state") != "ready":
            continue
        for pred in validated_predecessors[node_id]:
            predecessor = normalized[pred]
            pred_state = predecessor.get("state")
            if pred_state != "merged":
                v.error(
                    f"ready node {node_id} predecessor {pred} "
                    f"is {pred_state!r}, not merged"
                )

    dispatchable = data.get("dispatchable_now", [])
    if not isinstance(dispatchable, list):
        v.error("dispatchable_now must be an array")
        dispatchable = []

    for raw_id in dispatchable:
        try:
            node_id = as_issue_id(raw_id)
        except ValueError as exc:
            v.error(f"dispatchable_now: {exc}")
            continue
        node = normalized.get(node_id)
        if node is None:
            v.error(f"dispatchable node {node_id} is missing from nodes")
            continue
        if node.get("state") != "ready":
            v.error(
                f"dispatchable node {node_id} must have state 'ready', "
                f"found {node.get('state')!r}"
            )

    for list_name in ("review_or_ci_pending", "fix_needed", "blocked"):
        value = data.get(list_name, [])
        if not isinstance(value, list):
            v.error(f"{list_name} must be an array")
            continue
        for raw_id in value:
            try:
                node_id = as_issue_id(raw_id)
            except ValueError as exc:
                v.error(f"{list_name}: {exc}")
                continue
            if node_id not in normalized:
                v.error(f"{list_name} references missing node {node_id}")

    return v


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, help="raw JSON or Markdown state file")
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the validation result as JSON",
    )
    args = parser.parse_args()

    try:
        data = extract_data(args.path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {"ok": False, "errors": [str(exc)], "warnings": []}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = validate(data)
    payload = {
        "ok": not result.errors,
        "errors": result.errors,
        "warnings": result.warnings,
        "node_count": len(data.get("nodes", {}))
        if isinstance(data.get("nodes"), dict)
        else 0,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for warning in result.warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        if not result.errors:
            print(
                f"graph state valid: {payload['node_count']} nodes, "
                f"schema {SCHEMA}"
            )

    return 0 if not result.errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
