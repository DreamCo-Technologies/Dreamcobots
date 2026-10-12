"""Auto-generated sandbox bot from bots/lib-jest.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibJestBot(CompiledBot):
    slug = 'lib-jest'
    display_name = 'Jest Testing Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Jest, testing patterns, mocks, snapshots, and full unit test suite architecture.'
    capabilities = ['Unit test design', 'Mock & spy patterns', 'Snapshot testing', 'Coverage enforcement', 'Async test handling', 'Custom matchers', 'Module mock strategies', 'Timer mocking']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-jest.md'

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


def create() -> LibJestBot:
    return LibJestBot()
