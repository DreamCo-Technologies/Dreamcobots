# AI Side Hustle Bot

## Overview

The **AI Side Hustle Bot** is your personal assistant for discovering, launching, and scaling a side income. It combines curated opportunity data with AI-enhanced tools to help you generate content ideas, find freelance gigs, estimate your earning potential, and build a tailored marketing plan — all from the command line or via API.

Whether you want to make an extra $500/month or replace your full-time income, DreamCobots gives you a structured starting point.

---

## Features

| Feature | Description |
|---|---|
| **Content Idea Generator** | Generate viral content ideas for any niche (finance, fitness, tech, business) |
| **Freelance Opportunity Finder** | Match your skills to gigs on Upwork, Fiverr, and Toptal |
| **Income Potential Calculator** | Estimate monthly earnings based on hustle type and hours invested |
| **Marketing Plan Creator** | Get a custom weekly action plan with channels, tools, and monetization tips |
| **Multi-Platform Integration** | Connect to Zapier, N8n, Make.com, Notion, Google Sheets, and more |
| **OpenAI Support** | Optionally power idea generation with GPT for even better output |
| **CLI Interface** | Fully interactive command-line experience — no coding required |

---

## Side Hustle Categories

- `content_creation` — YouTube, TikTok, blogging, newsletters
- `freelancing` — Services on Upwork, Fiverr, Toptal
- `dropshipping` — Shopify + AliExpress/Spocket stores
- `affiliate_marketing` — SEO blogs, email lists, YouTube
- `digital_products` — eBooks, templates, courses on Gumroad/Etsy
- `social_media_management` — Managing accounts for small businesses

---

## Prerequisites

- Python 3.9+
- (Optional) OpenAI API key for AI-enhanced content generation

---

## Setup & Installation

### 1. Navigate to the bot directory

```bash
cd bots/ai-side-hustle-bots
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment (optional)

Create a `.env` file:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
DEFAULT_NICHE=business
MAX_IDEAS=5
WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/YOUR_HOOK_ID
```

---

## Usage

### Interactive CLI

```bash
python bot.py
```

You'll be guided through each feature with simple prompts.

### Generate Content Ideas

```python
from bot import AISideHustleBot

bot = AISideHustleBot()
ideas = bot.generate_content_ideas("finance", count=5)
for idea in ideas:
    print(f"[{idea['format']}] {idea['title']} — Est. {idea['estimated_views']} views")
```

### Find Freelance Gigs

```python
gigs = bot.find_freelance_opportunities(["python", "writing"], platform="upwork")
for gig in gigs:
    print(f"{gig['title']} | {gig['budget']}")
```

### Calculate Income Potential

```python
result = bot.calculate_income_potential("freelancing", hours_per_week=15)
print(f"Estimated monthly income: ${result['monthly_min']:,}–${result['monthly_max']:,}")
```

### Create a Marketing Plan

```python
plan = bot.create_marketing_plan("content_creation", budget=100)
print("Channels:", plan["channels"])
print("Weekly Actions:", plan["weekly_actions"])
```

---

## Integration Guide

### Zapier

1. Create a Zap: **Webhooks → Catch Hook**, copy the hook URL
2. Set `WEBHOOK_URL` in your `.env`
3. The bot POSTs results (ideas, plans, income estimates) to the hook
4. Connect to:
   - **Google Sheets**: Log income ideas and plans
   - **Notion**: Create a side hustle database
   - **Gmail**: Email yourself a weekly hustle plan
   - **Slack**: Get daily content idea reminders

### N8n

1. Create a **Webhook** node and copy the URL
2. Set `WEBHOOK_URL` in `.env`
3. Build a workflow:
   - Auto-generate content ideas each Monday morning
   - Send freelance opportunities to your email
   - Track income estimates in a spreadsheet

### Make.com (Integromat)

1. Create a **Custom Webhook** scenario
2. Set the webhook URL in `.env`
3. Connect to Google Sheets, Airtable, or Notion for automatic tracking

---

## Deployment

### Docker

```bash
docker build -t ai-side-hustle-bot .
docker run -it --env-file .env ai-side-hustle-bot
```

### Scheduled Content Ideas (GitHub Actions)

Add a weekly trigger to auto-generate ideas:

```yaml
on:
  schedule:
    - cron: '0 8 * * 1'   # Every Monday at 8 AM
```

---

## DreamCobots Competitive Advantage

| What Others Offer | What DreamCobots Provides |
|---|---|
| Generic "hustle ideas" blog posts | Personalized, actionable plans based on your skills and time |
| Manual research on 10+ platforms | One bot that aggregates opportunities across platforms |
| Expensive coaches and courses | Free, open-source tools you own and control |
| "Just post on social media" advice | Week-by-week marketing action plans with specific tools |
| No integration with your workflows | Native Zapier, N8n, Make.com webhook support |

---

## Non-Technical User Guide

1. **Install Python** from [python.org](https://python.org) — click the big download button
2. Open Terminal (Mac) or Command Prompt (Windows)
3. Type: `pip install requests python-dotenv openai` → press Enter
4. Navigate to the bot folder and type: `python bot.py`
5. Choose a menu option and answer the questions
6. Your personalized hustle plan, content ideas, and income estimates appear instantly!

> **No API key required** for the basic features. Add an OpenAI key only if you want AI-enhanced content ideas.

---

## License

MIT License — see repo root for details.
