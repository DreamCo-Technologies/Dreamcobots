"""Auto-generated sandbox bot from bots/lib-pandas.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibPandasBot(CompiledBot):
    slug = 'lib-pandas'
    display_name = 'Pandas Data Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Pandas for data wrangling, cleaning, analysis, and pipeline construction.'
    capabilities = ['DataFrame manipulation', 'GroupBy & aggregation', 'Pivot tables', 'Merge/join strategies', 'Time series resampling', 'Categorical data', 'Memory optimization (dtypes)', 'Method chaining']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-pandas.md'

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


def create() -> LibPandasBot:
    return LibPandasBot()
