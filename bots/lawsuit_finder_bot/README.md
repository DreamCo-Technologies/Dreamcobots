# Lawsuit Finder Bot

Tier-aware legal case research and lawsuit discovery assistant for the
Dreamcobots platform.

> **DISCLAIMER:** This bot provides informational assistance only and does not
> constitute legal advice.  Always consult a qualified attorney for legal
> matters.

---

## Overview

The Lawsuit Finder Bot helps individuals and businesses search court records,
locate class action lawsuits, look up statutes, track settlement amounts, and
connect with attorneys — all through a conversational interface.

---

## Tiers & Pricing

| Tier | Price/month | Requests/month | Highlights |
|---|---|---|---|
| **Free** | $0 | 500 | Public case search, statute lookup, jurisdiction info |
| **Pro** | $49 | 10,000 | Class action finder, settlement tracker, attorney matcher |
| **Enterprise** | $299 | Unlimited | PACER integration, litigation analytics, mass tort pipeline |

---

## Quick Start

```python
from bots.lawsuit_finder_bot import LawsuitFinderBot
from bots.ai_chatbot.tiers import Tier

bot = LawsuitFinderBot(tier=Tier.PRO)

# Natural-language chat
response = bot.chat("Find class action lawsuits against pharmaceutical companies")
print(response["message"])
print(response["disclaimer"])

# Structured case search
result = bot.search_cases("breach of contract", jurisdiction="CA")
print(result["cases"])

# Find class actions by industry
result = bot.find_class_actions("tech")
print(result["results"])
```

---

## Available Tools

### Free
- `case_search` — search public court databases (PACER public access)
- `statute_lookup` — look up federal and state statutes
- `jurisdiction_info` — information on court jurisdictions

### Pro (includes all Free)
- `class_action_finder` — active and settled class action lawsuits
- `settlement_tracker` — settlement amounts and claim deadlines
- `attorney_matcher` — find attorneys specializing in relevant areas
- `case_alerts` — email notifications for new relevant filings

### Enterprise (includes all Pro)
- `litigation_analytics` — trends, win rates, judge and venue analysis
- `pacer_integration` — direct PACER and RECAP data access
- `outcome_predictor` — AI-based case outcome probability scoring
- `mass_tort_aggregator` — aggregate claimant data for mass tort cases

---

## Monetization

- **SaaS subscription** — FREE / PRO ($49/mo) / ENTERPRISE ($299/mo)
- **Lead generation** — attorney referral fee model on PRO/ENTERPRISE
- **API pay-per-use** — per-search pricing for law firms and legal tech
- **White-label** — branded legal research portals (ENTERPRISE)

---

## BuddyAI Integration

```python
from BuddyAI import BuddyBot
from bots.lawsuit_finder_bot import LawsuitFinderBot
from bots.ai_chatbot.tiers import Tier

buddy = BuddyBot()
buddy.register_bot("legal", LawsuitFinderBot(tier=Tier.PRO))
response = buddy.chat("legal", "Are there class action suits against my employer?")
print(response["message"])
print(response["disclaimer"])
```

---

## Directory Structure

```
bots/lawsuit_finder_bot/
├── lawsuit_finder_bot.py   # Main bot class
├── tiers.py                # Tier config (tools & features)
├── __init__.py
└── README.md
```

## Running Tests

```bash
python -m pytest tests/test_lawsuit_finder_bot.py -v
```
