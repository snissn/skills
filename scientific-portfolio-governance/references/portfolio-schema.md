# Scientific portfolio board schema v2

A repository may use stricter limits and additional fields. The v2 minimum
classifies work by governed authority writes.

## Root board

```json
{
  "schema_version": 2,
  "scope": "PROGRAM_SCOPE",
  "snapshot_date": "YYYY-MM-DD",
  "limits": {
    "active_authority_writing_workstreams": 3,
    "active_qualification_workstreams": 2,
    "active_maintenance_workstreams": 2
  },
  "class_slot_groups": {
    "science": "authority_writing",
    "formalization": "authority_writing",
    "qualification": "qualification",
    "maintenance": "maintenance"
  },
  "occupying_statuses": ["ACTIVE", "REVIEW_OR_CI", "FIX_NEEDED"],
  "allowed_statuses": [
    "ACTIVE",
    "REVIEW_OR_CI",
    "FIX_NEEDED",
    "BLOCKED_SCIENTIFIC_REDESIGN",
    "PARKED",
    "DEFERRED_NARROWED",
    "SUPERSEDED",
    "COMPLETED"
  ],
  "rules": {
    "one_scientific_decision_per_pr": true,
    "workflow_generated_scientific_writes_forbidden": true,
    "exact_head_identity_required": true,
    "renewed_review_after_scientific_edit_required": true,
    "claim_changing_findings_only_after_default_repair_round": true,
    "downstream_requires_merged_positive_authority": true,
    "blocked_or_parked_authority_writes_allowed": false,
    "theorem_bearing_formalization_uses_authority_slot": true,
    "qualification_may_not_change_governed_authority_bytes": true,
    "maintenance_may_not_change_governed_authority_bytes": true,
    "one_active_writer_per_authority_surface": true,
    "one_active_qualifier_per_qualified_surface": true,
    "path_disjoint_parallelism_allowed": true,
    "governance_transitions_do_not_occupy_slots": true,
    "reconciliation_is_surface_local_not_global": true
  },
  "workstreams": [],
  "nonactive_workstreams": []
}
```

Every board must retain all five nonauthorizing statuses:
`BLOCKED_SCIENTIFIC_REDESIGN`, `PARKED`, `DEFERRED_NARROWED`,
`SUPERSEDED`, and `COMPLETED`. A repository may narrow its allowed occupying
statuses but may not remove the states needed to represent nonauthorization and
terminal provenance.

A modular board may replace the two inline arrays with:

```json
{
  "workstream_files": {
    "active": "PORTFOLIO.active.json",
    "nonactive": "PORTFOLIO.nonactive.json"
  }
}
```

Paths are resolved relative to the root board. The validator also accepts a
repository-prefixed path by searching the root board's ancestor directories.
Absolute paths and paths containing `..` are rejected.

## Active authority-writing entry

```json
{
  "id": "theorem-program",
  "class": "formalization",
  "slot_group": "authority_writing",
  "status": "ACTIVE",
  "owner": "issue-1",
  "issues": [1],
  "prs": [],
  "scientific_writes_allowed": true,
  "theorem_writes_allowed": true,
  "governed_authority_bytes_mutable": true,
  "load_bearing_question": "One bounded theorem question.",
  "next_action": "One exact constructor action.",
  "blocked_descendants": [2],
  "owned_paths": ["proof/package/"],
  "authority_surface": "proof/package/",
  "concurrency_key": "authority:theorem-program"
}
```

`science` has the same write flags and slot group.

## Active qualification entry

```json
{
  "id": "qualification-program",
  "class": "qualification",
  "slot_group": "qualification",
  "status": "ACTIVE",
  "owner": "issue-3",
  "issues": [3],
  "prs": [],
  "scientific_writes_allowed": false,
  "theorem_writes_allowed": false,
  "governed_authority_bytes_mutable": false,
  "source_repairs_allowed": false,
  "load_bearing_question": "Qualify immutable reviewed bytes.",
  "next_action": "Run exact-byte qualification.",
  "blocked_descendants": [4],
  "owned_paths": ["qualification/"],
  "qualified_surfaces": ["source:merge:manifest"],
  "frozen_inputs": [
    {
      "issue": 1,
      "pr": 5,
      "merge": "0123456789abcdef",
      "manifest": "abcdef0123456789",
      "mutable": false
    }
  ],
  "concurrency_key": "qualification:source"
}
```

`qualified_surfaces` and `frozen_inputs` are ordered one-to-one lists of equal
length. Each surface label at index `i` names the immutable input at index `i`.
The canonical qualified identity is the tuple:

```text
(issue, PR, merge, manifest)
```

That canonical identity must be globally unique across active qualification
lanes even when two lanes use different human-readable surface labels. A label
change cannot create a second lawful qualifier for the same exact frozen input.

## Active maintenance entry

Maintenance uses `slot_group: maintenance`, all governed write flags `false`,
and a nonempty `maintenance_surface`.

## Nonactive entries

Every nonactive entry must have a nonoccupying status, all governed write flags
`false`, a reason, and an exact reactivation or terminal action.

## Ownership and path semantics

Issue and PR ownership is globally unique across inline or modular rosters.
Concurrency keys and active authority or qualification surfaces are unique.

Owned paths must be repository-relative and pairwise nonoverlapping across
active workstreams. Equality, ancestor, and descendant collisions are all
forbidden. For example, active ownership of both `proof/` and
`proof/package/` is invalid.

## Semantics

- `science` and `formalization` share the authority-writing cap.
- `qualification` and `maintenance` have separate caps and may not mutate
  governed authority.
- one active writer exists per authority surface.
- one active qualifier exists per human-readable qualified surface and per
  canonical frozen-input identity.
- live GitHub remains authoritative for exact heads, CI, reviews, merges, and
  issue state; the board controls authorization and slot allocation.
