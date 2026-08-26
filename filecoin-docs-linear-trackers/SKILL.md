---
name: filecoin-docs-linear-trackers
description: Create, update, and reconcile Filecoin Docs Linear GER trackers and local todo markdown with durable tracker structure, live Linear API state, upstream filecoin-project PR policy, validation evidence, and PR handoff comments.
---

# Filecoin Docs Linear Trackers

Use this skill for Filecoin Docs work where Linear issues, local tracker files,
and upstream PRs need to stay aligned.

## When To Use

Use this skill when the user asks to:

- create or update Linear trackers for Filecoin Docs GER issues;
- sync local tracker files under `~/dev/snissn/todo/` with Linear and GitHub PR
  state;
- turn Filecoin Docs feedback into parent/child tracker bodies with milestones,
  scope boundaries, validation, and PR process;
- comment Linear issues with PR links, validation evidence, or closeout status.

Do not use this skill for generic GitHub tracker issues; use
`gh-issue-planner` for those. Do not use it for non-Filecoin Docs Linear work
unless the user explicitly asks to adapt the workflow.

## References

- Use [tracker template](references/tracker-template.md) when drafting local or
  Linear tracker bodies.
- Use [Linear API cheatsheet](references/linear-api-cheatsheet.md) when the
  Linear connector is unavailable or unreliable.

## Inputs Needed

- Linear issue identifiers, usually `GER-####`, or a parent issue plus child
  issue list.
- Filecoin Docs checkout, defaulting to
  `~/dev/fil-builders/filecoin-docs` when present.
- Local tracker directory, defaulting to `~/dev/snissn/todo/`.
- Whether the user wants local-only drafts or actual Linear/GitHub writes. If
  unclear, update local files first and ask before external writes.

## Workflow

1. Read repo-local instructions first: `AGENTS.md`, `CONTRIBUTING.md`,
   PR templates, `package.json`, and relevant roadmap/tracker files.
2. Verify repo authority before PR planning:
   `filecoin-project/filecoin-docs` is the authoritative upstream target, and
   implementation branches should be based on `filecoin-project/main` unless
   the user says otherwise.
3. Fetch live Linear state before changing trackers. Prefer a current Linear
   connector if available. If only the deprecated legacy connector is available
   or it fails, use the Linear GraphQL API with `LINEAR_API_KEY` or
   `LINEAR_TOKEN`; see the cheatsheet.
4. Fetch live GitHub state for related PRs with `gh pr view` or the GitHub app:
   title, base/head, draft status, checks, merge state, review decision, and
   URL.
5. Reconcile local tracker files against live state. Never mark aspirational
   work as done; distinguish `Current Evidence`, `Target`, and `Completion
   Criteria`.
6. For umbrella work, keep a parent tracker for sequencing and acceptance, then
   child trackers for executable slices. Cross-link parent and child Linear
   issues and local files.
7. Draft or update tracker bodies using the reference template:
   goal, why, current evidence, scope, non-goals, ordering/blocking,
   coordination, branch/PR policy, milestones, validation, and completion
   criteria.
8. For PR-backed work, require a start and close phase:
   inventory first, implement in a focused branch, validate on the current
   target branch, then update PR body and Linear with evidence.
9. Before creating branches, commits, PR text, GitHub comments, or Linear text,
   run the public-output hygiene checklist below. External outputs must read as
   ordinary project-maintainer work and must not contain tool branding or
   obvious AI provenance unless the user explicitly requests it or repo policy
   requires it.
10. Open PRs only when requested or approved. Default for this workstream is a
   ready-for-review PR unless the user explicitly asks for a draft.
11. After a mature PR exists, update the corresponding Linear issue to
    `In Review` and comment with PR URL, branch/base, scope, and validation
    evidence. Move to `Done` only after the issue's actual acceptance condition
    is met, usually merge or explicit maintainer/user acceptance.

## Filecoin Docs PR Policy

- Start topic branches from `filecoin-project/main`.
- Branch names must start with `mikers/`, for example
  `mikers/ger-1114-store-on-filecoin-upstream-main`.
- Never use branch names containing `codex`, `chatgpt`, `openai`, `ai-agent`,
  `bot`, `generated`, or similar tool/provenance markers.
- Push to the configured fork remote, then open PRs against
  `filecoin-project/filecoin-docs:main`.
