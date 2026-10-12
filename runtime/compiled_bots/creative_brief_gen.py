"""Auto-generated sandbox bot from bots/creative-brief-gen.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class CreativeBriefGenBot(CompiledBot):
    slug = 'creative-brief-gen'
    display_name = 'Creative Brief Generator'
    division = 'DreamArts'
    tier = 'pro'
    mission = 'Generates creative briefs with brand guideline integration and stakeholder input management.'
    capabilities = ['Brief template library', 'Brand guideline integration', 'Stakeholder feedback collection', 'Deadline management system', 'Asset requirement listing', 'Approval workflow automation', 'Advanced analytics dashboard', 'Priority email support']
    autonomy_ceiling = 'plan_only'
    source = 'bots/creative-brief-gen.md'

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


def create() -> CreativeBriefGenBot:
    return CreativeBriefGenBot()
