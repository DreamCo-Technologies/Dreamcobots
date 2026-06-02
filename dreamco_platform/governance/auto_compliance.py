from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List


@dataclass
class ComplianceSignal:
    regulation: str
    requirement: str
    status: str
    evidence: str


@dataclass
class ComplianceReport:
    generated_at: datetime
    signals: List[ComplianceSignal]
    remediation_steps: List[str]
    drift_detected: bool


class AutoCompliance:
    def __init__(self) -> None:
        self.baseline: Dict[str, str] = {}
        self.last_scan_at: datetime | None = None

    def scan(self, environment: Dict[str, object]) -> ComplianceReport:
        signals = [
            self._signal('GDPR', 'data_deletion', bool(environment.get('data_deletion_workflow'))),
            self._signal('CCPA', 'opt_out', bool(environment.get('opt_out_link'))),
            self._signal('SOC2', 'audit_logging', bool(environment.get('audit_logging'))),
            self._signal('PCI-DSS', 'card_encryption', bool(environment.get('card_encryption'))),
        ]
        drift = any(self.baseline.get(signal.requirement) not in {None, signal.status} for signal in signals)
        self.baseline = {signal.requirement: signal.status for signal in signals}
        self.last_scan_at = datetime.utcnow()
        remediation = [f'Improve {signal.requirement} for {signal.regulation}' for signal in signals if signal.status != 'pass']
        return ComplianceReport(self.last_scan_at, signals, remediation, drift)

    def next_daily_scan(self) -> datetime:
        base = self.last_scan_at or datetime.utcnow()
        return base + timedelta(days=1)

    def _signal(self, regulation: str, requirement: str, ok: bool) -> ComplianceSignal:
        return ComplianceSignal(regulation, requirement, 'pass' if ok else 'fail', 'auto-collected configuration evidence')

def compliance_score(self, report: ComplianceReport) -> float:
    passed = sum(1 for signal in report.signals if signal.status == 'pass')
    return round(passed / max(len(report.signals), 1), 3)


def baseline_snapshot(self) -> Dict[str, str]:
    return dict(self.baseline)


def drift_summary(self, report: ComplianceReport) -> str:
    if not report.drift_detected:
        return 'No compliance drift detected.'
    return 'Compliance drift detected; compare baseline to current signal states.'


AutoCompliance.compliance_score = compliance_score
AutoCompliance.baseline_snapshot = baseline_snapshot
AutoCompliance.drift_summary = drift_summary
