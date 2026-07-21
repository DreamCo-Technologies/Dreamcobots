# Payments Reporting Dashboard

Financial reporting dashboard for DreamCo Payments, including bot-performance tracking and Discount Dominator settings management (IDs 401–600).

## Features

- Revenue and payment summaries
- Bot performance tracking
- Discount Dominator settings (IDs 401–600) across 5 groups:
  - `analytics` (401–450)
  - `in_store` (451–500)
  - `online` (501–550)
  - `enterprise` (551–580)
  - `behavioral` (581–600)
- Report export (JSON / CSV / PDF based on tier)

## Tiers

| Tier       | View Settings | Update Settings | Export Formats        |
|------------|--------------|-----------------|----------------------|
| STARTER    | ✓            | ✗               | JSON                  |
| GROWTH     | ✓            | ✓               | JSON, CSV             |
| ENTERPRISE | ✓            | ✓               | JSON, CSV, PDF        |

## Source

Implementation: [`bots/dreamco_payments/reporting_dashboard.py`](../../bots/dreamco_payments/reporting_dashboard.py)

## Usage

```python
from bots.dreamco_payments.reporting_dashboard import ReportingDashboard
from bots.dreamco_payments.tiers import Tier

dash = ReportingDashboard(tier=Tier.GROWTH)
print(dash.get_analytics_summary())
dash.export_report(format="csv")
```
