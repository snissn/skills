# Report Templates

## Direct analytic result

```markdown
Disposition: <exact scoped disposition>

Commit: `<sha>` — `<subject>`

Artifacts:
- `<path>` — <role>
- `<path>` — <role>

Independent review:
- reviewer: <agent or human identity>
- reviewed base: `<sha>`
- candidate manifest: `<manifest sha256>`
- reviewed artifact set: <paths and file hashes>
- disposition: <ACCEPT/BLOCK/FAIL and decisive reason>

Validation:
- `<command>` — PASS: <exact result>
- `<command>` — PASS: <exact result>

Inference:
<what is established>

Not inferred:
<important stronger claims that remain open>

Graph:
- issue <number> <closed/open and why>
- parent dependencies <updated/unchanged>
- next task: <number and load-bearing question>

Scientific execution: none.
```

## Frozen scientific execution

```markdown
Freeze commit: `<sha>`
Result commit/artifact: `<sha or path>`

engineering_status: <status>
execution_validity: <status>
protocol_verdict: <verdict or unavailable>
scientific_inference: <scoped inference>

Comparator persistence:
- started: <count>
- completed: <count>
- atomically persisted: <count>

Defects or incidents:
- <none or exact infrastructure defect>

No stronger inference:
- <family no-go, empirical completion, etc.>
```

## Scoped failure

```markdown
Disposition: FAIL <stage or provider> — SELECTED REALIZATION ONLY

Exact obstruction:
<first missing or contradictory mathematical object>

Surviving results:
- <positive lemma>
- <positive control or reusable bound>

Scope:
- not a family no-go;
- frozen predecessors remain valid;
- no scientific execution occurred unless stated otherwise.

Architecture review:
<smallest concrete repair, new identity if required, and graph edge>
```

## GitHub issue closure comment

```markdown
## Disposition

Closed by `<sha>` with:

`<exact verdict>`

### Evidence

- <artifact and result>
- <independent review>
- <validation>

### Scientific inference

<precise scoped meaning>

### Not inferred

- <stronger claim 1>
- <stronger claim 2>

### Graph handoff

<next dependency or bounded architecture repair>
```
