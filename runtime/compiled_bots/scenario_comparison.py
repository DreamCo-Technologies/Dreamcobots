"""Auto-generated sandbox bot from bots/scenario-comparison.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class ScenarioComparisonBot(CompiledBot):
    slug = 'scenario-comparison'
    display_name = 'Scenario Comparison Dashboard'
    division = 'DreamDecision'
    tier = 'free'
    mission = 'Provides a visual dashboard comparing decision scenarios side-by-side.'
    capabilities = ['Side-by-side scenario views', 'Key metric comparison', 'Visual difference highlighting', 'Export and sharing features', 'Collaborative annotation', 'Basic analytics', 'Email support', 'Community access']
    autonomy_ceiling = 'plan_only'
    source = 'bots/scenario-comparison.md'

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


def create() -> ScenarioComparisonBot:
    return ScenarioComparisonBot()
