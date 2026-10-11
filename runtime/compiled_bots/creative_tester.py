"""Auto-generated sandbox bot from bots/creative-tester.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class CreativeTesterBot(CompiledBot):
    slug = 'creative-tester'
    display_name = 'Creative Tester'
    division = 'DreamAffiliate'
    tier = 'pro'
    mission = 'Sandbox creatives.'
    capabilities = ['copy-variants']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/creative-tester.md'

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


def create() -> CreativeTesterBot:
    return CreativeTesterBot()
