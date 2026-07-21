# Affiliate Bot

Tier-aware affiliate marketing automation bot. Recommends products, estimates income, tracks clicks, and generates performance reports.

## Tiers

| Feature | FREE | PRO | ENTERPRISE |
|---------|------|-----|------------|
| Niches | 3 | 10 | Unlimited |
| Products | 10 | 50 | Unlimited |
| Reports | Basic | Detailed | Custom |
| Earnings estimate | Basic | Advanced | AI-optimized |

## Usage

```python
from bots.affiliate_bot.affiliate_bot import AffiliateBot
from tiers import Tier

bot = AffiliateBot(tier=Tier.PRO)
products = bot.recommend_products("tech")
income = bot.estimate_daily_income("fitness")
report = bot.generate_report()
```

## Methods

- `recommend_products(niche)` — returns list of affiliate products for a niche
- `estimate_daily_income(niche)` — estimates daily affiliate earnings
- `track_clicks(product_id)` — logs a click and returns conversion stats
- `generate_report()` — generates performance summary report

## Directory Structure

```
bots/affiliate_bot/
├── affiliate_bot.py
├── tiers.py
├── __init__.py
└── README.md
```
