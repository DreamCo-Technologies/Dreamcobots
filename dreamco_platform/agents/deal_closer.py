from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List


class ClosingStrategy(Enum):
    EMAIL_SEQUENCE = 'email_sequence'
    DISCOUNT_OFFER = 'discount_offer'
    URGENCY_CREATION = 'urgency_creation'
    SOCIAL_PROOF = 'social_proof'


@dataclass
class ClosingRecommendation:
    deal_id: str
    strategy: ClosingStrategy
    confidence: float
    next_action: str


class DealCloser:
    def analyze_pipeline(self, deals: Iterable[dict]) -> List[ClosingRecommendation]:
        recommendations = []
        for deal in deals:
            stalled_days = deal.get('stalled_days', 0)
            value = deal.get('value_usd', 0.0)
            if stalled_days >= 21:
                strategy = ClosingStrategy.URGENCY_CREATION
                action = 'Offer limited implementation window with calendar link.'
            elif stalled_days >= 14:
                strategy = ClosingStrategy.SOCIAL_PROOF
                action = 'Send relevant customer success stories.'
            elif value >= 10000:
                strategy = ClosingStrategy.EMAIL_SEQUENCE
                action = 'Launch executive sponsor email sequence.'
            else:
                strategy = ClosingStrategy.DISCOUNT_OFFER
                action = 'Propose expiring incentive on annual plan.'
            confidence = min(0.95, 0.45 + stalled_days / 40 + value / 50000)
            recommendations.append(ClosingRecommendation(deal['deal_id'], strategy, round(confidence, 3), action))
        return recommendations
