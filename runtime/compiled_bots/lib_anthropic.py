"""Auto-generated sandbox bot from bots/lib-anthropic.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibAnthropicBot(CompiledBot):
    slug = 'lib-anthropic'
    display_name = 'Anthropic Claude Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in the Anthropic Claude API, prompt engineering, extended thinking, and computer use.'
    capabilities = ['Claude message API', 'Extended thinking (o1-style)', 'Prompt caching', 'Computer use tool', 'Vision & multimodal', 'Tool use (function calling)', 'Streaming completions', 'Constitutional AI prompting']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-anthropic.md'

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


def create() -> LibAnthropicBot:
    return LibAnthropicBot()
