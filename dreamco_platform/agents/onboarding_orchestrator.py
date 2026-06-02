from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class OnboardingPlan:
    user_id: str
    stages: List[str]
    personalized_steps: List[str]
    completed: List[str] = field(default_factory=list)


class OnboardingOrchestrator:
    DEFAULT_STAGES = ['welcome', 'profile_setup', 'first_bot_selection', 'first_run', 'revenue_celebration']

    def __init__(self) -> None:
        self.plans: Dict[str, OnboardingPlan] = {}

    def start(self, user_id: str, profile: Dict[str, str]) -> OnboardingPlan:
        personalized = [
            f"Highlight bots for {profile.get('industry', 'general business')}",
            f"Prioritize goal: {profile.get('goals', 'launch quickly')}",
            f"Respect budget band: {profile.get('budget', 'starter')}",
        ]
        plan = OnboardingPlan(user_id, list(self.DEFAULT_STAGES), personalized)
        self.plans[user_id] = plan
        return plan

    def complete_stage(self, user_id: str, stage: str) -> None:
        plan = self.plans[user_id]
        if stage in plan.stages and stage not in plan.completed:
            plan.completed.append(stage)

    def nudges_for_incomplete(self, user_id: str) -> List[str]:
        plan = self.plans[user_id]
        return [f'Nudge user to complete {stage}' for stage in plan.stages if stage not in plan.completed]
