"""
DreamCo Platform — Capability-Level Policies
=============================================

Re-exports ``GovernancePolicy`` from ``capabilities.models`` and adds
``CapabilityPolicySet``, a lightweight container that attaches policies to
a specific capability or workflow graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dreamco_platform.capabilities.models import GovernancePolicy  # noqa: F401


@dataclass
class CapabilityPolicySet:
    """A named set of governance policies for a capability or graph.

    Usage::

        ps = CapabilityPolicySet(target_id="lead_pipeline")
        ps.add(GovernancePolicy("no_pii", "deny_pii", "critical"))
    """

    target_id: str
    policies: list[GovernancePolicy] = field(default_factory=list)

    def add(self, policy: GovernancePolicy) -> None:
        self.policies.append(policy)

    def remove(self, policy_id: str) -> bool:
        before = len(self.policies)
        self.policies = [p for p in self.policies if p.policy_id != policy_id]
        return len(self.policies) < before

    def get(self, policy_id: str) -> GovernancePolicy | None:
        for p in self.policies:
            if p.policy_id == policy_id:
                return p
        return None

    def required_approvals(self) -> list[GovernancePolicy]:
        return [p for p in self.policies if "approval" in (p.action or "").lower()]

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "policies": [
                {"policy_id": p.policy_id, "action": p.action, "severity": p.severity}
                for p in self.policies
            ],
        }

    def __len__(self) -> int:
        return len(self.policies)


__all__ = ["GovernancePolicy", "CapabilityPolicySet"]
