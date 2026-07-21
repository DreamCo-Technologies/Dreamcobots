# AnalyticsDashboardBot

A tier-aware bot for tracking metrics, calculating ROI, and generating reports.

## Tiers
- **FREE**: 3 metric types, 30-day history, CSV export
- **PRO**: 20 metric types, 90-day history, funnel analysis, ROI tracking
- **ENTERPRISE**: Unlimited metrics, custom KPIs, predictive analytics

## Usage
```python
from bots.analytics_dashboard_bot import AnalyticsDashboardBot
from tiers import Tier

bot = AnalyticsDashboardBot(tier=Tier.PRO)
bot.track_metric("page_views", 1500, channel="website")
summary = bot.get_dashboard_summary()
```
