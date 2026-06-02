from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class ChurnSignal:
    user_id: str
    churn_probability: float
    risk_factors: List[str]
    days_to_churn: int


@dataclass
class AtRiskUser:
    signal: ChurnSignal
    intervention: str


class ChurnPrevention:
    PLAYBOOK = {
        'discount_offer': 'Offer temporary retention discount',
        'success_manager_call': 'Schedule proactive success manager call',
        'feature_highlight': 'Show unused high-value feature walkthrough',
    }

    def scan_users(self, users: Iterable[dict]) -> List[AtRiskUser]:
        at_risk = []
        for user in users:
            risk_factors = []
            probability = 0.1
            if user.get('usage_decline_pct', 0) > 30:
                probability += 0.35
                risk_factors.append('declining usage')
            if user.get('support_tickets', 0) >= 3:
                probability += 0.2
                risk_factors.append('support tickets')
            if user.get('feature_abandonment', False):
                probability += 0.18
                risk_factors.append('feature abandonment')
            if probability >= 0.4:
                signal = ChurnSignal(user['user_id'], round(min(probability, 0.99), 3), risk_factors, max(3, int(30 - probability * 20)))
                play = 'success_manager_call' if probability > 0.6 else 'feature_highlight'
                at_risk.append(AtRiskUser(signal, self.PLAYBOOK[play]))
        return at_risk
