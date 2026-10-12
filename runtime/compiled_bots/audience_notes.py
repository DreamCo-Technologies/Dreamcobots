"""Auto-generated sandbox bot from bots/audience-notes.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class AudienceNotesBot(CompiledBot):
    slug = 'audience-notes'
    display_name = 'Audience Notes'
    division = 'DreamStreaming'
    tier = 'pro'
    mission = 'Audience notes from comments you paste.'
    capabilities = ['notes']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/audience-notes.md'

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


def create() -> AudienceNotesBot:
    return AudienceNotesBot()
