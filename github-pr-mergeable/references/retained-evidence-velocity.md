# Retained Evidence Velocity

Apply this policy when a run will be retained as performance, scaling, or scientific acceptance evidence.

1. The harness/schema MUST be reviewed and landed before expensive collection. Focused pre-review MUST cover provenance binding, concurrency and isolation, fail-closed validation, and evidence wording.
2. After pre-review, the measured product/runtime source and harness/schema MUST be frozen to exact commits and explicit subtree/blob identities. Product or harness changes invalidate affected retained evidence and require review, freeze, and collection again.
3. Where dependency policy permits, use ordered product, harness/schema, and artifact-only evidence commits or PRs. The harness/schema depends on the measured product when necessary; artifact-only evidence depends on both frozen identities and MUST NOT change product or harness bytes.
4. A dedicated high-capacity runner with a persistent build cache and durable artifact storage SHOULD be used. If any is unavailable, record `INFRASTRUCTURE_UNAVAILABLE: <runner|cache|storage>: <reason>` and the real fallback; MUST NOT imply that unavailable infrastructure exists.
5. Candidate-related CI failures block the affected gate. Proven unrelated flakes MUST be classified with evidence and MUST NOT invalidate retained evidence; rerun only affected gates, while all required merge gates still MUST pass on the current head.
6. Validators and review workflows MAY accept artifact-only descendants only when recorded runtime/harness subtree identities and implementation blob provenance exactly match the frozen candidate. Any product/runtime or harness/schema drift invalidates the affected evidence.
