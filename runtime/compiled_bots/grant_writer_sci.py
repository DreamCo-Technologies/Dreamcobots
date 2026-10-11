"""Auto-generated sandbox bot from bots/grant-writer-sci.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class GrantWriterSciBot(CompiledBot):
    slug = 'grant-writer-sci'
    display_name = 'Research Grant Writer'
    division = 'DreamScience'
    tier = 'pro'
    mission = 'Assists in writing research grant proposals with funding opportunity matching.'
    capabilities = ['Funding opportunity database', 'Proposal structure templates', 'Budget justification builder', 'Specific aims drafting', 'Compliance requirement tracking', 'Reviewer feedback integration', 'Advanced analytics dashboard', 'Priority email support']
    autonomy_ceiling = 'plan_only'
    source = 'bots/grant-writer-sci.md'

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


def create() -> GrantWriterSciBot:
    return GrantWriterSciBot()
