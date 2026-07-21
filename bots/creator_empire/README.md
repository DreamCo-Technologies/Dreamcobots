# CreatorEmpire Bot

A multi-functional creator economy bot that equips digital creators with
everything they need to launch, grow, and monetise their brand — all governed
by the platform-wide FREE / PRO / ENTERPRISE tier system.

---

## Overview

| Module | File | Responsibility |
|--------|------|----------------|
| Tiers | `tiers.py` | Creator-economy feature flags and monetisation model lists per tier |
| Onboarding | `onboarding.py` | `OnboardingEngine` — profile creation, role assignment, action plans |
| Streaming | `streamer.py` | `StreamerEngine` — stream setup, go-live checklist, monetisation milestones |
| Event Planning | `event_planning.py` | `EventPlanningEngine` — event creation, task tracking, sponsor management |
| Monetization | `monetization.py` | `MonetizationEngine` — revenue models, ledger, strategy recommendations |
| Bot (main) | `creator_empire.py` | `CreatorEmpireBot` — unified interface over all four engines |

---

## Tier Overview

| Tier       | Price/month | API Calls/month | Key Creator Features                          |
|------------|-------------|-----------------|-----------------------------------------------|
| Free       | $0.00       | 500             | Basic profile, role onboarding, basic monetization |
| Pro        | $49.00      | 10,000          | + Branding kit, stream setup, event planner, analytics, contract templates |
| Enterprise | $299.00     | Unlimited        | + Sponsorship tools, social automation, AI branding, financial infra |

---

## Supported Creator Roles

`streamer`, `rapper`, `athlete`, `artist`, `content_creator`,
`podcaster`, `comedian`, `fitness_coach`, `gamer`, `dancer`

---

## Supported Revenue Models

| Model | Tiers |
|-------|-------|
| Tip Jar | Free, Pro, Enterprise |
| Basic Subscription | Free, Pro, Enterprise |
| Premium Subscription | Pro, Enterprise |
| Pay-Per-View | Pro, Enterprise |
| Merchandise | Pro, Enterprise |
| Direct Service Fee | Pro, Enterprise |
| Brand Deal | Enterprise |
| Licensing | Enterprise |
| Revenue Share | Enterprise |
| NFT / Digital Collectibles | Enterprise |

---

## Quick Start

```python
from bots.creator_empire.creator_empire import CreatorEmpireBot
from tiers import Tier  # bots/ai-models-integration/tiers.py

# Initialise on the Pro tier
bot = CreatorEmpireBot(tier=Tier.PRO)

# 1. Onboard a new streamer
profile = bot.onboard_creator("Alex", role="streamer", bio="Gaming & IRL streamer")
result  = bot.complete_onboarding("Alex")
print(result["action_plan"])          # Personalised 5-step plan

# 2. Set up streaming
cfg   = bot.setup_stream("Alex", platform="twitch", niche="gaming",
                          schedule=["Mon 18:00", "Thu 18:00"])
tips  = bot.get_stream_tips("gaming")
check = bot.get_go_live_checklist()

# 3. Plan an event
event = bot.create_event("Alex", "1k Celebration Stream",
                          "charity_stream", "2025-12-31", "twitch")
bot.complete_event_task(event.event_id, 0)
bot.add_event_sponsor(event.event_id, "Logitech")

# 4. Monetize
bot.enable_revenue_model("Alex", "subscription_basic")
bot.record_revenue("Alex", "tip_jar", 100.0, "streamlabs", "Stream tips")
print(bot.get_total_revenue("Alex"))  # 100.0
print(bot.get_revenue_breakdown("Alex"))

# 5. Tier information
bot.describe_tier()
bot.show_upgrade_path()
```

---

## Directory Structure

```
bots/creator_empire/
├── __init__.py          # Package marker
├── tiers.py             # Feature flags and monetisation models per tier
├── onboarding.py        # Talent Identity & Onboarding engine
├── streamer.py          # Streaming Launch System
├── event_planning.py    # Event Planning engine
├── monetization.py      # Revenue & Monetization engine
├── creator_empire.py    # Main bot class (orchestrates all engines)
└── README.md            # This file
```

---

## Running Tests

```bash
cd /path/to/Dreamcobots
pip install pytest
python -m pytest tests/test_creator_empire.py -v
```

109 tests covering all modules and the full end-to-end creator journey.

---

## Architecture Notes

* **Modular design** — each engine is independently instantiable and testable.
* **Tier-aware** — every feature gate check is performed at the engine level;
  the main bot class simply delegates to engines.
* **Extensible** — add new creator roles by appending to `CREATOR_ROLES` in
  `tiers.py` and adding entries in the role look-up dicts in `onboarding.py`.
* **Revenue ledger** — `MonetizationEngine` maintains an in-memory ledger that
  can be persisted to a database by injecting a storage adapter.
