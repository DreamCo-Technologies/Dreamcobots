"""Auto-generated sandbox bot from bots/mos-career-planner.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class MosCareerPlannerBot(CompiledBot):
    slug = 'mos-career-planner'
    display_name = 'MOS Career Path Planner'
    division = 'DreamMilitary'
    tier = 'pro'
    mission = 'Plans military career paths with MOS requirements and promotion tracking.'
    capabilities = ['MOS requirement mapping', 'Promotion board preparation', 'Career milestone tracking', 'Professional education planning', 'Assignment preference tools', 'Retirement planning calculator', 'Advanced analytics dashboard', 'Priority email support']
    autonomy_ceiling = 'plan_only'
    source = 'bots/mos-career-planner.md'

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


def create() -> MosCareerPlannerBot:
    return MosCareerPlannerBot()
