"""Auto-generated sandbox bot from bots/offline-pack.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class OfflinePackBot(CompiledBot):
    slug = 'offline-pack'
    display_name = 'Offline Pack'
    division = 'DreamTravel'
    tier = 'free'
    mission = 'Offline travel pack.'
    capabilities = ['pack']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/offline-pack.md'

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


def create() -> OfflinePackBot:
    return OfflinePackBot()
