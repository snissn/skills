#!/usr/bin/env python3
"""Validate a bounded scientific portfolio v2 board."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

DEFAULT_LIMITS = {
    "active_authority_writing_workstreams": 3,
    "active_qualification_workstreams": 2,
    "active_maintenance_workstreams": 2,
}
CLASSES = {"science", "formalization", "qualification", "maintenance"}
CLASS_SLOT_GROUPS = {
    "science": "authority_writing",
    "formalization": "authority_writing",
    "qualification": "qualification",
    "maintenance": "maintenance",
}
OCCUPYING = {"ACTIVE", "REVIEW_OR_CI", "FIX_NEEDED"}
NONACTIVE = {
    "BLOCKED_SCIENTIFIC_REDESIGN",
    "PARKED",
    "DEFERRED_NARROWED",
    "SUPERSEDED",
    "COMPLETED",
}
DEFAULT_STATUSES = OCCUPYING | NONACTIVE
REQUIRED_RULES = {
    "one_scientific_decision_per_pr": True,
    "workflow_generated_scientific_writes_forbidden": True,
    "exact_head_identity_required": True,
    "renewed_review_after_scientific_edit_required": True,
    "claim_changing_findings_only_after_default_repair_round": True,
    "downstream_requires_merged_positive_authority": True,
    "blocked_or_parked_authority_writes_allowed": False,
    "theorem_bearing_formalization_uses_authority_slot": True,
    "qualification_may_not_change_governed_authority_bytes": True,
    "maintenance_may_not_change_governed_authority_bytes": True,
    "one_active_writer_per_authority_surface": True,
    "one_active_qualifier_per_qualified_surface": True,
    "path_disjoint_parallelism_allowed": True,
    "governance_transitions_do_not_occupy_slots": True,
    "reconciliation_is_surface_local_not_global": True,
}

FrozenIdentity = tuple[int, int, str, str]


class BoardError(RuntimeError):
    """Raised when a portfolio board violates a governance invariant."""


def require(condition: bool, message: str) -> None:
    """Raise a board error when an invariant does not hold."""
    if not condition:
        raise BoardError(message)


def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Decode a JSON object while rejecting duplicate keys."""
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise BoardError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def load_json(path: Path) -> dict[str, Any]:
    """Load one board or roster file with duplicate-key rejection."""
    data = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicates,
    )
    require(isinstance(data, dict), f"{path}: root must be a JSON object")
    return data


def nonempty(value: Any, field: str) -> str:
    """Require nonempty text."""
    require(
        isinstance(value, str) and value.strip(),
        f"{field} must be nonempty text",
    )
    return value


def refs(value: Any, field: str) -> list[int | str]:
    """Require a duplicate-free list of positive integers or nonempty strings."""
    require(isinstance(value, list), f"{field} must be a list")
    require(
        all(
            (type(item) is int and item > 0)
            or (isinstance(item, str) and item.strip())
            for item in value
        ),
        f"{field} must contain positive integers or nonempty strings",
    )
    require(len(value) == len(set(value)), f"{field} contains duplicates")
    return value


def string_list(
    value: Any,
    field: str,
    *,
    nonempty_list: bool = True,
) -> list[str]:
    """Require a duplicate-free list of nonempty strings."""
    require(isinstance(value, list), f"{field} must be a list")
    require(
        all(isinstance(item, str) and item.strip() for item in value),
        f"{field} must contain nonempty strings",
    )
    require(len(value) == len(set(value)), f"{field} contains duplicates")
    if nonempty_list:
        require(bool(value), f"{field} must not be empty")
    return value


def normalize_repo_path(value: str, field: str) -> str:
    """Normalize one repository-relative ownership path."""
    raw = nonempty(value, field).strip().replace("\\", "/")
    require(not raw.startswith("/"), f"{field} must be repository-relative")
    parts = [part for part in raw.split("/") if part not in {"", "."}]
    require(parts and ".." not in parts, f"{field} contains an invalid segment")
    return "/".join(parts)


def paths_overlap(left: str, right: str) -> bool:
    """Return whether two normalized repository paths overlap by ancestry."""
    return (
        left == right
        or left.startswith(right + "/")
        or right.startswith(left + "/")
    )


def resolve_roster(root_path: Path, value: str) -> Path:
    """Resolve a modular roster relative to the board or any board ancestor."""
    relative = Path(nonempty(value, "workstream roster path"))
    require(
        not relative.is_absolute() and ".." not in relative.parts,
        f"invalid roster path: {value}",
    )
    seen: set[Path] = set()
    for ancestor in (root_path.parent, *root_path.parents):
        candidate = ancestor / relative
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.exists():
            return candidate
    raise BoardError(f"referenced roster not found: {value}")


