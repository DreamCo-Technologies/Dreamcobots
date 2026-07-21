# Roku TV Dashboard

Pushes KPI data to a Roku TV display for executive monitoring of the DreamCo ecosystem.

## Features

- Configurable device IP targeting
- Dark-theme KPI screen rendering
- Metrics: Revenue, Active Bots, Alerts, Throughput, Uptime
- Configurable refresh interval (default 30 s)
- Push log for audit trail

## Source

Implementation: [`ConnectionsControl/roku_dashboard.py`](../../ConnectionsControl/roku_dashboard.py)

## Usage

```python
from ConnectionsControl.roku_dashboard import RokuDashboard, KPIMetrics

dash = RokuDashboard()
dash.configure(device_ip="192.168.1.50")

metrics = KPIMetrics(
    revenue=125000.0,
    active_bots=34,
    alerts=2,
    throughput=98.5,
    uptime=99.7,
)
result = dash.push_dashboard(metrics)
print(result["screen"])
```
