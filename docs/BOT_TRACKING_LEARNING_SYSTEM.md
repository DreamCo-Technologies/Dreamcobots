# DreamCo Bot Tracking and Controlled Learning System

This is the production design for tracking every DreamCo bot's abilities, workflows, goals, learning paths, memory, and execution readiness.

## Core rule

Every bot must be configurable, measurable, and paced. No bot learns randomly. Every bot learns through approved goals, source sets, review checkpoints, and output tests.

## Bot control profile

Each bot should have a `bot.control.json` file next to its manifest or DreamCo profile.

```json
{
  "botId": "auto_client_hunter",
  "displayName": "Auto Client Hunter",
  "mode": "supervised",
  "division": "DreamSalesPro",
  "abilities": ["lead_search", "qualification", "outreach_draft"],
  "workflows": ["find_leads", "score_leads", "create_follow_up"],
  "goals": ["book_discovery_calls", "improve_lead_quality"],
  "learningPace": "weekly",
  "memoryPolicy": "approved_sources_only",
  "commandPolicy": "github_actions_supervised",
  "reviewers": ["owner", "buddyai"],
  "riskLevel": "medium"
}
```

## Tracking dimensions

| Dimension | What it tracks | Example |
| --- | --- | --- |
| Abilities | What a bot can do now | search, summarize, code, scrape, classify |
| Workflows | Repeatable business flows | lead capture, deal score, invoice follow-up |
| Goals | Outcomes the bot is trying to improve | revenue, quality, response speed |
| Learning path | Approved subjects and milestones | prompt design, API usage, sales scripts |
| Memory | What the bot may remember | user preferences, lessons, known failures |
| Evidence | Proof the bot learned correctly | tests, evals, sample outputs, reviewer notes |
| Commands | What the bot may run | read-only, test-only, deploy-with-approval |
| Risk | Operational danger level | low, medium, high, restricted |

## Two-year learning pace

The default controlled pace is 104 weekly checkpoints.

| Phase | Weeks | Focus | Output gate |
| --- | ---: | --- | --- |
| Foundation | 1-12 | Bot purpose, file structure, safety, prompts | Manifest and README complete |
| Workflow mastery | 13-26 | Business workflow execution | Workflow runbook and test cases |
| Tool use | 27-39 | GitHub, files, APIs, command limits | Tool permission profile |
| Memory | 40-52 | Short-term, long-term, vector, event memory | Memory audit report |
| Data quality | 53-65 | Source reliability and extraction | Source scorecards |
| Autonomy | 66-78 | Supervised action loops | Human approval checkpoints |
| Optimization | 79-91 | Cost, speed, quality, failures | Eval dashboard metrics |
| Production | 92-104 | Reliability, CI, recovery, governance | Release checklist complete |

## Memory storage styles

Use multiple memory styles, not one giant memory bucket.

- Profile memory: stable bot identity, role, division, owner, constraints.
- Task memory: current task context and temporary scratchpad.
- Event memory: what happened, when, by which bot, with result.
- Skill memory: reusable methods the bot has proven through tests.
- Source memory: approved articles, docs, transcripts, and code references.
- Failure memory: missing files, broken commands, bad outputs, blocked actions.
- Decision memory: why a route, model, or workflow was chosen.

## Memory storage guardrails

Memory should scale by design, not by hope. The repo uses `config/local_first_storage_policy.json` and `tools/storage_guard.py` to keep bot memory and generated libraries from becoming one huge file that breaks dashboards, reviews, or future deploys.

- Hot memory keeps active task state and recent bot context, then rolls over at the configured local budget.
- Warm memory keeps approved lessons, source notes, completed task summaries, and reusable skill memory.
- Cold memory keeps compressed audit archives and long-term evidence through content-addressed files.
- Vector memory stores searchable references in partitioned indexes, not one giant embedding file.
- Generated libraries must load from lightweight manifests and independently readable shards.
- Dashboards must read summaries and manifests first, then load detail only when a user opens it.
- Pull requests that change generated libraries or memory policy should run `npm run check:storage`.

## Agent modes

Every bot dashboard should expose mode toggles.

| Mode | Behavior |
| --- | --- |
| Observe | Read files and summarize only |
| Diagnose | Find missing files, broken imports, weak docs, bad configs |
| Draft | Create proposed changes without executing commands |
| Build | Modify files and run local checks |
| Test | Run tests, scans, and validation only |
| Command | Run approved commands through GitHub Actions |
| Autopilot | Execute approved low-risk workflows with logs |
| Locked | No actions; visible for audit only |

## GitHub as dashboard

GitHub should become the operating dashboard using:

- Issues for bot goals and missing-file tasks.
- Labels for division, risk, bot mode, priority, and stage.
- Projects for dashboard lanes: Intake, Spec, Build, Test, Review, Deploy, Learn.
- Actions for command execution, scans, tests, and reports.
- Markdown reports for human-readable summaries.
- JSON artifacts for machine-readable bot state.
- Pull requests for every production change.

## Required reports

- `reports/bot-health-report.md`
- `reports/bot-health-report.json`
- `reports/bot-learning-progress.json`
- `reports/workflow-readiness.json`
- `reports/command-permissions.json`
- `reports/dashboard-status.md`

## Quality standard

Use "ChatGPT-ready" as the internal quality bar, not as an official certification claim. A bot is ChatGPT-ready when it has clear purpose, source boundaries, tests, safe command permissions, readable output, and a reviewable learning trail.
