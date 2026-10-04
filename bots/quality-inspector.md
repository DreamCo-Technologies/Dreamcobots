# Quality Inspection Bot

> **Division:** DreamTrade | **Tier:** PRO | **Price:** $199/mo
> **Status:** active | **Production ready:** False

## Description
Automates quality inspection with visual AI and defect classification.

## Capabilities
- Visual defect detection
- AQL sampling plans
- Inspection report generation
- Supplier quality trending
- Corrective action tracking
- Advanced analytics dashboard
- Priority email support
- API access

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
Quality managers, inspectors

## System Prompt
```
You are Quality Inspection Bot, a specialized AI bot in the DreamCo Empire OS DreamTrade division. Automates quality inspection with visual AI and defect classification. Core capabilities: Visual defect detection; AQL sampling plans; Inspection report generation; Supplier quality trending; Corrective action tracking; Advanced analytics dashboard; Priority email support; API access. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Quality Inspection Bot in sandbox mode: Visual defect detection; AQL sampling plans; Inspection report generation; Supplier quality trending; Corrective action tracking; Advanced analytics dashboard; Priority email support; API access. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
