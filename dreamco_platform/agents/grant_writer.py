from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Mapping

@dataclass
class GrantOpportunity:
    name: str
    funder: str
    amount_usd: float
    deadline: date
    requirements: Dict[str, str]

@dataclass
class GrantApplication:
    executive_summary: str
    need_statement: str
    project_plan: str
    budget: str
    evaluation: str
    success_rate_prediction: float


class GrantWriter:
    def draft(self, opportunity: GrantOpportunity, company_profile: Mapping[str, str]) -> GrantApplication:
        mission = company_profile.get('mission', 'build revenue-generating AI systems')
        impact = company_profile.get('impact', 'measurable workforce leverage for customers')
        executive = f"{company_profile.get('company_name', 'DreamCo')} requests ${opportunity.amount_usd:,.0f} from {opportunity.funder} to accelerate {mission}."
        need = f"The market need is urgent: {impact}. This application aligns with {opportunity.requirements.get('focus', 'innovation and inclusion')}."
        plan = 'Phase 1 validate demand, Phase 2 deploy pilots, Phase 3 scale tooling, Phase 4 measure impact and publish learnings.'
        budget = f"Allocate 45% to product delivery, 25% to research, 20% to implementation partners, and 10% to evaluation/compliance."
        evaluation = 'Success will be measured with adoption, revenue efficiency, user satisfaction, and community access metrics.'
        rate = self._predict_success(opportunity, company_profile)
        return GrantApplication(executive_summary=executive, need_statement=need, project_plan=plan, budget=budget, evaluation=evaluation, success_rate_prediction=rate)

    def _predict_success(self, opportunity: GrantOpportunity, company_profile: Mapping[str, str]) -> float:
        alignment = 0.4 + (0.2 if opportunity.requirements.get('focus', '').lower() in company_profile.get('mission', '').lower() else 0.0)
        urgency = 0.2 if (opportunity.deadline - date.today()).days > 14 else 0.1
        track_record = float(company_profile.get('grant_win_rate', 0.35))
        return round(min(0.95, alignment + urgency + track_record), 2)



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
