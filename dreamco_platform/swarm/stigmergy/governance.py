from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from dreamco_platform.swarm.stigmergy.pheromone import PheromoneTrace


ApprovalFn = Callable[[PheromoneTrace], bool]


@dataclass
class GovernancePolicy:
    max_strength: float = 1.0
    max_risk: float = 1.0
    allowed_trace_types: set[str] = field(default_factory=set)
    require_approval: set[str] = field(default_factory=set)
    bot_role_permissions: dict[str, set[str]] = field(default_factory=dict)


@dataclass
class GovernanceDecision:
    allowed: bool
    reason: str
    requires_approval: bool = False


class StigmergyGovernance:
    def __init__(self, policy: GovernancePolicy | None = None, *, approval_fn: ApprovalFn | None = None) -> None:
        self.policy = policy or GovernancePolicy()
        self._approval_fn = approval_fn

    def validate_deposit(self, pheromone: PheromoneTrace, *, bot_role: str = "worker") -> GovernanceDecision:
        if pheromone.strength > self.policy.max_strength:
            return GovernanceDecision(False, "trace strength exceeds policy cap")
        if pheromone.risk > self.policy.max_risk:
            return GovernanceDecision(False, "trace risk exceeds policy cap")
        if self.policy.allowed_trace_types and pheromone.trace_type not in self.policy.allowed_trace_types:
            return GovernanceDecision(False, "trace type is not allowed")
        allowed_types = self.policy.bot_role_permissions.get(bot_role, set())
        if allowed_types and pheromone.trace_type not in allowed_types:
            return GovernanceDecision(False, f"role '{bot_role}' cannot deposit this trace type")
        if pheromone.trace_type in self.policy.require_approval:
            approved = self._approval_fn(pheromone) if self._approval_fn else False
            if not approved:
                return GovernanceDecision(False, "trace requires BuddyAI/human approval", requires_approval=True)
        return GovernanceDecision(True, "trace accepted")
