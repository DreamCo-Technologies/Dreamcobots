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

def optimize_batch(self, portfolio: Iterable[dict]) -> list[PriceAdjustment]:
    adjustments = []
    for item in portfolio:
        adjustments.append(
            self.optimize(
                item['bot_slug'],
                item['base_price'],
                item.get('sentiment', 0.0),
                item.get('demand_signal', 0.0),
                item.get('competitor_price', item['base_price']),
            )
        )
    return adjustments


def capped_change(self, current_price: float, recommended_price: float) -> float:
    if current_price == 0:
        return 0.0
    return round((recommended_price - current_price) / current_price, 4)


def market_reasoning(self, sentiment: float, demand_signal: float) -> str:
    if sentiment > 0.3 and demand_signal > 0.4:
        return 'Positive sentiment and strong demand support a premium move.'
    if sentiment < -0.2:
        return 'Weak sentiment suggests defensive pricing.'
    return 'Balanced market signals support modest optimization.'


SentimentPricingEngine.optimize_batch = optimize_batch
SentimentPricingEngine.capped_change = capped_change
SentimentPricingEngine.market_reasoning = market_reasoning

def recommended_delta(self, adjustment: PriceAdjustment) -> float:
    return round(adjustment.recommended_price - adjustment.current_price, 2)


SentimentPricingEngine.recommended_delta = recommended_delta
