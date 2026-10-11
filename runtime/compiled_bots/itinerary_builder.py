"""Auto-generated sandbox bot from bots/itinerary-builder.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class ItineraryBuilderBot(CompiledBot):
    slug = 'itinerary-builder'
    display_name = 'Itinerary Builder'
    division = 'DreamTravel'
    tier = 'pro'
    mission = 'Itineraries from old global/travel bots.'
    capabilities = ['itinerary']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/itinerary-builder.md'

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


def create() -> ItineraryBuilderBot:
    return ItineraryBuilderBot()
