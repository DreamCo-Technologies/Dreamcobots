# Owner Dashboard — Global Bot Network

Provides each DreamCo bot owner with a real-time view of their bots, chat feeds, activity logs, earnings, and kill-switch controls.

## Features

- Registered bot list per owner
- Live chat feed (last N messages per bot)
- Activity log with timestamps
- Earnings tracker with per-bot breakdown
- Kill switch — instantly disable a bot
- Designed to be backed by Firebase / Socket.IO in production

## Source

Implementation: [`bots/global_bot_network/owner_dashboard.py`](../../bots/global_bot_network/owner_dashboard.py)

## Usage

```python
from bots.global_bot_network.owner_dashboard import OwnerDashboard

dash = OwnerDashboard(owner_id="owner-001")
dash.register_bot("bot-123", name="SalesBot")
dash.log_activity("bot-123", "deal_closed", {"amount": 500})
print(dash.render())
```
