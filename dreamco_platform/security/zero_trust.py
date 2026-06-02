from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Dict, List


@dataclass
class ZeroTrustPolicy:
    source_bot: str
    target_bot: str
    allowed_capabilities: List[str]
    conditions: Dict[str, str] = field(default_factory=dict)


@dataclass
class PolicyDecision:
    outcome: str
    reason: str
    audit_required: bool


class CertificateAuthority:
    def __init__(self) -> None:
        self.certificates: Dict[str, datetime] = {}

    def issue(self, bot_id: str, days_valid: int = 30) -> None:
        self.certificates[bot_id] = datetime.utcnow() + timedelta(days=days_valid)

    def valid(self, bot_id: str) -> bool:
        return datetime.utcnow() < self.certificates.get(bot_id, datetime.min)


class PolicyEnforcer:
    def __init__(self) -> None:
        self.ca = CertificateAuthority()
        self.policies: List[ZeroTrustPolicy] = []

    def add_policy(self, policy: ZeroTrustPolicy) -> None:
        self.policies.append(policy)

    def validate(self, request: Dict[str, object]) -> PolicyDecision:
        source = str(request['source_bot'])
        target = str(request['target_bot'])
        capability = str(request['capability'])
        if not (self.ca.valid(source) and self.ca.valid(target)):
            return PolicyDecision('DENY', 'mTLS certificate missing or expired', True)
        for policy in self.policies:
            if policy.source_bot == source and policy.target_bot == target:
                if capability not in policy.allowed_capabilities:
                    return PolicyDecision('DENY', 'capability not authorized', True)
                for key, expected in policy.conditions.items():
                    if request.get(key) != expected:
                        return PolicyDecision('AUDIT', f'condition failed: {key}', True)
                return PolicyDecision('ALLOW', 'request satisfied zero-trust policy', False)
        return PolicyDecision('DENY', 'no matching policy', True)
