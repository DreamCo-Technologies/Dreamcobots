"""Service-level agreement enforcement helpers."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List


@dataclass
class IncidentEvent:
    customer: str
    started_at: datetime
    resolved_at: datetime
    severity: str
    target_minutes: int


class SLAEnforcer:
    def evaluate_event(self, event: IncidentEvent) -> Dict[str, object]:
        elapsed = int((event.resolved_at - event.started_at).total_seconds() // 60)
        breach = elapsed > event.target_minutes
        return {
            "customer": event.customer,
            "severity": event.severity,
            "elapsed_minutes": elapsed,
            "target_minutes": event.target_minutes,
            "breach": breach,
            "credit_due": self.credit_due(event) if breach else 0.0,
        }

    def credit_due(self, event: IncidentEvent) -> float:
        elapsed = max(0, int((event.resolved_at - event.started_at).total_seconds() // 60))
        overage = max(0, elapsed - event.target_minutes)
        multiplier = 0.05 if event.severity.lower() == 'critical' else 0.02
        return round(min(0.5, overage / max(event.target_minutes, 1) * multiplier), 3)

    def monthly_report(self, events: Iterable[IncidentEvent]) -> Dict[str, object]:
        rows = [self.evaluate_event(event) for event in events]
        breaches = [row for row in rows if row['breach']]
        return {
            "events": rows,
            "breach_count": len(breaches),
            "credit_exposure": round(sum(float(row['credit_due']) for row in breaches), 3),
        }


def enforce(events: Iterable[IncidentEvent]) -> Dict[str, object]:
    return SLAEnforcer().monthly_report(events)
