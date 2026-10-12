"""Auto-generated sandbox bot from bots/lib-nextjs.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibNextjsBot(CompiledBot):
    slug = 'lib-nextjs'
    display_name = 'Next.js Full-Stack Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Next.js App Router, Server Components, streaming, middleware, and edge deployment.'
    capabilities = ['App Router architecture', 'Server & Client Components', 'Streaming with Suspense', 'Middleware & edge functions', 'Static vs. dynamic rendering', 'ISR & revalidation', 'Server Actions', 'Route handlers']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-nextjs.md'

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


def create() -> LibNextjsBot:
    return LibNextjsBot()
