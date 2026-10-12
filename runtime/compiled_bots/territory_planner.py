"""Auto-generated sandbox bot from bots/territory-planner.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class TerritoryPlannerBot(CompiledBot):
    slug = 'territory-planner'
    display_name = 'Territory Planner'
    division = 'DreamFranchise'
    tier = 'pro'
    mission = 'Territory sketches.'
    capabilities = ['map-plan']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/territory-planner.md'

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


def create() -> TerritoryPlannerBot:
    return TerritoryPlannerBot()
