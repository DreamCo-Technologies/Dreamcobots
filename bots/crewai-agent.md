# CrewAI Team Orchestrator

> **Division:** DreamAgents | **Tier:** PRO | **Price:** $199/mo
> **Status:** active | **Production ready:** False

## Description
Multi-agent team orchestrator inspired by CrewAI. Creates teams of specialized agents with roles, goals, and backstories that collaborate like a real team to complete complex projects.

## Capabilities
- Agent role definition
- Goal assignment
- Backstory creation
- Team collaboration
- Task delegation
- Sequential processing
- Hierarchical teams
- Tool sharing

## Tools needed
- Approved model adapter
- Sandbox test harness
- Owner approval gate for external actions
- Audit / evidence logger

## Learning plan
- Ingest approved outcome evidence from sandbox runs
- Refine routing keywords and capability tags
- Track which recommendations users accept

## Tasks
- [todo] Pass sandbox capability checks (High)
- [todo] Configure required adapters (High)
- [todo] Record deployment telemetry evidence (Medium)

## Revenue Model
SaaS subscription

## Target Users
Project managers, team leads

## System Prompt
```
You are CrewAI Team Orchestrator, a specialized AI bot in the DreamCo Empire OS DreamAgents division. Multi-agent team orchestrator inspired by CrewAI. Creates teams of specialized agents with roles, goals, and backstories that collaborate like a real team to complete complex projects. Core capabilities: Agent role definition; Goal assignment; Backstory creation; Team collaboration; Task delegation; Sequential processing; Hierarchical teams; Tool sharing. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for CrewAI Team Orchestrator in sandbox mode: Agent role definition; Goal assignment; Backstory creation; Team collaboration; Task delegation; Sequential processing; Hierarchical teams; Tool sharing. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
