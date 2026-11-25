"""A deterministic paper broker. This module has no network or live-broker adapter."""

from __future__ import annotations

from dataclasses import dataclass


LIVE_TRADING_ENABLED = False


class RiskLimitError(ValueError):
    """Raised when a simulated order violates a paper-account risk limit."""


@dataclass(frozen=True)
class Fill:
    symbol: str
    side: str
    quantity: float
    reference_price: float
    execution_price: float
    fee: float
    timestamp: str


class PaperBroker:
    """Local simulated broker with cash, long-only positions, fees, and slippage."""

    mode = "paper_only"
    live_orders_enabled = LIVE_TRADING_ENABLED

    def __init__(
        self,
        initial_cash: float = 10_000.0,
        *,
        fee_bps: float = 1.0,
        slippage_bps: float = 5.0,
        max_order_notional: float = 5_000.0,
        max_position_notional: float = 5_000.0,
        allow_short: bool = False,
    ) -> None:
        if initial_cash <= 0:
            raise ValueError("initial_cash must be positive")
        if fee_bps < 0 or slippage_bps < 0:
            raise ValueError("fees and slippage cannot be negative")
        if max_order_notional <= 0 or max_position_notional <= 0:
            raise ValueError("notional risk limits must be positive")
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        self.fee_bps = float(fee_bps)
        self.slippage_bps = float(slippage_bps)
        self.max_order_notional = float(max_order_notional)
        self.max_position_notional = float(max_position_notional)
        self.allow_short = bool(allow_short)
        self.positions: dict[str, float] = {}
        self.fills: list[Fill] = []

    def submit_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        reference_price: float,
        timestamp: str,
    ) -> Fill:
        """Fill a simulated market order immediately at reference plus/minus slippage."""
        symbol = str(symbol).strip().upper()
        side = str(side).strip().lower()
        quantity = float(quantity)
        reference_price = float(reference_price)
        if not symbol:
            raise ValueError("symbol is required")
        if side not in {"buy", "sell"}:
            raise ValueError("side must be 'buy' or 'sell'")
        if quantity <= 0 or reference_price <= 0:
            raise ValueError("quantity and reference_price must be positive")

        slippage = self.slippage_bps / 10_000.0
        execution_price = reference_price * (1 + slippage if side == "buy" else 1 - slippage)
        notional = quantity * execution_price
        if notional > self.max_order_notional:
            raise RiskLimitError("order exceeds max_order_notional")

        current_position = self.positions.get(symbol, 0.0)
        fee = notional * self.fee_bps / 10_000.0
        if side == "buy":
            projected_position = current_position + quantity
            if projected_position * execution_price > self.max_position_notional:
                raise RiskLimitError("order exceeds max_position_notional")
            total_cost = notional + fee
            if total_cost > self.cash:
                raise RiskLimitError("insufficient paper cash")
            self.cash -= total_cost
            self.positions[symbol] = projected_position
        else:
            if quantity > current_position and not self.allow_short:
                raise RiskLimitError("short selling is disabled in this paper broker")
            projected_position = current_position - quantity
            if abs(projected_position) * execution_price > self.max_position_notional:
                raise RiskLimitError("order exceeds max_position_notional")
            self.cash += notional - fee
            if abs(projected_position) < 1e-12:
                self.positions.pop(symbol, None)
            else:
                self.positions[symbol] = projected_position

        fill = Fill(
            symbol=symbol,
            side=side,
            quantity=quantity,
            reference_price=reference_price,
            execution_price=execution_price,
            fee=fee,
            timestamp=str(timestamp),
        )
        self.fills.append(fill)
        return fill

    def equity(self, mark_prices: dict[str, float] | None = None) -> float:
        """Return cash plus marked-to-market positions."""
        marks = mark_prices or {}
        value = self.cash
        for symbol, quantity in self.positions.items():
            if symbol not in marks:
                raise ValueError(f"missing mark price for {symbol}")
            price = float(marks[symbol])
            if price <= 0:
                raise ValueError("mark prices must be positive")
            value += quantity * price
        return value

    def snapshot(self) -> dict:
        return {
            "mode": self.mode,
            "live_orders_enabled": self.live_orders_enabled,
            "cash": self.cash,
            "positions": dict(self.positions),
            "fill_count": len(self.fills),
        }
