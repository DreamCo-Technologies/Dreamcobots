"""Auto-generated sandbox bot from bots/lib-vercel-ai.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibVercelAiBot(CompiledBot):
    slug = 'lib-vercel-ai'
    display_name = 'Vercel AI SDK Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Vercel AI SDK for streaming AI responses, generative UI, and multi-provider LLM integration.'
    capabilities = ['streamText & streamObject', 'useChat & useCompletion hooks', 'AI SDK RSC (React Server Components)', 'Multi-provider routing', 'Tool calling & tool results', 'Structured output generation', 'Middleware pipeline', 'Image generation']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-vercel-ai.md'

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


def create() -> LibVercelAiBot:
    return LibVercelAiBot()
