"""Auto-generated sandbox bot from bots/eval-card.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class EvalCardBot(CompiledBot):
    slug = 'eval-card'
    display_name = 'Eval Card'
    division = 'DreamFoundry'
    tier = 'pro'
    mission = 'Eval cards for students.'
    capabilities = ['eval']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/eval-card.md'

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


def create() -> EvalCardBot:
    return EvalCardBot()
