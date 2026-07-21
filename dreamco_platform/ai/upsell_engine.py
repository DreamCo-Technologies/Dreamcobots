from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping

@dataclass
class UpsellOpportunity:
    user_id: str
    current_tier: str
    recommended_upgrade: str
    trigger_event: str
    message: str


class UpsellEngine:
    def find_opportunities(self, user_portfolio: Iterable[Mapping[str, object]]) -> List[UpsellOpportunity]:
        opportunities: List[UpsellOpportunity] = []
        for user in user_portfolio:
            tier = str(user.get('current_tier', 'free'))
            usage = float(user.get('usage_pct', 0))
            trigger = self._trigger(user, usage)
            if not trigger:
                continue
            target = self._recommend_tier(tier)
            message = self._message(str(user.get('user_id', 'unknown')), tier, target, trigger)
            opportunities.append(UpsellOpportunity(str(user.get('user_id', 'unknown')), tier, target, trigger, message))
        return opportunities

    @staticmethod
    def _trigger(user: Mapping[str, object], usage: float) -> str | None:
        if usage >= 0.95:
            return 'usage_cap_hit'
        if user.get('feature_request'):
            return 'feature_request'
        if user.get('competitor_comparison'):
            return 'competitor_comparison'
        return None

    @staticmethod
    def _recommend_tier(current_tier: str) -> str:
        order = ['free', 'pro', 'business', 'enterprise']
        try:
            return order[min(order.index(current_tier) + 1, len(order) - 1)]
        except ValueError:
            return 'pro'

    @staticmethod
    def _message(user_id: str, current_tier: str, target_tier: str, trigger: str) -> str:
        return f'User {user_id}: move from {current_tier} to {target_tier} because {trigger.replace("_", " ")} indicates expansion intent.'



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
