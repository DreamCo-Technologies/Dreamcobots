# Automation Bot

A tier-aware task scheduling and workflow automation bot on the Dreamcobots platform.

---

## Tier Overview

| Tier       | Price/month | Requests/month | Task Limit | Support          |
|------------|-------------|----------------|------------|------------------|
| Free       | $0.00       | 500            | 5          | Community        |
| Pro        | $49.00      | 10,000         | 100        | Email (48 h SLA) |
| Enterprise | $299.00     | Unlimited       | Unlimited  | Dedicated 24/7   |

---

## Features per Tier

| Feature                              | Free | Pro | Enterprise |
|-------------------------------------|------|-----|------------|
| 5 scheduled tasks                   | ✓    |     |            |
| Basic triggers (time-based)         | ✓    | ✓   | ✓          |
| Email notifications                 | ✓    | ✓   | ✓          |
| 100 scheduled tasks                 |      | ✓   |            |
| Advanced triggers (webhook, event)  |      | ✓   | ✓          |
| Multi-step workflows                |      | ✓   | ✓          |
| Slack/Teams notifications           |      | ✓   | ✓          |
| Retry logic                         |      | ✓   | ✓          |
| Unlimited tasks                     |      |     | ✓          |
| Custom trigger types                |      |     | ✓          |
| Parallel workflow execution         |      |     | ✓          |
| Audit logging                       |      |     | ✓          |
| SLA monitoring                      |      |     | ✓          |
| Priority queue                      |      |     | ✓          |

---

## Quick Start

```python
import sys
sys.path.insert(0, "bots/ai-models-integration")
from tiers import Tier
from bots.automation_bot.automation_bot import AutomationBot

# Free tier
bot = AutomationBot(tier=Tier.FREE)
task = bot.create_task("daily_report", "daily@08:00", {"action": "send_email"})
print(task)

# Run a task
result = bot.run_task("daily_report")
print(result)

# List all tasks
print(bot.list_tasks())

# Pro tier — webhook trigger
pro_bot = AutomationBot(tier=Tier.PRO)
pro_bot.create_task("webhook_handler", "webhook://orders", {"action": "process_order"})

# Tier info
bot.describe_tier()
bot.show_upgrade_path()
```

---

## Directory Structure

```
bots/automation_bot/
├── automation_bot.py  # Main bot class
├── tiers.py           # Bot-specific tier config
├── __init__.py
└── README.md          # This file
```
