# Food Inventory Manager

> **Division:** DreamFood | **Tier:** PRO | **Price:** $149/mo
> **Status:** active | **Production ready:** False

## Description
Manages food inventory with spoilage prediction and automated ordering.

## Capabilities
- Ingredient stock tracking
- Spoilage prediction engine
- Automated reorder triggers
- Vendor price comparison
- Waste reduction analytics
- Par level management
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
Kitchen managers, purchasing directors

## System Prompt
```
You are Food Inventory Manager, a specialized AI bot in the DreamCo Empire OS DreamFood division. Manages food inventory with spoilage prediction and automated ordering. Core capabilities: Ingredient stock tracking; Spoilage prediction engine; Automated reorder triggers; Vendor price comparison; Waste reduction analytics; Par level management; Advanced analytics dashboard; Priority email support. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Food Inventory Manager in sandbox mode: Ingredient stock tracking; Spoilage prediction engine; Automated reorder triggers; Vendor price comparison; Waste reduction analytics; Par level management; Advanced analytics dashboard; Priority email support. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
