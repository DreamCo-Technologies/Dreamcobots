from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping

@dataclass
class WhaleCustomer:
    user_id: str
    ltv_usd: float
    active_bots: int
    monthly_spend: float
    at_risk_score: float


class WhaleTracker:
    def identify(self, min_monthly_spend: float = 1000, customers: Iterable[Mapping[str, float]] | None = None) -> List[WhaleCustomer]:
        whales: List[WhaleCustomer] = []
        for customer in customers or []:
            spend = float(customer.get('monthly_spend', 0))
            if spend >= min_monthly_spend:
                risk = self._risk_score(customer)
                whales.append(WhaleCustomer(str(customer.get('user_id', 'unknown')), float(customer.get('ltv_usd', spend * 12)), int(customer.get('active_bots', 1)), spend, risk))
        return sorted(whales, key=lambda whale: whale.monthly_spend, reverse=True)

    def _risk_score(self, customer: Mapping[str, float]) -> float:
        usage_drop = float(customer.get('usage_drop_pct', 0))
        ticket_escalations = float(customer.get('ticket_escalations', 0))
        contract_days = float(customer.get('contract_days_remaining', 180))
        risk = usage_drop * 0.5 + ticket_escalations * 0.1 + (30 / max(contract_days, 30)) * 0.4
        return round(min(1.0, risk), 3)

    def vip_protocol(self, whale: WhaleCustomer) -> List[str]:
        return [
            f'Assign dedicated success manager to {whale.user_id}.',
            'Schedule executive business review.',
            'Offer roadmap briefing and priority support channel.',
        ]



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


