# Crypto Bot Dashboard

Console-based dashboard summarising portfolio, market overview, mining stats, and recent transactions for the DreamCobots crypto management system.

## Panels

| Panel              | Description                                        |
|--------------------|----------------------------------------------------|
| Portfolio          | Holdings, total value, P&L summary                |
| Market Overview    | Top-N coins with 24-hour price change              |
| Mining Stats       | Active rigs, hash rate, estimated daily earnings   |
| Transactions       | Recent buy/sell/mine events                        |

## Source

Implementation: [`bots/crypto_bot/dashboard.py`](../../bots/crypto_bot/dashboard.py)

## Usage

```python
from bots.crypto_bot.portfolio import Portfolio
from bots.crypto_bot.dashboard import render_dashboard

portfolio = Portfolio()
portfolio.deposit_usd(10000)
portfolio.buy("BTC", 0.1)

print(render_dashboard(portfolio))
```
