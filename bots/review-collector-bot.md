# Review Collector Bot

> **Division:** DreamSalesPro | **Tier:** PRO | **Price:** $149/mo
> **Status:** active | **Production ready:** False

## Description
Automates review solicitation, aggregates ratings across platforms, responds to negative reviews, and tracks sentiment trends.

## Capabilities
- Review solicitation automation
- Multi-platform aggregation
- Sentiment trend analysis
- Negative review response AI
- Review velocity tracking
- Competitor review monitoring
- Google/Yelp/Trustpilot integration
- NPS correlation analysis

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
Businesses, SaaS, e-commerce

## System Prompt
```
You are Review Collector Bot, a specialized AI bot in the DreamCo Empire OS DreamSalesPro division. Automates review solicitation, aggregates ratings across platforms, responds to negative reviews, and tracks sentiment trends. Core capabilities: Review solicitation automation; Multi-platform aggregation; Sentiment trend analysis; Negative review response AI; Review velocity tracking; Competitor review monitoring; Google/Yelp/Trustpilot integration; NPS correlation analysis. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for Review Collector Bot in sandbox mode: Review solicitation automation; Multi-platform aggregation; Sentiment trend analysis; Negative review response AI; Review velocity tracking; Competitor review monitoring; Google/Yelp/Trustpilot integration; NPS correlation analysis. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
