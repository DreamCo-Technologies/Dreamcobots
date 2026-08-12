from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class RoutingCandidate:
    processor: str
    estimated_cost: Decimal
    reliability_score: Decimal
    latency_ms: int
    available: bool = True


@dataclass(frozen=True)
class RoutingPolicy:
    strategy: str = "balanced"  # balanced | lowest_cost | highest_reliability | lowest_latency
    minimum_reliability: Decimal = Decimal("0.995")
    allowed_processors: tuple[str, ...] = ()


class PaymentRouter:
    """Merchant-policy router. It recommends and routes only within merchant-approved controls."""

    def choose(self, candidates: list[RoutingCandidate], policy: RoutingPolicy) -> RoutingCandidate:
        eligible = [
            c for c in candidates
            if c.available
            and c.reliability_score >= policy.minimum_reliability
            and (not policy.allowed_processors or c.processor in policy.allowed_processors)
        ]
        if not eligible:
            raise RuntimeError("no eligible payment processors for this merchant policy")
        if policy.strategy == "lowest_cost":
            return min(eligible, key=lambda c: (c.estimated_cost, -c.reliability_score, c.latency_ms))
        if policy.strategy == "highest_reliability":
            return max(eligible, key=lambda c: (c.reliability_score, -c.estimated_cost, -c.latency_ms))
        if policy.strategy == "lowest_latency":
            return min(eligible, key=lambda c: (c.latency_ms, c.estimated_cost))
        if policy.strategy != "balanced":
            raise ValueError(f"unsupported routing strategy: {policy.strategy}")
        return sorted(eligible, key=lambda c: (-c.reliability_score, c.estimated_cost, c.latency_ms))[0]
