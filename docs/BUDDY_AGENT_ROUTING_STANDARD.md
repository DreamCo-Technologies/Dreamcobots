# Buddy Specialist Agent Routing Standard

## Goal
Select the right specialist for each task instead of sending every task to the same agent.

## Routing pipeline

`Understand task → decompose → classify → select specialists → execute in parallel/sequence → cross-check → synthesize → test → present recommendation`

## Specialist examples

- repository explorer
- requirements analyst
- architect
- coder
- test engineer
- debugger
- security reviewer
- dependency reviewer
- performance engineer
- UX/accessibility reviewer
- data analyst
- documentation writer
- release engineer
- DevOps/CI specialist
- integration specialist
- benchmark evaluator

## Multi-agent rules

- Use multiple specialists when the task crosses disciplines.
- Give each specialist a bounded objective.
- Prefer independent verification for high-impact conclusions.
- Preserve evidence and disagreements.
- The synthesizer must not hide uncertainty.
- Do not let agent count become a proxy for quality.

## User control

Buddy may recommend a plan automatically, but consequential writes, merges, deployments, financial actions, communications, and device control follow the user's configured approval policy.
