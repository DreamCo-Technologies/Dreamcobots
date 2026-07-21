# Home Flipping Analyzer Bot

A tier-aware bot that analyzes real estate properties for fix-and-flip potential. Calculates After Repair Value (ARV), renovation costs, ROI, and a proprietary **Flip Score** (0–100).

## Features by Tier

| Feature | FREE | PRO | ENTERPRISE |
|---|---|---|---|
| Properties at once | 1 | 5 | Unlimited |
| Basic ARV estimate | ✓ | ✓ | ✓ |
| Flip score (0-100) | ✓ | ✓ | ✓ |
| Itemized renovation breakdown | — | ✓ | ✓ |
| Holding & financing cost calc | — | ✓ | ✓ |
| Contractor bidding simulator | — | — | ✓ |
| Market timing analysis | — | — | ✓ |

## Quick Start

```python
from bots.home_flipping_analyzer.home_flipping_analyzer import HomeFlippingAnalyzerBot
from bots.ai_models_integration.tiers import Tier  # or: sys.path trick

# FREE tier — analyze one property
bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
result = bot.analyze_flip("FLP001")
print(result["flip_score"])       # 0-100
print(result["estimated_profit_usd"])

# Get top opportunities
top = bot.get_top_flip_opportunities(limit=5)

# PRO tier — detailed breakdown
bot_pro = HomeFlippingAnalyzerBot(tier=Tier.PRO)
detail = bot_pro.analyze_flip("FLP003")
print(detail["itemized_renovation"])   # kitchen, bath, roof, HVAC, etc.

# Calculate ARV with your own comps
arv = bot_pro.calculate_arv("FLP003", comparable_sales=[270000, 260000, 275000])
```

## Key Methods

| Method | Description |
|---|---|
| `analyze_flip(address_or_id)` | Full flip analysis: ARV, costs, profit, flip score |
| `estimate_renovation_cost(pid, scope)` | Cost breakdown (`cosmetic`/`moderate`/`full_gut`) |
| `calculate_arv(pid, comparable_sales)` | After Repair Value (blends comps on PRO+) |
| `get_top_flip_opportunities(limit)` | Ranked list of best flip deals |
| `describe_tier()` | Print current tier features |
| `run()` | Execute the GlobalAISourcesFlow pipeline |

## Database

20 sample flip properties across: Memphis, Cleveland, Atlanta, Indianapolis, Tampa, Phoenix, Kansas City, Charlotte, Dallas, Nashville, Pittsburgh, Las Vegas, Columbus, Detroit, Denver, Houston, Austin, Sacramento, San Antonio.
