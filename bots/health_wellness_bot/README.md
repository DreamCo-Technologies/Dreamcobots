# Health & Wellness Bot

A tier-aware health tracking and wellness management bot on the Dreamcobots platform.

---

## Tier Overview

| Tier       | Price/month | Requests/month | Support          |
|------------|-------------|----------------|------------------|
| Free       | $0.00       | 500            | Community        |
| Pro        | $49.00      | 10,000         | Email (48 h SLA) |
| Enterprise | $299.00     | Unlimited       | Dedicated 24/7   |

---

## Features per Tier

| Feature                          | Free | Pro | Enterprise |
|---------------------------------|------|-----|------------|
| BMI calculation                  | ✓    | ✓   | ✓          |
| Basic calorie tracking           | ✓    | ✓   | ✓          |
| Step counter                     | ✓    | ✓   | ✓          |
| Macro nutrient tracking          |      | ✓   | ✓          |
| Workout plans                    |      | ✓   | ✓          |
| Sleep tracking                   |      | ✓   | ✓          |
| Heart rate zones                 |      | ✓   | ✓          |
| Progress photos (5/month)        |      | ✓   | ✓          |
| AI health coach                  |      |     | ✓          |
| Integration with health devices  |      |     | ✓          |
| Medical record summaries         |      |     | ✓          |
| Personalized nutrition plans     |      |     | ✓          |
| Telehealth scheduling            |      |     | ✓          |

---

## Quick Start

```python
import sys
sys.path.insert(0, "bots/ai-models-integration")
from tiers import Tier
from bots.health_wellness_bot.health_wellness_bot import HealthWellnessBot

# Calculate BMI
bot = HealthWellnessBot(tier=Tier.FREE)
bmi = bot.calculate_bmi(70.0, 1.75)
print(bmi)

# Log a workout
workout = bot.log_workout("running", 30, 300)
print(workout)

# Log nutrition (basic on all tiers)
meal = bot.log_nutrition("Lunch", 600)
print(meal)

# Pro tier — track macros
pro_bot = HealthWellnessBot(tier=Tier.PRO)
pro_bot.log_nutrition("Dinner", 800, {"protein": 40, "carbs": 80, "fat": 25})

# Health summary
summary = bot.get_health_summary()
print(summary)

# Tier info
bot.describe_tier()
bot.show_upgrade_path()
```

---

## Directory Structure

```
bots/health_wellness_bot/
├── health_wellness_bot.py  # Main bot class
├── tiers.py                # Bot-specific tier config
├── __init__.py
└── README.md               # This file
```
