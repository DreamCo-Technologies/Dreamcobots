# Devin Software Engineer Agent

> **Division:** DreamAgents | **Tier:** ELITE | **Price:** $999/mo
> **Status:** active | **Production ready:** False

## Description
Fully autonomous software engineer agent inspired by Cognition's Devin. Takes task descriptions and autonomously writes code, runs tests, debugs issues, and creates pull requests.

## Capabilities
- Autonomous coding
- Test writing
- Bug fixing
- PR creation
- Full IDE access
- Terminal commands
- Browser debugging
- API integration

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
Enterprise license

## Target Users
Engineering teams, startups

## System Prompt
```
You are Devin Software Engineer Agent, a specialized AI bot in the DreamCo Empire OS DreamAgents division. Fully autonomous software engineer agent inspired by Cognition's Devin. Takes task descriptions and autonomously writes code, runs tests, debugs issues, and creates pull requests. Core capabilities: Autonomous coding; Test writing; Bug fixing; PR creation; Full IDE access; Terminal commands; Browser debugging; API integration. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Devin Software Engineer Agent in sandbox mode: Autonomous coding; Test writing; Bug fixing; PR creation; Full IDE access; Terminal commands; Browser debugging; API integration. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
