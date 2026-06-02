from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List
import hashlib

@dataclass
class BugReport:
    reporter_id: str
    severity: str
    component: str
    description: str
    poc_code: str
    reward_usd: float = 0.0

@dataclass
class BountyDecision:
    accepted: bool
    cvss_score: float
    estimated_reward: float
    duplicate_of: str | None
    patch_status: str


class BugBounty:
    BASE_REWARDS = {'critical': 5000, 'high': 2500, 'medium': 900, 'low': 250}

    def __init__(self) -> None:
        self.seen: Dict[str, str] = {}

    def process_report(self, report: BugReport) -> BountyDecision:
        digest = hashlib.sha256((report.component + report.description).encode()).hexdigest()
        duplicate = self.seen.get(digest)
        severity = self._triage(report)
        cvss = self._cvss(severity, report)
        reward = self.BASE_REWARDS[severity] * (1.0 + (cvss - int(cvss)) / 10)
        if not duplicate:
            self.seen[digest] = report.reporter_id
        return BountyDecision(accepted=duplicate is None, cvss_score=cvss, estimated_reward=round(0 if duplicate else reward, 2), duplicate_of=duplicate, patch_status='queued_for_patch' if duplicate is None else 'duplicate_closed')

    def _triage(self, report: BugReport) -> str:
        text = f'{report.severity} {report.description} {report.poc_code}'.lower()
        if any(term in text for term in ('rce', 'privilege escalation', 'exfiltration')):
            return 'critical'
        if any(term in text for term in ('sql injection', 'ssrf', 'auth bypass')):
            return 'high'
        if any(term in text for term in ('xss', 'dos', 'csrf')):
            return 'medium'
        return 'low'

    def _cvss(self, severity: str, report: BugReport) -> float:
        base = {'critical': 9.4, 'high': 8.0, 'medium': 6.2, 'low': 3.7}[severity]
        exploitability = min(1.0, len(report.poc_code) / 200)
        return round(min(10.0, base + exploitability * 0.6), 1)



def module_summary() -> dict:
    """Provide a compact runtime summary for orchestration tooling."""
    public_items = [name for name in globals() if not name.startswith('_')]
    return {
        'module': __name__,
        'public_items': sorted(public_items),
        'line_count': len(__doc__.splitlines()) if __doc__ else 0,
    }


def demo_payload() -> dict:
    """Return a deterministic payload useful for smoke-free integration wiring."""
    return {'module': __name__, 'status': 'ready'}
