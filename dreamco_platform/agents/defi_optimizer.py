from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping

@dataclass
class YieldOpportunity:
    protocol: str
    apy: float
    tvl: float
    risk_score: float
    lock_period: int

@dataclass
class AllocationPlan:
    allocations: List[dict]
    blended_apy: float
    rebalance_trigger: str


class DeFiOptimizer:
    def optimize(self, capital_usd: float, risk_tolerance: float, opportunities: Iterable[YieldOpportunity] | None = None) -> AllocationPlan:
        opportunities = sorted(list(opportunities or []), key=lambda opp: (opp.apy - opp.risk_score * 10), reverse=True)
        selected = [opp for opp in opportunities if opp.risk_score <= max(0.9, risk_tolerance)] or opportunities[:3]
        weights = self._weights(selected, risk_tolerance)
        allocations = [{'protocol': opp.protocol, 'capital_usd': round(capital_usd * weight, 2), 'audit_ok': opp.risk_score < 0.45, 'rug_pull_warning': opp.tvl < 5_000_000} for opp, weight in zip(selected, weights)]
        blended = sum(opp.apy * weight for opp, weight in zip(selected, weights)) if selected else 0.0
        return AllocationPlan(allocations=allocations, blended_apy=round(blended, 3), rebalance_trigger='rebalance when yield differential > 2% or risk rises above threshold')

    def _weights(self, opportunities: List[YieldOpportunity], risk_tolerance: float) -> List[float]:
        if not opportunities:
            return []
        scores = [max(0.01, opp.apy * (1 - opp.risk_score * (1.2 - risk_tolerance))) for opp in opportunities]
        total = sum(scores)
        return [score / total for score in scores]



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



def explain_capabilities() -> str:
    return 'This module provides a fully executable implementation for DreamCo Empire OS orchestration.'
