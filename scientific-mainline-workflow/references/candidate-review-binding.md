# Candidate Review Binding

Use this contract when an independent scientific review must authorize the
freeze and mainline integration of a pushed mutable-branch candidate.

## Candidate manifest

Generate a deterministic manifest from the explicit candidate path set:

```bash
python3 /home/mikers/.codex/skills/scientific-mainline-workflow/scripts/candidate_manifest.py \
  --repo /path/to/worktree \
  --base <candidate-base-sha> \
  --path path/to/definition.md \
  --path path/to/ledger.json \
  --path path/to/validator.py
```

The manifest binds:

- the candidate base commit;
- the worktree `HEAD`;
- the exact sorted path set;
- each file's byte count and SHA-256;
- the corresponding base and `HEAD` Git blob when present;
- one hash of the canonical manifest payload.

Generate it from a clean pushed feature-branch commit. Mutable commits before
that point are durable development provenance, not scientific authority. A
review bound to one branch commit does not cover a later scientific edit.

Pass the manifest, source paths, frozen inputs, and acceptance predicates to the
reviewer. The reviewer must return `ACCEPT`, `BLOCK`, or a scoped failure bound
to the manifest hash and candidate base.

## Two-stage review

Use an early adversarial design review to find mathematical and semantic
problems while the candidate is cheap to change. Treat its acceptance as
provisional.

After dedicated and inherited validation passes, regenerate the manifest and
ask an independent reviewer for the integration disposition on:

- the exact candidate bytes and base;
- the frozen inputs and source bindings;
- the validation commands, outcomes, and decisive hashes;
- every previously blocking finding;
- the issue exit gate and forbidden inferences.

Only this final exact-candidate `ACCEPT` authorizes the freeze and mainline
integration.
Validation does not replace scientific review, and review does not replace
validation.

## Change rule

Any change to a scientific byte, formula, source binding, predicate, tolerance,
control, or inference invalidates the prior acceptance. Commit and push the
revision on the mutable branch, regenerate the manifest, and obtain a new
review.

A representation-only or execution-only repair may use a focused semantic
review, but the repair must still demonstrate that all scientific values and
decision surfaces are unchanged.

## Base-drift rule

Immediately before integration, fetch the remote and compare the accepted base
with current `main`.

- If candidate paths, frozen inputs, or theorem dependencies changed, rebase or
  transplant the draft, rerun validation, regenerate the manifest, and obtain a
  renewed independent review.
- If the movement is demonstrably unrelated, preserve the accepted candidate
  file bytes, document the base-drift audit, rerun affected inherited checks,
  and bind the integration evidence to both manifests.

Do not infer that a clean textual merge proves scientific compatibility.

## Freeze and mainline verification

After creating the freeze commit and before mainline execution:

1. verify the committed path set is exactly the reviewed set;
2. verify every committed blob reproduces the accepted candidate SHA-256;
3. inspect the full commit diff;
4. rerun any check whose input is the committed tree rather than the mutable
   worktree;
5. confirm the remote has not advanced;
6. merge, squash, or transplant only under repository history policy;
7. if the commit identity changes, verify every scientific file hash against
   the accepted manifest;
8. push without force and verify remote `main` equals the integrated freeze.

Retain the pushed mutable branch as non-authoritative provenance. Its history
does not acquire scientific authority merely because its reviewed freeze was
integrated.

The manifest is provenance evidence, not a scientific theorem. Independent
formula derivation and substantive validation remain mandatory.

## Reviewer request template

```text
Review this pushed scientific candidate for freeze and mainline integration.

Base: <sha>
Candidate branch and HEAD: <branch> <sha>
Manifest: <sha256>
Candidate paths: <exact list>
Frozen inputs: <exact files and hashes>
Issue exit gate: <predicates>
Prior blockers: <list and claimed resolutions>
Validation evidence: <commands and exact outcomes>

Inspect the actual files and recompute load-bearing mathematics independently.
Do not edit files or rely on the constructor summary. Return ACCEPT, BLOCK, FAIL
SELECTED REALIZATION, or CLASS-LEVEL OBSTRUCTION, bound to the base and
manifest. State the exact inference boundary and surviving obligations.
```
