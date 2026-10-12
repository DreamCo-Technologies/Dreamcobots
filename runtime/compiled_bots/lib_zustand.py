"""Auto-generated sandbox bot from bots/lib-zustand.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibZustandBot(CompiledBot):
    slug = 'lib-zustand'
    display_name = 'Zustand & Jotai State Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Zustand, Jotai, Valtio, and XState for lightweight, atomic, and finite-state machine management.'
    capabilities = ['Zustand store design', 'Slice pattern for large stores', 'Jotai atom composition', 'Valtio proxy state', 'XState machine design', 'Devtools integration', 'Persisted state patterns', 'Async action handling']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-zustand.md'

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


def create() -> LibZustandBot:
    return LibZustandBot()
