# Skills repository policy

## Scientific workstream coordination

Skills that manage scientific repositories must prefer lightweight issue-and-branch coordination:

1. explicit owner direction or a clear issue assignment authorizes a lane;
2. one issue-scoped branch has one writer;
3. agents check same-decision and owned-path overlap before writing;
4. disjoint lanes may proceed independently;
5. no checked-in live scheduler, global slot pool, class taxonomy, or activation PR is required by default;
6. unrelated mainline changes do not halt or invalidate a branch;
7. one scientific decision belongs in one PR by default;
8. workflows may not generate or push scientific or governance authority;
9. exact-candidate review remains proportional to the claim and is renewed after scientific edits;
10. declared downstream scientific dependencies require merged predecessor authority; and
11. no successor activates automatically.

A repository may choose a stricter local policy, but a skill must not invent scheduling bureaucracy that the repository or owner did not request.

Use `scientific-portfolio-governance` as lightweight workstream coordination. Do not require or generate portfolio schemas, modular rosters, activation transitions, slot arithmetic, or workflow-authored board changes unless the owner explicitly requests that structure.

## Internal review fallback

A hosted Codex quota, usage-limit, rate-limit, capacity, or service-unavailable response is evidence that the review did not run. Record it as `CODEX_REVIEW_UNAVAILABLE_QUOTA`; it is neither acceptance nor a finding.

Unless target-repository policy explicitly requires a different reviewer identity or hosted-only review, an internal read-only subagent review (`INTERNAL_SUBAGENT_REVIEW`) or a separate same-agent mock subagent review (`LOCAL_MOCK_SUBAGENT_REVIEW`) is an acceptable fallback. The mock mode performs an actual adversarial reviewer pass and is labeled as same-agent rather than independent. Bind either mode to the exact candidate, record the actual model, reviewed paths and claims, checks, findings, `ACCEPT` or `REJECT`, and confirmation of no candidate edits. Later scientific or review-relevant edits require renewed review.

Use [the shared internal review fallback contract](github-pr-mergeable/references/internal-review-fallback.md). Preserve target-repository model, independent-review, human-approval, scientific, and merge requirements.
