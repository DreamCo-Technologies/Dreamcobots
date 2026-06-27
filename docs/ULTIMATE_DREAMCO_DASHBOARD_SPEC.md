# Ultimate DreamCo Dashboard Specification

Goal: make GitHub the control room while the DreamCo dashboard becomes the visual operator layer for bots, workflows, learning, actions, and production readiness.

## Dashboard pages

| Page | Purpose |
| --- | --- |
| Actions | Every task, missing file, build issue, bot command, and goal checkpoint |
| Agents | Bot roster, modes, permissions, abilities, memory, learning status |
| Workflows | Multi-step bot processes, triggers, inputs, outputs, owners |
| Goals | Business goals, bot learning goals, weekly milestones, evidence |
| Memory | Profile, task, event, skill, source, failure, and decision memory |
| Resources | Approved AI, business, coding, and infrastructure learning sources |
| Commands | GitHub Actions command launcher with risk gating |
| Missing Files | Live output from `npm run scan:missing` |
| Model Router | Model choice, context window, tool permissions, output format |
| Debate Room | Multi-agent prompt debate and decision review |
| Production | CI checks, deployment readiness, secrets, dependencies, incidents |

## Replit-to-GitHub processing layers

| Layer | Required fields |
| --- | --- |
| Input layer | user request, files, repo, issue, logs, screenshots, priority |
| Role definition | bot role, scope, risk level, permissions, owner |
| Task specification | purpose, acceptance criteria, constraints, deadline |
| Format requirement | JSON, Markdown, PR, issue, report, command output |
| Processing layer | context loading, file search, source retrieval, dependency check |
| Context window | selected files, retrieved docs, memory, known failures |
| Model selection | task difficulty, cost, latency, tool needs, reasoning mode |
| Extended thinking | enabled for architecture, debugging, security, production fixes |
| Switch-me layer | hand off between BuddyAI, BuildBot, DealAnalyzer, QA, Security |
| Projects layer | GitHub Projects lanes and labels |
| Document library | READMEs, runbooks, manifests, schemas, prompts, reports |
| Instructions layer | system prompts, bot policies, command policies, style guides |
| Memory layer | profile, task, event, skill, source, failure, decision memory |
| Output layer | final answer, files changed, tests run, next actions |

## Bot command safety

Bots can run code and commands only through explicit policies.

| Command tier | Allowed examples | Approval |
| --- | --- | --- |
| Read | list files, inspect logs, parse reports | automatic |
| Check | lint, test, typecheck, scan missing files | automatic or scheduled |
| Build | build dashboard, generate reports | supervised |
| Write | edit files, create PRs, update manifests | PR required |
| Deploy | production deploys, secrets, billing | owner approval required |

## Actions page requirements

The Actions page must show:

- Action title, bot owner, linked goal, linked workflow, priority, risk, status.
- Missing file or dependency if blocked.
- Command to run or GitHub Action workflow to dispatch.
- Evidence required before completion.
- Learning update created after completion.
- Human approval state.

## Agents page requirements

The Agents page must show:

- Bot identity and division.
- Abilities and proficiency level.
- Active workflows.
- Current mode toggle.
- Command permission tier.
- Memory policy.
- Learning pace and next checkpoint.
- Missing file count.
- Latest test/build health.

## Production-ready checklist

- All bot folders have README, manifest/profile, tests or examples, owner, and mode policy.
- All dashboard routes load without missing imports.
- All API routes have validation, errors, logs, auth posture, and tests.
- GitHub Actions run missing-file scans, tests, lint, and report uploads.
- Every automation writes an event log.
- Every learning update has approved source references.
- Every high-risk command requires human approval.
