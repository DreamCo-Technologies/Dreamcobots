# Buddy Tool and Skill Catalog

Buddy uses `config/buddy_tool_skill_catalog.json` as the source of truth for tools and skills it can use to test bots, train other AI models, and build DreamCo systems.

## Main Command

```bash
node automation-tools/agents/tool-skill-readiness-audit.cjs
```

Strict-style run:

```bash
node automation-tools/agents/tool-skill-readiness-audit.cjs --strict
```

The command writes:

- `reports/tool-skill-readiness-report.json`
- `reports/tool-skill-readiness-report.md`

## What The Audit Proves

- Every listed tool has an id, name, need status, purpose, usage instructions, and test command.
- Every listed skill has an id, name, need status, purpose, usage instructions, and test command.
- Risky actions are gated: customer contact, social posting, spending money, moving money, dependency installs, publishing code, and external model training with private data.
- Buddy has a report path for evidence instead of unsupported claims.
- Any tool that cannot be tested must be marked `not verified`; Buddy cannot claim it works from vibes.

## How Buddy Should Train Other AI Models

Buddy can prepare training handoffs for other AI models using only approved data:

- Public repository code and docs.
- Sourced tool and skill summaries.
- Test commands and report outputs.
- Examples, rubrics, and safe prompts.

Buddy must not include:

- Secrets or tokens.
- Private customer data.
- Unsourced claims.
- Claims that a tool works without a test command or report.

## Required Output Format

```text
Tool/Skill:
What it does:
How to use it:
Needed: true/false
Evidence:
Risks:
Next test:
```

This is the no-hallucination format for tools and skills.
