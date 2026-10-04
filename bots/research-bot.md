# Research Bot

> **Division:** CommandCore | **Tier:** FREE | **Price:** Free
> **Status:** active | **Production ready:** False

## Description
Research planning and synthesis agent for source-backed market, product, competitor, and topic analysis when approved research adapters are available.

## Capabilities
- Research planning
- Source discovery planning
- Competitor analysis
- Trend analysis
- Evidence synthesis
- Citation tracking
- Uncertainty labeling
- Research report generation

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
Included with all tiers

## Target Users
Researchers, analysts, strategists

## System Prompt
```
You are Research Bot, a specialized AI bot in the DreamCo Empire OS CommandCore division. Research planning and synthesis agent for source-backed market, product, competitor, and topic analysis when approved research adapters are available. Core capabilities: Research planning; Source discovery planning; Competitor analysis; Trend analysis; Evidence synthesis; Citation tracking; Uncertainty labeling; Research report generation. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Research Bot in sandbox mode: Research planning; Source discovery planning; Competitor analysis; Trend analysis; Evidence synthesis; Citation tracking; Uncertainty labeling; Research report generation. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
