"""Autonomous patent landscape monitor."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Sequence


@dataclass
class PatentAlert:
    patent_id: str
    assignee: str
    relevance_score: float
    filing_date: date
    claims: List[str]


class PatentMonitor:
    def __init__(self) -> None:
        self.catalog = [
            PatentAlert("US-1001", "Acme AI", 0.0, date(2023, 5, 1), ["autonomous agent orchestration", "adaptive pricing"]),
            PatentAlert("US-1002", "Nova Systems", 0.0, date(2024, 2, 20), ["social graph clustering", "behavior-based trust scoring"]),
            PatentAlert("US-1003", "Orbit Labs", 0.0, date(2022, 11, 15), ["distributed fine-tuning across workers", "gradient aggregation"]),
        ]

    def scan(self, technology_keywords: Sequence[str]) -> List[PatentAlert]:
        keywords = {keyword.lower() for keyword in technology_keywords}
        alerts: List[PatentAlert] = []
        for alert in self.catalog:
            overlap = sum(any(keyword in claim.lower() for keyword in keywords) for claim in alert.claims)
            if overlap:
                alerts.append(PatentAlert(alert.patent_id, alert.assignee, overlap / len(alert.claims), alert.filing_date, alert.claims))
        return sorted(alerts, key=lambda item: item.relevance_score, reverse=True)

    def freedom_to_operate(self, technology_keywords: Sequence[str]) -> dict:
        alerts = self.scan(technology_keywords)
        blocked_claims = sum(len(alert.claims) for alert in alerts)
        return {
            "alerts": alerts,
            "freedom_to_operate": max(0.0, 1.0 - blocked_claims / 10.0),
            "summary": "Lower scores imply more overlapping claims to review with counsel.",
        }

    def ip_risk_score(self, new_capabilities: Sequence[str]) -> float:
        alerts = self.scan(new_capabilities)
        novelty_penalty = min(0.4, len(new_capabilities) * 0.03)
        overlap_penalty = sum(alert.relevance_score for alert in alerts) * 0.2
        return round(min(1.0, novelty_penalty + overlap_penalty), 3)
