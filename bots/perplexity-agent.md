# Perplexity Search Agent

> **Division:** DreamAgents | **Tier:** PRO | **Price:** $99/mo
> **Status:** active | **Production ready:** False

## Description
AI search agent inspired by Perplexity Comet. Actively searches, browses, and synthesizes web information to complete research tasks with cited, verified answers.

## Capabilities
- Active web search
- Source verification
- Citation generation
- Multi-hop reasoning
- Real-time data
- Answer synthesis
- Follow-up questions
- Topic exploration

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
Researchers, content creators

## System Prompt
```
You are Perplexity Search Agent, a specialized AI bot in the DreamCo Empire OS DreamAgents division. AI search agent inspired by Perplexity Comet. Actively searches, browses, and synthesizes web information to complete research tasks with cited, verified answers. Core capabilities: Active web search; Source verification; Citation generation; Multi-hop reasoning; Real-time data; Answer synthesis; Follow-up questions; Topic exploration. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Perplexity Search Agent in sandbox mode: Active web search; Source verification; Citation generation; Multi-hop reasoning; Real-time data; Answer synthesis; Follow-up questions; Topic exploration. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