def materialize(path: Path) -> dict[str, Any]:
    """Load an inline board or materialize its active/nonactive roster files."""
    data = load_json(path)
    files = data.get("workstream_files")
    if files is None:
        return data
    require(isinstance(files, dict), "workstream_files must be an object")
    require(
        set(files) == {"active", "nonactive"},
        "workstream_files keys changed",
    )
    active_path = resolve_roster(
        path,
        nonempty(files.get("active"), "workstream_files.active"),
    )
    nonactive_path = resolve_roster(
        path,
        nonempty(files.get("nonactive"), "workstream_files.nonactive"),
    )
    active_data = load_json(active_path)
    nonactive_data = load_json(nonactive_path)
    require(
        active_data.get("schema_version") == 2,
        "active roster schema mismatch",
    )
    require(
        nonactive_data.get("schema_version") == 2,
        "nonactive roster schema mismatch",
    )
    require(
        set(active_data) == {"schema_version", "workstreams"},
        "active roster keys changed",
    )
    require(
        set(nonactive_data) == {"schema_version", "nonactive_workstreams"},
        "nonactive roster keys changed",
    )
    require(
        "workstreams" not in data and "nonactive_workstreams" not in data,
        "root board duplicates modular rosters",
    )
    return {
        **data,
        "workstreams": active_data["workstreams"],
        "nonactive_workstreams": nonactive_data["nonactive_workstreams"],
    }


def write_flags(
    entry: dict[str, Any],
    lane_id: str,
) -> tuple[bool, bool, bool]:
    """Read and type-check the three governed-write flags."""
    fields = (
        "scientific_writes_allowed",
        "theorem_writes_allowed",
        "governed_authority_bytes_mutable",
    )
    values: list[bool] = []
    for field in fields:
        value = entry.get(field)
        require(type(value) is bool, f"{lane_id}.{field} must be boolean")
        values.append(value)
    return values[0], values[1], values[2]


def validate_frozen_inputs(
    value: Any,
    field: str,
) -> list[FrozenIdentity]:
    """Validate immutable inputs and return their canonical identities."""
    require(
        isinstance(value, list) and value,
        f"{field} must be a nonempty list",
    )
    seen: set[FrozenIdentity] = set()
    identities: list[FrozenIdentity] = []
    for index, item in enumerate(value):
        require(
            isinstance(item, dict),
            f"{field}[{index}] must be an object",
        )
        require(
            item.get("mutable") is False,
            f"{field}[{index}] must be immutable",
        )
        for key in ("issue", "pr"):
            require(
                type(item.get(key)) is int and item[key] > 0,
                f"{field}[{index}].{key} invalid",
            )
        merge = nonempty(item.get("merge"), f"{field}[{index}].merge")
        manifest = nonempty(
            item.get("manifest"),
            f"{field}[{index}].manifest",
        )
        identity: FrozenIdentity = (
            item["issue"],
            item["pr"],
            merge,
            manifest,
        )
        require(
            identity not in seen,
            f"{field} contains duplicate frozen input",
        )
        seen.add(identity)
        identities.append(identity)
    return identities


