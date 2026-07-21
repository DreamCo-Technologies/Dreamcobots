# AdCopyGeneratorBot

A tier-aware bot for generating ad copy across multiple platforms.

## Tiers
- **FREE**: 5 ads/month, Google & Facebook only
- **PRO**: 50 ads/month, all platforms, A/B variants, CTR estimation
- **ENTERPRISE**: Unlimited ads, multilingual, performance tracking

## Usage
```python
from bots.ad_copy_generator_bot import AdCopyGeneratorBot
from tiers import Tier

bot = AdCopyGeneratorBot(tier=Tier.PRO)
ad = bot.generate_ad("CloudSync", "google", "small business owners")
variants = bot.create_ab_variants(ad, num_variants=3)
```
