"""Run a self-contained synthetic-data paper-trading demonstration."""

from __future__ import annotations

import json
import math

from .backtest import BacktestConfig, Bar, run_backtest
from .momentum import rank_momentum_universe


def synthetic_bars(count: int = 80) -> list[Bar]:
    if count < 12:
        raise ValueError("count must be at least 12")
    bars = []
    previous = 100.0
    for index in range(count):
        close = 100.0 + 0.18 * index + 3.5 * math.sin(index / 5.0)
        open_price = previous
        bars.append(
            Bar(
                timestamp=f"bar-{index:03d}",
                symbol="SYNTH",
                open=open_price,
                high=max(open_price, close) + 0.8,
                low=min(open_price, close) - 0.8,
                close=close,
                volume=1_000.0 + index,
            )
        )
        previous = close
    return bars



def synthetic_momentum_universe(
    symbol_count: int = 50,
    observations: int = 253,
) -> dict[str, list[float]]:
    """Create a deterministic 50-symbol universe for momentum-ranking practice."""
    if symbol_count <= 0 or observations < 253:
        raise ValueError("require a positive universe and at least 253 daily prices")
    histories = {}
    midpoint = (symbol_count - 1) / 2
    for index in range(symbol_count):
        symbol = f"SYN{index + 1:02d}"
        daily_drift = (index - midpoint) * 0.00005
        histories[symbol] = [
            100.0 * ((1 + daily_drift) ** step) * (1 + 0.002 * math.sin(step / 13 + index / 7))
            for step in range(observations)
        ]
    return histories


def main() -> None:
    result = run_backtest(
        synthetic_bars(),
        config=BacktestConfig(
            initial_cash=10_000.0,
            allocation_fraction=0.20,
            fee_bps=1.0,
            slippage_bps=5.0,
            max_order_notional=2_000.0,
            max_position_notional=2_000.0,
        ),
    )
    report = result.to_dict()
    universe = synthetic_momentum_universe()
    report["momentum_universe_size"] = len(universe)
    report["momentum_lookback_bars"] = 252
    report["top_momentum_symbols"] = rank_momentum_universe(universe, lookback=252, top_n=5)
    report["momentum_selection_note"] = "synthetic ranking demonstration only; no multi-symbol portfolio orders are executed"
    report["data_source"] = "deterministic_synthetic_ohlcv"
    report["safety_notice"] = "paper simulation only; no broker connection or live orders"
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
