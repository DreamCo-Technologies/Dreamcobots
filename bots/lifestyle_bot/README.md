# Lifestyle Bot

A tier-aware habit tracking and wellness management bot on the Dreamcobots platform.

---

## Tier Overview

| Tier       | Price/month | Requests/month | Habit Limit | Support          |
|------------|-------------|----------------|-------------|------------------|
| Free       | $0.00       | 500            | 5           | Community        |
| Pro        | $49.00      | 10,000         | Unlimited   | Email (48 h SLA) |
| Enterprise | $299.00     | Unlimited       | Unlimited   | Dedicated 24/7   |

---

## Features per Tier

| Feature                          | Free | Pro | Enterprise |
|---------------------------------|------|-----|------------|
| 5 habit trackers                 | ✓    |     |            |
| Daily reminders                  | ✓    | ✓   | ✓          |
| Basic goal setting               | ✓    | ✓   | ✓          |
| Unlimited habits                 |      | ✓   | ✓          |
| Habit analytics                  |      | ✓   | ✓          |
| Goal milestone tracking          |      | ✓   | ✓          |
| Mood journaling                  |      | ✓   | ✓          |
| Weekly reports                   |      | ✓   | ✓          |
| AI coaching                      |      |     | ✓          |
| Team habit challenges            |      |     | ✓          |
| Integration with wearables       |      |     | ✓          |
| Custom wellness programs         |      |     | ✓          |
| Advanced analytics               |      |     | ✓          |

---

## Quick Start

```python
import sys
sys.path.insert(0, "bots/ai-models-integration")
from tiers import Tier
from bots.lifestyle_bot.lifestyle_bot import LifestyleBot

# Track habits
bot = LifestyleBot(tier=Tier.FREE)
result = bot.track_habit("morning_run", True, "2025-01-15")
print(result)

# Set a goal
goal = bot.set_goal("Run a 5K", "2025-06-01")
print(goal)

# Get habits summary
summary = bot.get_habits_summary()
print(summary)

# Pro tier — mood journaling
pro_bot = LifestyleBot(tier=Tier.PRO)
mood = pro_bot.log_mood("happy", "Had a great workout!")
print(mood)

# Tier info
bot.describe_tier()
bot.show_upgrade_path()
```

---

## Directory Structure

```
bots/lifestyle_bot/
├── lifestyle_bot.py  # Main bot class
├── tiers.py          # Bot-specific tier config
├── __init__.py
└── README.md         # This file
```
