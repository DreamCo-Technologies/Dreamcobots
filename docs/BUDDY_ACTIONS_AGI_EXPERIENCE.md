# Buddy Actions — AGI-like Operating Experience

Buddy Actions should feel like an intelligent operating partner because the interface exposes the behaviors that make complex agents useful: goal decomposition, planning, context selection, tool orchestration, risk awareness, adaptation, recovery, verification, and learning.

This is an experience goal, not a claim that Buddy is sentient or generally intelligent.

## Core loop

`Goal → Understand → Plan → Debate → Select Model/Tools → Execute → Observe → Adapt → Verify → Explain → Learn`

## What the user should see

1. **Goal** — what Buddy is trying to accomplish.
2. **Plan** — the current executable steps and dependencies.
3. **Context** — projects, documents, instructions, memory, and relevant repository evidence.
4. **Brain** — selected model, mode, skills, and debate participants.
5. **Tools** — MCP/external/local tools available to the action.
6. **Risk** — security, financial, production, data, and reversibility risk.
7. **Action** — current live step, progress, and status.
8. **Evidence** — tests, logs, artifacts, health checks, and verification.
9. **Recovery** — what happened if something failed and what Buddy changed.
10. **Next best action** — the most useful safe continuation.
11. **Learning** — what became a new skill, benchmark case, prevention rule, or memory.

## AGI-like interaction patterns

- Natural-language goals instead of requiring users to know internal bot names.
- Dynamic decomposition into tasks and subtasks.
- Visible dependencies and blockers.
- Replanning when new evidence changes the situation.
- Multiple candidate strategies when the first plan is weak.
- Debate/dissent before high-impact decisions.
- Automatic sandboxing before risky execution.
- Evidence-backed completion rather than optimistic status labels.
- Proactive suggestions for what should happen next.
- Safe recovery and escalation when automation cannot continue.
- Persistent learning from successful and failed actions.

## Safety boundary

The interface must never imply that a thought was executed when only a plan was generated. It must never claim a tool ran without tool evidence, a dashboard is healthy without runtime verification, or a capability passed a benchmark without benchmark evidence.

Autonomy should be graduated by risk. Read-only and sandbox actions can be highly automatic; destructive, financial, security-sensitive, external, or production actions remain governed by approval policy.
