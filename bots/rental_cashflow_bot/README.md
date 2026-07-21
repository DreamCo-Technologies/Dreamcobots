# Rental Cash Flow Bot

A tier-aware bot for analyzing rental property cash flow, cap rate, cash-on-cash returns, and portfolio performance. Supports 10-year projections and tax benefit analysis on ENTERPRISE tier.

## Features by Tier

| Feature | FREE | PRO | ENTERPRISE |
|---|---|---|---|
| Properties tracked | 1 | 10 | Unlimited |
| Basic cash flow calc | ✓ | ✓ | ✓ |
| Cap rate & GRM | ✓ | ✓ | ✓ |
| Full expense modeling | — | ✓ | ✓ |
| Portfolio summary | — | ✓ | ✓ |
| 10-year projection | — | ✓ | ✓ |
| Depreciation / tax benefits | — | — | ✓ |

## Quick Start

```python
from bots.rental_cashflow_bot.rental_cashflow_bot import RentalCashflowBot
from tiers import Tier

# FREE tier
bot = RentalCashflowBot(tier=Tier.FREE)
result = bot.analyze_property("RNT001")
print(result["monthly_cashflow_usd"])
print(result["cap_rate_pct"])
print(result["cash_on_cash_return_pct"])

# PRO tier — full expense breakdown + portfolio
bot_pro = RentalCashflowBot(tier=Tier.PRO)
analysis = bot_pro.analyze_property("RNT001")
print(analysis["expense_breakdown"])
print(analysis["investment_grade"])   # A / B+ / B / C+ / C

portfolio = bot_pro.get_portfolio_summary()

# ENTERPRISE — 10-year projection
bot_ent = RentalCashflowBot(tier=Tier.ENTERPRISE)
proj = bot_ent.project_returns("RNT001", years=10)
print(proj["estimated_irr_pct"])
```

## Key Methods

| Method | Description |
|---|---|
| `analyze_property(address_or_id)` | Full cash flow analysis for one property |
| `get_portfolio_summary()` | Aggregate metrics across tracked properties (PRO+) |
| `add_property(property_dict)` | Add custom property to portfolio |
| `project_returns(pid, years=10)` | Multi-year return projection (PRO+) |
| `describe_tier()` | Print current tier features |
| `run()` | Execute the GlobalAISourcesFlow pipeline |

## Database

20 sample rental properties across: Austin, Phoenix, Nashville, Denver, Tampa, Charlotte, Atlanta, Dallas, Houston, Las Vegas.

## Metrics Computed

- Monthly & annual cash flow
- Net Operating Income (NOI)
- Cap Rate
- Gross Rent Multiplier (GRM)
- Cash-on-Cash Return
- Debt Service Coverage Ratio (DSCR)
- Annual depreciation (ENTERPRISE)
