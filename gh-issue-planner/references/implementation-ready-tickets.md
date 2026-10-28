# Implementation-Ready Tickets

Use when drafting or applying implementation issues, or reviewing whether an
existing ticket is ready for an implementer. This is a body-content contract,
not a requirement for another tracker, report, agent, or approval ceremony.
Keep requirements proportional: a small edit may need only a few precise
sentences; an architectural deletion needs an inventory and explicit contracts.

## Self-Contained Execution Contract

The owning issue body must contain the consequential instructions. Links supply
source evidence and shared policy; they must not hide the actual edit plan in
chat history, inaccessible local files, or an unverified advisor proposal.

Record the repository and audited revision, actual public entry points and
selected implementation, and these details wherever relevant:

- **Required behavior:** inputs, defaults and eligibility; successful results;
  rejected/unsupported cases and error contract; ordering, state transitions,
  ownership and side effects. Name the boundary before which validation must
  finish. Include mixed valid/invalid requests, persisted input, fallback and
  mutation/reopen cases when they change the outcome.
- **Edit map:** exact existing paths and symbols/sections, the action at each,
  the replacement or retained consumer, and the invariant/check protecting it.
  Label proposed new files/symbols as new; do not invent existing paths. Group
  explicitly enumerated files only when they have the same action. A broad glob
  is a discovery aid, not a deletion instruction or complete inventory.
- **Concrete tasks:** an implementable order through the existing seam, covering
  callers, validation, shared helpers/state, adapters and generated sources,
  failure cleanup, tests and docs. State required data/control-flow decisions;
  use short pseudocode only where it removes a consequential ambiguity. Do not
  prescribe every local variable or pretend a speculative patch is verified.
- **Validation:** name existing test files/cases or clearly labelled new cases,
  fixture/configuration, required assertions and intended pre-change failure
  or characterized-refactor exception. Supply verified commands and working
  directory for the initial check and affected suites/harnesses, plus expected
  pass/fail observables. Add the applicable performance contract and repo merge
  gates; "run tests" and "no regressions" alone are not acceptance evidence.
- **Completion and decisions:** say what output closes the packet, who accepts
  it, which dependencies consume accepted decisions versus merged code, and
  what remains unresolved. Replace phrases such as "where appropriate" or
  "handle compatibility" with a selected rule, a bounded decision and owner,
  or an explicit non-goal. If a consequential design choice is still unknown,
  do not label the dependent implementation ready.

For repeated surfaces, a compact body table is useful:

| Path / symbol at revision | Action and required result | Consumer or invariant to preserve | Acceptance check |
| --- | --- | --- | --- |
| Exact existing path and symbol | Change, extract, migrate, remove or retain; what the edit accomplishes | Named caller/contract | Named test/observable |

Keep shared gate ownership singular. A child may link a parent's common review
policy, but it still carries its own technical actions and acceptance criteria.
Deferred feature tickets state their gap, activation decision and expected
public contract; refresh their detailed edit maps when selected rather than
inventing a distant implementation now.

## Removal And Retirement Inventory

For "remove all", backend retirement, API deletion, or a broad replacement,
publish a source-pinned inventory in the issue body before calling the packet
implementation-ready. Inspect references and actual callers, including aliases,
registration/dispatch, flags/defaults, persisted/wire decoders, generated output,
tests, examples, benchmark producers and result validators. Searching only the
deprecated name is not proof of completeness.

Assign each discovered target a concrete disposition:

| Disposition | Required instruction |
| --- | --- |
| Delete | Exact file or symbols to remove, caller disposition and prerequisite proving no retained consumer needs them. Distinguish whole-file deletion from removal of one branch. |
| Extract, then delete | Specific shared primitives and retained consumers; intended internal destination/contract; proof to obtain before deleting the obsolete owner. Do not hide the entire retired engine behind a new name. |
| Migrate | Existing caller, new public/shared entry point and behavior/ownership differences; unsupported shapes must have the selected error or deferred contract. |
| Keep | Specific modern/shared behavior or historical evidence that survives and why; identify which obsolete branches within a shared file still go. |

