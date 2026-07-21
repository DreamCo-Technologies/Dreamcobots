# DreamCo Job Titles Bot

> Replace manual labor with intelligent bots — covering every known job title.

## Overview

The **Job Titles Bot** is a tier-aware DreamCo automation platform that:

- **Searches** 100+ job titles across 25+ industries.
- **Generates** a dedicated automation bot for any job role in seconds.
- **Trains** humans and AI agents for face recognition, object recognition, and item valuation (antiques, coins, currency).
- **Justifies** costs autonomously — explains ROI, presents payment options, and decides whether to proceed.
- **Propagates** Buddy Bot upgrades to all deployed job bots instantly.

## Tiers

| Tier       | Price        | Job Titles | Bot Generation | Item Valuation | Face Recognition |
|------------|-------------|------------|----------------|----------------|------------------|
| FREE       | $0/month    | 50         | ✗              | ✗              | ✗                |
| PRO        | $49/month   | 1,000+     | ✓              | ✓              | ✗                |
| ENTERPRISE | $299/month  | Unlimited  | ✓              | ✓              | ✓                |

## Quick Start

```python
from bots.job_titles_bot import JobTitlesBot, Tier

# Browse job titles (free)
bot = JobTitlesBot()
results = bot.search_jobs("accountant")

# Generate a bot for any job (PRO+)
bot = JobTitlesBot(tier=Tier.PRO)
job_bot = bot.generate_bot("Data Analyst")
print(job_bot.chat("What can you do?"))

# Valuate an antique or coin (PRO+)
result = bot.valuate_item("1955 double-die penny", condition="excellent")
print(f"Estimated value: ${result.estimated_value_usd:,.2f}")

# Autonomous cost justification
report = bot.justify_cost("PRO Upgrade", monthly_usd=49.0, savings_usd=200.0)
print(bot.format_cost_report(report))

# Register with Buddy Bot
from BuddyAI.buddy_bot import BuddyBot
buddy = BuddyBot()
bot.register_with_buddy(buddy)
```

## Architecture

```
bots/job_titles_bot/
├── __init__.py
├── tiers.py                  — FREE / PRO / ENTERPRISE tier definitions
├── job_titles_database.py    — 100+ titles across 25+ industries
├── job_bot_generator.py      — creates job-specific automation bots
├── autonomous_trainer.py     — face/object recognition, item valuation, training
├── cost_justification.py     — autonomous ROI explanation & payment options
└── job_titles_bot.py         — main entry point (GlobalAISourcesFlow compliant)
```

## Payment Options

Clients can pay via:
- **Credit/Debit Card** (monthly or annual with 20% discount)
- **PayPal** (monthly)
- **DreamCo Tokens** (usage-based; 15% platform markup)

## Tests

```bash
pytest tests/test_job_titles_bot.py -v
```
