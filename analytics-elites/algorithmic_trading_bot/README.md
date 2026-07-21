# Algorithmic Trading Bot

Technical indicator signals (SMA crossover, RSI, MACD) and backtesting for educational use.

**DISCLAIMER:** For educational and research purposes only. Not financial advice.

## Tiers
- **Free** ($0/mo): Moving average signals, 3 symbols/month
- **Pro** ($99/mo): RSI signals, MACD, backtesting, 10 symbols
- **Enterprise** ($499/mo): All indicators, unlimited symbols, live trading hooks

## Usage
```python
import sys
sys.path.insert(0, "analytics-elites/algorithmic_trading_bot")
from algorithmic_trading_bot import AlgorithmicTradingBot

bot = AlgorithmicTradingBot(tier="pro")
signal = bot.rsi_signal("AAPL", prices)
```
