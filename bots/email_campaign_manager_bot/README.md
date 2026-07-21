# EmailCampaignManagerBot

A tier-aware bot for managing email campaigns and drip sequences.

## Tiers
- **FREE**: 500 subscribers, 2 campaigns/month, basic templates
- **PRO**: 10,000 subscribers, 10 campaigns/month, A/B testing, segmentation
- **ENTERPRISE**: Unlimited subscribers, drip sequences, automation triggers

## Usage
```python
from bots.email_campaign_manager_bot import EmailCampaignManagerBot
from tiers import Tier

bot = EmailCampaignManagerBot(tier=Tier.PRO)
bot.add_subscriber("user@example.com", "Jane Doe")
camp = bot.create_campaign("Summer Sale", "Big Summer Deals!", "general")
```
