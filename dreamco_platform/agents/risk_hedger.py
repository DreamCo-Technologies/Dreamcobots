from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

@dataclass
class RiskExposure:
    category: str
    probability: float
    impact_usd: float
    current_hedge: Optional[str] = None

@dataclass
class HedgingStrategy:
    instrument: str
    cost: float
    coverage_pct: float
    duration: int

@dataclass
class HedgingPlan:
    strategies: Dict[str, HedgingStrategy]
    expected_loss_before: float
    expected_loss_after: float
    notes: List[str]


class RiskHedger:
    INSTRUMENTS = {
        'currency': ('fx_forward', 0.012, 0.85, 180),
        'concentration': ('revenue_diversification_program', 0.03, 0.55, 365),
        'operational': ('business_interruption_policy', 0.018, 0.7, 365),
        'market': ('index_put_spread', 0.02, 0.65, 90),
        'regulatory': ('compliance_retainer', 0.015, 0.5, 365),
    }

    def optimize_portfolio(self, exposures: Iterable[RiskExposure]) -> HedgingPlan:
        strategies: Dict[str, HedgingStrategy] = {}
        notes: List[str] = []
        before = after = 0.0
        for exposure in exposures:
            expected_loss = exposure.probability * exposure.impact_usd
            before += expected_loss
            instrument, rate, coverage, duration = self.INSTRUMENTS.get(exposure.category, ('reserve_buffer', 0.01, 0.4, 120))
            cost = exposure.impact_usd * rate
            residual = expected_loss * (1 - coverage)
            after += residual + cost
            strategies[exposure.category] = HedgingStrategy(instrument=instrument, cost=round(cost, 2), coverage_pct=coverage, duration=duration)
            notes.append(f'{exposure.category} risk hedged with {instrument} covering {coverage:.0%}.')
        return HedgingPlan(strategies=strategies, expected_loss_before=round(before, 2), expected_loss_after=round(after, 2), notes=notes)



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
