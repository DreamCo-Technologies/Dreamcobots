"""
Crypto Bot — Tier-aware cryptocurrency management system.

Allows users to mine, buy, sell, and track cryptocurrencies for profit.
Supports all major global cryptocurrencies with real-time or simulated
price data, a full portfolio tracker, mining simulation, and per-coin
prospectus pages.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.crypto_bot import CryptoBot, Tier

    bot = CryptoBot(tier=Tier.PRO, initial_usd_balance=5_000)

    # Buy some Bitcoin
    bot.buy("BTC", usd_amount=1_000)

    # Check P&L
    print(bot.pnl_report())

    # View a coin prospectus
    print(bot.prospectus("ETH"))

    # Simulate mining
    print(bot.mine("BTC", hours=24))

    # View full dashboard
    print(bot.dashboard())
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.crypto_bot.tiers import (
    BOT_FEATURES,
    COIN_LIMITS,
    MINING_COIN_LIMITS,
    get_bot_tier_info,
)
from bots.crypto_bot.crypto_database import (
    CRYPTO_DATABASE,
    get_coin,
    list_coins,
    list_mineable_coins,
    search_coins,
    list_categories,
)
from bots.crypto_bot.price_feed import (
    get_price,
    get_prices,
    get_price_change_24h,
    get_market_summary,
)
from bots.crypto_bot.portfolio import Portfolio, PortfolioError
from bots.crypto_bot.trading import TradingEngine, TradingError
from bots.crypto_bot.mining import (
    simulate_mining,
    mining_leaderboard,
    calculate_break_even,
    get_mining_profile,
)
from bots.crypto_bot.prospectus import (
    get_coin_prospectus,
    list_all_prospectuses,
    prospectus_text,
)
from bots.crypto_bot.dashboard import (
    render_portfolio,
    render_market_overview,
    render_transactions,
    render_mining_stats,
    render_full_dashboard,
)


class CryptoBotError(Exception):
    """Raised when a CryptoBot operation fails."""


class CryptoBot:
    """
    Tier-aware cryptocurrency management bot.

    Tiers
    -----
    FREE       : track 5 coins, view prices, simulated BTC mining.
    PRO        : track 50 coins, buy/sell, mining for 20 coins, dashboard.
    ENTERPRISE : unlimited coins, full mining suite, API access, tax reporting.
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        initial_usd_balance: float = 10_000.0,
        use_live_prices: bool = False,
    ) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self.use_live = use_live_prices
        self._portfolio = Portfolio(initial_usd_balance=initial_usd_balance)
        self._trading = TradingEngine(
            self._portfolio, fee_pct=0.001, use_live=use_live_prices
        )
        self._tracked_coins: list[str] = ["BTC", "ETH", "SOL", "ADA", "DOT"]
        self._mining_sessions: list[dict] = []

    # ------------------------------------------------------------------
    # Tier checks
    # ------------------------------------------------------------------

    def _require_tier(self, minimum: Tier, feature: str) -> None:
        tier_order = [Tier.FREE, Tier.PRO, Tier.ENTERPRISE]
        if tier_order.index(self.tier) < tier_order.index(minimum):
            raise CryptoBotError(
                f"'{feature}' requires {minimum.value} tier or higher. "
                f"You are on {self.tier.value}. "
                f"Upgrade path: {get_upgrade_path(self.tier)}"
            )

    def _check_coin_limit(self, symbol: str) -> None:
        sym = symbol.upper()
        limit = COIN_LIMITS[self.tier]
        if limit is not None and sym not in self._tracked_coins:
            if len(self._tracked_coins) >= limit:
                raise CryptoBotError(
                    f"Tracking limit reached ({limit} coins on {self.tier.value} tier). "
                    "Upgrade to PRO or ENTERPRISE to track more."
                )

    def _check_mining_coin(self, symbol: str) -> None:
        sym = symbol.upper()
        allowed = MINING_COIN_LIMITS[self.tier]
        if allowed is not None and sym not in allowed:
            raise CryptoBotError(
                f"Mining '{sym}' is not available on {self.tier.value} tier. "
                f"Allowed: {allowed[:5]}... Upgrade to access more coins."
            )

    # ------------------------------------------------------------------
    # Coin tracking / market data
    # ------------------------------------------------------------------

    def track(self, symbol: str) -> dict:
        """Add *symbol* to the tracked list."""
        self._check_coin_limit(symbol)
        sym = symbol.upper()
        coin = get_coin(sym)
        if not coin:
            raise CryptoBotError(f"Unknown coin: {sym}")
        if sym not in self._tracked_coins:
            self._tracked_coins.append(sym)
        return {"symbol": sym, "tracked_coins": list(self._tracked_coins)}

    def untrack(self, symbol: str) -> dict:
        """Remove *symbol* from the tracked list."""
        sym = symbol.upper()
        self._tracked_coins = [c for c in self._tracked_coins if c != sym]
        return {"symbol": sym, "tracked_coins": list(self._tracked_coins)}

    def get_tracked_coins(self) -> list[str]:
        """Return the list of currently tracked coin symbols."""
        return list(self._tracked_coins)

    def price(self, symbol: str) -> dict:
        """Return the current price and 24h change for *symbol*."""
        sym = symbol.upper()
        coin = get_coin(sym)
        if not coin:
            raise CryptoBotError(f"Unknown coin: {sym}")
        p = get_price(sym, use_live=self.use_live) or coin["price_usd"]
        change = get_price_change_24h(sym)
        return {
            "symbol": sym,
            "name": coin["name"],
            "price_usd": p,
            "change_24h_pct": change,
        }

    def market_overview(self, symbols: list[str] | None = None) -> list[dict]:
        """
        Return market summary for *symbols* (defaults to tracked coins).
        """
        syms = symbols or self._tracked_coins
        return get_market_summary(syms, use_live=self.use_live)

    def search(self, query: str) -> list[dict]:
        """Search for coins by name or symbol."""
        return search_coins(query)

    def list_all_coins(self, category: str | None = None) -> list[dict]:
        """
        Return all coins in the database, optionally filtered by category.
        """
        return list_coins(category=category)

    def list_categories(self) -> list[str]:
        """Return all coin categories."""
        return list_categories()

    # ------------------------------------------------------------------
    # Portfolio / Trading
    # ------------------------------------------------------------------

    def deposit(self, usd_amount: float) -> dict:
        """Deposit USD into the portfolio."""
        return self._portfolio.deposit_usd(usd_amount)

    def withdraw(self, usd_amount: float) -> dict:
        """Withdraw USD from the portfolio."""
        return self._portfolio.withdraw_usd(usd_amount)

    def buy(self, symbol: str, usd_amount: float) -> dict:
        """
        Buy *symbol* with *usd_amount* USD at the current market price.
        Requires PRO or ENTERPRISE tier.
        """
        self._require_tier(Tier.PRO, "buy")
        self._check_coin_limit(symbol)
        sym = symbol.upper()
        if sym not in self._tracked_coins:
            self._tracked_coins.append(sym)
        return self._trading.market_buy(sym, usd_amount)

    def sell(self, symbol: str, amount: float) -> dict:
        """
        Sell *amount* of *symbol* at the current market price.
        Requires PRO or ENTERPRISE tier.
        """
        self._require_tier(Tier.PRO, "sell")
        return self._trading.market_sell(symbol, amount)

    def sell_all(self, symbol: str) -> dict:
        """Sell entire holding of *symbol*. Requires PRO or ENTERPRISE."""
        self._require_tier(Tier.PRO, "sell_all")
        return self._trading.sell_all(symbol)

    def limit_buy(self, symbol: str, amount: float, limit_price: float) -> dict:
        """Place a limit buy order. Requires PRO or ENTERPRISE."""
        self._require_tier(Tier.PRO, "limit_buy")
        return self._trading.limit_buy(symbol, amount, limit_price)

    def limit_sell(self, symbol: str, amount: float, limit_price: float) -> dict:
        """Place a limit sell order. Requires PRO or ENTERPRISE."""
        self._require_tier(Tier.PRO, "limit_sell")
        return self._trading.limit_sell(symbol, amount, limit_price)

    def portfolio_summary(self) -> dict:
        """Return a full portfolio summary."""
        return self._portfolio.summary(use_live_prices=self.use_live)

    def pnl_report(self) -> dict:
        """Return a profit/loss report. Requires PRO or ENTERPRISE."""
        self._require_tier(Tier.PRO, "pnl_report")
        return self._trading.pnl_report()

    def transaction_history(
        self, symbol: str | None = None, tx_type: str | None = None, limit: int = 20
    ) -> list[dict]:
        """Return transaction history. Requires PRO or ENTERPRISE."""
        self._require_tier(Tier.PRO, "transaction_history")
        return self._portfolio.get_transactions(
            symbol=symbol, tx_type=tx_type, limit=limit
        )

    # ------------------------------------------------------------------
    # Mining
    # ------------------------------------------------------------------

    def mine(
        self,
        symbol: str,
        hours: float = 1.0,
        electricity_rate: float = 0.10,
        credit_to_portfolio: bool = True,
    ) -> dict:
        """
        Simulate mining *symbol* for *hours*.

        Parameters
        ----------
        symbol              : coin to mine
        hours               : duration of the mining session
        electricity_rate    : cost per kWh in USD
        credit_to_portfolio : if True, mined coins are added to the portfolio
        """
        self._check_mining_coin(symbol)
        result = simulate_mining(
            symbol,
            duration_hours=hours,
            electricity_rate=electricity_rate,
            use_live_price=self.use_live,
        )
        self._mining_sessions.append(result)

        if credit_to_portfolio and result["coins_mined"] > 0:
            self._portfolio.add_mined(
                symbol,
                result["coins_mined"],
                cost_usd=result["electricity_cost_usd"],
            )
            if symbol.upper() not in self._tracked_coins:
                self._tracked_coins.append(symbol.upper())

        return result

    def mining_leaderboard(self, top_n: int = 10) -> list[dict]:
        """
        Return the top-N most profitable coins to mine right now.
        Requires PRO or ENTERPRISE tier for coins beyond BTC.
        """
        allowed = MINING_COIN_LIMITS[self.tier]
        symbols = (
            [c["symbol"] for c in list_mineable_coins()]
            if allowed is None
            else allowed
        )
        return mining_leaderboard(
            symbols=symbols, use_live_price=self.use_live, top_n=top_n
        )

    def break_even(self, symbol: str, hardware_cost_usd: float) -> dict:
        """Calculate break-even days for a mining setup."""
        self._check_mining_coin(symbol)
        return calculate_break_even(
            symbol, hardware_cost_usd, use_live_price=self.use_live
        )

    def mining_profile(self, symbol: str) -> dict:
        """Return the mining hardware profile for *symbol*."""
        self._check_mining_coin(symbol)
        return get_mining_profile(symbol)

    # ------------------------------------------------------------------
    # Prospectus
    # ------------------------------------------------------------------

    def prospectus(self, symbol: str) -> str:
        """Return a formatted prospectus page for *symbol*."""
        return prospectus_text(symbol, use_live_price=self.use_live)

    def prospectus_dict(self, symbol: str) -> dict:
        """Return a structured prospectus dict for *symbol*."""
        return get_coin_prospectus(symbol, use_live_price=self.use_live)

    def all_prospectuses(self, category: str | None = None) -> list[dict]:
        """
        Return prospectus dicts for all coins (or a filtered category).
        Requires ENTERPRISE tier for full library.
        """
        if category is None:
            self._require_tier(Tier.ENTERPRISE, "all_prospectuses (full library)")
        return list_all_prospectuses(category=category, use_live_prices=self.use_live)

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self, market_symbols: list[str] | None = None) -> str:
        """
        Render a full text dashboard. Requires PRO or ENTERPRISE tier.
        """
        self._require_tier(Tier.PRO, "dashboard")
        return render_full_dashboard(
            self._portfolio,
            mining_results=self._mining_sessions[-5:] if self._mining_sessions else None,
            market_symbols=market_symbols or self._tracked_coins,
            use_live=self.use_live,
        )

    def market_board(self, symbols: list[str] | None = None) -> str:
        """Render the market overview board (available on all tiers)."""
        return render_market_overview(
            symbols=symbols or self._tracked_coins, use_live=self.use_live
        )

    # ------------------------------------------------------------------
    # Tier info
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Crypto Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            f"Coin Tracking Limit: {info['coin_limit'] or 'Unlimited'}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output
