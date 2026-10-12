"""Auto-generated sandbox bot from bots/funding-finder.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class FundingFinderBot(CompiledBot):
    slug = 'funding-finder'
    display_name = 'Startup Funding Finder'
    division = 'DreamBizLaunch'
    tier = 'pro'
    mission = 'Finds startup funding opportunities with investor matching and application tracking.'
    capabilities = ['Investor database search', 'Funding round matching', 'Application tracking system', 'Pitch deck templates', 'Due diligence checklist', 'Term sheet comparison tools', 'Advanced analytics dashboard', 'Priority email support']
    autonomy_ceiling = 'plan_only'
    source = 'bots/funding-finder.md'

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


def create() -> FundingFinderBot:
    return FundingFinderBot()
