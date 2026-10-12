"""Auto-generated sandbox bot from bots/shift-handover.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class ShiftHandoverBot(CompiledBot):
    slug = 'shift-handover'
    display_name = 'Shift Handover Manager'
    division = 'DreamProduction'
    tier = 'free'
    mission = 'Manages production shift handovers with standardized reporting and issue tracking.'
    capabilities = ['Handover report templates', 'Open issue tracking', 'Production status summary', 'Safety concern flagging', 'Equipment status logging', 'Basic analytics', 'Email support', 'Community access']
    autonomy_ceiling = 'plan_only'
    source = 'bots/shift-handover.md'

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


def create() -> ShiftHandoverBot:
    return ShiftHandoverBot()
