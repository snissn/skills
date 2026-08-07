---
name: scientific-portfolio-governance
description: Project-manage a scientific repository with bounded authority-writing, qualification, and maintenance pools; explicit workstream classes and statuses; surface-local concurrency; one decision per PR; exact-head review and CI identity; no workflow-generated authority; and merged-predecessor gates. Use when the user asks what scientific lanes are active, wants lanes parked or activated, asks to impose or repair WIP limits, requests a portfolio board, or asks to reconcile scientific, formalization, qualification, and maintenance work before further construction.
---

# Scientific Portfolio Governance

## Purpose

Use this skill to control the number, authority type, and concurrency surface of
active scientific work before theorem construction, formalization,
qualification, CI, review, or merge workflows proceed. It governs authorization
and sequencing. It does not decide the mathematics or replace scientific review.

Compose with:

- `scientific-mainline-workflow` for model, theorem, or obstruction work inside
  an active `science` lane;
- proof-assistant/build skills for an active `formalization` lane;
- review or CI skills for an active `qualification` lane;
- `gpt56-pro-issue-graph-executor` for dependency-graph execution across the
  available pools; and
- repository-specific `AGENTS.md`, source-lock, review, and merge rules.

Repository-local policy overrides these defaults when it is stricter. A local
policy that is internally contradictory should be repaired by an explicit
governance transition rather than followed mechanically.

## Classify by governed writes

Classify the workstream by what authority it is allowed to create or change,
not by programming language, directory name, or labels such as `Lean`,
`review`, `integration`, or `maintenance`.

### `science`

Science creates or changes scientific authority: ontology, state space, action,
Hamiltonian, analytic theorem, obstruction, source authority, scientific
manifest, classification, reduction, recovery, preparation, probability, or
physical-interface maps.

Science occupies the `authority_writing` pool.

### `formalization`

Formalization creates or changes a public machine-checked theorem surface:
definitions, theorem statements, compiled countermodels, theorem locks, or
source-to-formalization claim boundaries.

Formalization occupies the same `authority_writing` pool as science. A proof
language does not make theorem construction maintenance.

A proof-only compiler or compatibility repair is maintenance only when public
theorem statements, mathematical definition values, theorem locks, and
scientific classifications are prospectively frozen and proven unchanged.

### `qualification`

Qualification validates and integrates exact immutable scientific or theorem
bytes. It may own adapters, deterministic manifest reproduction, source-lock
verification, CI/runtime evidence, integration metadata, and qualification
receipts.

Qualification may not alter the governed authority it qualifies. A source
defect returns to the source owner or a separately activated replacement.

Qualification occupies the `qualification` pool.

### `maintenance`

Maintenance is non-authority engineering: build/toolchain compatibility,
packaging, proof-only locked-surface repair, governance, and documentation
reconciliation.

Maintenance may not create or change governed scientific or theorem authority.
It occupies the `maintenance` pool.

## Default limits

Absent repository-specific policy, allow at most:

- three active authority-writing workstreams (`science` + `formalization`);
- two active qualification workstreams; and
- two active maintenance workstreams.

These are conservative circuit breakers, not scientific dependencies.
`ACTIVE`, `REVIEW_OR_CI`, and `FIX_NEEDED` occupy a slot. Governance-only board
transitions consume no implementation slot when they change no governed
candidate bytes.

Path-disjoint work on distinct authority or qualification surfaces may proceed
in parallel. Do not serialize unrelated programs merely because both happen to
use Lean, CI, or review tooling.

## Status taxonomy

Use one repository-defined status when available. Otherwise use:

- `ACTIVE`: bounded construction or qualification is authorized now;
- `REVIEW_OR_CI`: governed construction is frozen; exact-head review, CI, or
  merge closeout is in flight;
- `FIX_NEEDED`: one bounded claim-changing or evidence-path repair is active;
- `BLOCKED_SCIENTIFIC_REDESIGN`: preserve and redesign, but write no new
  authority to the current identity;
- `PARKED`: no implementation or review-fix work is authorized;
- `DEFERRED_NARROWED`: a named future obligation survives, but work is not
  authorized now;
- `SUPERSEDED`: preserve provenance and extract reusable evidence only;
- `COMPLETED`: a reviewed scoped disposition is merged and no successor opens
  automatically.

Class and status are orthogonal. `maintenance` and `qualification` are classes,
not statuses.

Every nonactive entry must forbid scientific writes, theorem writes, and
mutation of governed authority bytes.

## Startup reconciliation

1. Resolve the repository and default-branch SHA through the connected GitHub
   adapter.
2. Read root and nested `AGENTS.md` files applying to candidate paths.
3. Locate the human and machine portfolio boards.
4. Read parent issues, active children, open PRs, exact heads, CI, reviews, and
   latest status comments.
5. Reconcile exact live state against board authorization.
6. When they disagree, pause only the conflicting authority or qualification
   surface and publish a governance reconciliation.
7. Count the three slot groups and identify the scientific critical path.
8. Check authority surfaces, qualified surfaces, owned paths, and concurrency
   keys before declaring that two lanes can proceed in parallel.

An open issue or PR does not imply authorization. A lane is writable only when
the board or another explicit repository authority says so.

## Active-lane contract

An active authority-writing lane should record:

```text
workstream_id:
class: science | formalization
slot_group: authority_writing
portfolio_status:
owner:
parent_gate:
load_bearing_question:
active_issues:
active_prs:
owned_paths:
authority_surface:
concurrency_key:
predecessors:
blocked_descendants:
exact_next_action:
```

