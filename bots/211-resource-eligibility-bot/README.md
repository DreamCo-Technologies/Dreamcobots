# 211 Resource & Eligibility Bot

## Overview

The **211 Resource & Eligibility Bot** helps individuals and families quickly find local social services and determine which assistance programs they qualify for — all without navigating complex government websites or waiting on hold.

Inspired by the national 211 helpline, this bot automates eligibility screening based on household income and family size, then surfaces relevant programs in categories like food assistance, housing, healthcare, utilities, and childcare.

Perfect for social workers, nonprofits, community organizations, and individuals seeking help.

---

## Features

| Feature | Description |
|---|---|
| **Eligibility Checker** | Enter income and family size to instantly see which programs you qualify for |
| **Resource Finder** | Search for services by location and category (food, housing, health, etc.) |
| **Category Filtering** | Narrow results to specific needs: food, housing, health, utility, childcare |
| **Multi-Platform Integration** | Push results to Zapier, N8n, Make.com workflows |
| **CLI Interface** | Simple interactive command-line interface for immediate use |
| **Human-Readable Output** | Formats resource lists with phone numbers and websites |

---

## Prerequisites

- Python 3.9+
- No external API keys required for basic use
- (Optional) Zapier / N8n webhook URL for integration

---

## Setup & Installation

### 1. Navigate to the bot directory

```bash
cd bots/211-resource-eligibility-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure environment

Create a `.env` file for webhook integration:

```env
WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/YOUR_HOOK_ID
DEFAULT_LOCATION=Austin, TX
MAX_RESULTS=10
```

---

## Usage

### Interactive CLI

```bash
python bot.py
```

You will be guided through:
1. Entering your income and family size
2. Viewing programs you qualify for
3. Searching for resources by location and category

### Programmatic Usage

```python
from bot import ResourceEligibilityBot

bot = ResourceEligibilityBot(config={"default_location": "Seattle, WA", "max_results": 5})

# Check eligibility
result = bot.check_eligibility({
    "annual_income": 28000,
    "family_size": 3,
    "location": "Seattle, WA"
})
print(result["summary"])
for program in result["eligible_programs"]:
    print(f"- {program['name']}: {program['description']}")

# Find resources by category
resources = bot.find_resources("Seattle, WA", category="food")
print(bot.format_resource_list(resources))
```

---

## Configuration Options

Pass a `config` dictionary when instantiating the bot:

| Key | Type | Default | Description |
|---|---|---|---|
| `default_location` | str | `"your area"` | Fallback location for searches |
| `max_results` | int | `10` | Maximum resources to return per query |

---

## Integration Guide

### Zapier

1. Create a new Zap with trigger: **Webhooks by Zapier → Catch Hook**
2. Set your `WEBHOOK_URL` environment variable to the hook URL
3. When the bot finds eligible programs, it POSTs results to this URL
4. Connect the action to:
   - **Google Sheets**: Log client assessments
   - **Gmail / Outlook**: Send resource lists by email
   - **Airtable**: Track client service referrals
   - **Slack**: Alert caseworkers in real time

### N8n

1. Add a **Webhook** node and copy the URL
2. Set `WEBHOOK_URL` in your `.env`
3. Chain nodes to:
   - Filter resources by category
   - Send SMS via Twilio
   - Add to a CRM or database

---

## Deployment

### Docker

```bash
docker build -t 211-resource-bot .
docker run -it --env-file .env 211-resource-bot
```

### GitHub Actions

Use `bot-ci.yml` in `.github/workflows/` to run automated smoke tests on every push.

---

## Non-Technical User Guide

**You don't need to know how to code to use this bot.** Here's how to get started:

1. **Download** the DreamCobots repository (green "Code" button → "Download ZIP")
2. **Install Python** from [python.org](https://python.org) — click the big yellow download button
3. Open a terminal (search "Terminal" on Mac, "Command Prompt" on Windows)
4. Type: `pip install requests python-dotenv` and press Enter
5. Navigate to the bot folder and type: `python bot.py`
6. Answer the questions on screen — the bot does the rest!

---

## License

MIT License — see repo root for details.
