# Lightweight scientific workstream coordination policy

This directory must stay small and coordination-focused.

## Required behavior

- Do not require a checked-in live scheduler, slot pool, class taxonomy, activation PR, modular roster, or schema migration by default.
- Treat explicit owner direction or a clear issue assignment as sufficient to start a dependency-ready lane.
- Require one writer per issue-scoped branch and check same-decision or owned-path overlap before writing.
- Allow path-disjoint work to proceed in parallel.
- Do not pause unrelated branches because `main` advanced.
- Keep one bounded scientific decision per PR by default.
- Preserve merged-predecessor gates declared by the scientific issue.
- Preserve proportional exact-candidate review and the documented GPT-5.6 Pro quota fallback.
- Never use a workflow to author or push scientific or governance authority.
- Never activate a successor automatically.

The optional issue-comment marker in `references/workstream-marker.md` is coordination metadata only and creates no scientific authority.
