# Big Bro AI — Master Dashboard

Unified view aggregating data from all Big Bro AI sub-systems into a single, executive-level dashboard.

## Panels

| Panel                  | Description                                      |
|------------------------|--------------------------------------------------|
| `overview`             | High-level system health and revenue snapshot    |
| `memory_system`        | Memory engine status and storage metrics         |
| `bot_factory`          | Bot creation and deployment activity             |
| `continuous_study`     | Ongoing learning and research progress           |
| `prospectus_system`    | Business prospectus generation stats             |
| `courses_system`       | Course completion and engagement metrics         |
| `route_gps`            | Route navigation and optimization data           |
| `sales_monetization`   | Sales pipeline and revenue conversion            |
| `catalog_franchise`    | Franchise catalog health and listings            |
| `mentor_engine`        | Mentorship sessions and learner progress         |

## Source

Implementation: [`bots/big_bro_ai/master_dashboard.py`](../../bots/big_bro_ai/master_dashboard.py)

## Usage

```python
from bots.big_bro_ai.master_dashboard import MasterDashboard

dash = MasterDashboard()
snap = dash.snapshot()
print(dash.render(snap))
```
