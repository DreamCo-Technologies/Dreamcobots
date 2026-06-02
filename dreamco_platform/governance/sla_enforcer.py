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
            'customer': event.customer,
            'severity': event.severity,
            'elapsed_minutes': elapsed,
            'target_minutes': event.target_minutes,
            'breach': breach,
            'credit_due': self.credit_due(event) if breach else 0.0,
            'severity_weight': self.severity_weight(event.severity),
        }

    def severity_weight(self, severity: str) -> float:
        mapping = {'critical': 1.0, 'high': 0.7, 'medium': 0.4, 'low': 0.2}
        return mapping.get(severity.lower(), 0.3)

    def credit_due(self, event: IncidentEvent) -> float:
        elapsed = max(0, int((event.resolved_at - event.started_at).total_seconds() // 60))
        overage = max(0, elapsed - event.target_minutes)
        multiplier = 0.05 if event.severity.lower() == 'critical' else 0.02
        return round(min(0.5, overage / max(event.target_minutes, 1) * multiplier), 3)

    def monthly_report(self, events: Iterable[IncidentEvent]) -> Dict[str, object]:
        rows = [self.evaluate_event(event) for event in events]
        breaches = [row for row in rows if row['breach']]
        weighted_breach_rate = 0.0
        if rows:
            weighted_breach_rate = sum(float(row['breach']) * float(row['severity_weight']) for row in rows) / len(rows)
        return {
            'events': rows,
            'breach_count': len(breaches),
            'credit_exposure': round(sum(float(row['credit_due']) for row in breaches), 3),
            'weighted_breach_rate': round(weighted_breach_rate, 3),
        }

    def remediation_actions(self, events: Iterable[IncidentEvent]) -> List[str]:
        actions: List[str] = []
        for event in events:
            evaluation = self.evaluate_event(event)
            if evaluation['breach']:
                actions.append(f"Review support staffing for {event.customer} {event.severity} incidents.")
        return actions


def enforce(events: Iterable[IncidentEvent]) -> Dict[str, object]:
    enforcer = SLAEnforcer()
    events = list(events)
    report = enforcer.monthly_report(events)
    report['actions'] = enforcer.remediation_actions(events)
    return report
