---
name: scientific-portfolio-governance
description: Project-manage a scientific repository with a bounded active-workstream portfolio, explicit lane statuses, one scientific decision per PR, exact-head review and CI identity, no workflow-generated scientific revisions, and merged-authority dependency gates. Use when the user asks what scientific lanes are active, wants lanes parked or activated, asks to impose WIP limits, requests a portfolio board, or asks to reconcile many scientific issues and PRs before further construction.
---

# Scientific Portfolio Governance

## Purpose

Use this skill to control the number and shape of active scientific workstreams
before applying theorem-construction, issue-graph, review, CI, or merge
workflows. It governs portfolio state. It does not decide the mathematics or
replace the repository's scientific review policy.

Compose with:

- `scientific-mainline-workflow` for theorem, model, scientific decision, and
  exact-candidate work inside an active lane;
- `gpt56-pro-issue-graph-executor` for dependency-graph execution inside the
  available portfolio slots; and
- repository-specific build, formalization, or domain skills as required.

Repository-local `AGENTS.md`, board files, issue trackers, and explicit user
instructions override the defaults below when they are stricter.

## Default limits

Absent repository-specific policy, allow at most:

- three active scientific workstreams; and
- one active maintenance workstream.

A workstream occupies a slot while its status is `ACTIVE`, `REVIEW_OR_CI`, or
`FIX_NEEDED`. Several issues may share one workstream when they belong to one
parent theorem program and one coupled contract surface. Do not count children
as separate lanes merely to bypass the cap.

A lane waiting on hosted CI or external review remains one workstream but need
not monopolize local implementation capacity. Work on another already-active
ready lane and return at a deliberate synchronization point.

## Status taxonomy

Use one repository-defined status when available. Otherwise use:

- `ACTIVE`: bounded scientific construction is authorized now;
- `REVIEW_OR_CI`: only exact-head review or CI is pending;
- `FIX_NEEDED`: one bounded claim-changing or evidence-path repair is active;
- `BLOCKED_SCIENTIFIC_REDESIGN`: preserve and redesign, but make no new
  scientific candidate commits to the current identity;
- `PARKED`: no implementation or review-fix work is authorized;
- `MAINTENANCE`: engineering-only work with no theorem or claim change;
- `DEFERRED_NARROWED`: a named bounded obligation survives but broad work is
  prohibited;
- `SUPERSEDED`: preserve provenance and extract reusable evidence only;
- `COMPLETED`: a reviewed scoped disposition is merged and no successor opens
  automatically.

Blocked, parked, maintenance-only, deferred, superseded, and completed entries
must state whether scientific writes are forbidden. Default to forbidden.

## Startup reconciliation

1. Resolve the repository and current default-branch SHA through the connected
   GitHub adapter.
2. Read root and nested `AGENTS.md` files that apply to candidate paths.
3. Locate repository portfolio files, commonly named `SCIENTIFIC-PORTFOLIO`,
   `STAGE3-PORTFOLIO`, `PROGRAM-BOARD`, or similar.
4. Read parent issues, active children, open PRs, latest comments, exact heads,
   CI, and review threads.
5. Reconcile live state against the checked-in board. Live GitHub wins for exact
   branch, PR, CI, and merge facts. The board wins for authorized portfolio
   status and slot allocation.
6. When board and live state disagree, stop scientific writes and publish a
   narrow governance reconciliation before resuming construction.
7. Count occupied science and maintenance slots and identify the critical path.

Do not infer active work merely from an open issue or PR. A lane is active only
when the board or an explicit repository authority says implementation,
review-fix, or merge work is authorized.

## Activation gate

A new or resumed scientific workstream may occupy a slot only after recording:

```text
workstream_id:
portfolio_status:
owner:
parent_gate:
load_bearing_question:
active_issues:
active_prs:
predecessors:
blocked_descendants:
exact_next_action:
displaced_or_vacant_slot:
```

Require merged positive predecessor authority for descendants unless a reviewed
repository graph amendment defines a new identity. An open PR, diagnostic
packet, successful local run, constructor handoff, or git-mergeable state is not
merged authority.

When the portfolio is full, finish, park, block, supersede, or complete an
existing workstream before activating another. Do not silently exceed the cap.

## One scientific decision per PR

A scientific PR should own one scientific identity and one decision surface.
Separate by default:

