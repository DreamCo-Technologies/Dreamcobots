from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping

@dataclass
class CurrentStage:
    stage: str
    next_best_action: str
    velocity_days: float


class JourneyOrchestrator:
    STAGE_ORDER = ['awareness', 'consideration', 'decision', 'onboarding', 'expansion']

    def place_user(self, user_id: str, profile: Mapping[str, float] | None = None) -> CurrentStage:
        profile = dict(profile or {})
        score = float(profile.get('engagement_score', 0.0))
        index = min(len(self.STAGE_ORDER) - 1, int(score * len(self.STAGE_ORDER)))
        stage = self.STAGE_ORDER[index]
        action = self._next_action(stage)
        velocity = round(float(profile.get('days_since_last_stage', 7.0)), 2)
        return CurrentStage(stage=stage, next_best_action=action, velocity_days=velocity)

    @staticmethod
    def _next_action(stage: str) -> str:
        mapping = {
            'awareness': 'serve proof-driven educational content',
            'consideration': 'offer ROI calculator and case study',
            'decision': 'trigger pricing assist and objection handling',
            'onboarding': 'launch activation checklist and support concierge',
            'expansion': 'recommend adjacent bots and multi-seat plan',
        }
        return mapping[stage]



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
