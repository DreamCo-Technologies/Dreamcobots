"""Auto-generated sandbox bot from bots/lib-bun.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibBunBot(CompiledBot):
    slug = 'lib-bun'
    display_name = 'Bun Runtime Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Bun runtime, Bun bundler, Bun test runner, and Bun shell for ultra-fast JavaScript tooling.'
    capabilities = ['Bun runtime APIs', 'Bun.serve HTTP server', 'Bun test framework', 'Bun bundler config', 'Bun Shell scripting', 'SQLite integration', 'WebSocket server', 'Hot reload']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-bun.md'

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


def create() -> LibBunBot:
    return LibBunBot()