- Do not push directly to `main`.
- Keep PRs focused around one tracker or one tightly coupled stack such as a
  Store-on-Filecoin section plus main-nav changes.
- Include Linear links, validation evidence, and known risks in every PR body.
- Request reviews only after the PR is coherent, validated, and has no known
  local blockers. Do not mention AI-assisted review tooling in public PR or
  Linear text unless the user explicitly asks or repo policy requires it.
- If CI is backed up, use only latest-head checks as mergeability evidence.
- If docs work touches scripts, builds, generated output, or runtime assets,
  material build/runtime/performance regressions block mergeability until fixed
  or explicitly accepted.

## Public Output Hygiene

Apply this to all durable or external-facing output: branch names, commit
subjects/bodies, PR titles/bodies/comments, Linear titles/descriptions/comments,
GitHub issues/comments, and local tracker files that may be copied into those
systems.

- Use neutral maintainer language. Do not write "Codex", "ChatGPT", "OpenAI",
  "AI-generated", "generated by", "authored by an AI", "agent", "bot", or
  similar provenance markers.
- Do not add `Co-authored-by` trailers for tool identities.
- Do not use branch prefixes such as `codex/`, `ai/`, `bot/`, or
  `generated/`; use `mikers/<issue>-<short-topic>-upstream-main`.
- Commit messages should be conventional, concise, and task-focused, for
  example `docs: add store on filecoin section`.
- PR and Linear text should describe scope, evidence, validation, and next
  steps without discussing who or what produced the work.
- Internal reasoning may mention tools when needed, but do not copy those
  mentions into public artifacts.
- If a repository, organization, reviewer, or user explicitly requires AI/tool
  disclosure, follow that higher-priority requirement and say so in the final
  report.

Before publishing, audit drafted text and the branch name:

```sh
git branch --show-current
rg -n -i '\b(codex|chatgpt|openai|ai-generated|generated by|authored by an ai|ai agent|agent-generated|bot-generated|co-authored-by:.*(codex|chatgpt|openai|bot))\b' \
  /tmp/filecoin-docs-pr.md \
  /tmp/filecoin-docs-linear-comment.md \
  /tmp/filecoin-docs-commit-message.txt \
  ~/dev/snissn/todo
```

The branch name must begin with `mikers/`, and the search should return no
matches unless the user explicitly approved a disclosure.

## Validation Policy

- Use validation commands available on the current upstream target branch. Do
  not assume fork-only scripts exist.
- For scoped Markdown docs changes, run focused Markdown lint on touched files
  when available, plus `npm run build`.
- Run `npm run check-links` and `npm run check:redirects` when those commands
  exist on the target branch or the user explicitly accepts fork tooling.
- For moved/deleted pages, validate `SUMMARY.md`, internal links, and redirects
  or document production URL compatibility.
- Record exact commands and outcomes in local tracker files, PR bodies, and
  Linear comments.

## Linear Write Rules

- Treat every Linear write as an external action. Perform it only when the user
  requested it or approved the exact scope.
- Before changing state, query the issue's team states and choose by state name;
  do not hardcode state IDs.
- Before creating child issues, check whether they already exist by identifier,
  title, or parent relationship.
- Preserve user/team wording unless it is stale or contradicted by current
  evidence.
- Use absolute dates for status updates.
- Keep Linear descriptions and comments free of tool/provenance markers. State
  what changed, where the PR is, what validation passed, and what remains.
- If the Linear app connector is deprecated or failing, mention that the new
  Linear connector should be used when available, then fall back to the direct
  API if credentials are present.

## Failure Handling

Pause and report if:

- no Linear connector works and no `LINEAR_API_KEY` or `LINEAR_TOKEN` is
  available for requested Linear writes;
- the repo remotes do not clearly identify the upstream and fork;
- the target branch has drifted in a way that changes validation or URL policy;
- Linear state names are ambiguous;
- a branch, commit, PR body, or Linear draft contains public AI/tool provenance
  language that the user has not approved;
- a requested issue closeout depends on an unmerged PR or unresolved review.

## Final Report Format

Return:

- tracker files created or updated;
- Linear issues created, updated, commented, or left local-only;
- PRs opened or inspected, including base/head and review/check state;
- validation commands run and outcomes;
- what is done, what remains, and the recommended next order.
