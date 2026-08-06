# Scientific portfolio board schema

A repository may use a stricter schema. The minimum recommended shape is:

```json
{
  "schema_version": 1,
  "scope": "PROGRAM_SCOPE",
  "snapshot_date": "YYYY-MM-DD",
  "limits": {
    "active_scientific_workstreams": 3,
    "active_maintenance_workstreams": 1
  },
  "occupying_statuses": [
    "ACTIVE",
    "REVIEW_OR_CI",
    "FIX_NEEDED"
  ],
  "allowed_statuses": [
    "ACTIVE",
    "REVIEW_OR_CI",
    "FIX_NEEDED",
    "BLOCKED_SCIENTIFIC_REDESIGN",
    "PARKED",
    "MAINTENANCE",
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
    "blocked_or_parked_scientific_writes_allowed": false,
    "maintenance_uses_separate_slot": true
  },
  "workstreams": [
    {
      "id": "active-program",
      "class": "science",
      "status": "ACTIVE",
      "owner": "issue-123",
      "issues": [123],
      "prs": [456],
      "load_bearing_question": "One bounded question.",
      "next_action": "One exact next action.",
      "blocked_descendants": [124]
    }
  ],
  "nonactive_workstreams": [
    {
      "id": "parked-program",
      "class": "science",
      "status": "PARKED",
      "owner": "issue-200",
      "issues": [200],
      "prs": [],
      "scientific_writes_allowed": false,
      "reason": "Why the program is not active.",
      "next_action": "Exact reactivation condition."
    }
  ]
}
```

## Semantics

`workstreams` contains slot-occupying entries only. Their status must be one of
the declared occupying statuses.

`nonactive_workstreams` contains blocked, parked, maintenance-only, deferred,
superseded, or completed entries. They should explicitly set
`scientific_writes_allowed` to `false` unless repository policy defines a
narrower non-scientific exception.

A workstream may contain several issues and PRs when they form one parent
program and coupled contract. The board should not be used to hide multiple
independent scientific decisions under one identifier.

The board records authorization and sequencing. Live GitHub remains the source
of truth for exact heads, CI, review threads, merges, and issue state.