def validate_entry(
    entry: Any,
    *,
    active: bool,
    allowed: set[str],
    occupying: set[str],
) -> None:
    """Validate one active or nonactive portfolio entry."""
    require(isinstance(entry, dict), "workstream entry must be an object")
    lane_id = nonempty(entry.get("id"), "id")
    lane_class = entry.get("class")
    require(lane_class in CLASSES, f"{lane_id}: invalid class")
    require(
        entry.get("slot_group") == CLASS_SLOT_GROUPS[lane_class],
        f"{lane_id}: class/slot-group mismatch",
    )
    status = entry.get("status")
    require(status in allowed, f"{lane_id}: invalid status {status}")
    nonempty(entry.get("owner"), f"{lane_id}.owner")
    refs(entry.get("issues", []), f"{lane_id}.issues")
    refs(entry.get("prs", []), f"{lane_id}.prs")
    nonempty(entry.get("next_action"), f"{lane_id}.next_action")
    flags = write_flags(entry, lane_id)

    if active:
        require(
            status in occupying,
            f"{lane_id}: active entry does not occupy a slot",
        )
        nonempty(
            entry.get("load_bearing_question"),
            f"{lane_id}.load_bearing_question",
        )
        refs(
            entry.get("blocked_descendants", []),
            f"{lane_id}.blocked_descendants",
        )
        owned_paths = string_list(
            entry.get("owned_paths"),
            f"{lane_id}.owned_paths",
        )
        for index, path in enumerate(owned_paths):
            normalize_repo_path(path, f"{lane_id}.owned_paths[{index}]")
        nonempty(entry.get("concurrency_key"), f"{lane_id}.concurrency_key")

        if lane_class in {"science", "formalization"}:
            require(
                flags == (True, True, True),
                f"{lane_id}: authority writer must enable all governed write flags",
            )
            nonempty(
                entry.get("authority_surface"),
                f"{lane_id}.authority_surface",
            )
        elif lane_class == "qualification":
            require(
                flags == (False, False, False),
                f"{lane_id}: qualification may not mutate governed authority",
            )
            surfaces = string_list(
                entry.get("qualified_surfaces"),
                f"{lane_id}.qualified_surfaces",
            )
            frozen = validate_frozen_inputs(
                entry.get("frozen_inputs"),
                f"{lane_id}.frozen_inputs",
            )
            require(
                len(surfaces) == len(frozen),
                f"{lane_id}: qualified surfaces must bind frozen inputs one-to-one",
            )
            require(
                entry.get("source_repairs_allowed") is False,
                f"{lane_id}: qualification may not repair source authority",
            )
        else:
            require(
                flags == (False, False, False),
                f"{lane_id}: maintenance may not mutate governed authority",
            )
            nonempty(
                entry.get("maintenance_surface"),
                f"{lane_id}.maintenance_surface",
            )
    else:
        require(
            status not in occupying,
            f"{lane_id}: nonactive entry has occupying status",
        )
        require(
            flags == (False, False, False),
            f"{lane_id}: nonactive entry must forbid governed writes",
        )
        nonempty(entry.get("reason"), f"{lane_id}.reason")


def require_unique(
    entries: Iterable[dict[str, Any]],
    field: str,
) -> None:
    """Require unique issue or PR ownership across all workstreams."""
    owners: dict[int | str, str] = {}
    for entry in entries:
        for value in entry.get(field, []):
            prior = owners.get(value)
            require(
                prior is None,
                f"{field[:-1]} {value} is owned by both {prior} and {entry['id']}",
            )
            owners[value] = entry["id"]


def validate_surfaces(active: list[dict[str, Any]]) -> None:
    """Enforce active concurrency, ownership, and qualification uniqueness."""
    keys: dict[str, str] = {}
    authority: dict[str, str] = {}
    qualified: dict[str, str] = {}
    frozen_inputs: dict[FrozenIdentity, str] = {}
    owned_paths: list[tuple[str, str]] = []

    for entry in active:
        lane_id = entry["id"]
        key = entry["concurrency_key"]
        require(
            key not in keys,
            f"concurrency key {key} has multiple active owners",
        )
        keys[key] = lane_id

        for index, path in enumerate(entry["owned_paths"]):
            normalized = normalize_repo_path(
                path,
                f"{lane_id}.owned_paths[{index}]",
            )
            for prior_path, prior_owner in owned_paths:
                require(
                    not paths_overlap(normalized, prior_path),
                    "owned paths overlap for "
                    f"{prior_owner} and {lane_id}: "
                    f"{prior_path} / {normalized}",
                )
            owned_paths.append((normalized, lane_id))

        if entry["slot_group"] == "authority_writing":
            surface = normalize_repo_path(
                entry["authority_surface"],
                f"{lane_id}.authority_surface",
            )
            require(
                surface not in authority,
                f"authority surface {surface} has multiple active writers",
            )
            authority[surface] = lane_id
        elif entry["slot_group"] == "qualification":
            surfaces = entry["qualified_surfaces"]
            identities = validate_frozen_inputs(
                entry["frozen_inputs"],
                f"{lane_id}.frozen_inputs",
            )
            require(
                len(surfaces) == len(identities),
                f"{lane_id}: qualified surfaces must bind frozen inputs one-to-one",
            )
            for surface, identity in zip(surfaces, identities, strict=True):
                require(
                    surface not in qualified,
                    f"qualified surface {surface} has multiple active qualifiers",
                )
                qualified[surface] = lane_id
                prior_owner = frozen_inputs.get(identity)
                require(
                    prior_owner is None,
                    "frozen input "
                    f"{identity} is qualified by both {prior_owner} and {lane_id}",
                )
                frozen_inputs[identity] = lane_id


