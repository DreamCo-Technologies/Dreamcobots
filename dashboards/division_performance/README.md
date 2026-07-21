# Division Performance Dashboard

Tracks revenue, growth, API utilization, and bot performance across all DreamCo divisions.

## Features

- Division revenue recording and summaries
- Month-over-month growth analysis
- 6-month revenue projection (ENTERPRISE)
- API call metrics per endpoint and division
- Bot performance insights
- Predictive analytics (ENTERPRISE)

## Tiers

| Tier       | Revenue Tracking | Growth Analysis | API Metrics | Bot Insights | Predictive |
|------------|-----------------|-----------------|-------------|--------------|------------|
| FREE       | ✗               | ✗               | ✗           | ✗            | ✗          |
| PRO        | ✓               | ✓               | ✓           | ✓            | ✗          |
| ENTERPRISE | ✓               | ✓               | ✓           | ✓            | ✓          |

## Source

Implementation: [`bots/division_performance_dashboard/division_performance_dashboard.py`](../../bots/division_performance_dashboard/division_performance_dashboard.py)

## Usage

```python
from bots.division_performance_dashboard.division_performance_dashboard import DivisionPerformanceDashboard
from bots.division_performance_dashboard.tiers import Tier

dashboard = DivisionPerformanceDashboard(tier=Tier.PRO)
dashboard.add_division_revenue("div-1", "Marketing", 50000, 12000, month=1, year=2026)
print(dashboard.get_revenue_summary())
```
