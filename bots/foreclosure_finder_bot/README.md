# Foreclosure Finder Bot

A tier-aware bot for finding foreclosure, pre-foreclosure, and REO properties. Provides discount-from-market analysis, title risk assessment, and an auction calendar.

## Features by Tier

| Feature | FREE | PRO | ENTERPRISE |
|---|---|---|---|
| County searches | 1 | 5 | Unlimited |
| Results per search | 5 | 25 | Unlimited |
| Basic foreclosure info | ✓ | ✓ | ✓ |
| Market discount % | ✓ | ✓ | ✓ |
| Lien & tax delinquency status | — | ✓ | ✓ |
| Auction calendar | — | ✓ | ✓ |
| Title risk assessment | — | ✓ | ✓ |
| Predictive foreclosure alerts | — | — | ✓ |
| Bank REO pipeline | — | — | ✓ |

## Quick Start

```python
from bots.foreclosure_finder_bot.foreclosure_finder_bot import ForeclosureFinderBot
from tiers import Tier

# FREE tier — search one county
bot = ForeclosureFinderBot(tier=Tier.FREE)
results = bot.search_foreclosures("cook", max_price=120000)
for prop in results:
    print(prop["address"], prop["discount_pct"], "%")

# Evaluate a specific listing
evaluation = bot.evaluate_foreclosure("FC001")
print(evaluation["risk_level"])        # LOW / MEDIUM / HIGH / VERY HIGH
print(evaluation["potential_gross_profit_usd"])

# PRO tier — auction calendar + title risks
bot_pro = ForeclosureFinderBot(tier=Tier.PRO)
auctions = bot_pro.get_auction_calendar()
title = bot_pro.check_title_risks("FC001")

# ENTERPRISE — predictive alerts
bot_ent = ForeclosureFinderBot(tier=Tier.ENTERPRISE)
detail = bot_ent.evaluate_foreclosure("FC001")
print(detail["predictive_alert"])
```

## Key Methods

| Method | Description |
|---|---|
| `search_foreclosures(county, max_price)` | Find foreclosures in a county |
| `evaluate_foreclosure(property_id)` | Risk assessment + discount analysis |
| `get_auction_calendar(county=None)` | Upcoming auctions (PRO+) |
| `check_title_risks(property_id)` | Lien/title risk report (PRO+) |
| `describe_tier()` | Print current tier features |
| `run()` | Execute the GlobalAISourcesFlow pipeline |

## Database

20 foreclosure listings across counties: Cook (IL), Maricopa (AZ), Harris (TX), Wayne (MI), Hillsborough (FL), Mecklenburg (NC), Cuyahoga (OH), Clark (NV), Fulton (GA), Davidson (TN), Dallas (TX), Marion (IN), Bexar (TX), Jefferson (KY), Sacramento (CA), Denver (CO), Wake (NC), East Baton Rouge (LA), King (WA), Hamilton (OH).

## Property Statuses

- `pre_foreclosure` — delinquent, not yet foreclosed
- `auction` — scheduled courthouse steps auction
- `reo` — bank-owned (Real Estate Owned) after failed auction
