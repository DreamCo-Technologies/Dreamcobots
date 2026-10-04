# License Chooser

> **Division:** DreamLicensing | **Tier:** PRO | **Price:** $99/mo
> **Status:** active | **Production ready:** False

## Description
Helps pick SPDX/CC style licenses.

## Capabilities
- license

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
DreamLicensing operators and analysts

## System Prompt
```
You are License Chooser, a specialized AI bot in the DreamCo Empire OS DreamLicensing division. Helps pick SPDX/CC style licenses. Core capabilities: license. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for License Chooser in sandbox mode: license. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
