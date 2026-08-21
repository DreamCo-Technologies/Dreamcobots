# Buddy AI Operating System

Buddy is the master orchestration layer for DreamCo. This package defines a modular control plane for task intake, model selection, memory, autonomous debate, bot execution, MCP integrations, dashboards, and skills.

## Layers

1. **Input** — role, task, requirements, intent, goals, priority, and risk.
2. **Processing** — context assembly, model routing, extended-thinking mode, planning, multi-agent coordination, and validation.
3. **Memory** — project memory, document library, instructions, semantic/episodic/long-term memory, and pluggable storage.
4. **Debate** — architect, security, performance, compliance, revenue, QA, and Buddy decision agents.
5. **Execution** — text/JSON/report output, agent modes, command runners, bot controls, and MCP tools.
6. **Control Center** — live dashboard registry and repository-backed bot controls.
7. **Skills** — a registry of capabilities Buddy can discover, train, test, and assign.

## Design principle

This is an additive control plane. Existing DreamCo bots and services remain the execution implementations; Buddy provides common contracts and orchestration rather than duplicating every bot.

## Safety

Command execution, deployments, external tools, payments, and destructive repository operations should be permission-gated. Autonomous mode must respect repository governance and approval policies.
