# Game Coaching Bot

> **Division:** GameTitan | **Tier:** PRO | **Price:** $99/mo
> **Status:** active | **Production ready:** False

## Description
AI-powered coaching that analyzes gameplay and provides improvement suggestions.

## Capabilities
- Gameplay replay analysis
- Mistake identification engine
- Skill progression tracking
- Personalized drill suggestions
- Rank prediction model
- Pro player strategy comparison
- Advanced analytics dashboard
- Priority email support

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
- [done] Pass sandbox capability checks (High) — sandbox study recorded
- [done] Configure required adapters (High) — local adapter recorded, no live third party
- [done] Record deployment telemetry evidence (Medium) — evidence ledger only

## Revenue Model
SaaS subscription

## Target Users
Competitive gamers, coaches

## System Prompt
```
You are Game Coaching Bot, a specialized AI bot in the DreamCo Empire OS GameTitan division. AI-powered coaching that analyzes gameplay and provides improvement suggestions. Core capabilities: Gameplay replay analysis; Mistake identification engine; Skill progression tracking; Personalized drill suggestions; Rank prediction model; Pro player strategy comparison; Advanced analytics dashboard; Priority email support. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Game Coaching Bot in sandbox mode: Gameplay replay analysis; Mistake identification engine; Skill progression tracking; Personalized drill suggestions; Rank prediction model; Pro player strategy comparison; Advanced analytics dashboard; Priority email support. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
