# Social Media Bot

A tier-aware AI-powered social media scheduling and analytics bot for the Dreamcobots platform. Schedules posts, analyzes engagement, and generates hashtags based on your subscription tier.

## Installation

```bash
pip install -r requirements.txt
```

```python
from bots.social_media_bot.bot import SocialMediaBot
from bots.social_media_bot.tiers import get_social_media_tier_info
```

## Tiers

| Feature                  | Free ($0/mo)        | Pro ($49/mo)                             | Enterprise ($299/mo)                          |
|--------------------------|---------------------|------------------------------------------|-----------------------------------------------|
| Connected accounts       | 1                   | 5                                        | Unlimited                                     |
| Posts per month          | 10                  | 200                                      | Unlimited                                     |
| Scheduling               | ✅ (basic)          | ✅ (advanced)                            | ✅ (advanced)                                 |
| Analytics                | Basic               | Enhanced                                 | Full influencer analytics                     |
| Hashtag generation       | 3 hashtags          | 10 optimized                             | 20 AI-selected                                |
| Hashtag optimization     | ❌                  | ✅                                       | ✅                                            |
| Engagement tracking      | ❌                  | ✅                                       | ✅                                            |
| AI content generation    | ❌                  | ❌                                       | ✅                                            |
| API access               | ❌                  | ❌                                       | ✅                                            |

## Usage

### Initialize the bot

```python
from bots.social_media_bot.bot import SocialMediaBot
from tiers import Tier

bot = SocialMediaBot(tier=Tier.PRO)
```

### Schedule a post

```python
post = {
    "content": "Check out our latest product update! 🚀",
    "platform": "twitter",
    "scheduled_time": "2025-01-15T10:00:00"
}

result = bot.schedule_post(post)
print(result)
# {
#   "post_id": "uuid-...",
#   "platform": "twitter",
#   "scheduled_time": "2025-01-15T10:00:00",
#   "status": "scheduled",
#   "tier": "pro"
# }
```

### Analyze engagement

```python
result = bot.analyze_engagement("my_twitter_account")
print(result)
# {
#   "account_id": "my_twitter_account",
#   "followers": 1500,
#   "engagement_rate": 0.045,
#   "top_posts": [
#     {"post_id": "sample_1", "likes": 120, "shares": 30, "comments": 15},
#     ...
#   ],
#   "tier": "pro"
# }
```

### Generate hashtags

```python
hashtags = bot.generate_hashtags("AI marketing")
print(hashtags)
# Free:  ["#AImarketing", "#AImarketingTips", "#DreamcobotsAI"]
# Pro:   10 optimized hashtags
# Enterprise: 20 AI-selected hashtags
```

### Get bot statistics

```python
stats = bot.get_stats()
print(stats)
# {
#   "tier": "pro",
#   "requests_used": 3,
#   "requests_remaining": "197",
#   "posts_scheduled": 2,
#   "posts_this_month": 2,
#   "buddy_integration": True
# }
```

## License

MIT
