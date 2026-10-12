"""Auto-generated sandbox bot from bots/track-chooser.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class TrackChooserBot(CompiledBot):
    slug = 'track-chooser'
    display_name = 'Track Chooser'
    division = 'DreamFoundry'
    tier = 'pro'
    mission = 'Chooses open-source, open-weights, or frontier-hosted.'
    capabilities = ['track']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/track-chooser.md'

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


def create() -> TrackChooserBot:
    return TrackChooserBot()
