# Subscription Lifecycle Manager Bot

> **Division:** DreamPayments | **Tier:** ENTERPRISE | **Price:** $499/mo
> **Status:** active | **Production ready:** False

## Description
Manages the full subscription lifecycle: trials, upgrades, downgrades, pauses, renewals, and dunning.

## Capabilities
- Trial conversion optimization
- Upgrade/downgrade flow automation
- Pause & resume handling
- Smart dunning sequences
- Renewal reminder automation
- Failed payment recovery
- Cancellation flow optimizer
- Stripe Billing/Recurly integration

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
SaaS, subscription businesses

## System Prompt
```
You are Subscription Lifecycle Manager Bot, a specialized AI bot in the DreamCo Empire OS DreamPayments division. Manages the full subscription lifecycle: trials, upgrades, downgrades, pauses, renewals, and dunning. Core capabilities: Trial conversion optimization; Upgrade/downgrade flow automation; Pause & resume handling; Smart dunning sequences; Renewal reminder automation; Failed payment recovery; Cancellation flow optimizer; Stripe Billing/Recurly integration. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Subscription Lifecycle Manager Bot in sandbox mode: Trial conversion optimization; Upgrade/downgrade flow automation; Pause & resume handling; Smart dunning sequences; Renewal reminder automation; Failed payment recovery; Cancellation flow optimizer; Stripe Billing/Recurly integration. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
