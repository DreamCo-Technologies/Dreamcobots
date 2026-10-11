"""Auto-generated sandbox bot from bots/recipe-scaler.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class RecipeScalerBot(CompiledBot):
    slug = 'recipe-scaler'
    display_name = 'Recipe Scaling Tool'
    division = 'DreamFood'
    tier = 'free'
    mission = 'Scales recipes for different batch sizes with unit conversion and yield calculation.'
    capabilities = ['Batch size scaling engine', 'Unit conversion calculator', 'Yield percentage adjustment', 'Ingredient substitution suggestions', 'Nutrition calculation tools', 'Basic analytics', 'Email support', 'Community access']
    autonomy_ceiling = 'plan_only'
    source = 'bots/recipe-scaler.md'

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


def create() -> RecipeScalerBot:
    return RecipeScalerBot()
