# Standard TreeDB JSONBench Breakdown Template

Use this shape for tracker comments, PR summaries, and optimization planning.

```markdown
# TreeDB JSONBench Breakdown

## Evidence

- TreeDB artifact: `<path>`
- TreeDB cell/result: `<path or n/a>`
- parity artifact: `<path or n/a>`
- ClickHouse artifact: `<path or n/a>` (`fresh run` / `reference only`)
- colgranule artifact: `<path or n/a>` (`historical/prototype only`)
- gomap head: `<sha or unknown>`
- JSONBench head: `<sha or unknown>`

## Headline TreeDB Row

| field | value |
|---|---|
| scale | `<scale>` |
| data shape | `full-retained-json` |
| layout | `column-store-full-prepared` |
| execution | `prepared` |
| storage source | `typed_column_part` |
| typed column owner | `typed_column_part` |
| retained payload | `non-column` |
| fallback | `none` |
| document scan fallback | `false` |
| reconstruction | `valid` / `unknown` |

## Storage

| system/basis | bytes | decimal MB | MiB | notes |
|---|---:|---:|---:|---|
| TreeDB total |  |  |  | includes WAL if present |
| TreeDB durable excluding WAL |  |  |  | comparison target |
| TreeDB WAL excluded |  |  |  | command WAL bytes removed from durable comparison |
| ClickHouse total |  |  |  | reference/fresh |
| ClickHouse data |  |  |  | optional |
| ClickHouse index |  |  |  | optional |

TreeDB durable-excluding-WAL / ClickHouse total: `<ratio>x`.

### TreeDB durable category breakdown

| category | bytes | decimal MB | MiB |
|---|---:|---:|---:|
| leaf_vlog |  |  |  |
| value_vlog |  |  |  |
| column assets |  |  |  |
| typed-column part sections |  |  |  |
| primary index |  |  |  |
| manifest/control/other |  |  |  |

## q1-q5 timings

| query | TreeDB production full-prepared | TreeDB direct (parity artifact, label scale) | colgranule historical kernel | ClickHouse | TreeDB/ClickHouse | notes |
|---|---:|---:|---:|---:|---:|---|
| q1 |  |  |  |  |  |  |
| q2 |  |  |  |  |  |  |
| q3 |  |  |  |  |  |  |
| q4 |  |  |  |  |  |  |
| q5 |  |  |  |  |  |  |

If direct evidence comes from a smaller parity artifact, label the row count in the direct cell and do not present it as same-scale headline evidence.

## Correctness and fallback gates

- q1-q5 same loaded DB: `<yes/no/unknown>`
- row/direct/prepared hash parity: `<scale and status>`
- reconstruction hash valid: `<yes/no/unknown>`
- fallback reason: `<none or reason>`
- document scan fallback: `<false/true>`

## Optimization targets

Storage priorities:

1. `<largest durable category>`
2. `<next category>`
3. `<next category>`

Query priorities:

1. `<slowest q>`
2. `<next q>`
3. `<next q>`

## Optional profile insights

| focus | top CPU signal | top allocation signal | optimization hypothesis |
|---|---|---|---|
| `q2_prepared` |  |  |  |
| `q3_prepared` |  |  |  |
| `q5_prepared` |  |  |  |

Profile artifacts:

- profiles dir: `<path>`
- profile insights: `<path>/profile_insights.md`

Treat profile findings as hypotheses. Confirm with a before/after rerun of both the canonical JSONBench metric and the same profile focus.

Notes:

- Do not optimize against WAL-inclusive total unless explicitly targeting WAL volume.
- Do not optimize to colgranule numbers by routing production through `experiments/colgranule`; use them only as a ceiling/reference for production designs.
- Do not claim fresh ClickHouse parity without a fresh same-row ClickHouse run.
```