An active qualification lane should record:

```text
workstream_id:
class: qualification
slot_group: qualification
portfolio_status:
owner:
qualified_surfaces:
frozen_inputs:
  - issue
  - PR
  - merge
  - manifest
  - mutable: false
governed_authority_bytes_mutable: false
source_repairs_allowed: false
owned_paths:
concurrency_key:
blocked_descendants:
exact_next_action:
```

An active maintenance lane should record a bounded maintenance surface and set
all governed write flags to false.

## Surface-level concurrency

Require one active writer per authority surface and concurrency key. Require one
active qualifier per exact qualified surface.

A qualifier may coexist with an authority writer only when it binds an earlier
immutable candidate and cannot mutate the active surface. Broad ownership such
as `.github/workflows/` does not grant every workflow; each PR still needs an
exact changed-path allowlist.

Do not hide multiple independent decisions inside one workstream merely to
bypass the cap.

## Activation gate

Activate a new or resumed workstream only after recording:

```text
class and slot group
owner and parent gate
load-bearing question
issues and PRs
owned or qualified surface
concurrency key
exact predecessors or frozen inputs
blocked descendants
one exact next action
slot counts after transition
```

Require merged positive predecessor authority unless a reviewed graph amendment
names a materially different identity. Open PRs, local tests, constructor
handoffs, diagnostic packets, and git mergeability are not merged authority.

Merged predecessors do not activate successors automatically. A separate board
transition is still required, but capacity must not be used to invent a false
scientific dependency between unrelated programs.

## One decision per PR

Separate by default:

1. science or theorem-bearing formalization;
2. immutable-byte qualification and runtime engineering;
3. branch coordination, lease, or publication automation;
4. governance transition; and
5. downstream parent acceptance.

A combined PR is acceptable only when one exact independent review can
adjudicate one indivisible decision surface and repository policy allows it.

Do not append source repairs to a qualification PR or public theorem
construction to a maintenance PR. Reclassify or split first.

## No workflow-generated authority

Automation may validate pre-existing bytes, reproduce manifests, upload
artifacts, post status, or maintain a non-authority coordination ref.

Automation must not generate, repair, commit, or push scientific definitions,
theorem statements, proof definitions, source-authority ledgers,
classifications, claim-bearing validators, or scientific manifests that become
new authority.

The constructor publishes an inspectable commit first. CI is evidence about that
commit, not its author or reviewer.

## Exact-head and immutable-byte gates

Before review credit or merge, align:

- PR body or handoff;
- candidate manifest or digest;
- independent review;
- latest-head CI and qualification; and
- merge expected head or exact immutable source set.

Any governed edit invalidates prior authority review and qualification.
Execution-only or representation-only changes require a new exact-head
semantic-equivalence review.

GitHub `mergeable: true` is only a git property.

A qualification lane must fail closed when a frozen input differs from its
reviewed merge or manifest. It may repair only qualification-owned bytes.

## Review-stop gate

For one bounded authority-writing decision, default to one independent review
and one batched repair. Continue only for findings that can change the theorem,
action, state typing, source authority, recovery map, decision predicate, or
claim-bearing evidence path.

Move parser polish, redundant mutations, alternate Markdown encodings, and
review orchestration into qualification or maintenance unless they expose a
real authority defect.

## Codex quota fallback

Classify a quota, usage-limit, review-limit, rate-limit, capacity, or service
response as `CODEX_REVIEW_UNAVAILABLE_QUOTA`. It is neither acceptance nor a
finding.

When repository policy permits, use an independent read-only GPT-5.6 Pro
subagent or a documented local clean-room `LOCAL_GPT56_REVIEW`. Bind the exact
head or manifest, reviewed paths and claims, checks, findings, disposition, and
confirmation of no candidate edits.

Other CI, predecessor, branch-protection, thread-resolution, human-review, and
merge gates remain in force.

## Modular board representation

Prefer:

```text
PORTFOLIO.json             root rules and file references
PORTFOLIO.active.json      active slot-occupying workstreams
PORTFOLIO.nonactive.json   parked/completed/provenance roster
PORTFOLIO.md               human board
```

A single-file board remains valid. A modular board reduces merge contention by
allowing active scheduling changes without rewriting the completed roster.
The validator must materialize all files and enforce global ownership and slot
invariants.

Use [the v2 portfolio schema](references/portfolio-schema.md) as a starting
point. Validate with:

```sh
python3 scientific-portfolio-governance/scripts/validate_portfolio.py \
  path/to/PORTFOLIO.json
```

## Applying status to GitHub

A portfolio transition should update the board and owning issue or PR together.
Use a receipt containing:

```text
portfolio_status:
workstream:
class:
slot_group:
exact_head_or_merge:
scientific_writes_authorized:
theorem_writes_authorized:
governed_authority_bytes_mutable:
next_action:
blocked_descendants:
```

Do not edit governed source bytes merely to make status comments agree.

## Completion

Before ending:

1. publish policy and board changes on a governance branch;
2. run the validator and fail-closed mutation tests;
3. obtain exact-head governance review;
4. merge or leave a precise external gate;
5. update affected issue/PR receipts;
6. report occupied and vacant pools;
7. identify exactly which lanes may write authority, qualify frozen authority,
   or perform maintenance; and
8. name the next board transition required for every parked successor.

This skill manages authorization and sequencing. It never promotes a scientific
result or weakens a banked obstruction.
