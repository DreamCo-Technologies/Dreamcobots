"""Auto-generated sandbox bot from bots/resource-directory.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class ResourceDirectoryBot(CompiledBot):
    slug = 'resource-directory'
    display_name = 'Community Resource Directory'
    division = 'DreamSocial'
    tier = 'free'
    mission = 'Provides a searchable community resource directory with service information.'
    capabilities = ['Resource database search', 'Service category filtering', 'Location-based results', 'Operating hours tracking', 'Eligibility requirement display', 'Basic analytics', 'Email support', 'Community access']
    autonomy_ceiling = 'plan_only'
    source = 'bots/resource-directory.md'

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


def create() -> ResourceDirectoryBot:
    return ResourceDirectoryBot()
