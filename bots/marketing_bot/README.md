# Marketing Bot

Tier-aware digital marketing and campaign automation assistant for the
Dreamcobots platform.

---

## Overview

The Marketing Bot automates social media content, multi-channel campaigns,
A/B testing, SEO recommendations, paid-ads copy, and full-funnel orchestration
through a conversational interface.

---

## Tiers & Pricing

| Tier | Price/month | Requests/month | Highlights |
|---|---|---|---|
| **Free** | $0 | 500 | Social posts, email subjects, hashtag generator, basic SEO |
| **Pro** | $49 | 10,000 | Multi-channel campaigns, A/B testing, paid ads, analytics |
| **Enterprise** | $299 | Unlimited | Full-funnel orchestration, influencer matching, white-label |

---

## Quick Start

```python
from bots.marketing_bot import MarketingBot
from bots.ai_chatbot.tiers import Tier

bot = MarketingBot(tier=Tier.PRO)

# Natural-language chat
response = bot.chat("Write a Twitter thread about our product launch")
print(response["message"])

# Create a campaign
result = bot.create_campaign("email_marketing", "Black Friday 30% off sale")
print(result["campaign"])

# List channels
print(bot.list_channels())
```

---

## Available Channels

### Free
- `social_media` — posts for Twitter, Instagram, LinkedIn, Facebook
- `email_marketing` — subject lines and email body drafts
- `seo` — keyword research and on-page recommendations

### Pro (includes all Free)
- `paid_ads` — Google Ads and Meta Ads copy
- `content_calendar` — 30-day editorial calendar
- `ab_testing` — copy variant generation and winner selection

### Enterprise (includes all Pro)
- `influencer` — influencer research, scoring, and outreach templates
- `brand_voice` — custom brand voice guidelines and enforcement
- `attribution_reporting` — multi-touch attribution dashboards
- `full_funnel_orchestration` — awareness → conversion workflow automation

---

## Monetization

- **SaaS subscription** — FREE / PRO ($49/mo) / ENTERPRISE ($299/mo)
- **API pay-per-use** — per-campaign pricing on PRO/ENTERPRISE
- **White-label** — custom-branded marketing portals on ENTERPRISE

---

## BuddyAI Integration

```python
from BuddyAI import BuddyBot
from bots.marketing_bot import MarketingBot
from bots.ai_chatbot.tiers import Tier

buddy = BuddyBot()
buddy.register_bot("marketing", MarketingBot(tier=Tier.PRO))
response = buddy.chat("marketing", "Generate 5 Instagram captions for our new product")
print(response["message"])
```

---

## Directory Structure

```
bots/marketing_bot/
├── marketing_bot.py   # Main bot class
├── tiers.py           # Tier config (channels & features)
├── __init__.py
└── README.md
```

## Running Tests

```bash
python -m pytest tests/test_marketing_bot.py -v
```
