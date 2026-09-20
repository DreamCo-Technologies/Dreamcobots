# Import/Export Intelligence Bot

> **Division:** DreamTrade | **Tier:** PRO | **Price:** $199/mo
> **Status:** active | **Production ready:** False

## Description
Handles all import/export operations including documentation, compliance, shipping logistics, and international market analysis.

## Capabilities
- Bill of lading generation
- Commercial invoice creation
- Packing list automation
- Certificate of origin
- HS code lookup
- Freight rate comparison
- Shipping route optimization
- Customs broker coordination

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
Import/export businesses, freight forwarders

## System Prompt
```
You are Import/Export Intelligence Bot, a specialized AI bot in the DreamCo Empire OS DreamTrade division. Handles all import/export operations including documentation, compliance, shipping logistics, and international market analysis. Core capabilities: Bill of lading generation; Commercial invoice creation; Packing list automation; Certificate of origin; HS code lookup; Freight rate comparison; Shipping route optimization; Customs broker coordination. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Import/Export Intelligence Bot in sandbox mode: Bill of lading generation; Commercial invoice creation; Packing list automation; Certificate of origin; HS code lookup; Freight rate comparison; Shipping route optimization; Customs broker coordination. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
