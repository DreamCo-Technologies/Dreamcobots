"""Auto-generated sandbox bot from bots/creative-writer.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class CreativeWriterBot(CompiledBot):
    slug = 'creative-writer'
    display_name = 'Creative Writer Agent'
    division = 'DreamContent'
    tier = 'pro'
    mission = 'Creative content agent that writes articles, stories, marketing copy, scripts, and any form of written content.'
    capabilities = ['Article writing', 'Story creation', 'Marketing copy', 'Script writing', 'SEO content', 'Social media posts', 'Email campaigns', 'Brand voice matching']
    autonomy_ceiling = 'plan_only'
    source = 'bots/creative-writer.md'

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


def create() -> CreativeWriterBot:
    return CreativeWriterBot()
