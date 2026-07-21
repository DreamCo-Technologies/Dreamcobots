# Revenue Growth Bot

A tier-aware revenue analytics and pricing optimization bot on the Dreamcobots platform.

---

## Tier Overview

| Tier       | Price/month | Requests/month | Product Limit | Support          |
|------------|-------------|----------------|---------------|------------------|
| Free       | $0.00       | 500            | 3             | Community        |
| Pro        | $49.00      | 10,000         | 50            | Email (48 h SLA) |
| Enterprise | $299.00     | Unlimited       | Unlimited     | Dedicated 24/7   |

---

## Features per Tier

| Feature                         | Free | Pro | Enterprise |
|--------------------------------|------|-----|------------|
| Basic sales analytics           | ✓    | ✓   | ✓          |
| Revenue tracking                | ✓    | ✓   | ✓          |
| 3 product listings              | ✓    |     |            |
| Advanced analytics              |      | ✓   | ✓          |
| Pricing optimization            |      | ✓   | ✓          |
| 50 product listings             |      | ✓   |            |
| Conversion funnel analysis      |      | ✓   | ✓          |
| A/B testing (2 variants)        |      | ✓   | ✓          |
| Unlimited products              |      |     | ✓          |
| AI pricing engine               |      |     | ✓          |
| Competitor analysis             |      |     | ✓          |
| Revenue forecasting             |      |     | ✓          |
| Custom dashboards               |      |     | ✓          |
| CRM integration                 |      |     | ✓          |

---

## Quick Start

```python
import sys
sys.path.insert(0, "bots/ai-models-integration")
from tiers import Tier
from bots.revenue_growth_bot.revenue_growth_bot import RevenueGrowthBot

# Free tier — revenue analysis
bot = RevenueGrowthBot(tier=Tier.FREE)
result = bot.analyze_revenue({"sales": [1000, 1200, 1100, 1400]})
print(result)

# Pro tier — pricing optimization
pro_bot = RevenueGrowthBot(tier=Tier.PRO)
price = pro_bot.optimize_pricing({"name": "Widget", "current_price": 49.99})
print(price)

# Enterprise — revenue forecast
ent_bot = RevenueGrowthBot(tier=Tier.ENTERPRISE)
forecast = ent_bot.forecast_revenue(period_months=6)
print(forecast)

# Tier info
bot.describe_tier()
bot.show_upgrade_path()
```

---

## Directory Structure

```
bots/revenue_growth_bot/
├── revenue_growth_bot.py  # Main bot class
├── tiers.py               # Bot-specific tier config
├── __init__.py
└── README.md              # This file
```
