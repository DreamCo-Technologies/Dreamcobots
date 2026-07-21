# Control Center

Central orchestration and monitoring dashboard for all Dreamcobots. Register bots, track income, run all bots, and view the monitoring dashboard.

## Usage

```python
from bots.control_center.control_center import ControlCenter
from bots.affiliate_bot.affiliate_bot import AffiliateBot
from bots.mining_bot.mining_bot import MiningBot
from tiers import Tier

cc = ControlCenter()
cc.register_bot("affiliate", AffiliateBot(tier=Tier.PRO))
cc.register_bot("mining", MiningBot(tier=Tier.PRO))

status = cc.get_status()
cc.add_income_entry("affiliate", 125.50)
summary = cc.get_income_summary()
results = cc.run_all()
dashboard = cc.get_monitoring_dashboard()
```

## Methods

- `register_bot(name, bot_instance)` — registers a bot with the control center
- `get_status()` — returns status of all registered bots
- `add_income_entry(source, amount)` — logs an income entry
- `get_income_summary()` — returns income summary across all sources
- `run_all()` — runs all registered bots and collects results
- `get_monitoring_dashboard()` — returns full monitoring dashboard

## Directory Structure

```
bots/control_center/
├── control_center.py
├── __init__.py
└── README.md
```
