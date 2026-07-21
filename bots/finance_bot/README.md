# Finance Bot

Tier-aware personal and business finance assistant for the Dreamcobots platform.

---

## Overview

The Finance Bot helps individuals and businesses track budgets, analyze
investments, estimate taxes, and generate compliance-ready financial reports —
all through a conversational interface.

---

## Tiers & Pricing

| Tier | Price/month | Requests/month | Highlights |
|---|---|---|---|
| **Free** | $0 | 500 | Budget tracker, expense categorization, savings planner |
| **Pro** | $49 | 10,000 | Portfolio analyzer, tax estimator, cash flow reports |
| **Enterprise** | $299 | Unlimited | Multi-entity consolidation, ERP sync, compliance reporting |

---

## Quick Start

```python
from bots.finance_bot import FinanceBot
from bots.ai_chatbot.tiers import Tier

bot = FinanceBot(tier=Tier.PRO)

# Natural-language chat
response = bot.chat("Analyze my Q3 cash flow")
print(response["message"])

# Direct tool call
result = bot.analyze("tax_estimator", {"income": 95000, "filing_status": "single"})
print(result["result"])
```

---

## Available Tools

### Free
- `budget_tracker` — track income vs. expenses month by month
- `expense_categorizer` — categorize spending automatically
- `savings_planner` — set and monitor savings goals

### Pro (includes all Free)
- `portfolio_analyzer` — evaluate investment portfolio performance
- `tax_estimator` — estimate W-2 and 1099 tax liability
- `cash_flow_report` — weekly/monthly cash flow statements
- `debt_payoff_calculator` — debt avalanche/snowball calculator

### Enterprise (includes all Pro)
- `multi_entity_consolidator` — consolidate financials across subsidiaries
- `compliance_reporter` — SOX, GAAP audit-ready reports
- `erp_sync` — connect to QuickBooks, SAP, NetSuite
- `scenario_modeler` — financial forecasting and what-if analysis

---

## Monetization

- **SaaS subscription** — FREE / PRO ($49/mo) / ENTERPRISE ($299/mo)
- **API pay-per-use** — per-analysis pricing on PRO/ENTERPRISE
- **Client deployment** — white-label financial portals on ENTERPRISE

---

## BuddyAI Integration

```python
from BuddyAI import BuddyBot
from bots.finance_bot import FinanceBot
from bots.ai_chatbot.tiers import Tier

buddy = BuddyBot()
buddy.register_bot("finance", FinanceBot(tier=Tier.PRO))
response = buddy.chat("finance", "What is my investment portfolio return this year?")
print(response["message"])
```

---

## Directory Structure

```
bots/finance_bot/
├── finance_bot.py   # Main bot class
├── tiers.py         # Tier config (tools & features)
├── __init__.py
└── README.md
```

## Running Tests

```bash
python -m pytest tests/test_finance_bot.py -v
```