Include the runtime code and its coupled tests/docs/harnesses. State which
positive legacy fixtures disappear, which assertions move to the replacement,
and which negative rejection/recovery tests are required. Removing a test is not
proof that its still-required invariant holds elsewhere. Preserve authoritative
sources when regenerating derived files. Do not accidentally delete a newer
implementation merely because it shares a type name or algorithm with the old one.

Define external and stored behavior explicitly: removal of selectors/aliases,
unsupported input errors, no-effect admission boundaries, reserved numeric tags,
old persisted data/replay/reopen, and fallback prohibition where applicable.
Compatibility or migration is a product decision, not an automatic requirement.
Deleting active code does not authorize deleting user data or rewriting Git
history. State any approved historical-artifact exception separately.

Require an end inventory at the implemented revision: all initial targets and
newly discovered related paths have a disposition; every old caller is migrated,
removed or rejected; no reachable retired implementation/default/fallback or
positive fixture asserting continued execution of the retired backend remains;
retained replacement behavior passes its checks. Inventoried fixtures for an
accepted migration/compatibility contract or retained shared behavior may remain
with their consumer and justification; they must not silently keep the old backend.
Name the reference searches and build/call-path checks. Any allowed remaining
identifier must have a specific reason and location, such as a negative test,
reserved-tag explanation or immutable historical artifact. A zero-text-match
claim is inappropriate when these are deliberately retained; a renamed or dead
copy of the full engine does not count as removal.

For a large inventory, use grouped explicit paths or collapsible sections in the
body. A versioned supplemental manifest can hold repetitive detail, but the body
must still give each affected area its concrete actions, shared-code boundaries,
completion rules and authoritative manifest identity. Never make a local-only
path the implementer's sole access to required instructions.

## Revision During Implementation

Treat the file map as verified at a stated revision, not as a permanent patch.
Make the outcome, supported/unsupported behavior, preservation requirements and
acceptance guards explicit; identify provisional mechanics separately.

During authorized execution, new callers, source drift, shared-code dependencies
or failed evidence can require a revised plan. The assigned executor may adjust
in-scope local mechanics and inventory without asking permission for each file;
the coordinator owns changed shared contracts, ownership and graph edges. Update
the authoritative issue body and affected downstream bodies/edges before dependent
work relies on the changed plan. Record the finding/source, old-to-new action,
reason, preserved obligations and any invalidated evidence. Keep history as
history, not as contradictory active instructions.

If a deletion target turns out to contain required shared code, replace the row
with extraction/preservation tasks and their proof; do not obey the stale list
blindly. If another file owns the same retired behavior, add it and its caller
disposition. Ordinary discovery is not a scope escape. Split a packet only for
an actual ownership/contract boundary or independently necessary deliverable.

A changed goal, weakened acceptance guard, new unsupported capability, or external
action beyond authorization needs the appropriate decision authority; identify
the specific change and keep independent work moving. Evidence does not grant
permission to silently reduce the outcome. In inspect/read-only mode, propose
revisions rather than applying them; a prior halt still prohibits implementation.

## Readiness Review

Before publishing an implementation-ready claim, read the ticket as an executor
who has no conversation history. Can they locate the exact source, start a useful
test/edit, distinguish required decisions from choices, handle relevant error and
state boundaries, protect shared code, and tell when the packet is complete?
Check that each task has an observable exit and each retirement target has a
disposition. Verify paths, symbols and commands against the audited revision;
label unexecuted commands and proposed test names honestly.

For a complex packet or an explicit implementability request, a bounded independent
read-through can improve this check. Give the reviewer the actual issue body and
named repository/policies, not hidden intended answers or chat context. Ask for
their first actions, consequential unresolved decisions and missing acceptance
criteria. Fix substantive ambiguity or mark its affected work unready. This is
not a mandatory extra reviewer/model or a claim that implementation has run.
