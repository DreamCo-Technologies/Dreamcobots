"""Auto-generated sandbox bot from bots/onboarding-funnel-bot.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class OnboardingFunnelBotBot(CompiledBot):
    slug = 'onboarding-funnel-bot'
    display_name = 'Onboarding Funnel Bot'
    division = 'DreamSalesPro'
    tier = 'pro'
    mission = 'Optimizes user onboarding with step analysis, drop-off detection, personalized flow branching, and activation event tracking.'
    capabilities = ['Onboarding step analysis', 'Drop-off point detection', 'Personalized flow branching', 'Activation event tracking', 'Time-to-value optimization', 'Email/push sequence automation', 'Tooltip & guide generator', 'In-app survey integration']
    autonomy_ceiling = 'plan_only'
    source = 'bots/onboarding-funnel-bot.md'

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


def create() -> OnboardingFunnelBotBot:
    return OnboardingFunnelBotBot()
