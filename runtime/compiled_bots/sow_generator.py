"""Auto-generated sandbox bot from bots/sow-generator.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class SowGeneratorBot(CompiledBot):
    slug = 'sow-generator'
    display_name = 'SOW Generator Bot'
    division = 'DreamProServices'
    tier = 'pro'
    mission = 'Generates detailed Statements of Work from discovery notes and templates.'
    capabilities = ['SOW template library', 'Deliverable definition engine', 'Assumption documentation', 'Acceptance criteria builder', 'Rate and budget calculator', 'Advanced analytics dashboard', 'Priority email support', 'API access']
    autonomy_ceiling = 'plan_only'
    source = 'bots/sow-generator.md'

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


def create() -> SowGeneratorBot:
    return SowGeneratorBot()
