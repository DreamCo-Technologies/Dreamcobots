# DreamCo Upgrade Ladder — Lite to Super

## Principle

DreamCo expands only after the previous level proves value. Architecture is earned by usage, not added in advance.

## Level 1 — DreamCo Lite

Current target:

- Money Bot v1
- Debug Bot v1
- one simple UI
- leads → outreach → usable output

Upgrade only after Proof Mode passes.

## Level 2 — First Lite System

The first proven bot becomes the first Lite System candidate.

For Money Bot, possible upgrades include:

- lightweight telemetry for runs, successes, failures, and lead/message quality signals;
- local error handling and targeted fallback behavior for failures actually observed in Proof Mode;
- minimal prompt/workflow adaptation based on niche and validated user needs.

Do not add all possible features automatically. Add only improvements supported by evidence.

## Level 3 — Reusable Lite System Template

After one bot has been upgraded successfully, extract the useful parts into a reusable template.

Candidate template modules:

- telemetry
- error/debug adapter
- task-specific configuration
- small workflow extension points

The template should remain optional and composable rather than forcing every bot into the same architecture.

## Level 4 — Selective Expansion

Apply the Lite System template only to bots that demonstrate meaningful usage, revenue potential, operational importance, or recurring failure patterns.

Avoid repo-wide attachment merely because a bot exists.

## Level 5 — Workflow Intelligence

When users consistently need multi-step execution, add explicit workflow chaining.

Example progression:

1. leads → messages → export
2. leads → messages → approved send action
3. domain-specific workflow templates

Human approval checkpoints remain available for consequential actions.

## Level 6 — Visual Builder

Build drag-and-drop workflow composition when real users need customization beyond prebuilt workflows.

The visual builder should expose proven capabilities as blocks rather than creating a second, disconnected execution system.

## Level 7 — Multi-Agent Systems

Introduce specialized cooperating agents only when workflows genuinely benefit from role separation or parallel execution.

Potential roles:

- researcher/lead finder
- outreach writer
- validator
- analyst
- domain specialist

Multi-agent orchestration should improve measurable quality, speed, reliability, or cost—not exist for appearance.

## Level 8 — Buddy Orchestrator

Buddy becomes the platform-wide orchestration layer after DreamCo has multiple proven bots/systems that need coordinated routing.

Long-term Buddy responsibilities may include:

- task classification and routing
- permission and human-approval enforcement
- workload distribution
- health and performance monitoring
- cost/resource awareness
- cross-bot workflow orchestration
- selecting Lite versus Super execution paths

## Super System Upgrade Triggers

A Lite System may become a Super System when evidence shows that the simpler architecture is a constraint. Triggers can include:

- sustained high workload
- repeated queue/backlog pressure
- workflows that benefit materially from parallel processing
- reliability requirements beyond the Lite implementation
- multiple clients requiring isolation
- long-running tasks that require durable orchestration
- measurable need for autoscaling or distributed workers

Potential Super capabilities include:

- multi-tenant isolated worker pools
- durable queues
- parallel execution
- workflow checkpointing/resume
- advanced observability
- targeted auto-repair/retry policies
- horizontally scalable workers

These are upgrade options, not default requirements.

## Repository Scanner — Later Gate

A repository-wide scanner becomes useful only after the Lite System template and upgrade criteria are proven.

Future scanner responsibilities may include:

- inventorying bots and capabilities
- detecting duplicate or missing dependencies
- identifying disconnected integrations
- reading usage/health metadata
- recommending Lite/System/Super status
- identifying candidates for consolidation or retirement

The scanner should initially **recommend** changes rather than automatically modifying every bot.

## Anti-Drift Rules

1. Do not build v2 before v1 produces evidence.
2. Do not attach Lite Systems globally before the template is proven.
3. Do not build a visual builder before users need workflow customization.
4. Do not introduce distributed infrastructure before workload requires it.
5. Do not make Buddy responsible for systems that are not yet reliable independently.
6. Prefer measurable user value over capability count.

## Long-Term Architecture

The intended end state remains ambitious:

- independently useful bots;
- proven bots upgraded into Lite Systems;
- high-demand Lite Systems upgraded into Super Systems;
- Buddy coordinating the full ecosystem.

The difference is sequencing: **prove → upgrade → template → scale → orchestrate.**
