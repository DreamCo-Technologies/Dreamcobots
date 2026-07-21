"""Autonomous legal compliance checker."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List
from datetime import datetime


REGULATIONS = ["GDPR Article 6", "CCPA Section 1798", "SOX", "HIPAA", "PCI-DSS"]


@dataclass
class ComplianceRule:
    regulation: str
    requirement: str
    test_fn: Callable[[Dict[str, object]], bool]
    remediation: str


@dataclass
class ComplianceFinding:
    regulation: str
    requirement: str
    passed: bool
    remediation: str


@dataclass
class ComplianceAuditReport:
    bot_id: str
    generated_at: datetime
    findings: List[ComplianceFinding]
    evidence: List[str] = field(default_factory=list)
    soc2_type_ii_evidence: List[str] = field(default_factory=list)

    @property
    def compliant(self) -> bool:
        return all(item.passed for item in self.findings)


class LegalCompliance:
    def __init__(self, bot_registry: Dict[str, Dict[str, object]] | None = None) -> None:
        self.bot_registry = bot_registry or {}
        self.rules = [
            ComplianceRule("GDPR Article 6", "Lawful basis documented", lambda d: bool(d.get("lawful_basis")), "Document lawful basis for processing."),
            ComplianceRule("CCPA Section 1798", "Consumer delete/export workflow", lambda d: bool(d.get("ccpa_workflow")), "Implement delete and access request workflow."),
            ComplianceRule("SOX", "Material financial changes logged", lambda d: bool(d.get("audit_log")), "Enable immutable audit logs for financial events."),
            ComplianceRule("HIPAA", "Protected health information encrypted", lambda d: not d.get("handles_phi") or bool(d.get("phi_encryption")), "Encrypt PHI at rest and in transit."),
            ComplianceRule("PCI-DSS", "Card data tokenized", lambda d: not d.get("handles_card") or bool(d.get("card_tokenization")), "Use tokenization for payment data."),
        ]

    def _collect_evidence(self, bot_id: str, profile: Dict[str, object]) -> List[str]:
        evidence = [
            f"bot:{bot_id}",
            f"owner:{profile.get('owner', 'unknown')}",
            f"logging:{profile.get('audit_log', False)}",
            f"data_map:{profile.get('data_inventory', 'not supplied')}",
        ]
        return evidence

    def _collect_soc2_evidence(self, profile: Dict[str, object]) -> List[str]:
        return [
            f"control-monitoring={bool(profile.get('continuous_monitoring'))}",
            f"incident-response={bool(profile.get('incident_response_plan'))}",
            f"access-review={bool(profile.get('access_review'))}",
            "evidence-ready-for-soc2-type-ii",
        ]

    def audit(self, bot_id: str) -> ComplianceAuditReport:
        profile = dict(self.bot_registry.get(bot_id, {}))
        findings = [
            ComplianceFinding(rule.regulation, rule.requirement, rule.test_fn(profile), rule.remediation)
            for rule in self.rules
        ]
        return ComplianceAuditReport(
            bot_id=bot_id,
            generated_at=datetime.utcnow(),
            findings=findings,
            evidence=self._collect_evidence(bot_id, profile),
            soc2_type_ii_evidence=self._collect_soc2_evidence(profile),
        )
