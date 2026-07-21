# Stack & Profit AI Bot

Tier-aware deal-stacking, penny-hunting, receipt-scanning, flip-finding, and coupon-stacking bot.
Implements the full DreamCo $1,000 Launch Plan pipeline.

## Tiers

| Feature | FREE | PRO | ENTERPRISE |
|---------|------|-----|------------|
| dealBot | 5 deals | 50 deals, 10 sources | Unlimited |
| pennyBot | Basic | All sources | Real-time alerts |
| receiptBot | ✗ | ✓ OCR scanning | Batch + auto-match |
| flipBot | ✗ | ✓ Local resale | Multi-city AI scoring |
| couponBot | 3 sources | All sources | Auto-stack |
| AI ranking | ✗ | ✓ | ✓ |
| Affiliate links | ✗ | ✓ | ✓ |
| Referral system | ✗ | ✗ | ✓ |
| White-label API | ✗ | ✗ | ✓ |

## Usage

```python
from bots.stack_and_profit_bot.stack_and_profit_bot import StackAndProfitBot
from tiers import Tier

bot = StackAndProfitBot(tier=Tier.PRO)

# Run all bots at once
results = bot.run_all_bots(min_profit=20.0)

# Get AI-ranked top deals
top = bot.get_top_deals(limit=10)

# Get alerts for high-profit deals
alerts = bot.get_alerts(top)

# Calculate profit for a custom deal
profit = bot.calculate_profit({"current": 25, "coupon": 5, "cashback": 3, "resale": 70})
```

## Data

`data/first_50_deals.json` — 50 preloaded high-profit deals across Walmart, Amazon,
Target, Dollar General, eBay, Facebook Marketplace, Walgreens, Best Buy, Home Depot, and more.

## Deal Sources

Electronics, appliances, groceries, apparel, tools, home goods, gaming, and outdoor categories —
the highest resale value categories for maximum profit.
