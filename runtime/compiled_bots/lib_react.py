"""Auto-generated sandbox bot from bots/lib-react.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibReactBot(CompiledBot):
    slug = 'lib-react'
    display_name = 'React Core Expert Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Deep expertise in React 19, hooks, concurrent features, Suspense, Server Components, and optimization.'
    capabilities = ['React 19 features & Actions', 'Custom hook architecture', 'Suspense & lazy loading', 'Error boundary patterns', 'React Server Components', 'Concurrent rendering optimization', 'Context optimization', 'useReducer state machines']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-react.md'

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


def create() -> LibReactBot:
    return LibReactBot()
