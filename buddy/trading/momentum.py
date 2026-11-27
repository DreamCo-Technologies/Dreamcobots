"""Cross-sectional momentum scoring for approved price histories."""

from __future__ import annotations

import math


def calculate_momentum_score(prices: list[float], *, lookback: int = 252) -> float:
    """Return simple trailing momentum: latest close / close lookback bars ago - 1."""
    if lookback <= 0:
        raise ValueError("lookback must be positive")
    values = [float(value) for value in prices]
    if len(values) < lookback + 1:
        raise ValueError(f"need at least {lookback + 1} prices for this lookback")
    if any(not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError("prices must be finite and positive")
    return values[-1] / values[-lookback - 1] - 1.0


def rank_momentum_universe(
    price_histories: dict[str, list[float]],
    *,
    lookback: int = 252,
    top_n: int = 10,
) -> list[dict[str, float | str]]:
    """Rank symbols by trailing momentum; ties are resolved by symbol."""
    if top_n <= 0:
        raise ValueError("top_n must be positive")
    ranked = []
    for raw_symbol, prices in price_histories.items():
        symbol = str(raw_symbol).strip().upper()
        if not symbol:
            raise ValueError("every symbol must be non-empty")
        ranked.append(
            {
                "symbol": symbol,
                "momentum_score": calculate_momentum_score(prices, lookback=lookback),
            }
        )
    return sorted(ranked, key=lambda row: (-float(row["momentum_score"]), str(row["symbol"])))[:top_n]
