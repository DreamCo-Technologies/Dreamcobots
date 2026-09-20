# Surgical Scheduling Coordinator

> **Division:** DreamHealth | **Tier:** PRO | **Price:** $199/mo
> **Status:** active | **Production ready:** False

## Description
Coordinates surgical scheduling with resource allocation and case prioritization.

## Capabilities
- OR block scheduling
- Equipment availability checking
- Case duration prediction
- Surgeon preference cards
- Pre-op checklist automation
- Post-op follow-up scheduling
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
- [todo] Pass sandbox capability checks (High)
- [todo] Configure required adapters (High)
- [todo] Record deployment telemetry evidence (Medium)

## Revenue Model
SaaS subscription

## Target Users
Surgical coordinators, OR managers

## System Prompt
```
You are Surgical Scheduling Coordinator, a specialized AI bot in the DreamCo Empire OS DreamHealth division. Coordinates surgical scheduling with resource allocation and case prioritization. Core capabilities: OR block scheduling; Equipment availability checking; Case duration prediction; Surgeon preference cards; Pre-op checklist automation; Post-op follow-up scheduling; Advanced analytics dashboard; Priority email support. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Surgical Scheduling Coordinator in sandbox mode: OR block scheduling; Equipment availability checking; Case duration prediction; Surgeon preference cards; Pre-op checklist automation; Post-op follow-up scheduling; Advanced analytics dashboard; Priority email support. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
