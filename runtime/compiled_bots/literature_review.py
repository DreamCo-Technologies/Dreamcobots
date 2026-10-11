"""Auto-generated sandbox bot from bots/literature-review.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LiteratureReviewBot(CompiledBot):
    slug = 'literature-review'
    display_name = 'Literature Review Engine'
    division = 'DreamScience'
    tier = 'pro'
    mission = 'Automates literature reviews with citation analysis and knowledge gap identification.'
    capabilities = ['Citation network mapping', 'Knowledge gap identification', 'Systematic review automation', 'Abstract screening tools', 'Reference management integration', 'Trend analysis dashboard', 'Advanced analytics dashboard', 'Priority email support']
    autonomy_ceiling = 'plan_only'
    source = 'bots/literature-review.md'

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


def create() -> LiteratureReviewBot:
    return LiteratureReviewBot()
