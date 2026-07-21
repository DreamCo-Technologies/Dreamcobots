# Mining Bot

Tier-aware cryptocurrency mining management bot. Scans coins, switches mining targets, tracks profitability, and manages withdrawals.

## Tiers

| Feature | FREE | PRO | ENTERPRISE |
|---------|------|-----|------------|
| Coins | 1 (BTC) | 5 | All 10 coins |
| Auto-switch | ✗ | ✓ | ✓ |
| Multi-exchange | ✗ | ✗ | ✓ |
| Portfolio optimization | ✗ | ✗ | ✓ |

## Usage

```python
from bots.mining_bot.mining_bot import MiningBot
from tiers import Tier

bot = MiningBot(tier=Tier.PRO)
coins = bot.scan_coins()
bot.switch_coin("ETH")
profitability = bot.track_profitability()
bot.auto_withdraw(threshold=50.0)
```

## Methods

- `scan_coins()` — returns list of mineable coins with profitability data
- `switch_coin(coin)` — switches to mining a different coin
- `track_profitability()` — returns current profitability metrics
- `auto_withdraw(threshold)` — configures auto-withdrawal (PRO+)
- `get_current_coin()` — returns the coin currently being mined
- `multi_exchange_route(amount)` — calculates optimal routing (ENTERPRISE)

## Directory Structure

```
bots/mining_bot/
├── mining_bot.py
├── tiers.py
├── __init__.py
└── README.md
```
