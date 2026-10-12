"""Auto-generated sandbox bot from bots/travel-agency.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class TravelAgencyBot(CompiledBot):
    slug = 'travel-agency'
    display_name = 'DreamTravel Agency AI'
    division = 'DreamGlobal'
    tier = 'pro'
    mission = 'Full-service AI travel agency that books flights, hotels, rental cars, and creates custom itineraries. Finds the best deals and manages loyalty programs.'
    capabilities = ['Flight search and booking', 'Hotel comparison', 'Rental car deals', 'Custom itinerary creation', 'Loyalty program optimization', 'Travel insurance comparison', 'Visa requirement checking', 'Currency exchange alerts']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/travel-agency.md'

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


def create() -> TravelAgencyBot:
    return TravelAgencyBot()
