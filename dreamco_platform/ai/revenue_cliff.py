from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, List, Mapping

@dataclass
class RevenueCliff:
    component: str
    current_revenue: float
    projected_drop_pct: float
    trigger_date: date
    trigger_type: str
    mitigation_playbook: List[str]

    @classmethod
    def scan(cls, revenue_forecast: Iterable[Mapping[str, object]]) -> List['RevenueCliff']:
        cliffs: List['RevenueCliff'] = []
        for row in revenue_forecast:
            drop = float(row.get('projected_drop_pct', 0))
            if drop < 0.15:
                continue
            trigger = str(row.get('trigger_type', 'contract_expiry'))
            component = str(row.get('component', 'unknown'))
            cliffs.append(cls(component, float(row.get('current_revenue', 0)), drop, date.today() + timedelta(days=int(row.get('days_until_trigger', 30))), trigger, cls._playbook(trigger)))
        return cliffs

    @staticmethod
    def _playbook(trigger: str) -> List[str]:
        mapping = {
            'contract_expiry': ['renewal outreach', 'exec sponsorship', 'discount guardrails'],
            'churn_acceleration': ['save offer', 'usage recovery program', 'success intervention'],
            'competitor_pricing_change': ['repackage bundles', 'value proof campaign', 'targeted retention credits'],
        }
        return mapping.get(trigger, ['diagnose cause', 'deploy revenue squad'])



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


def default_triggers() -> List[str]:
    return ['contract_expiry', 'churn_acceleration', 'competitor_pricing_change']



