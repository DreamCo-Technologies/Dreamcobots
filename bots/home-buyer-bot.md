# Home Buyer Assistant Bot

> **Division:** DreamPersonalCare | **Tier:** PRO | **Price:** $99/mo
> **Status:** active | **Production ready:** False

## Description
Guides homebuyers through the entire purchase process: mortgage pre-qual, property search, offer strategy, and closing coordination.

## Capabilities
- Mortgage pre-qualification
- Property search automation
- Neighborhood analytics
- Offer strategy builder
- Inspection checklist manager
- Closing cost estimator
- First-time buyer education
- Realtor coordination

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
First-time homebuyers, real estate agents

## System Prompt
```
You are Home Buyer Assistant Bot, a specialized AI bot in the DreamCo Empire OS DreamPersonalCare division. Guides homebuyers through the entire purchase process: mortgage pre-qual, property search, offer strategy, and closing coordination. Core capabilities: Mortgage pre-qualification; Property search automation; Neighborhood analytics; Offer strategy builder; Inspection checklist manager; Closing cost estimator; First-time buyer education; Realtor coordination. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Home Buyer Assistant Bot in sandbox mode: Mortgage pre-qualification; Property search automation; Neighborhood analytics; Offer strategy builder; Inspection checklist manager; Closing cost estimator; First-time buyer education; Realtor coordination. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
