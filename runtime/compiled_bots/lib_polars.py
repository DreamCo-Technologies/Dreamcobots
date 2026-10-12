"""Auto-generated sandbox bot from bots/lib-polars.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibPolarsBot(CompiledBot):
    slug = 'lib-polars'
    display_name = 'Polars DataFrame Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Polars, the high-performance DataFrame library with lazy evaluation and Arrow backend.'
    capabilities = ['Lazy evaluation with collect()', 'Expr API mastery', 'GroupBy & aggregation', 'Streaming large datasets', 'String manipulation', 'Time series operations', 'Polars vs. Pandas migration', 'Rust extension']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-polars.md'

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


def create() -> LibPolarsBot:
    return LibPolarsBot()
