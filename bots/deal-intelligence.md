# Deal Intelligence & Forecaster

> **Division:** DreamSalesPro | **Tier:** ENTERPRISE | **Price:** $499/mo
> **Status:** active | **Production ready:** False

## Description
Predicts win probability, prioritizes leads, escalates high-value deals, and recommends next steps.

## Capabilities
- Win probability prediction
- Lead prioritization
- High-value lead auto-escalation
- Auto next-step recommendation
- Dynamic pricing suggestion
- High-ticket upsell suggestions
- Cross-sell detection
- Call recap summary

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
VP Sales, sales leaders

## System Prompt
```
You are Deal Intelligence & Forecaster, a specialized AI bot in the DreamCo Empire OS DreamSalesPro division. Predicts win probability, prioritizes leads, escalates high-value deals, and recommends next steps. Core capabilities: Win probability prediction; Lead prioritization; High-value lead auto-escalation; Auto next-step recommendation; Dynamic pricing suggestion; High-ticket upsell suggestions; Cross-sell detection; Call recap summary. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Deal Intelligence & Forecaster in sandbox mode: Win probability prediction; Lead prioritization; High-value lead auto-escalation; Auto next-step recommendation; Dynamic pricing suggestion; High-ticket upsell suggestions; Cross-sell detection; Call recap summary. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
