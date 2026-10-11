"""Auto-generated sandbox bot from bots/hr-onboarding.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class HrOnboardingBot(CompiledBot):
    slug = 'hr-onboarding'
    display_name = 'HR Onboarding Automation'
    division = 'DreamAutomation'
    tier = 'pro'
    mission = 'Automates new hire onboarding with task sequencing and compliance tracking.'
    capabilities = ['Onboarding checklist engine', 'Document collection automation', 'IT provisioning triggers', 'Training assignment', 'Compliance form tracking', 'Advanced analytics dashboard', 'Priority email support', 'API access']
    autonomy_ceiling = 'plan_only'
    source = 'bots/hr-onboarding.md'

    def execute(self, task: dict | None = None) -> BotResult:
        task = task or {}
        plan = [f"Capability: {cap}" for cap in self.capabilities[:12]]
        return self.success(
            data={
                "plan": plan,
                "task": task,
                "mode": "sandbox",
                "live_actions": [],
            },
            metrics={"planned_steps": len(plan), "live_writes": 0},
        )


def create() -> HrOnboardingBot:
    return HrOnboardingBot()
