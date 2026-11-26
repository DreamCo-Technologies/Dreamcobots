"""Deterministic, long-only backtesting with next-bar execution and risk limits."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from statistics import mean

from .paper_broker import PaperBroker, RiskLimitError


@dataclass(frozen=True)
class Bar:
    timestamp: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    def __post_init__(self) -> None:
        if not self.timestamp or not self.symbol.strip():
            raise ValueError("bar timestamp and symbol are required")
        try:
            values = tuple(float(value) for value in (
                self.open, self.high, self.low, self.close, self.volume
            ))
        except (TypeError, ValueError, OverflowError):
            raise ValueError("OHLCV values must be finite numbers") from None
        if not all(math.isfinite(value) for value in values):
            raise ValueError("OHLCV values must be finite numbers")
        if min(values[:4]) <= 0:
            raise ValueError("OHLC prices must be positive")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("bar high is inconsistent")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("bar low is inconsistent")
        if values[4] < 0:
            raise ValueError("volume cannot be negative")


@dataclass(frozen=True)
class BacktestConfig:
    initial_cash: float = 10_000.0
    allocation_fraction: float = 0.25
    fee_bps: float = 1.0
    slippage_bps: float = 5.0
    max_order_notional: float = 5_000.0
    max_position_notional: float = 5_000.0
    liquidate_at_end: bool = True

    def __post_init__(self) -> None:
        try:
            values = tuple(float(value) for value in (
                self.initial_cash, self.allocation_fraction, self.fee_bps,
                self.slippage_bps, self.max_order_notional, self.max_position_notional,
            ))
        except (TypeError, ValueError, OverflowError):
            raise ValueError("backtest configuration values must be finite numbers") from None
        if not all(math.isfinite(value) for value in values):
            raise ValueError("backtest configuration values must be finite numbers")
        if self.initial_cash <= 0:
            raise ValueError("initial_cash must be positive")
        if not 0 < self.allocation_fraction <= 1:
            raise ValueError("allocation_fraction must be in (0, 1]")
        if self.fee_bps < 0 or not 0 <= self.slippage_bps < 10_000:
            raise ValueError("fees must be non-negative and slippage must be in [0, 10000) bps")
        if self.max_order_notional <= 0 or self.max_position_notional <= 0:
            raise ValueError("notional risk limits must be positive")


@dataclass(frozen=True)
class BacktestResult:
    mode: str
    live_orders_enabled: bool
    symbol: str
    starting_cash: float
    ending_cash: float
    ending_equity: float
    total_return: float
    max_drawdown: float
    fill_count: int
    equity_curve: tuple[float, ...]
    fills: tuple[dict, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def sma_crossover_signals(
    bars: list[Bar],
    *,
    fast_window: int = 3,
    slow_window: int = 8,
) -> list[int]:
    """Return long/flat signals; signal[i] uses closes strictly before bar i."""
    if fast_window <= 0 or slow_window <= fast_window:
        raise ValueError("require 0 < fast_window < slow_window")
    closes = [float(bar.close) for bar in bars]
    signals = [0] * len(bars)
    for index in range(slow_window, len(bars)):
        history = closes[index - slow_window:index]
        fast_average = mean(history[-fast_window:])
        slow_average = mean(history)
        signals[index] = 1 if fast_average > slow_average else 0
    return signals



def _sell_in_chunks(
    broker: PaperBroker,
    symbol: str,
    quantity: float,
    reference_price: float,
    timestamp: str,
) -> None:
    """Liquidate a position without violating the per-order notional cap."""
    execution_factor = 1 - broker.slippage_bps / 10_000.0
    executable_price = reference_price * execution_factor
    if executable_price <= 0:
        raise ValueError("sell execution price must be positive")
    max_chunk = broker.max_order_notional / executable_price
    remaining = quantity
    while remaining > 1e-9:
        chunk = min(remaining, max_chunk)
        broker.submit_market_order(symbol, "sell", chunk, reference_price, timestamp)
        remaining -= chunk


def run_backtest(
    bars: list[Bar],
    *,
    signals: list[int] | None = None,
    config: BacktestConfig | None = None,
) -> BacktestResult:
    """Run a single-symbol long-only simulation; signals execute at the next bar open."""
    if not bars:
        raise ValueError("at least one bar is required")
    symbol = bars[0].symbol.strip().upper()
    if any(bar.symbol.strip().upper() != symbol for bar in bars):
        raise ValueError("this MVP accepts one symbol per backtest")
    if any(bars[index].timestamp > bars[index + 1].timestamp for index in range(len(bars) - 1)):
        raise ValueError("bars must be ordered chronologically")

    settings = config or BacktestConfig()
    signal_values = signals if signals is not None else sma_crossover_signals(bars)
    if len(signal_values) != len(bars) or any(value not in {0, 1} for value in signal_values):
        raise ValueError("signals must contain one long/flat value (0 or 1) per bar")

    broker = PaperBroker(
        settings.initial_cash,
        fee_bps=settings.fee_bps,
        slippage_bps=settings.slippage_bps,
        max_order_notional=settings.max_order_notional,
        max_position_notional=settings.max_position_notional,
        allow_short=False,
    )
    equity_curve = [settings.initial_cash]
    peak = settings.initial_cash
    max_drawdown = 0.0

    for index, bar in enumerate(bars):
        desired_position = signal_values[index]
        current_quantity = broker.positions.get(symbol, 0.0)
        if desired_position == 1 and current_quantity <= 0:
            budget = min(
                broker.cash * settings.allocation_fraction,
                settings.max_order_notional,
                settings.max_position_notional,
            )
            execution_factor = 1 + settings.slippage_bps / 10_000.0
            quantity = budget / (bar.open * execution_factor)
            if quantity > 0:
                try:
                    broker.submit_market_order(symbol, "buy", quantity, bar.open, bar.timestamp)
                except RiskLimitError:
                    # A risk rejection leaves the portfolio unchanged; never bypass it.
                    pass
        elif desired_position == 0 and current_quantity > 0:
            _sell_in_chunks(broker, symbol, current_quantity, bar.open, bar.timestamp)

        marked_equity = broker.equity({symbol: bar.close})
        equity_curve.append(marked_equity)
        peak = max(peak, marked_equity)
        if peak > 0:
            max_drawdown = max(max_drawdown, (peak - marked_equity) / peak)

    if settings.liquidate_at_end and broker.positions.get(symbol, 0.0) > 0:
        last_bar = bars[-1]
        _sell_in_chunks(
            broker,
            symbol,
            broker.positions[symbol],
            last_bar.close,
            f"{last_bar.timestamp}:end_of_backtest",
        )
        equity_curve[-1] = broker.cash
        peak = max(peak, broker.cash)
        if peak > 0:
            max_drawdown = max(max_drawdown, (peak - broker.cash) / peak)

    ending_equity = broker.equity({symbol: bars[-1].close}) if broker.positions else broker.cash
    total_return = (ending_equity / settings.initial_cash) - 1
    return BacktestResult(
        mode=broker.mode,
        live_orders_enabled=broker.live_orders_enabled,
        symbol=symbol,
        starting_cash=settings.initial_cash,
        ending_cash=broker.cash,
        ending_equity=ending_equity,
        total_return=total_return,
        max_drawdown=max_drawdown,
        fill_count=len(broker.fills),
        equity_curve=tuple(equity_curve),
        fills=tuple(asdict(fill) for fill in broker.fills),
    )
