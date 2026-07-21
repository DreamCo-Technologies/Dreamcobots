"""
Portfolio — tracks holdings, balances, and transaction history.

GLOBAL AI SOURCES FLOW: participates via crypto_bot.py pipeline.
"""

from __future__ import annotations

import sys
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from bots.crypto_bot.crypto_database import get_coin
from bots.crypto_bot.price_feed import get_prices


# ---------------------------------------------------------------------------
# Transaction types
# ---------------------------------------------------------------------------

class TransactionType:
    BUY = "buy"
    SELL = "sell"
    MINE = "mine"
    SEND = "send"
    RECEIVE = "receive"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Transaction:
    """A single portfolio transaction record."""
    tx_id: str
    tx_type: str
    symbol: str
    amount: float
    price_usd: float
    total_usd: float
    fee_usd: float
    timestamp: str
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "tx_id": self.tx_id,
            "tx_type": self.tx_type,
            "symbol": self.symbol,
            "amount": self.amount,
            "price_usd": self.price_usd,
            "total_usd": self.total_usd,
            "fee_usd": self.fee_usd,
            "timestamp": self.timestamp,
            "notes": self.notes,
        }


@dataclass
class Holding:
    """Aggregate holding for one coin."""
    symbol: str
    total_amount: float = 0.0
    cost_basis_usd: float = 0.0    # total USD spent acquiring the holding
    realised_pnl_usd: float = 0.0  # profit/loss already locked in by sells

    @property
    def avg_cost_usd(self) -> float:
        """Average cost per coin."""
        return self.cost_basis_usd / self.total_amount if self.total_amount else 0.0

    def unrealised_pnl(self, current_price_usd: float) -> float:
        """Unrealised P&L given the current market price."""
        market_value = self.total_amount * current_price_usd
        return round(market_value - self.cost_basis_usd, 8)

    def to_dict(self, current_price_usd: Optional[float] = None) -> dict:
        result = {
            "symbol": self.symbol,
            "total_amount": self.total_amount,
            "cost_basis_usd": round(self.cost_basis_usd, 8),
            "avg_cost_usd": round(self.avg_cost_usd, 8),
            "realised_pnl_usd": round(self.realised_pnl_usd, 8),
        }
        if current_price_usd is not None:
            market_value = round(self.total_amount * current_price_usd, 8)
            result["current_price_usd"] = current_price_usd
            result["market_value_usd"] = market_value
            result["unrealised_pnl_usd"] = self.unrealised_pnl(current_price_usd)
            result["total_pnl_usd"] = round(
                result["unrealised_pnl_usd"] + self.realised_pnl_usd, 8
            )
        return result


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------

class PortfolioError(Exception):
    """Raised on invalid portfolio operations."""


