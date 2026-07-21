# DreamOps Dashboard

Formatted summary views for all DreamOps subsystems — anomaly detection, auto-scaling, operations commander, bottleneck detector, and more.

## Panels

| Panel                | Description                                     |
|----------------------|-------------------------------------------------|
| Anomaly Detection    | Active alerts by severity                       |
| Auto-Scaling         | Recent scaling events and last action           |
| Ops Commander        | System health — total, healthy, degraded, open incidents |
| Bottleneck Detector  | Detected bottlenecks and affected services      |
| Cost Reduction       | Savings opportunities identified                |
| Resilience Score     | Overall system resilience rating                |
| Task Delegation      | Pending and active delegated tasks              |
| Throughput           | Current throughput metrics per service          |

## Source

Implementation: [`bots/dreamops/dashboard.py`](../../bots/dreamops/dashboard.py)

## Usage

```python
from bots.dreamops.dreamops_bot import DreamOpsBot

bot = DreamOpsBot()
print(bot.render_dashboard())
```
