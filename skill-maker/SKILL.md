---
name: skill-maker
description: Create high-quality reusable agent skills in the shared skills repo (~/.codex/skills) and wire them for Antigravity (AGY), Codex, and optionally Pi. Use when the user asks to create, improve, validate, or package a skill with best-practice SKILL.md structure, progressive disclosure, references, and AGY discovery manifest integration.
---

# Skill Maker

Use this skill to create or revise agent skills in the shared skills repository (`~/.codex/skills/<skill-name>/`) so they are automatically discoverable by Antigravity (`agy` CLI, App, and IDE via `~/.gemini/config/skills.json`), Codex, and optionally Pi (`~/.pi/agent/settings.json`).

## Goals

A good skill should be:

- **Discoverable**: frontmatter `name`/`description` clearly tell the agent when to load it.
- **Focused**: one coherent workflow or capability, not a broad catch-all.
- **Actionable**: provides concrete steps, commands, checklists, templates, and success criteria.
- **Progressively disclosed**: keeps `SKILL.md` concise (ideally under ~40 KB / ~600 lines so Antigravity's 46 KB / 800-line `read_file` loads it in a single call) and moves long templates/contracts into `references/`.
- **Portable**: uses relative links inside the skill directory and avoids hardcoded `/home/<user>` or single-harness assumptions unless the skill is intentionally harness-specific.
- **Safe**: calls out destructive commands, credentials, network access, review requirements, and performance-regression gates when creating issue/PR/execution workflows.
- **Testable**: includes validation steps for frontmatter, file paths, scripts, and expected outputs.
- **AGY-discoverable**: wired via `~/.gemini/config/skills.json` (absolute paths, no `~` expansion, exact names in `exclude`/`include_only`) and verified with `/skills reload` or `/skills`.

## Standard Workflow

### 1. Clarify the skill's purpose

Before creating files, identify:

- skill name, in lowercase hyphen form;
- exact trigger/use cases;
- non-goals and boundaries;
- tools or commands it expects;
- output/reporting format;
- whether references, scripts, or templates are needed.

If the request is vague, ask a short clarifying question. Otherwise make a reasonable narrow skill.

### 2. Choose a valid skill name

Rules:

- lowercase letters, numbers, and hyphens only;
- 1-64 characters;
- no leading/trailing hyphen;
- no consecutive hyphens;
- prefer verb-noun or domain-noun names: `github-pr-mergeable`, `orca-subagent-manager`, `skill-maker`.

Directory convention:

```text
~/.codex/skills/<skill-name>/SKILL.md
```

### 3. Create the skill structure

Recommended layout:

```text
<skill-name>/
├── SKILL.md
├── references/
│   └── ... optional long docs/templates ...
├── scripts/
│   └── ... optional helper scripts ...
└── assets/
    └── ... optional static assets ...
```

Only `SKILL.md` is required. Add `references/` when content would make `SKILL.md` too long.

### 4. Write required frontmatter

Every `SKILL.md` must start with YAML frontmatter:

```yaml
---
name: skill-name
description: Specific description of what this skill does and when to use it.
---
```

Description best practices:

- mention concrete actions and trigger phrases;
- include the environment/tool if relevant;
- avoid vague descriptions like “helps with tasks”;
- keep under 1024 characters;
- do not promise capabilities the skill does not implement.

### 5. Write concise, operational instructions

Good `SKILL.md` sections often include:

- `# Skill Name`
- `When To Use`
- `Inputs Needed`
- `Workflow`
- `Commands`
- `Validation`
- `Failure Handling`
- `Final Report Format`

Prefer checklists, command snippets, and decision tables. Avoid long prose unless it prevents mistakes.

### 6. Use progressive disclosure

Put detailed templates, long examples, and reference material in files under `references/`, then link from `SKILL.md`:

```markdown
See [prompt templates](references/prompts.md).
```

When a skill references relative paths, agents should resolve them relative to the skill directory.

### 7. Add helper scripts only when useful

If adding scripts:

- put them in `scripts/`;
- make them executable when intended to run;
- document required dependencies and safe usage;
- avoid hidden destructive behavior;
- prefer dry-run flags for risky operations.

### 8. Verify Antigravity (AGY) discovery (and optional Pi registration)

Antigravity CLI, App, and IDE all read `~/.gemini/config/skills.json` globally across workspaces. Ensure the shared skills repo is registered using an **absolute path** (Antigravity does **not** expand `~` and does **not** support wildcards in `exclude`/`include_only`):

```json
{
  "entries": [
    {
      "path": "/Users/<user>/.codex/skills",
      "exclude": ["<legacy-or-other-harness-skill>"]
    }
  ]
}
```

When `~/.gemini/config/skills.json` uses `entries` with `exclude`, new skills added to `~/.codex/skills/<skill-name>/` load automatically without editing the manifest. Inside an active `agy` CLI session, run `/skills reload` (or start a new conversation) and confirm the skill appears in `/skills` and as `/<skill-name>`. Ensure no stale duplicate with the same name exists in `~/.gemini/skills/` (which shadows `~/.gemini/config/skills.json` in `agy` CLI).

If Pi is also used on the machine, optionally register `~/.codex/skills/<skill-name>` in `~/.pi/agent/settings.json` idempotently (see [references/skill-template.md](references/skill-template.md)).

### 9. Validate

Run lightweight validation:

```sh
test -f ~/.codex/skills/<skill-name>/SKILL.md
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  ~/.codex/skills/<skill-name>
wc -l -c ~/.codex/skills/<skill-name>/SKILL.md
```

Also inspect `~/.gemini/config/skills.json` to confirm the skill is not excluded and run `/skills reload` in `agy`.

## Quality Checklist

Before reporting done, verify:

- [ ] Skill directory is under `~/.codex/skills/`.
- [ ] `SKILL.md` exists, passes `quick_validate.py`, and stays comfortably under 46 KB / 800 lines.
- [ ] `name` is valid lowercase hyphen form.
- [ ] `description` is specific, third-person, and trigger-oriented.
- [ ] Instructions are scoped, actionable, and free of hardcoded user home paths.
- [ ] Long examples/templates live in `references/`.
- [ ] Relative links point to existing files.
- [ ] Commands preserve existing user settings and are idempotent.
- [ ] Issue/PR/execution skills include the normalized rule that material performance regressions block mergeability until optimized or explicitly accepted.
- [ ] `~/.gemini/config/skills.json` exposes the skill (and no stale shadow exists in `~/.gemini/skills/`).
- [ ] Final response lists created/modified paths.

## Common Pitfalls

Avoid:

- creating a broad “general helper” skill with no clear trigger;
- omitting frontmatter or using invalid names;
- making the description too vague for automatic discovery;
- letting `SKILL.md` exceed 46 KB / 800 lines (forces multi-call reads in AGY);
- using `~` or wildcards in `~/.gemini/config/skills.json` (unsupported by AGY);
- using hardcoded `/home/<user>` paths inside skill instructions unless intentionally machine-specific;
- overwriting settings manifests instead of updating them;
- adding destructive scripts without warnings and dry-run guidance;
- claiming the skill is installed without verifying `~/.gemini/config/skills.json` / `/skills`;
- omitting a performance regression gate from skills that create issues, execute PRs, or declare PRs mergeable.

## Template

Use [the reusable skill template](references/skill-template.md) when drafting new skills.

## Final Response Format

When creating or updating a skill, report:

- skill name;
- files created/modified;
- whether `~/.gemini/config/skills.json` (or Pi settings) was updated;
- any validation performed;
- how to invoke it, e.g. `/<skill-name>` in Antigravity (or `/skill:<skill-name>` in Pi).
