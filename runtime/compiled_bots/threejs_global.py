"""Auto-generated sandbox bot from bots/threejs-global.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class ThreejsGlobalBot(CompiledBot):
    slug = 'threejs-global'
    display_name = 'threejs-global'
    division = 'CommandCore'
    tier = 'free'
    mission = 'Study bot for the three.js global category.'
    capabilities = ['plan-task']
    autonomy_ceiling = 'plan_only'
    source = 'bots/threejs-global.md'

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


def create() -> ThreejsGlobalBot:
    return ThreejsGlobalBot()
