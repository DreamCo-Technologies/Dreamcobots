"""Auto-generated sandbox bot from bots/research-bot.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class ResearchBotBot(CompiledBot):
    slug = 'research-bot'
    display_name = 'Research Bot'
    division = 'CommandCore'
    tier = 'free'
    mission = 'Research planning and synthesis agent for source-backed market, product, competitor, and topic analysis when approved research adapters are available.'
    capabilities = ['Research planning', 'Source discovery planning', 'Competitor analysis', 'Trend analysis', 'Evidence synthesis', 'Citation tracking', 'Uncertainty labeling', 'Research report generation']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/research-bot.md'

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


def create() -> ResearchBotBot:
    return ResearchBotBot()
