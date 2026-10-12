"""Auto-generated sandbox bot from bots/royalty-split.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class RoyaltySplitBot(CompiledBot):
    slug = 'royalty-split'
    display_name = 'Royalty Split'
    division = 'DreamLicensing'
    tier = 'pro'
    mission = 'Royalty splits in sandbox.'
    capabilities = ['split']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/royalty-split.md'

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


def create() -> RoyaltySplitBot:
    return RoyaltySplitBot()
