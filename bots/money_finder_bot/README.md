# Money Finder Bot

Tier-aware unclaimed funds, government benefits, and cashback finder. Scans for unclaimed money, checks benefit eligibility, and surfaces cashback opportunities.

## Tiers

| Feature | FREE | PRO | ENTERPRISE |
|---------|------|-----|------------|
| Search scope | 1 US state | All US states | States + International |
| Benefits checker | ✗ | ✓ | ✓ |
| Automated recovery | ✗ | ✗ | ✓ |
| Bulk family search | ✗ | ✗ | ✓ |

## Usage

```python
from bots.money_finder_bot.money_finder_bot import MoneyFinderBot
from tiers import Tier

bot = MoneyFinderBot(tier=Tier.PRO)
funds = bot.scan_unclaimed_funds("John Smith", "CA")
benefits = bot.check_government_benefits({"annual_income_usd": 30000, "household_size": 3})
cashback = bot.find_cashback_opportunities()
report = bot.generate_recovery_report("John Smith")
```

## Methods

- `scan_unclaimed_funds(name, state)` — returns potentially unclaimed fund records
- `check_government_benefits(profile)` — returns eligible government programs (PRO+)
- `find_cashback_opportunities()` — returns cashback and rebate opportunities
- `generate_recovery_report(name)` — generates comprehensive recovery report

## Directory Structure

```
bots/money_finder_bot/
├── money_finder_bot.py
├── tiers.py
├── __init__.py
└── README.md
```
