"""Auto-generated sandbox bot from bots/offer-researcher.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class OfferResearcherBot(CompiledBot):
    slug = 'offer-researcher'
    display_name = 'Offer Researcher'
    division = 'DreamAffiliate'
    tier = 'pro'
    mission = 'Researches affiliate offers; no silent signups.'
    capabilities = ['research']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/offer-researcher.md'

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


def create() -> OfferResearcherBot:
    return OfferResearcherBot()
