# Reusable Skill Template

Copy this into `~/.codex/skills/<skill-name>/SKILL.md` and replace placeholders.

```markdown
---
name: <skill-name>
description: <Specific description of what this skill does and when to use it. Mention concrete trigger tasks.>
---

# <Human Skill Title>

## When To Use

Use this skill when:

- <trigger/use case 1>;
- <trigger/use case 2>;
- <trigger/use case 3>.

Do not use this skill for:

- <non-goal 1>;
- <non-goal 2>.

## Inputs Needed

- <input 1>
- <input 2>
- <input 3>

If missing critical input, ask a concise clarifying question.

## Workflow

1. <Step 1: inventory/context>
2. <Step 2: plan>
3. <Step 3: execute>
4. <Step 4: validate>
5. <Step 5: report>

## Commands / Examples

```sh
<safe command example>
```

## Validation

Before claiming done, verify:

- [ ] <validation item 1>
- [ ] <validation item 2>
- [ ] <validation item 3>

## Failure Handling

Pause and report if:

- <blocker condition 1>;
- <blocker condition 2>.

## Final Report Format

Return:

- summary;
- files changed;
- tests/validation;
- risks or follow-ups.
```

## Description Examples

Good descriptions:

```yaml
description: Create or update GitHub tracker issues in snissn/gomap with milestones, tests, benchmark evidence, AI review requirements, and completion criteria.
```

```yaml
description: Coordinate Pi subagents inside Orca for multi-issue implementation work: spawn managers, split subtasks, run execution/review/fix loops, and drive PRs to mergeable state.
```

Weak descriptions:

```yaml
description: Helps with GitHub.
```

```yaml
description: General coding workflow.
```

## Pi Installation Snippet

```sh
python3 - <<'PY'
import json
from pathlib import Path
skill = '<skill-name>'
entry = f'~/.codex/skills/{skill}'
p = Path.home() / '.pi/agent/settings.json'
data = json.loads(p.read_text()) if p.exists() else {}
skills = data.setdefault('skills', [])
if entry not in skills:
    skills.append(entry)
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(data, indent=2) + '\n')
PY
```
