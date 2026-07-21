# SocialMediaManagerBot

A tier-aware bot for managing social media posts and scheduling.

## Tiers
- **FREE**: Instagram only, 10 posts/month, basic captions
- **PRO**: 5 platforms, 50 posts/month, hashtag research, analytics
- **ENTERPRISE**: All platforms, AI captions, auto-scheduling, competitor analysis

## Usage
```python
from bots.social_media_manager_bot import SocialMediaManagerBot
from tiers import Tier

bot = SocialMediaManagerBot(tier=Tier.PRO)
post = bot.create_post("instagram", "new product launch")
```