def validate(
    data: dict[str, Any],
    *,
    max_authority: int = DEFAULT_LIMITS[
        "active_authority_writing_workstreams"
    ],
    max_qualification: int = DEFAULT_LIMITS[
        "active_qualification_workstreams"
    ],
    max_maintenance: int = DEFAULT_LIMITS[
        "active_maintenance_workstreams"
    ],
) -> dict[str, int]:
    """Validate a fully materialized portfolio board."""
    require(data.get("schema_version") == 2, "schema_version must be 2")
    nonempty(data.get("scope"), "scope")
    nonempty(data.get("snapshot_date"), "snapshot_date")

    class_groups = data.get("class_slot_groups")
    require(
        class_groups == CLASS_SLOT_GROUPS,
        "class/slot-group contract changed",
    )
    allowed = set(data.get("allowed_statuses", []))
    occupying = set(data.get("occupying_statuses", []))
    require(
        NONACTIVE <= allowed <= DEFAULT_STATUSES,
        "allowed status set must retain every nonactive state",
    )
    require(
        occupying == allowed & OCCUPYING,
        "occupying statuses changed active semantics",
    )

    rules = data.get("rules")
    require(isinstance(rules, dict), "rules must be an object")
    for key, expected in REQUIRED_RULES.items():
        require(
            rules.get(key) is expected,
            f"required operating rule changed: {key}",
        )

    limits = data.get("limits")
    require(isinstance(limits, dict), "limits must be an object")
    for key, default in DEFAULT_LIMITS.items():
        value = limits.get(key)
        require(type(value) is int and value >= 0, f"invalid limit: {key}")
        require(
            value <= default,
            f"board limit exceeds default maximum: {key}",
        )
    cli_limits = {
        "active_authority_writing_workstreams": max_authority,
        "active_qualification_workstreams": max_qualification,
        "active_maintenance_workstreams": max_maintenance,
    }
    for key, maximum in cli_limits.items():
        require(
            type(maximum) is int
            and 0 <= maximum <= DEFAULT_LIMITS[key],
            f"command-line maximum may only narrow default: {key}",
        )
        require(
            limits[key] <= maximum,
            f"board limit exceeds command-line maximum: {key}",
        )

    active = data.get("workstreams")
    nonactive = data.get("nonactive_workstreams")
    require(isinstance(active, list), "workstreams must be a list")
    require(
        isinstance(nonactive, list),
        "nonactive_workstreams must be a list",
    )
    for entry in active:
        validate_entry(
            entry,
            active=True,
            allowed=allowed,
            occupying=occupying,
        )
    for entry in nonactive:
        validate_entry(
            entry,
            active=False,
            allowed=allowed,
            occupying=occupying,
        )

    entries = [*active, *nonactive]
    ids = [entry["id"] for entry in entries]
    require(len(ids) == len(set(ids)), "duplicate workstream id")
    require_unique(entries, "issues")
    require_unique(entries, "prs")
    validate_surfaces(active)

    counts = {
        group: sum(entry["slot_group"] == group for entry in active)
        for group in ("authority_writing", "qualification", "maintenance")
    }
    require(
        counts["authority_writing"]
        <= limits["active_authority_writing_workstreams"],
        "authority-writing limit exceeded",
    )
    require(
        counts["qualification"]
        <= limits["active_qualification_workstreams"],
        "qualification limit exceeded",
    )
    require(
        counts["maintenance"]
        <= limits["active_maintenance_workstreams"],
        "maintenance limit exceeded",
    )

    return {
        "authority_writing_active": counts["authority_writing"],
        "qualification_active": counts["qualification"],
        "maintenance_active": counts["maintenance"],
        "nonactive": len(nonactive),
        "total": len(ids),
    }


def main() -> int:
    """Parse CLI arguments, validate the board, and emit a JSON summary."""
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    parser.add_argument(
        "--max-authority",
        type=int,
        default=DEFAULT_LIMITS["active_authority_writing_workstreams"],
    )
    parser.add_argument(
        "--max-qualification",
        type=int,
        default=DEFAULT_LIMITS["active_qualification_workstreams"],
    )
    parser.add_argument(
        "--max-maintenance",
        type=int,
        default=DEFAULT_LIMITS["active_maintenance_workstreams"],
    )
    args = parser.parse_args()
    summary = validate(
        materialize(args.board),
        max_authority=args.max_authority,
        max_qualification=args.max_qualification,
        max_maintenance=args.max_maintenance,
    )
    print(json.dumps({"status": "PASS", **summary}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
