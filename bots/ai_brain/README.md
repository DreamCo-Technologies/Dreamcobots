# DreamCo AI Brain — Decision Engine

Weighted, data-driven decision engine for the DreamCo autonomous system.

## Overview

The Decision Engine replaces the original random-choice decision logic with a
fully explainable, weighted algorithm that analyses three data sources before
committing to an action:

| Source | Description |
|--------|-------------|
| Revenue data | Per-source USD revenue; low-revenue areas are boosted |
| CRM trends | Bot conversion rates; bottom performers trigger corrective actions |
| Workflow data | Error rates per pipeline step; bottlenecks take top priority |

## Tiers

| Tier | Price | Features |
|------|-------|----------|
| FREE | $0/mo | Basic revenue analysis, 5 decision options |
| PRO | $49/mo | Revenue + CRM analysis, bottleneck detection, decision history |
| ENTERPRISE | $199/mo | All PRO features + full CRM integration, autonomous cycles, API |

## Quick start

```python
from bots.ai_brain.decision_engine import DecisionEngine
from bots.ai_brain.tiers import Tier

engine = DecisionEngine(tier=Tier.PRO)

result = engine.make_decision(
    revenue_data={"lead_gen": 80.0, "sales": 600.0, "real_estate": 40.0},
    crm_data={
        "lead_gen_bot": {"conversion_rate": 0.06},
        "sales_bot":    {"conversion_rate": 0.22},
    },
    workflow_data={
        "lead_scraping": {"error_rate": 0.02},
        "sms_outreach":  {"error_rate": 0.15},
    },
)

print(result["decision"]["key"])    # e.g. "fix_bottleneck"
print(result["decision"]["reason"]) # human-readable explanation
```
