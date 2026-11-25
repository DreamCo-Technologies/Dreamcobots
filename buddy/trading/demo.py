"""Run a self-contained synthetic-data paper-trading demonstration."""

from __future__ import annotations

import json
import math

from .backtest import BacktestConfig, Bar, run_backtest


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
    report["data_source"] = "deterministic_synthetic_ohlcv"
    report["safety_notice"] = "paper simulation only; no broker connection or live orders"
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
