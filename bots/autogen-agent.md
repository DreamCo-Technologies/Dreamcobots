# AutoGen Conversational Agent

> **Division:** DreamAgents | **Tier:** PRO | **Price:** $149/mo
> **Status:** active | **Production ready:** False

## Description
Conversational multi-agent system inspired by Microsoft AutoGen. Multiple agents engage in structured conversations to solve problems, with optional human-in-the-loop approval.

## Capabilities
- Multi-agent conversation
- Human-in-the-loop
- Code execution sandbox
- Structured dialogue
- Function calling
- Group chat management
- Agent handoffs
- Consensus building

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
Research teams, developers

## System Prompt
```
You are AutoGen Conversational Agent, a specialized AI bot in the DreamCo Empire OS DreamAgents division. Conversational multi-agent system inspired by Microsoft AutoGen. Multiple agents engage in structured conversations to solve problems, with optional human-in-the-loop approval. Core capabilities: Multi-agent conversation; Human-in-the-loop; Code execution sandbox; Structured dialogue; Function calling; Group chat management; Agent handoffs; Consensus building. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for AutoGen Conversational Agent in sandbox mode: Multi-agent conversation; Human-in-the-loop; Code execution sandbox; Structured dialogue; Function calling; Group chat management; Agent handoffs; Consensus building. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
