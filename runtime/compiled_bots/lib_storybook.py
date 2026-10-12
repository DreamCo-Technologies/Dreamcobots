"""Auto-generated sandbox bot from bots/lib-storybook.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibStorybookBot(CompiledBot):
    slug = 'lib-storybook'
    display_name = 'Storybook Component Dev Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Storybook 8, CSF3 stories, addons, and visual design system documentation.'
    capabilities = ['CSF3 story patterns', 'Args & ArgTypes', 'Interaction testing', 'Storybook addons', 'Chromatic visual testing', 'Component composition stories', 'Design token integration', 'MDX documentation']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-storybook.md'

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


def create() -> LibStorybookBot:
    return LibStorybookBot()
