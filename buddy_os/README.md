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

## Existing DreamCo systems Buddy now maps to

The control plane deliberately reuses the repository's existing implementations instead of creating parallel bots and runtimes:

- `server/fleet-runtime.ts` — governed bot routing, sandbox execution, capability contracts, and end-to-end certification.
- `server/buddy-model-policy.ts` — model routing and free/premium approval policy.
- `dreamco_platform/automation/task_runner.py` — bounded scheduling, recurring work, checkpoints, pause/resume, and failure recovery.
- `tools/buddy_local_bridge.py` — loopback-only laptop actions and secure macOS Keychain intake.
- `tools/buddy_cli.py` — local Buddy command-center and preflight controls.
- `website/buddy-command-center.html/js` — user-facing task planning, capability routing, benchmark creation, and evidence journal.
- `config/buddy-connector-registry.json` — connection, authentication, secret-reference, and token-transfer policy.
- `.github/workflows/dreamco-control-center.yml` — repository health, fleet, website, resource, and full-test control.
- `.github/workflows/buddy-actions-test-lab.yml` — Buddy verification suites and evidence artifacts.

See `buddy_os/integration/runtime_map.yaml` for the authoritative mapping.

## Design principle

This is an additive control plane. Existing DreamCo bots and services remain the execution implementations; Buddy provides common contracts and orchestration rather than duplicating every bot.

## Truth contract

A registered dashboard is not automatically live. A catalog entry is not a provider connection. A declared capability is not a benchmark pass. A sandbox run is not a live external action. Buddy must preserve these distinctions in UI, APIs, reports, and autonomous decisions.

## Safety

Command execution, deployments, external tools, payments, and destructive repository operations should be permission-gated. Autonomous mode must respect repository governance and approval policies. Secrets and credentials are never persisted in Buddy memory contracts.

## Verification

`tests/test_buddy_os_contracts.py` verifies the new contracts and their links to existing runtime components. `.github/workflows/buddy-os-contracts.yml` runs those checks automatically for relevant changes.
