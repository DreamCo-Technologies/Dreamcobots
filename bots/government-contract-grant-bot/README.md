# Government Contract & Grant Automation Bot

## Overview

The **Government Contract & Grant Automation Bot** automates the process of discovering, filtering, and responding to federal contract and grant opportunities. It integrates directly with [SAM.gov](https://sam.gov) — the official U.S. government contract portal — to search for solicitations matching your business profile, parse opportunity details, and generate proposal draft templates so you can respond faster than competitors.

Whether you're a small business owner, a grant writer, or a government contractor, this bot saves hours of manual searching and drafting every week.

---

## Features

| Feature | Description |
|---|---|
| **SAM.gov API Integration** | Pulls live contract and grant opportunities directly from SAM.gov's public API |
| **Keyword & NAICS Filtering** | Filter results by keywords, NAICS codes, agency, set-aside type, and dollar value |
| **Email Notifications** | Receive instant email alerts when matching opportunities are posted |
| **Zapier / N8n Webhooks** | Push new opportunities to any downstream workflow (CRM, Slack, Notion, etc.) |
| **Proposal Template Generation** | Auto-generate structured proposal drafts using Jinja2 templates |
| **Scheduled Polling** | Runs on a configurable schedule (hourly, daily) to continuously monitor SAM.gov |
| **Results Export** | Export filtered opportunities to JSON or CSV for reporting |

---

## Prerequisites

- Python 3.9+
- A SAM.gov API key ([register here](https://open.gsa.gov/api/sam/))
- (Optional) A configured email account for SMTP notifications
- (Optional) Docker for containerized deployment

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-org/dreamcobots.git
cd dreamcobots/bots/government-contract-grant-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the bot

Copy the example config and fill in your credentials:

```bash
cp ../../config.json config.local.json
```

Edit `config.local.json` (see [Configuration Guide](#configuration-guide) below).

Alternatively, create a `.env` file:

```env
SAM_GOV_API_KEY=your_sam_gov_api_key_here
NOTIFICATION_EMAIL=alerts@yourbusiness.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your_app_password
WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/...
```

---

## Usage

### Run once (immediate search)

```bash
python government_contract_grant_bot.py
```

### Run on a schedule (continuous monitoring)

```bash
python government_contract_grant_bot.py --schedule
```

### Filter by keyword

```bash
python government_contract_grant_bot.py --keywords "cybersecurity,cloud,IT services"
```

### Export results to CSV

```bash
python government_contract_grant_bot.py --export csv --output opportunities.csv
```

---

## Configuration Guide

All settings can be placed in `config.local.json` or as environment variables in `.env`.

```json
{
  "sam_gov": {
    "api_key": "YOUR_API_KEY",
    "base_url": "https://api.sam.gov/opportunities/v2/search",
    "keywords": ["cybersecurity", "software development", "IT support"],
    "naics_codes": ["541511", "541512", "541519"],
    "set_aside_types": ["SBA", "8A", "WOSB", "SDVOSBC"],
    "min_value": 10000,
    "max_value": 5000000,
    "posted_from_days": 7
  },
  "notifications": {
    "email_enabled": true,
    "email_recipients": ["owner@yourbusiness.com"],
    "webhook_enabled": true,
    "webhook_url": "https://hooks.zapier.com/hooks/catch/YOUR_HOOK_ID"
  },
  "schedule": {
    "interval_hours": 6
  },
  "proposal": {
    "company_name": "Your Company LLC",
    "company_address": "123 Main St, Washington DC 20001",
    "cage_code": "XXXXX",
    "duns_number": "XXXXXXXXX",
    "capabilities_summary": "Brief description of your core capabilities."
  }
}
```

### Key Configuration Options

| Key | Description |
|---|---|
| `sam_gov.api_key` | Your SAM.gov API key |
| `sam_gov.keywords` | List of search keywords to filter opportunities |
| `sam_gov.naics_codes` | NAICS codes matching your business category |
| `sam_gov.set_aside_types` | Filter for small business set-asides (SBA, 8A, WOSB, etc.) |
| `notifications.webhook_url` | Zapier/N8n webhook URL for downstream automation |
| `schedule.interval_hours` | How often the bot checks for new opportunities |
| `proposal.company_name` | Your company name for auto-generated proposals |

---

## Zapier Integration

1. In Zapier, create a new Zap: **Trigger → Webhooks by Zapier → Catch Hook**
2. Copy the webhook URL and paste it into `notifications.webhook_url` in your config
3. Connect the action to your preferred destination:
   - **Slack**: Post opportunity summaries to a channel
   - **Google Sheets**: Log every new opportunity automatically
   - **Gmail**: Send formatted email alerts
   - **Trello/Notion**: Create a card or database entry for each opportunity

---

## N8n Integration

1. In N8n, add a **Webhook** node and copy the URL
2. Set `notifications.webhook_url` to that URL
3. Chain downstream nodes:
   - **HTTP Request** → Call SAM.gov for full details
   - **Send Email** → Notify your team
   - **Google Sheets** → Log opportunities
   - **IF node** → Route by opportunity value or agency

---

## Deployment

### Docker

```bash
docker build -t gov-contract-bot .
docker run --env-file .env gov-contract-bot
```

To run continuously with restart:

```bash
docker run -d --restart=always --env-file .env gov-contract-bot
```

### GitHub Actions (Scheduled)

Add `.github/workflows/bot-ci.yml` to run the bot on a cron schedule:

```yaml
on:
  schedule:
    - cron: '0 */6 * * *'   # Every 6 hours
```

---

## Competitive Advantage for Non-Technical Users

Most small businesses miss out on government contracts because manual SAM.gov searching is time-consuming and easy to forget. This bot gives you:

- ✅ **Automated monitoring** — never miss a relevant solicitation again
- ✅ **Pre-built proposal drafts** — get a head start on every response
- ✅ **Instant notifications** — know about opportunities before competitors
- ✅ **No coding required** — configure once via a JSON file, run with one command
- ✅ **Connects to your existing tools** — Zapier, Slack, Google Sheets, email

Government contracting is a **$700B+ annual market**. With DreamCobots, even a solo consultant or micro-business can compete.

---

## License

MIT License — see repo root for details.
