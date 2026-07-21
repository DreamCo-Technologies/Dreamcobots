"""
Compliance Tools — Regulatory compliance checker and audit utilities.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import re
import hashlib
import datetime
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Regulatory frameworks
# ---------------------------------------------------------------------------

FRAMEWORKS = {
    "GDPR": {
        "name": "General Data Protection Regulation",
        "region": "EU",
        "checks": [
            "data_minimization", "consent_mechanism", "right_to_erasure",
            "data_breach_notification", "privacy_policy", "data_processor_agreements",
            "dpo_designation", "cross_border_transfers",
        ],
    },
    "CCPA": {
        "name": "California Consumer Privacy Act",
        "region": "US-CA",
        "checks": [
            "opt_out_sale", "privacy_policy", "consumer_request_process",
            "data_inventory", "employee_training", "third_party_disclosures",
        ],
    },
    "HIPAA": {
        "name": "Health Insurance Portability and Accountability Act",
        "region": "US",
        "checks": [
            "phi_encryption", "access_controls", "audit_logs",
            "baa_agreements", "incident_response_plan", "employee_training",
            "minimum_necessary_standard", "disposal_procedures",
        ],
    },
    "SOC2": {
        "name": "Service Organization Control 2",
        "region": "Global",
        "checks": [
            "security_policies", "availability_monitoring", "processing_integrity",
            "confidentiality_controls", "privacy_notice", "change_management",
            "vendor_management", "incident_response",
        ],
    },
    "PCI_DSS": {
        "name": "Payment Card Industry Data Security Standard",
        "region": "Global",
        "checks": [
            "cardholder_data_encryption", "network_segmentation", "access_control",
            "vulnerability_management", "monitoring_logging", "security_policy",
            "firewall_configuration", "anti_malware",
        ],
    },
    "ADA": {
        "name": "Americans with Disabilities Act",
        "region": "US",
        "checks": [
            "wcag_compliance", "alt_text_images", "keyboard_navigation",
            "color_contrast", "screen_reader_support", "captions_transcripts",
        ],
    },
    "OSHA": {
        "name": "Occupational Safety and Health Administration",
        "region": "US",
        "checks": [
            "hazard_communication", "ppe_program", "emergency_action_plan",
            "recordkeeping", "training_requirements", "incident_reporting",
        ],
    },
    "ISO_27001": {
        "name": "ISO/IEC 27001 Information Security",
        "region": "Global",
        "checks": [
            "isms_scope", "risk_assessment", "security_controls",
            "asset_management", "access_management", "cryptography_policy",
            "physical_security", "supplier_relationships", "incident_management",
        ],
    },
}

SEVERITY_WEIGHTS = {"critical": 4, "high": 3, "medium": 2, "low": 1}


# ---------------------------------------------------------------------------
# Main compliance checker class
# ---------------------------------------------------------------------------

class ComplianceChecker:
    """Evaluates organizational and technical compliance against regulatory
    frameworks.

    Usage
    -----
    >>> checker = ComplianceChecker()
    >>> report = checker.check_compliance("GDPR", profile)
    >>> score = report["score_pct"]
    """

    def __init__(self):
        self.flow = GlobalAISourcesFlow(bot_name="ComplianceChecker")
        self._audit_log: list[dict] = []

    # ------------------------------------------------------------------
    # Framework information
    # ------------------------------------------------------------------

    def list_frameworks(self) -> list[dict]:
        """Return all supported compliance frameworks."""
        return [
            {
                "id": fid,
                "name": fw["name"],
                "region": fw["region"],
                "total_checks": len(fw["checks"]),
            }
            for fid, fw in FRAMEWORKS.items()
        ]

    def get_framework(self, framework_id: str) -> dict:
        """Return details for a single framework."""
        fw = FRAMEWORKS.get(framework_id.upper())
        if fw is None:
            return {"error": f"Framework {framework_id!r} not found."}
        return {"id": framework_id.upper(), **fw}

    # ------------------------------------------------------------------
    # Compliance checking
    # ------------------------------------------------------------------

    def check_compliance(
        self,
        framework_id: str,
        profile: Optional[dict] = None,
    ) -> dict:
        """Run compliance checks against a framework.

        Parameters
        ----------
        framework_id : str
            One of the supported framework IDs (e.g., "GDPR", "HIPAA").
        profile : dict, optional
            Organizational profile with boolean flags matching check names.
            If not provided, all checks are treated as failed.

        Returns
        -------
        dict
            Compliance report with score, findings, and recommendations.
        """
        framework_id = framework_id.upper()
        fw = FRAMEWORKS.get(framework_id)
        if fw is None:
            return {"error": f"Unsupported framework: {framework_id!r}"}

        profile = profile or {}
        findings = []
        passed = 0

        for check in fw["checks"]:
            is_compliant = bool(profile.get(check, False))
            severity = self._check_severity(check, framework_id)
            findings.append({
                "check": check,
                "label": check.replace("_", " ").title(),
                "status": "pass" if is_compliant else "fail",
                "severity": severity,
                "recommendation": self._recommendation(check, framework_id),
            })
            if is_compliant:
                passed += 1

        total = len(fw["checks"])
        score_pct = round((passed / total * 100) if total else 0, 1)
        risk_level = (
            "low" if score_pct >= 80
            else "medium" if score_pct >= 50
            else "high"
        )

        report = {
            "framework": framework_id,
            "framework_name": fw["name"],
            "score_pct": score_pct,
            "passed": passed,
            "failed": total - passed,
            "total_checks": total,
            "risk_level": risk_level,
            "findings": findings,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        self._audit_log.append({
            "action": "check_compliance",
            "framework": framework_id,
            "score_pct": score_pct,
            "timestamp": report["generated_at"],
        })

        return report

    def check_multiple_frameworks(
        self,
        framework_ids: list[str],
        profile: Optional[dict] = None,
    ) -> list[dict]:
        """Run compliance checks for multiple frameworks at once."""
        return [self.check_compliance(fid, profile) for fid in framework_ids]

    # ------------------------------------------------------------------
    # Risk scoring
    # ------------------------------------------------------------------

    def calculate_risk_score(self, reports: list[dict]) -> dict:
        """Aggregate risk score across multiple compliance reports."""
        if not reports:
            return {"overall_risk": "unknown", "overall_score_pct": 0}

        total_weight = 0
        weighted_score = 0
        for report in reports:
            if "error" in report:
                continue
            weight = len(FRAMEWORKS.get(report["framework"], {}).get("checks", [])) or 1
            weighted_score += report["score_pct"] * weight
            total_weight += weight

        if total_weight == 0:
            return {"overall_risk": "unknown", "overall_score_pct": 0}

        overall_pct = round(weighted_score / total_weight, 1)
        return {
            "overall_score_pct": overall_pct,
            "overall_risk": (
                "low" if overall_pct >= 80
                else "medium" if overall_pct >= 50
                else "high"
            ),
            "frameworks_evaluated": [r["framework"] for r in reports if "error" not in r],
        }

    # ------------------------------------------------------------------
    # Data validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate an email address format using a basic RFC-5321 subset pattern.

        Note: This covers common email formats (ASCII local-part, standard domains).
        It does not handle internationalized domain names (IDN), quoted strings,
        or IP address literals. For production use, consider the ``email-validator``
        library for full RFC compliance.
        """
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_ssn(ssn: str) -> bool:
        """Validate US Social Security Number format (does not check real SSNs)."""
        pattern = r'^\d{3}-\d{2}-\d{4}$'
        return bool(re.match(pattern, ssn))

    @staticmethod
    def mask_pii(text: str) -> str:
        """Mask PII patterns (email, SSN, phone) in a text string."""
        # Mask emails
        text = re.sub(
            r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
            '[EMAIL REDACTED]', text,
        )
        # Mask SSNs
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN REDACTED]', text)
        # Mask phone numbers
        text = re.sub(
            r'\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b',
            '[PHONE REDACTED]', text,
        )
        return text

    @staticmethod
    def hash_identifier(identifier: str) -> str:
        """One-way hash of a PII identifier for pseudonymization."""
        return hashlib.sha256(identifier.encode()).hexdigest()

    # ------------------------------------------------------------------
    # Audit log
    # ------------------------------------------------------------------

    def get_audit_log(self) -> list[dict]:
        """Return the audit log of all compliance check actions."""
        return list(self._audit_log)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_severity(self, check: str, framework: str) -> str:
        critical_checks = {
            "phi_encryption", "cardholder_data_encryption", "data_breach_notification",
            "access_controls", "audit_logs", "firewall_configuration",
        }
        high_checks = {
            "consent_mechanism", "baa_agreements", "risk_assessment",
            "incident_response_plan", "incident_response", "network_segmentation",
        }
        if check in critical_checks:
            return "critical"
        if check in high_checks:
            return "high"
        return "medium"

    def _recommendation(self, check: str, framework: str) -> str:
        recs = {
            "data_minimization": "Audit data collection practices; retain only what is strictly necessary.",
            "consent_mechanism": "Implement explicit opt-in consent with granular controls.",
            "right_to_erasure": "Build a data deletion workflow and document the process.",
            "data_breach_notification": "Establish a 72-hour breach notification procedure (GDPR) or state-specific timelines.",
            "privacy_policy": "Draft and publish a clear privacy policy covering all data processing activities.",
            "phi_encryption": "Encrypt all PHI at rest (AES-256) and in transit (TLS 1.2+).",
            "access_controls": "Implement role-based access controls and enforce least-privilege.",
            "audit_logs": "Enable and retain audit logs for at least 6 years (HIPAA) or per framework requirement.",
            "baa_agreements": "Execute Business Associate Agreements with all PHI-handling vendors.",
            "cardholder_data_encryption": "Tokenize or encrypt cardholder data; never store CVV.",
            "network_segmentation": "Isolate cardholder data environment from other networks.",
            "wcag_compliance": "Conduct WCAG 2.1 AA audit and remediate accessibility gaps.",
            "risk_assessment": "Perform annual information security risk assessment and document results.",
        }
        return recs.get(check, f"Review and implement controls for {check.replace('_', ' ')}.")


# If run directly, show a sample report
if __name__ == '__main__':
    checker = ComplianceChecker()
    frameworks = checker.list_frameworks()
    print(f"Compliance Tools — {len(frameworks)} frameworks available")

    sample_profile = {
        "data_minimization": True,
        "consent_mechanism": True,
        "privacy_policy": True,
        "right_to_erasure": False,
        "data_breach_notification": True,
        "data_processor_agreements": False,
        "dpo_designation": False,
        "cross_border_transfers": True,
    }
    report = checker.check_compliance("GDPR", sample_profile)
    print(f"GDPR Score: {report['score_pct']}%  |  Risk: {report['risk_level']}")
