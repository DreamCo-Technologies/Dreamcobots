"""Transaction fraud scoring based on behavior heuristics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List


@dataclass
class TransactionEvent:
    account_id: str
    amount: float
    country: str
    ip_velocity: int
    device_changes: int
    tags: List[str] = field(default_factory=list)


class FraudDetector:
    def score_event(self, event: TransactionEvent) -> float:
        score = 0.0
        score += min(0.35, event.amount / 10_000)
        score += min(0.25, event.ip_velocity / 20)
        score += min(0.2, event.device_changes / 5)
        if 'chargeback_history' in event.tags:
            score += 0.2
        if 'new_country' in event.tags:
            score += 0.15
        if 'vpn' in event.tags:
            score += 0.1
        return round(min(score, 1.0), 3)

    def explain(self, event: TransactionEvent) -> List[str]:
        reasons: List[str] = []
        if event.amount > 2500:
            reasons.append('high_amount')
        if event.ip_velocity > 5:
            reasons.append('high_ip_velocity')
        if event.device_changes > 1:
            reasons.append('device_churn')
        reasons.extend(tag for tag in event.tags if tag in {'chargeback_history', 'new_country', 'vpn'})
        return reasons

    def account_risk(self, events: Iterable[TransactionEvent]) -> Dict[str, float]:
        grouped: Dict[str, List[float]] = {}
        for event in events:
            grouped.setdefault(event.account_id, []).append(self.score_event(event))
        return {account_id: round(sum(scores) / len(scores), 3) for account_id, scores in grouped.items()}

    def flag_batch(self, events: Iterable[TransactionEvent], threshold: float = 0.65) -> List[Dict[str, object]]:
        flagged = []
        for event in events:
            score = self.score_event(event)
            if score >= threshold:
                flagged.append({
                    'account_id': event.account_id,
                    'score': score,
                    'reasons': self.explain(event),
                })
        return flagged


def batch_score(events: Iterable[TransactionEvent]) -> List[Dict[str, object]]:
    events = list(events)
    detector = FraudDetector()
    account_risk = detector.account_risk(events)
    return [
        {'account_id': event.account_id, 'score': detector.score_event(event), 'account_risk': account_risk[event.account_id]}
        for event in events
    ]
