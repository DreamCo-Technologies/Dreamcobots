"""
Trading — buy/sell execution engine with profit/loss reporting.

Integrates with Portfolio and PriceFeed to execute trades and produce
detailed P&L summaries.

GLOBAL AI SOURCES FLOW: participates via crypto_bot.py pipeline.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from bots.crypto_bot.crypto_database import get_coin
from bots.crypto_bot.portfolio import Portfolio, PortfolioError
from bots.crypto_bot.price_feed import get_price, get_price_change_24h


class TradingError(Exception):
    """Raised when a trade cannot be executed."""


class TradingEngine:
    """
    Executes buy/sell orders against a Portfolio, using live or simulated prices.

    Parameters
    ----------
    portfolio   : the Portfolio instance to trade against
    fee_pct     : default trading fee (fraction, e.g. 0.001 = 0.1 %)
    use_live    : whether to fetch live prices from CoinGecko
    """

    DEFAULT_FEE = 0.001  # 0.1 % — typical exchange fee

    def __init__(
        self,
        portfolio: Portfolio,
        fee_pct: float = DEFAULT_FEE,
        use_live: bool = False,
    ) -> None:
        self.portfolio = portfolio
        self.fee_pct = fee_pct
        self.use_live = use_live

    # ------------------------------------------------------------------
    # Price helpers
    # ------------------------------------------------------------------

    def current_price(self, symbol: str) -> float:
        """Return the current price for *symbol* in USD."""
        sym = symbol.upper()
        coin = get_coin(sym)
        if not coin:
            raise TradingError(f"Unknown cryptocurrency: {sym}")
        price = get_price(sym, use_live=self.use_live)
        if price is None:
            raise TradingError(f"Price unavailable for {sym}")
        return price

    # ------------------------------------------------------------------
    # Market orders
    # ------------------------------------------------------------------

    def market_buy(self, symbol: str, usd_amount: float) -> dict:
        """
        Buy as much of *symbol* as possible with *usd_amount* USD.

        Parameters
        ----------
        symbol     : coin ticker
        usd_amount : USD to spend (excluding fees)
        """
        if usd_amount <= 0:
            raise TradingError("USD amount must be positive.")
        price = self.current_price(symbol)
        fee = usd_amount * self.fee_pct
        net_usd = usd_amount - fee
        amount = net_usd / price

        try:
            result = self.portfolio.buy(
                symbol, amount, price, fee_pct=self.fee_pct
            )
        except PortfolioError as exc:
            raise TradingError(str(exc)) from exc

        result["order_type"] = "market_buy"
        result["requested_usd"] = usd_amount
        result["price_usd"] = price
        result["amount_received"] = amount
        return result

    def market_sell(self, symbol: str, amount: float) -> dict:
        """
        Sell *amount* of *symbol* at the current market price.

        Parameters
        ----------
        symbol : coin ticker
        amount : quantity to sell
        """
        if amount <= 0:
            raise TradingError("Amount must be positive.")
        price = self.current_price(symbol)

        try:
            result = self.portfolio.sell(
                symbol, amount, price, fee_pct=self.fee_pct
            )
        except PortfolioError as exc:
            raise TradingError(str(exc)) from exc

        result["order_type"] = "market_sell"
        result["price_usd"] = price
        return result

    def sell_all(self, symbol: str) -> dict:
        """Sell the entire holding of *symbol*."""
        sym = symbol.upper()
        holding = self.portfolio.holdings.get(sym)
        if not holding or holding.total_amount <= 0:
            raise TradingError(f"No {sym} holding to sell.")
        return self.market_sell(sym, holding.total_amount)

    # ------------------------------------------------------------------
    # Limit orders (simulated — executes immediately if price meets limit)
    # ------------------------------------------------------------------

    def limit_buy(self, symbol: str, amount: float, limit_price: float) -> dict:
        """
        Place a simulated limit buy.  Executes immediately if the current
        price is at or below *limit_price*.
        """
        price = self.current_price(symbol)
        if price > limit_price:
            return {
                "order_type": "limit_buy",
                "status": "pending",
                "symbol": symbol.upper(),
                "amount": amount,
                "limit_price": limit_price,
                "current_price": price,
                "message": (
                    f"Limit buy for {amount} {symbol.upper()} @ ${limit_price:.4f} "
                    f"is pending. Current price: ${price:.4f}"
                ),
            }
        try:
            result = self.portfolio.buy(symbol, amount, price, fee_pct=self.fee_pct)
        except PortfolioError as exc:
            raise TradingError(str(exc)) from exc
        result["order_type"] = "limit_buy"
        result["status"] = "filled"
        result["limit_price"] = limit_price
        return result

    def limit_sell(self, symbol: str, amount: float, limit_price: float) -> dict:
        """
        Place a simulated limit sell.  Executes immediately if the current
        price is at or above *limit_price*.
        """
        price = self.current_price(symbol)
        if price < limit_price:
            return {
                "order_type": "limit_sell",
                "status": "pending",
                "symbol": symbol.upper(),
                "amount": amount,
                "limit_price": limit_price,
                "current_price": price,
                "message": (
                    f"Limit sell for {amount} {symbol.upper()} @ ${limit_price:.4f} "
                    f"is pending. Current price: ${price:.4f}"
                ),
            }
        try:
            result = self.portfolio.sell(symbol, amount, price, fee_pct=self.fee_pct)
        except PortfolioError as exc:
            raise TradingError(str(exc)) from exc
        result["order_type"] = "limit_sell"
        result["status"] = "filled"
        result["limit_price"] = limit_price
        return result

    # ------------------------------------------------------------------
    # P&L report
    # ------------------------------------------------------------------

    def pnl_report(self) -> dict:
        """
        Return a complete profit/loss report for the portfolio.
        """
        summary = self.portfolio.summary(use_live_prices=self.use_live)
        holdings = summary["holdings"]

        rows = []
        for h in holdings:
            sym = h["symbol"]
            price = get_price(sym, use_live=self.use_live) or 0.0
            change = get_price_change_24h(sym)
            rows.append({
                "symbol": sym,
                "amount": h["total_amount"],
                "avg_cost_usd": h["avg_cost_usd"],
                "current_price_usd": price,
                "market_value_usd": h.get("market_value_usd", 0.0),
                "cost_basis_usd": h["cost_basis_usd"],
                "unrealised_pnl_usd": h.get("unrealised_pnl_usd", 0.0),
                "realised_pnl_usd": h["realised_pnl_usd"],
                "total_pnl_usd": h.get("total_pnl_usd", 0.0),
                "change_24h_pct": change,
            })

        return {
            "holdings": rows,
            "usd_balance": summary["usd_balance"],
            "total_market_value_usd": summary["total_market_value_usd"],
            "total_portfolio_value_usd": summary["total_portfolio_value_usd"],
            "total_cost_basis_usd": summary["total_cost_basis_usd"],
            "total_unrealised_pnl_usd": summary["total_unrealised_pnl_usd"],
            "total_realised_pnl_usd": summary["total_realised_pnl_usd"],
            "total_pnl_usd": summary["total_pnl_usd"],
            "num_transactions": summary["num_transactions"],
        }
