# 🪙 Crypto Bot — Dreamcobots Cryptocurrency Management System

A tier-aware cryptocurrency management bot that lets users **mine**, **buy**, **sell**, and **track** cryptocurrencies for profit. Supports 66+ global coins with real-time or simulated price data, a full portfolio tracker, mining simulation, and per-coin prospectus pages.

---

## Features

| Feature | FREE | PRO | ENTERPRISE |
|---|---|---|---|
| Track coins | 5 | 50 | Unlimited |
| View prices & market data | ✓ | ✓ | ✓ |
| Coin prospectus pages | ✓ | ✓ | ✓ |
| Simulated mining | BTC only | 20 coins | All coins |
| Buy & sell | — | ✓ | ✓ |
| Profit/loss tracking | — | ✓ | ✓ |
| Transaction history | — | ✓ | ✓ |
| Interactive dashboard | — | ✓ | ✓ |
| Price alerts | — | ✓ | ✓ |
| Full mining suite | — | — | ✓ |
| Tax reporting | — | — | ✓ |
| API access | — | — | ✓ |
| White-label dashboard | — | — | ✓ |

---

## Quick Start

```python
from bots.crypto_bot import CryptoBot
from tiers import Tier

# Create a PRO-tier bot with $10,000 starting balance
bot = CryptoBot(tier=Tier.PRO, initial_usd_balance=10_000.0)

# --- Market Data ---
print(bot.price("BTC"))
# {'symbol': 'BTC', 'name': 'Bitcoin', 'price_usd': 67420.0, 'change_24h_pct': +3.42}

print(bot.market_board())
# Renders a formatted market overview table

# --- Search ---
results = bot.search("eth")
# Returns Ethereum and any other coins matching "eth"

# --- Buy & Sell ---
bot.buy("BTC", usd_amount=2_000)    # buy $2,000 worth of BTC
bot.buy("ETH", usd_amount=1_500)    # buy $1,500 worth of ETH
bot.sell("BTC", amount=0.01)        # sell 0.01 BTC
bot.sell_all("ETH")                 # sell entire ETH holding

# --- Limit Orders ---
bot.limit_buy("SOL", amount=10, limit_price=150.0)
bot.limit_sell("BTC", amount=0.05, limit_price=75_000.0)

# --- P&L ---
report = bot.pnl_report()
print(f"Total P&L: ${report['total_pnl_usd']:.2f}")

# --- Mining ---
result = bot.mine("BTC", hours=24)
print(f"Mined: {result['coins_mined']} BTC | Net profit: ${result['net_profit_usd']:.2f}")

leaderboard = bot.mining_leaderboard(top_n=5)

be = bot.break_even("BTC", hardware_cost_usd=5_000)
print(be["message"])  # "Break-even in approximately 190 days."

# --- Prospectus ---
print(bot.prospectus("ETH"))
# Renders a full formatted prospectus page

p = bot.prospectus_dict("SOL")
print(p["investment_thesis"])

# --- Dashboard ---
print(bot.dashboard())
# Renders portfolio + market overview + transactions + mining stats
```

---

## Tiers & Pricing

```python
bot.describe_tier()
```

| Tier | Price | Highlights |
|---|---|---|
| FREE | $0/month | 5 coins, price viewing, BTC mining simulation |
| PRO | $49/month | 50 coins, buy/sell, 20-coin mining, full dashboard |
| ENTERPRISE | $299/month | Unlimited coins, all mining, tax reporting, API |

---

## Real-Time Prices

By default the bot uses **simulated prices** (a small ±5% random walk applied to
database baseline values). To use live CoinGecko prices:

```python
bot = CryptoBot(tier=Tier.PRO, use_live_prices=True)
```

No API key is required for CoinGecko's free public endpoint. The bot
automatically falls back to simulated prices if the request fails.

---

## Supported Coins (66+)

Coins span all major categories:

- **Layer 1** — BTC, ETH, SOL, BNB, ADA, AVAX, DOT, NEAR, FTM, SUI, APT …
- **Layer 2** — MATIC, OP, ARB, IMX, STX …
- **DeFi** — UNI, AAVE, MKR, COMP, SNX, CRV, 1INCH, KAVA …
- **Stablecoins** — USDT, USDC, DAI …
- **Privacy / Mining** — XMR, ZEC, BEAM, GRIN, FIRO …
- **Mineable PoW** — BTC, LTC, DOGE, RVN, ERG, FLUX, KAS, ALPH, VTC …
- **NFT / Metaverse** — SAND, MANA, AXS, FLOW …
- **AI / Data** — GRT, FET, OCEAN, RNDR …
- **Exchange Tokens** — BNB, CRO, OKB …
- **Meme** — DOGE, SHIB, PEPE …
- **Storage** — FIL, AR …
- **IoT / Identity** — HNT, WLD …

Use `bot.list_all_coins()` or `bot.list_categories()` to explore the full list.

---

## Running Tests

```bash
cd /path/to/Dreamcobots
python -m pytest tests/test_crypto_bot.py -v
```

---

## Architecture

```
bots/crypto_bot/
├── __init__.py           — public package exports
├── crypto_bot.py         — CryptoBot main class (entry point)
├── tiers.py              — tier configuration (FREE/PRO/ENTERPRISE)
├── crypto_database.py    — 250+ coin reference database
├── price_feed.py         — simulated / live price feed (CoinGecko)
├── portfolio.py          — holdings, balances, transaction tracking
├── trading.py            — buy/sell execution engine
├── mining.py             — mining simulation & profitability engine
├── prospectus.py         — per-coin prospectus pages
├── dashboard.py          — console dashboard renderer
└── README.md             — this file
```

---

## Developer Notes

- All prices are simulated by default using a seeded random walk.
  Seed changes every minute so prices feel live without API calls.
- Set `use_live_prices=True` to hit the CoinGecko public API.
- The bot follows the **GLOBAL AI SOURCES FLOW** framework (see
  `framework/global_ai_sources_flow.py`).
- Tier enforcement uses the shared `tiers.py` from `bots/ai-models-integration/`.
