# Bot Generator Bot

The **DreamCo Bot Generator Bot** is the core multiplier of the Dreamcobots
ecosystem.  Given a natural-language description of a desired bot (e.g.
"Make a Dentist Lead Bot"), it autonomously:

1. **Parses** the request into a structured Bot DNA (`parser.py`)
2. **Injects** appropriate scraping / processing tools (`tool_injector.py`)
3. **Builds** the bot source code from a dynamic template (`template_engine.py`)
4. **Deploys** the generated bot to the filesystem (`deployer.py`)

## Pricing

| Tier       | Price        | Bots/Month | Industries | Key Features                          |
|------------|-------------|-----------|-----------|---------------------------------------|
| Free       | $0/mo        | 3          | 5          | Basic generation                       |
| Pro        | $49/mo       | 30         | 20         | Tool injection, advanced templates, auto-deploy, Stripe hooks |
| Enterprise | $199/mo      | Unlimited  | Unlimited  | Custom DNA, white-label deploy         |

## Quick Start

```python
from bots.bot_generator_bot.bot_generator_bot import BotGeneratorBot
from bots.bot_generator_bot.tiers import Tier

# FREE tier — basic generation
bot = BotGeneratorBot(tier=Tier.FREE)
result = bot.generate("Make a real estate lead bot")
print(result["source"])          # generated Python source code
print(result["intent"])          # parsed industry + goal

# PRO tier — with tool injection & auto-deploy dry-run
pro_bot = BotGeneratorBot(tier=Tier.PRO)
result = pro_bot.generate("Build a dentist lead bot", deploy=True, dry_run=True)
print(result["deploy_result"])   # deployment plan

# ENTERPRISE — custom DNA
ent_bot = BotGeneratorBot(tier=Tier.ENTERPRISE)
custom_dna = {
    "industry": "legal",
    "goal": "generate_leads",
    "bot_name": "law_firm_leads_bot",
    "tools": ["google_maps", "email_finder"],
    "monetization": ["subscriptions", "pay_per_use"],
}
result = ent_bot.generate("", custom_dna=custom_dna)
```

## Bot DNA Format

```json
{
  "industry": "real_estate",
  "goal": "generate_leads",
  "bot_name": "real_estate_generate_leads_bot",
  "tools": ["google_maps", "zillow_scraper", "email_finder"],
  "monetization": ["subscriptions", "lead_sales"]
}
```

## Available Tools

| Tool              | Category   | API Key Required |
|-------------------|-----------|-----------------|
| google_maps       | scraping  | ✅ GOOGLE_MAPS_API_KEY |
| email_finder      | processing | ❌              |
| zillow_scraper    | scraping  | ❌              |
| mls_api           | scraping  | ✅ MLS_API_KEY  |
| yelp_scraper      | scraping  | ✅ YELP_API_KEY |
| linkedin_scraper  | scraping  | ❌              |
| stripe_api        | payment   | ✅ STRIPE_SECRET_KEY |
| analytics_tracker | analytics | ❌              |
| email_sender      | export    | ✅ SENDGRID_API_KEY |

## Autonomy Loop

```
User Input → Parser → Tool Injector → Template Engine → Deployer → Live Bot
```
