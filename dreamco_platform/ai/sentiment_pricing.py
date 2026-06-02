from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class PriceAdjustment:
    current_price: float
    recommended_price: float
    reason: str
    confidence: float


class SentimentPricingEngine:
    def optimize(self, bot_slug: str, base_price: float, sentiment: float, demand_signal: float, competitor_price: float) -> PriceAdjustment:
        pressure = sentiment * 0.08 + demand_signal * 0.1 + ((competitor_price - base_price) / max(base_price, 1)) * 0.15
        raw_price = base_price * (1 + pressure)
        lower = base_price * 0.8
        upper = base_price * 1.2
        recommended = min(upper, max(lower, raw_price))
        reason = f'{bot_slug} repriced from sentiment={sentiment:.2f}, demand={demand_signal:.2f}, competitor={competitor_price:.2f}'
        confidence = min(0.95, 0.5 + abs(sentiment) * 0.2 + demand_signal * 0.2)
        return PriceAdjustment(base_price, round(recommended, 2), reason, round(confidence, 3))
