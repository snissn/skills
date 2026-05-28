---
name: skill-maker
description: Create high-quality reusable agent skills in ~/.codex/skills and install them for Pi. Use when the user asks to create, improve, validate, or package a skill with best-practice SKILL.md structure, progressive disclosure, references, and Pi settings integration.
---

# Skill Maker

Use this skill to create or revise agent skills that live in `~/.codex/skills/<skill-name>/` and are discoverable by Pi through `~/.pi/agent/settings.json`.

## Goals

A good skill should be:

- **Discoverable**: frontmatter name/description clearly tell the agent when to load it.
- **Focused**: one coherent workflow or capability, not a broad catch-all.
- **Actionable**: provides concrete steps, commands, checklists, templates, and success criteria.
- **Progressively disclosed**: keeps `SKILL.md` concise and moves long examples/references into `references/`.
- **Portable**: uses relative paths inside the skill directory and avoids machine-specific assumptions unless required.
- **Safe**: calls out destructive commands, credentials, network access, review requirements, and performance-regression gates when creating issue/PR/execution workflows.
- **Testable**: includes validation steps for frontmatter, file paths, scripts, and expected outputs.
- **Pi-accessible**: installed in Pi settings so `/skill:<name>` and automatic discovery can find it.

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

### 8. Install the skill for Pi

Add the skill directory to `~/.pi/agent/settings.json` under `skills` if not already present:

```json
{
  "skills": [
    "~/.codex/skills/<skill-name>"
  ]
}
```

Use an idempotent update so existing settings are preserved.

Example:

```sh
python3 - <<'PY'
import json
from pathlib import Path
p = Path.home() / '.pi/agent/settings.json'
data = json.loads(p.read_text()) if p.exists() else {}
skills = data.setdefault('skills', [])
entry = '~/.codex/skills/<skill-name>'
if entry not in skills:
    skills.append(entry)
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(data, indent=2) + '\n')
PY
```

### 9. Validate

Run lightweight validation:

```sh
test -f ~/.codex/skills/<skill-name>/SKILL.md
python3 - <<'PY'
from pathlib import Path
p = Path.home() / '.codex/skills/<skill-name>/SKILL.md'
text = p.read_text()
assert text.startswith('---\n')
assert 'name: <skill-name>' in text
assert 'description:' in text
print('skill frontmatter sanity ok')
PY
```

Also inspect `~/.pi/agent/settings.json` to confirm the skill path is present.

## Quality Checklist

Before reporting done, verify:

- [ ] Skill directory is under `~/.codex/skills/`.
- [ ] `SKILL.md` exists and starts with valid frontmatter.
- [ ] `name` is valid lowercase hyphen form.
- [ ] `description` is specific and trigger-oriented.
- [ ] Instructions are scoped and actionable.
- [ ] Long examples/templates live in `references/`.
- [ ] Relative links point to existing files.
- [ ] Commands preserve existing user settings and are idempotent.
- [ ] Issue/PR/execution skills include the normalized rule that material performance regressions block mergeability until optimized or explicitly accepted.
- [ ] Pi settings include `~/.codex/skills/<skill-name>`.
- [ ] Final response lists created/modified paths.

## Common Pitfalls

Avoid:

- creating a broad “general helper” skill with no clear trigger;
- omitting frontmatter or using invalid names;
- making the description too vague for automatic discovery;
- embedding huge reference docs in `SKILL.md`;
- using absolute paths inside skill instructions unless the path is intentionally user-specific;
- overwriting Pi settings instead of updating them;
- adding destructive scripts without warnings and dry-run guidance;
- claiming the skill is installed without checking settings;
- omitting a performance regression gate from skills that create issues, execute PRs, or declare PRs mergeable.

## Template

Use [the reusable skill template](references/skill-template.md) when drafting new skills.

## Final Response Format

When creating or updating a skill, report:

- skill name;
- files created/modified;
- whether Pi settings were updated;
- any validation performed;
- how to invoke it, e.g. `/skill:<skill-name>`.