class Portfolio:
    """
    Tracks cryptocurrency holdings, USD balance, and transaction history.

    Attributes
    ----------
    usd_balance : float
        Available USD (cash) balance.
    holdings : dict[str, Holding]
        Per-coin holdings keyed by symbol.
    transactions : list[Transaction]
        Ordered list of all transactions.
    """

    def __init__(self, initial_usd_balance: float = 10_000.0) -> None:
        self.usd_balance: float = initial_usd_balance
        self.holdings: dict[str, Holding] = {}
        self.transactions: list[Transaction] = []
        self._tx_counter: int = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _new_tx_id(self) -> str:
        self._tx_counter += 1
        return f"TX{self._tx_counter:06d}"

    def _ensure_holding(self, symbol: str) -> Holding:
        sym = symbol.upper()
        if sym not in self.holdings:
            self.holdings[sym] = Holding(symbol=sym)
        return self.holdings[sym]

    def _record(
        self,
        tx_type: str,
        symbol: str,
        amount: float,
        price_usd: float,
        total_usd: float,
        fee_usd: float = 0.0,
        notes: str = "",
    ) -> Transaction:
        tx = Transaction(
            tx_id=self._new_tx_id(),
            tx_type=tx_type,
            symbol=symbol.upper(),
            amount=amount,
            price_usd=price_usd,
            total_usd=total_usd,
            fee_usd=fee_usd,
            timestamp=datetime.now(timezone.utc).isoformat(),
            notes=notes,
        )
        self.transactions.append(tx)
        return tx

    # ------------------------------------------------------------------
    # Deposit / Withdraw USD
    # ------------------------------------------------------------------

    def deposit_usd(self, amount: float) -> dict:
        """Add USD to the cash balance."""
        if amount <= 0:
            raise PortfolioError("Deposit amount must be positive.")
        self.usd_balance = round(self.usd_balance + amount, 8)
        tx = self._record(TransactionType.DEPOSIT, "USD", amount, 1.0, amount)
        return {"usd_balance": self.usd_balance, "tx": tx.to_dict()}

    def withdraw_usd(self, amount: float) -> dict:
        """Remove USD from the cash balance."""
        if amount <= 0:
            raise PortfolioError("Withdrawal amount must be positive.")
        if amount > self.usd_balance:
            raise PortfolioError(
                f"Insufficient USD balance. Available: ${self.usd_balance:.2f}"
            )
        self.usd_balance = round(self.usd_balance - amount, 8)
        tx = self._record(TransactionType.WITHDRAW, "USD", amount, 1.0, amount)
        return {"usd_balance": self.usd_balance, "tx": tx.to_dict()}

    # ------------------------------------------------------------------
    # Buy
    # ------------------------------------------------------------------

    def buy(
        self,
        symbol: str,
        amount: float,
        price_usd: float,
        fee_pct: float = 0.001,
    ) -> dict:
        """
        Buy *amount* of *symbol* at *price_usd* each.

        Parameters
        ----------
        symbol      : coin ticker (e.g. "BTC")
        amount      : quantity to buy
        price_usd   : purchase price per coin in USD
        fee_pct     : trading fee as a fraction (default 0.1 %)
        """
        if amount <= 0:
            raise PortfolioError("Buy amount must be positive.")
        if price_usd <= 0:
            raise PortfolioError("Price must be positive.")

        gross_usd = amount * price_usd
        fee_usd = round(gross_usd * fee_pct, 8)
        total_usd = round(gross_usd + fee_usd, 8)

        if total_usd > self.usd_balance:
            raise PortfolioError(
                f"Insufficient USD balance. Need ${total_usd:.2f}, "
                f"have ${self.usd_balance:.2f}."
            )

        self.usd_balance = round(self.usd_balance - total_usd, 8)
        holding = self._ensure_holding(symbol)
        holding.total_amount = round(holding.total_amount + amount, 8)
        holding.cost_basis_usd = round(holding.cost_basis_usd + gross_usd, 8)

        tx = self._record(
            TransactionType.BUY, symbol, amount, price_usd, total_usd, fee_usd,
            notes=f"Bought {amount} {symbol.upper()} @ ${price_usd:.4f}",
        )
        return {
            "tx": tx.to_dict(),
            "holding": holding.to_dict(),
            "usd_balance": self.usd_balance,
        }

    # ------------------------------------------------------------------
    # Sell
    # ------------------------------------------------------------------

    def sell(
        self,
        symbol: str,
        amount: float,
        price_usd: float,
        fee_pct: float = 0.001,
    ) -> dict:
        """
        Sell *amount* of *symbol* at *price_usd* each.

        Parameters
        ----------
        symbol      : coin ticker
        amount      : quantity to sell
        price_usd   : sale price per coin in USD
        fee_pct     : trading fee as a fraction (default 0.1 %)
        """
        if amount <= 0:
            raise PortfolioError("Sell amount must be positive.")
        if price_usd <= 0:
            raise PortfolioError("Price must be positive.")

        sym = symbol.upper()
        holding = self.holdings.get(sym)
        if not holding or holding.total_amount < amount:
            available = holding.total_amount if holding else 0.0
            raise PortfolioError(
                f"Insufficient {sym} balance. "
                f"Have {available:.8f}, trying to sell {amount:.8f}."
            )

        gross_usd = amount * price_usd
        fee_usd = round(gross_usd * fee_pct, 8)
        net_usd = round(gross_usd - fee_usd, 8)

        # Calculate realised P&L using average cost
        avg_cost = holding.avg_cost_usd
        cost_of_sold = round(amount * avg_cost, 8)
        realised = round(net_usd - cost_of_sold, 8)

        # Update holding
        holding.total_amount = round(holding.total_amount - amount, 8)
        holding.cost_basis_usd = round(
            holding.cost_basis_usd - cost_of_sold, 8
        )
        if holding.cost_basis_usd < 0:
            holding.cost_basis_usd = 0.0
        holding.realised_pnl_usd = round(holding.realised_pnl_usd + realised, 8)

        self.usd_balance = round(self.usd_balance + net_usd, 8)

        tx = self._record(
            TransactionType.SELL, symbol, amount, price_usd, gross_usd, fee_usd,
            notes=f"Sold {amount} {sym} @ ${price_usd:.4f} | P&L: ${realised:.4f}",
        )
        return {
            "tx": tx.to_dict(),
            "holding": holding.to_dict(),
            "usd_balance": self.usd_balance,
            "realised_pnl_usd": realised,
        }

    # ------------------------------------------------------------------
    # Mine (add mined coins)
    # ------------------------------------------------------------------

    def add_mined(self, symbol: str, amount: float, cost_usd: float = 0.0) -> dict:
        """
        Credit *amount* of *symbol* from mining activity.

        Parameters
        ----------
        symbol   : coin ticker
        amount   : quantity mined
        cost_usd : electricity / operational cost (reduces P&L baseline)
        """
        if amount <= 0:
            raise PortfolioError("Mined amount must be positive.")
        holding = self._ensure_holding(symbol)
        holding.total_amount = round(holding.total_amount + amount, 8)
        holding.cost_basis_usd = round(holding.cost_basis_usd + cost_usd, 8)
        tx = self._record(
            TransactionType.MINE, symbol, amount, 0.0, cost_usd, 0.0,
            notes=f"Mined {amount} {symbol.upper()} (cost: ${cost_usd:.4f})",
        )
        return {"tx": tx.to_dict(), "holding": holding.to_dict()}

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self, use_live_prices: bool = False) -> dict:
        """
        Return a full portfolio summary including current market values.
        """
        symbols = list(self.holdings.keys())
        prices = get_prices(symbols, use_live=use_live_prices) if symbols else {}

        holdings_data = []
        total_market_value = 0.0
        total_cost_basis = 0.0
        total_realised_pnl = 0.0

        for sym, holding in self.holdings.items():
            price = prices.get(sym, 0.0)
            h_dict = holding.to_dict(current_price_usd=price)
            holdings_data.append(h_dict)
            total_market_value += h_dict.get("market_value_usd", 0.0)
            total_cost_basis += holding.cost_basis_usd
            total_realised_pnl += holding.realised_pnl_usd

        total_unrealised_pnl = round(total_market_value - total_cost_basis, 8)
        total_portfolio_value = round(total_market_value + self.usd_balance, 8)

        return {
            "usd_balance": round(self.usd_balance, 8),
            "total_market_value_usd": round(total_market_value, 8),
            "total_portfolio_value_usd": total_portfolio_value,
            "total_cost_basis_usd": round(total_cost_basis, 8),
            "total_unrealised_pnl_usd": total_unrealised_pnl,
            "total_realised_pnl_usd": round(total_realised_pnl, 8),
            "total_pnl_usd": round(total_unrealised_pnl + total_realised_pnl, 8),
            "holdings": holdings_data,
            "num_holdings": len(holdings_data),
            "num_transactions": len(self.transactions),
        }

    def get_transactions(
        self,
        symbol: Optional[str] = None,
        tx_type: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Return recent transactions, optionally filtered."""
        txs = self.transactions
        if symbol:
            txs = [t for t in txs if t.symbol == symbol.upper()]
        if tx_type:
            txs = [t for t in txs if t.tx_type == tx_type]
        return [t.to_dict() for t in txs[-limit:]]
