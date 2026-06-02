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

def execute_with_closerbot(self, recommendations: Iterable[ClosingRecommendation]) -> List[str]:
    return [
        f"CloserBot scheduled {item.strategy.value} for {item.deal_id}: {item.next_action}"
        for item in recommendations
    ]


def stalled_deals(self, deals: Iterable[dict], days: int = 14) -> List[dict]:
    return [deal for deal in deals if deal.get('stalled_days', 0) >= days]


DealCloser.execute_with_closerbot = execute_with_closerbot
DealCloser.stalled_deals = stalled_deals

def summary_table(self, deals: Iterable[dict]) -> List[dict]:
    return [{'deal_id': deal['deal_id'], 'stalled_days': deal.get('stalled_days', 0)} for deal in deals]


DealCloser.summary_table = summary_table
