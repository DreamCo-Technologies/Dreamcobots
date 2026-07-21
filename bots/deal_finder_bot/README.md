# Deal Finder Bot

Tier-aware deal scanning and arbitrage automation bot. Scans marketplaces, evaluates deals, estimates profits, and surfaces the best opportunities.

## Tiers

| Feature | FREE | PRO | ENTERPRISE |
|---------|------|-----|------------|
| Platforms | 1 (eBay) | 5 | All platforms |
| Items | 10 | 100 | Unlimited |
| Deal scoring | Basic | Advanced | AI-powered |
| Arbitrage routing | ✗ | ✗ | ✓ |

## Usage

```python
from bots.deal_finder_bot.deal_finder_bot import DealFinderBot
from tiers import Tier

bot = DealFinderBot(tier=Tier.PRO)
deals = bot.scan_marketplace("amazon")
best = bot.get_best_deals(limit=5)
evaluation = bot.evaluate_deal(deals[0])
```

## Methods

- `scan_marketplace(platform)` — returns deals from a marketplace platform
- `evaluate_deal(item)` — returns deal score, margin, and recommendation
- `estimate_profit(item)` — returns estimated flip profit after fees
- `get_best_deals(limit)` — returns top deals sorted by profit potential

## Directory Structure

```
bots/deal_finder_bot/
├── deal_finder_bot.py
├── tiers.py
├── __init__.py
└── README.md
```
