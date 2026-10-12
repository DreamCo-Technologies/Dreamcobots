"""Auto-generated sandbox bot from bots/parts-list.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class PartsListBot(CompiledBot):
    slug = 'parts-list'
    display_name = 'Parts List'
    division = 'DreamRobotics'
    tier = 'pro'
    mission = 'Parts lists.'
    capabilities = ['bom']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/parts-list.md'

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


def create() -> PartsListBot:
    return PartsListBot()
