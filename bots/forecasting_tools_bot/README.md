# Forecasting Tools Bot

Tier-aware revenue forecasting, seasonality detection, and scenario planning bot.

## Features by Tier

| Feature | FREE | PRO | ENTERPRISE |
|---|---|---|---|
| 3-month forecast | ✓ | ✓ | ✓ |
| 12-month forecast | ✗ | ✓ | ✓ |
| Confidence intervals | ✗ | ✓ | ✓ |
| Seasonality detection | ✗ | ✓ | ✓ |
| Scenario planning | ✗ | ✓ | ✓ |
| ML-powered / unlimited | ✗ | ✗ | ✓ |

## Usage

```python
from bots.forecasting_tools_bot import ForecastingToolsBot
from bots.ai-models-integration.tiers import Tier

bot = ForecastingToolsBot(tier=Tier.PRO)
forecast = bot.forecast_revenue([100, 110, 121, 133], periods=12)
growth = bot.calculate_growth_rate([100, 110, 121, 133])
seasonality = bot.detect_seasonality([80, 120, 100, 90, 85, 125, 105, 95])
scenarios = bot.build_scenario(forecast["forecast"], {"optimistic_growth_pct": 25})
```
