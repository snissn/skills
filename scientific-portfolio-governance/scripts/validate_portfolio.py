#!/usr/bin/env python3
"""Validate a generic bounded scientific portfolio JSON board."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_STATUSES = {
    "ACTIVE",
    "REVIEW_OR_CI",
    "FIX_NEEDED",
    "BLOCKED_SCIENTIFIC_REDESIGN",
    "PARKED",
    "MAINTENANCE",
    "DEFERRED_NARROWED",
    "SUPERSEDED",
    "COMPLETED",
}
DEFAULT_OCCUPYING = {"ACTIVE", "REVIEW_OR_CI", "FIX_NEEDED"}
REQUIRED_RULES = {
    "one_scientific_decision_per_pr": True,
    "workflow_generated_scientific_writes_forbidden": True,
    "exact_head_identity_required": True,
    "renewed_review_after_scientific_edit_required": True,
    "claim_changing_findings_only_after_default_repair_round": True,
    "downstream_requires_merged_positive_authority": True,
    "blocked_or_parked_scientific_writes_allowed": False,
    "maintenance_uses_separate_slot": True,
}


class BoardError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BoardError(message)


def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise BoardError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)
    require(isinstance(data, dict), "board must be a JSON object")
    return data


def nonempty(value: Any, field: str) -> str:
    require(isinstance(value, str) and value.strip(), f"{field} must be nonempty text")
    return value


def refs(value: Any, field: str) -> list[int | str]:
    require(isinstance(value, list), f"{field} must be a list")
    require(
        all((type(item) is int and item > 0) or (isinstance(item, str) and item.strip()) for item in value),
        f"{field} must contain positive integers or nonempty strings",
    )
    require(len(value) == len(set(value)), f"{field} contains duplicates")
    return value


def validate_entry(entry: Any, *, active: bool, occupying: set[str], allowed: set[str]) -> None:
    require(isinstance(entry, dict), "workstream entry must be an object")
    lane_id = nonempty(entry.get("id"), "id")
    require(entry.get("class") in {"science", "maintenance"}, f"{lane_id}: invalid class")
    status = entry.get("status")
    require(status in allowed, f"{lane_id}: invalid status {status}")
    nonempty(entry.get("owner"), f"{lane_id}.owner")
    refs(entry.get("issues", []), f"{lane_id}.issues")
    refs(entry.get("prs", []), f"{lane_id}.prs")
    nonempty(entry.get("next_action"), f"{lane_id}.next_action")

    if active:
        require(status in occupying, f"{lane_id}: active entry does not occupy a slot")
        nonempty(entry.get("load_bearing_question"), f"{lane_id}.load_bearing_question")
        refs(entry.get("blocked_descendants", []), f"{lane_id}.blocked_descendants")
    else:
        require(status not in occupying, f"{lane_id}: nonactive entry has an occupying status")
        require(entry.get("scientific_writes_allowed") is False, f"{lane_id}: nonactive entry must forbid scientific writes")
        nonempty(entry.get("reason"), f"{lane_id}.reason")


def validate(data: dict[str, Any], max_science: int | None, max_maintenance: int | None) -> dict[str, int]:
    require(data.get("schema_version") == 1, "schema_version must be 1")
    nonempty(data.get("scope"), "scope")
    nonempty(data.get("snapshot_date"), "snapshot_date")

    allowed = set(data.get("allowed_statuses", []))
    occupying = set(data.get("occupying_statuses", []))
    require(allowed == DEFAULT_STATUSES, "allowed status set differs from the default contract")
    require(occupying == DEFAULT_OCCUPYING, "occupying status set differs from the default contract")
    require(data.get("rules") == REQUIRED_RULES, "required operating rules changed")

    limits = data.get("limits")
    require(isinstance(limits, dict), "limits must be an object")
    science_limit = limits.get("active_scientific_workstreams")
    maintenance_limit = limits.get("active_maintenance_workstreams")
    require(type(science_limit) is int and science_limit >= 0, "invalid science limit")
    require(type(maintenance_limit) is int and maintenance_limit >= 0, "invalid maintenance limit")
    if max_science is not None:
        require(science_limit <= max_science, "board science limit exceeds command-line maximum")
    if max_maintenance is not None:
        require(maintenance_limit <= max_maintenance, "board maintenance limit exceeds command-line maximum")

    active = data.get("workstreams")
    nonactive = data.get("nonactive_workstreams")
    require(isinstance(active, list), "workstreams must be a list")
    require(isinstance(nonactive, list), "nonactive_workstreams must be a list")
    for entry in active:
        validate_entry(entry, active=True, occupying=occupying, allowed=allowed)
    for entry in nonactive:
        validate_entry(entry, active=False, occupying=occupying, allowed=allowed)

    ids = [entry["id"] for entry in [*active, *nonactive]]
    require(len(ids) == len(set(ids)), "duplicate workstream id")

    science_active = sum(entry["class"] == "science" for entry in active)
    maintenance_active = sum(entry["class"] == "maintenance" for entry in active)
    require(science_active <= science_limit, "active scientific workstream limit exceeded")
    require(maintenance_active <= maintenance_limit, "active maintenance workstream limit exceeded")

    return {
        "scientific_active": science_active,
        "maintenance_active": maintenance_active,
        "nonactive": len(nonactive),
        "total": len(ids),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    parser.add_argument("--max-science", type=int)
    parser.add_argument("--max-maintenance", type=int)
    args = parser.parse_args()

    summary = validate(load(args.board), args.max_science, args.max_maintenance)
    print(json.dumps({"status": "PASS", **summary}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
