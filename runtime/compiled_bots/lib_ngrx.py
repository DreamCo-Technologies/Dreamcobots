"""Auto-generated sandbox bot from bots/lib-ngrx.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibNgrxBot(CompiledBot):
    slug = 'lib-ngrx'
    display_name = 'NgRx State Management Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in NgRx Store, Effects, Entity, ComponentStore, and Signal Store for Angular state management.'
    capabilities = ['NgRx Store architecture', 'Effects for side effects', 'Entity adapter patterns', 'ComponentStore for local state', 'Signal Store (NgRx 17+)', 'Router Store integration', 'Devtools & time-travel', 'Selector memoization']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-ngrx.md'

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


def create() -> LibNgrxBot:
    return LibNgrxBot()
