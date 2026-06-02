"""Lightweight legal compliance checks for operational policies."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, Iterable, List


@dataclass
class ComplianceRule:
    name: str
    jurisdiction: str
    renewal_days: int
    required_controls: List[str] = field(default_factory=list)


@dataclass
class ComplianceRecord:
    rule_name: str
    owner: str
    last_reviewed: date
    controls_present: List[str] = field(default_factory=list)


class LegalComplianceMonitor:
    def evaluate(self, rules: Iterable[ComplianceRule], records: Iterable[ComplianceRecord], today: date | None = None) -> List[Dict[str, object]]:
        today = today or date.today()
        record_map = {record.rule_name: record for record in records}
        results: List[Dict[str, object]] = []
        for rule in rules:
            record = record_map.get(rule.name)
            if record is None:
                results.append({
                    "rule": rule.name,
                    "jurisdiction": rule.jurisdiction,
                    "status": "missing",
                    "days_until_due": -1,
                    "missing_controls": rule.required_controls,
                })
                continue
            next_due = record.last_reviewed + timedelta(days=rule.renewal_days)
            days_until_due = (next_due - today).days
            missing_controls = [c for c in rule.required_controls if c not in record.controls_present]
            status = "compliant"
            if days_until_due < 0 or missing_controls:
                status = "action_required"
            elif days_until_due <= 14:
                status = "expiring"
            results.append({
                "rule": rule.name,
                "jurisdiction": rule.jurisdiction,
                "status": status,
                "days_until_due": days_until_due,
                "missing_controls": missing_controls,
                "owner": record.owner,
            })
        return results

    def score(self, evaluations: Iterable[Dict[str, object]]) -> float:
        rows = list(evaluations)
        if not rows:
            return 1.0
        penalty = 0.0
        for row in rows:
            if row["status"] == "missing":
                penalty += 0.5
            elif row["status"] == "action_required":
                penalty += 0.25
            elif row["status"] == "expiring":
                penalty += 0.1
        return round(max(0.0, 1.0 - penalty / len(rows)), 3)

    def remediation_plan(self, evaluations: Iterable[Dict[str, object]]) -> List[str]:
        actions: List[str] = []
        for row in evaluations:
            if row["status"] == "missing":
                actions.append(f"Create compliance record for {row['rule']} in {row['jurisdiction']}.")
            elif row["missing_controls"]:
                controls = ", ".join(row["missing_controls"])
                actions.append(f"Add controls for {row['rule']}: {controls}.")
            elif row["status"] == "expiring":
                actions.append(f"Schedule review for {row['rule']} within two weeks.")
        return actions


def portfolio_summary(rules: Iterable[ComplianceRule], records: Iterable[ComplianceRecord]) -> Dict[str, object]:
    monitor = LegalComplianceMonitor()
    evaluations = monitor.evaluate(rules, records)
    return {"score": monitor.score(evaluations), "issues": monitor.remediation_plan(evaluations)}
