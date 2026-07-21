# LogoGeneratorBot

A tier-aware bot for generating logos and brand guides.

## Tiers
- **FREE**: 3 logo concepts/month, 5 style options, JPG export
- **PRO**: 25 concepts/month, SVG output, custom palettes, brand guide
- **ENTERPRISE**: Unlimited concepts, animated logos, white label, bulk generation

## Usage
```python
from bots.logo_generator_bot import LogoGeneratorBot
from tiers import Tier

bot = LogoGeneratorBot(tier=Tier.PRO)
logo = bot.generate_logo("Acme Corp", "tech", style="modern")
guide = bot.get_brand_guide("Acme Corp")
```
