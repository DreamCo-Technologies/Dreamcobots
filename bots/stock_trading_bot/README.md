# Stock Trading Bot

A tier-aware AI-powered stock analysis and trading signals bot for the Dreamcobots platform. Analyzes stocks, generates signals with technical indicators, and supports backtesting based on your subscription tier.

## Installation

```bash
pip install -r requirements.txt
```

```python
from bots.stock_trading_bot.bot import StockTradingBot
from bots.stock_trading_bot.tiers import get_stock_trading_tier_info
```

## Tiers

| Feature                    | Free ($0/mo)           | Pro ($49/mo)                          | Enterprise ($299/mo)                        |
|----------------------------|------------------------|---------------------------------------|---------------------------------------------|
| Watchlist size             | 5 stocks               | 100 stocks                            | Unlimited                                   |
| Signal frequency           | Daily                  | Real-time                             | Algorithmic (real-time)                     |
| Technical indicators       | 2 (SMA, RSI)           | 5+ (EMA, MACD, Bollinger, ...)        | Full suite + volume + institutional flow    |
| Signal confidence          | 0.60                   | 0.75                                  | 0.90                                        |
| Backtesting                | ❌                     | ✅                                    | ✅ (enhanced)                               |
| Options flow               | ❌                     | ❌                                    | ✅                                          |
| Institutional data         | ❌                     | ❌                                    | ✅                                          |
| API trading                | ❌                     | ❌                                    | ✅                                          |

## Usage

### Initialize the bot

```python
from bots.stock_trading_bot.bot import StockTradingBot
from tiers import Tier

bot = StockTradingBot(tier=Tier.PRO)
```

### Analyze a stock

```python
result = bot.analyze_stock("AAPL")
print(result)
# {
#   "ticker": "AAPL",
#   "signal": "BUY",
#   "confidence": 0.75,
#   "indicators": {
#     "sma_20": 150.0,
#     "rsi": 50.0,
#     "ema_50": 148.5,
#     "macd": 1.2,
#     "bollinger_bands": {"upper": 158.0, "lower": 142.0}
#   },
#   "tier": "pro"
# }
```

### Get trading signals

```python
result = bot.get_signals("TSLA")
print(result)
# {
#   "ticker": "TSLA",
#   "signals": [
#     {"type": "real_time", "signal": "HOLD", "timestamp": "..."},
#     {"type": "momentum", "signal": "BUY", "timestamp": "..."},
#     {"type": "trend", "signal": "HOLD", "timestamp": "..."}
#   ],
#   "tier": "pro"
# }
```

### Backtest a strategy (PRO/ENTERPRISE)

```python
strategy = {
    "name": "moving_average_crossover",
    "parameters": {"short_window": 20, "long_window": 50}
}

result = bot.backtest(strategy)
print(result)
# {
#   "strategy": "moving_average_crossover",
#   "returns": 0.18,
#   "sharpe_ratio": 1.4,
#   "tier": "pro"
# }
```

### Get bot statistics

```python
stats = bot.get_stats()
print(stats)
# {
#   "tier": "pro",
#   "requests_used": 4,
#   "requests_remaining": "996",
#   "watchlist_count": 3,
#   "buddy_integration": True
# }
```

## License

MIT
