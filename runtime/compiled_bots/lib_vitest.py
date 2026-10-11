"""Auto-generated sandbox bot from bots/lib-vitest.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibVitestBot(CompiledBot):
    slug = 'lib-vitest'
    display_name = 'Vitest Framework Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Vitest for fast Vite-native testing with browser mode, coverage, and UI.'
    capabilities = ['Vitest config & setup', 'Browser mode testing', 'Coverage with v8/istanbul', 'Snapshot strategies', 'In-source testing', 'Mocking with vi.mock', 'Fake timers', 'Concurrent test files']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-vitest.md'

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


def create() -> LibVitestBot:
    return LibVitestBot()
