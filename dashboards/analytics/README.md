# Analytics Dashboard Bot

Tier-aware analytics dashboard for tracking metrics, calculating ROI, and performing funnel analysis across all DreamCo channels.

## Features

- Multi-channel metric tracking (FREE: 3 metric types, PRO: 20, ENTERPRISE: unlimited)
- ROI calculation per campaign
- Funnel analysis (PRO/ENTERPRISE)
- Channel attribution breakdown
- Export in JSON, CSV, PDF (tier-dependent)

## Tiers

| Tier       | Metric Limit | Funnel Analysis | Export Formats |
|------------|-------------|-----------------|----------------|
| FREE       | 3 types     | ✗               | JSON           |
| PRO        | 20 types    | ✓               | JSON, CSV      |
| ENTERPRISE | Unlimited   | ✓               | JSON, CSV, PDF |

## Source

Implementation: [`bots/analytics_dashboard_bot/analytics_dashboard_bot.py`](../../bots/analytics_dashboard_bot/analytics_dashboard_bot.py)

## Usage

```python
from bots.analytics_dashboard_bot.analytics_dashboard_bot import AnalyticsDashboardBot
from tiers import Tier

bot = AnalyticsDashboardBot(tier=Tier.PRO)
bot.track_metric("revenue", 1500.0, channel="email")
summary = bot.get_dashboard_summary()
print(summary)
```
