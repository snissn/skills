# GitHub Actions Fallback for Python Validation

Use this fallback when a required deterministic Python validator cannot be run in the local environment because Python, dependencies, filesystem permissions, process execution, or the local sandbox are unavailable or blocked.

The fallback is an execution environment substitution, not a reduction of the scientific burden.

## Eligible work

GitHub Actions is an appropriate fallback for:

- Python compilation and import checks;
- deterministic repository, ledger, schema, source-hash, and graph validators;
- non-decisive symbolic recomputations whose exact inputs are committed;
- unit, mutation, representation-invariance, and negative-control tests;
- execution-only qualification checks that do not start a protected scientific trial.

Do not silently move a decision-bearing scientific execution to CI. A frozen comparator run remains subject to the workflow's review, qualification, trial-start, persistence, replay, and disposition rules.

## Required repository workflow

The repository-owned workflow should:

1. trigger on `push` and `pull_request` for issue-scoped branches;
2. expose `workflow_dispatch` once the workflow exists on the default branch;
3. use least-privilege permissions, normally `contents: read`;
4. check out the exact triggering commit;
5. print the Python version and commit SHA;
6. run the same documented commands expected locally;
7. fail the job when a validator fails;
8. preserve useful logs or artifacts with bounded retention;
9. state that structural or software validation is not mathematical proof.

A minimal pattern is:

```yaml
name: Repository Python Validators

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python --version
      - run: git rev-parse HEAD
      - run: python -m compileall -q scripts
      - run: python scripts/validate_repository.py
```

Pin third-party actions to reviewed immutable commit SHAs when repository policy requires it.

## Triggering with `gh`

Let:

```bash
workflow=repository-python-validators.yml
branch=$(git branch --show-current)
sha=$(git rev-parse HEAD)
```

When the workflow file is present on the default branch, manual dispatch is available:

```bash
gh workflow run "$workflow" --ref "$branch"
run_id=$(gh run list \
  --workflow "$workflow" \
  --branch "$branch" \
  --event workflow_dispatch \
  --limit 1 \
  --json databaseId \
  --jq '.[0].databaseId')
gh run watch "$run_id" --exit-status
```

Inspect failures with:

```bash
gh run view "$run_id" --log-failed
```

Download retained artifacts with:

```bash
gh run download "$run_id"
```

GitHub only accepts `workflow_dispatch` when the workflow file exists on the repository's default branch. Before that integration, use the workflow's `push` or `pull_request` trigger on the issue-scoped branch:

```bash
git push origin HEAD
gh run list --workflow "$workflow" --branch "$branch" --limit 5
gh run watch <run-id> --exit-status
```

Do not create empty or claim-changing commits merely to manufacture CI evidence. Use a real coherent branch commit, an existing PR synchronization event, or rerun an existing workflow attempt.

## Evidence binding

Record at least:

- repository and branch;
- exact tested commit SHA;
- workflow path and workflow-file commit SHA;
- workflow run ID and attempt number;
- event type (`push`, `pull_request`, or `workflow_dispatch`);
- Python version and runner image;
- exact commands executed;
- exit status of every decisive step;
- artifact names or log locations;
- whether the result is local validation, CI fallback validation, qualification, or a scientific execution.

A passing CI job is valid process evidence only for the committed bytes it tested. It does not review a theorem, promote a candidate, confer freeze authority, or create a scientific verdict.

## Failure classification

Separate:

- **validator failure** — the committed artifact does not satisfy the validator;
- **environment or workflow failure** — checkout, action availability, runner capacity, permissions, dependency installation, or infrastructure prevented a valid run;
- **scientific failure** — only a qualified frozen scientific execution can establish this under its declared protocol.

An environment failure is `ENGINEERING DEFECT — NO SCIENTIFIC VERDICT`. Repair the workflow or use another qualified runner, then rerun the same bound commit when the protocol permits it.