1. ontology, state space, action, theorem, or obstruction construction;
2. validator, runtime, or execution-only qualification engineering;
3. branch coordination, lease, repair, or publication automation; and
4. downstream synthesis or parent acceptance.

A combined PR is acceptable only when one exact independent review can
adjudicate the entire surface as one indivisible claim and repository policy
explicitly allows it. Large construction plus validator architecture plus
automated repair publishers is a split signal, even when all files share one
issue number.

When a current PR violates this rule, do not keep appending repairs. Preserve
its head, mark it `BLOCKED_SCIENTIFIC_REDESIGN`, and define narrow replacement
identities with explicit stack contracts.

## No workflow-generated scientific revisions

Automation may validate pre-existing candidate bytes, reproduce deterministic
manifests for comparison, run bounded qualification, upload artifacts, post
status, or maintain a non-scientific coordination ref.

Automation must not generate, repair, commit, or push:

- Hamiltonians or equations of motion;
- state-space or ontology definitions;
- theorem or obstruction statements;
- source-authority or scientific-classification ledgers;
- candidate validators or decision predicates; or
- scientific manifests that become new branch authority.

The constructor must publish an inspectable commit first. CI is evidence about
that commit, not its author or scientific reviewer.

A workflow with write permission must have a narrow non-scientific allowlist,
fail closed on partial publication, and never rely on a token-authenticated push
that cannot retrigger required exact-head validation.

## Exact-head gate

Before review credit, readiness, or merge, verify that all of these identify the
same exact head:

- PR body or constructor handoff;
- candidate manifest or scientific digest;
- independent review disposition;
- latest-head CI and qualification; and
- merge expected-head SHA.

Any scientific edit invalidates prior scientific review and qualification.
Execution-only or representation-only changes may use a focused semantic-
equivalence review, but must still bind the new head and prove no scientific
value or decision surface changed.

GitHub's `mergeable: true` is only a git property. Never report it as scientific
merge readiness.

## Review-stop gate

For a scoped analytic theorem or construction, default to one independent review
and one batched repair. Continue only for a finding that can change the theorem,
action, state-space typing, source authority, recovery map, decision predicate,
or evidence path supporting the claim.

After the bounded repair round, defer or split:

- parser hardening for unsupported encodings;
- redundant mutation classes;
- alternative Markdown representations;
- review orchestration and review-of-review artifacts; and
- nonblocking workflow polish.

Do not expand a scientific PR indefinitely to silence automated reviewers. If a
late finding reveals a real scientific defect, block or repair within an
explicitly renewed budget. If it reveals only engineering hardening, move it to
the maintenance slot.

## Board representation

Prefer a human Markdown board plus a machine-readable JSON board. The machine
board should record:

- scope and snapshot date;
- science and maintenance limits;
- statuses that occupy slots;
- operating-rule booleans;
- active workstreams with owner, issue/PR set, load-bearing question, next
  action, and blocked descendants; and
- nonactive workstreams with status, reason, scientific-write permission, and
  exact reactivation condition.

Use [the portfolio schema](references/portfolio-schema.md) as a starting point.
Validate a compatible board with:

```sh
python3 scientific-portfolio-governance/scripts/validate_portfolio.py \
  path/to/SCIENTIFIC-PORTFOLIO.json
```

Repository-specific validators may impose stronger exact entries and human-
board cross-checks.

## Applying status to live GitHub state

A portfolio change should update the checked-in board and the owning issue or PR
in the same operation when permissions permit. Use a comment containing:

```text
portfolio_status:
workstream:
exact_head_or_merge:
scientific_writes_authorized:
next_action:
blocked_descendants:
```

Convert an implementation PR back to draft when the current identity is blocked
for redesign. Do not close it if its branch is still useful scientific
provenance. Mark superseded engineering PRs clearly and prevent their accidental
merge without deleting evidence.

## Completion and handoff

Before ending:

1. publish every board and policy change on a dedicated governance branch;
2. run the portfolio validator;
3. open a draft PR unless the user explicitly requests direct integration;
4. update affected issue or PR statuses without editing their scientific bytes;
5. report occupied and vacant slots;
6. list exactly which lanes may receive scientific writes; and
7. name the next board transition required to activate any blocked successor.

This skill manages authorization and sequencing. It does not promote a
scientific result, reopen a completed obstruction, or weaken a banked theorem.
