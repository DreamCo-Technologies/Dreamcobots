"""Auto-generated sandbox bot from bots/api-map.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class ApiMapBot(CompiledBot):
    slug = 'api-map'
    display_name = 'API Map'
    division = 'DreamIntegrations'
    tier = 'pro'
    mission = 'API maps from the old API automation system.'
    capabilities = ['map']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/api-map.md'

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


def create() -> ApiMapBot:
    return ApiMapBot()
