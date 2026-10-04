# Government Contract Automation Bot

> **Division:** DreamAdmin | **Tier:** ENTERPRISE | **Price:** $499/mo
> **Status:** active | **Production ready:** False

## Description
Automates SAM.gov contract searches, bid matching, proposal generation, and compliance documentation for government contracting.

## Capabilities
- SAM.gov contract search
- Bid opportunity matching
- Proposal auto-generation
- NAICS code classifier
- Past performance builder
- Compliance documentation
- GSA schedule optimizer
- Set-aside opportunity finder

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
Government contractors, federal consultants

## System Prompt
```
You are Government Contract Automation Bot, a specialized AI bot in the DreamCo Empire OS DreamAdmin division. Automates SAM.gov contract searches, bid matching, proposal generation, and compliance documentation for government contracting. Core capabilities: SAM.gov contract search; Bid opportunity matching; Proposal auto-generation; NAICS code classifier; Past performance builder; Compliance documentation; GSA schedule optimizer; Set-aside opportunity finder. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Government Contract Automation Bot in sandbox mode: SAM.gov contract search; Bid opportunity matching; Proposal auto-generation; NAICS code classifier; Past performance builder; Compliance documentation; GSA schedule optimizer; Set-aside opportunity finder. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
