# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""Governance layer for the Global AI Learning Matrix."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class GovernancePolicy:
    policy_id: str
    name: str
    description: str
    enabled: bool
    severity: str  # "low" | "medium" | "high" | "critical"


@dataclass
class GovernanceAlert:
    alert_id: str
    policy_id: str
    message: str
    severity: str
    resolved: bool = False


_DEFAULT_POLICIES: list[GovernancePolicy] = [
    GovernancePolicy("pol-001", "Data Privacy", "Ensure PII is anonymized before model training.", True, "critical"),
    GovernancePolicy("pol-002", "Bias Detection", "Run fairness audits on all trained models.", True, "high"),
    GovernancePolicy("pol-003", "Model Drift", "Alert when model accuracy drops > 5% from baseline.", True, "high"),
    GovernancePolicy("pol-004", "Regulatory Compliance", "Validate outputs against GDPR/CCPA/HIPAA rules.", True, "critical"),
    GovernancePolicy("pol-005", "Security Scanning", "Scan model artifacts for adversarial vulnerabilities.", True, "high"),
    GovernancePolicy("pol-006", "Explainability", "All production models must expose feature attribution.", True, "medium"),
    GovernancePolicy("pol-007", "Data Lineage", "Track provenance of all training datasets.", True, "medium"),
    GovernancePolicy("pol-008", "Resource Quota", "Cap GPU/CPU spend per project per month.", True, "low"),
    GovernancePolicy("pol-009", "Access Control", "Enforce role-based access to model artifacts.", True, "high"),
    GovernancePolicy("pol-010", "Audit Logging", "Immutable logs for all inference requests.", True, "medium"),
    GovernancePolicy("pol-011", "Model Versioning", "Every deployed model must have a semantic version.", False, "low"),
    GovernancePolicy("pol-012", "Environmental Impact", "Report carbon footprint for training runs.", False, "low"),
]


class GovernanceLayer:
    """Manages governance policies and alerts for the AI system."""

    def __init__(self):
        self._policies: dict[str, GovernancePolicy] = {p.policy_id: p for p in _DEFAULT_POLICIES}
        self._alerts: dict[str, GovernanceAlert] = {}

    # --- Policies ---

    def get_policy(self, policy_id: str) -> GovernancePolicy:
        if policy_id not in self._policies:
            raise KeyError(f"Policy '{policy_id}' not found.")
        return self._policies[policy_id]

    def list_policies(self, severity: Optional[str] = None) -> list[GovernancePolicy]:
        policies = list(self._policies.values())
        if severity:
            policies = [p for p in policies if p.severity.lower() == severity.lower()]
        return policies

    # --- Alerts ---

    def raise_alert(self, policy_id: str, message: str) -> GovernanceAlert:
        policy = self.get_policy(policy_id)
        alert_id = f"alert-{uuid.uuid4().hex[:8]}"
        alert = GovernanceAlert(
            alert_id=alert_id,
            policy_id=policy_id,
            message=message,
            severity=policy.severity,
        )
        self._alerts[alert_id] = alert
        return alert

    def resolve_alert(self, alert_id: str) -> None:
        if alert_id not in self._alerts:
            raise KeyError(f"Alert '{alert_id}' not found.")
        self._alerts[alert_id].resolved = True

    def list_alerts(self, resolved: Optional[bool] = None) -> list[GovernanceAlert]:
        alerts = list(self._alerts.values())
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        return alerts

    # --- Scoring / Reporting ---

    def get_governance_score(self) -> float:
        """Return a 0-100 score based on enabled policies and unresolved alerts."""
        all_policies = list(self._policies.values())
        enabled_ratio = (
            sum(1 for p in all_policies if p.enabled) / len(all_policies) if all_policies else 1.0
        )

        all_alerts = list(self._alerts.values())
        if not all_alerts:
            alert_penalty = 0.0
        else:
            severity_weights = {"critical": 20, "high": 10, "medium": 5, "low": 2}
            unresolved_penalty = sum(
                severity_weights.get(a.severity, 2) for a in all_alerts if not a.resolved
            )
            alert_penalty = min(unresolved_penalty, 40)

        score = enabled_ratio * 100 - alert_penalty
        return round(max(0.0, min(100.0, score)), 2)

    def audit_report(self) -> dict:
        all_alerts = list(self._alerts.values())
        open_alerts = [a for a in all_alerts if not a.resolved]
        severity_breakdown: dict[str, int] = {}
        for a in open_alerts:
            severity_breakdown[a.severity] = severity_breakdown.get(a.severity, 0) + 1

        return {
            "total_policies": len(self._policies),
            "enabled_policies": sum(1 for p in self._policies.values() if p.enabled),
            "total_alerts": len(all_alerts),
            "open_alerts": len(open_alerts),
            "resolved_alerts": len(all_alerts) - len(open_alerts),
            "open_by_severity": severity_breakdown,
            "governance_score": self.get_governance_score(),
        }
