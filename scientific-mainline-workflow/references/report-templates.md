# Report Templates

Use [the evidence scope ladder](evidence-scope-ladder.md) to report the selected
burden. Every scientific report should make clear which predicates were required
and which stronger items remain optional or deferred.

## Direct analytic result

```markdown
Disposition: <exact scoped disposition>

Evidence scope:
- level: <E0-E4>
- quantifier: <Q0-Q3>
- stability: <S0-S4>
- prepared domain: <exact domain and nonemptiness evidence>

Commit: `<sha>` — `<subject>`

Artifacts:
- `<path>` — <role>
- `<path>` — <role>

Independent review:
- reviewer: <agent or human identity>
- reviewed base: `<sha>`
- candidate manifest: `<manifest sha256>`
- reviewed artifact set: <paths and file hashes>
- reviewed NEED set: <predicates>
- disposition: <ACCEPT/BLOCK/FAIL and decisive reason>

Validation:
- `<command>` — PASS: <exact result>
- `<command>` — PASS: <exact result>

Scientific inference:
<what is established at the declared level>

Effective assumptions:
- <fixed background, finite band, selected family, horizon, etc.>

SHOULD strengthening — nonblocking:
- <item>

COULD extensions — deferred:
- <item>

Not inferred:
<important stronger claims that remain open>

Stop rule:
<why the checkpoint stops here>

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

Evidence scope:
- level: <E0-E4>
- quantifier: <Q0-Q3>
- stability: <S0-S4>
- reviewed NEED set: <predicates>

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

Effective assumptions:
- <list>

Nonblocking strengthening:
- SHOULD: <items>
- COULD: <items>

No stronger inference:
- <global regularity, family no-go, empirical completion, etc.>
```

## Scoped failure

```markdown
Disposition: FAIL <stage or provider> — SELECTED REALIZATION ONLY

Evidence scope:
- level: <E0-E4>
- quantifier: <Q0-Q3>
- stability: <S0-S4>
- failed NEED predicate: <predicate>

Exact obstruction:
<first missing or contradictory mathematical object>

Surviving results:
- <positive lemma>
- <positive control or reusable bound>

Scope:
- not a family no-go;
- frozen predecessors remain valid;
- no scientific execution occurred unless stated otherwise.

Nonblocking items:
- SHOULD: <items that did not cause the failure>
- COULD: <deferred extensions>

Architecture review:
<smallest concrete repair, new identity if required, and graph edge>
```

## GitHub issue closure comment

```markdown
## Disposition

Closed by `<sha>` with:

`<exact verdict>`

### Evidence scope

- level: <E0-E4>
- quantifier: <Q0-Q3>
- stability: <S0-S4>
- prepared domain: <domain and nonemptiness evidence>
- NEED predicates: <resolved predicates>

### Evidence

- <artifact and result>
- <independent review>
- <validation>

### Scientific inference

<precise scoped meaning>

### Effective assumptions

- <assumption>

### Nonblocking follow-up

- SHOULD: <strengthening>
- COULD: <deferred extension>

### Not inferred

- <stronger claim 1>
- <stronger claim 2>

### Graph handoff

<next dependency or bounded architecture repair>
```
