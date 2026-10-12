"""Auto-generated sandbox bot from bots/lib-parcel.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibParcelBot(CompiledBot):
    slug = 'lib-parcel'
    display_name = 'Parcel & Rome Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Parcel 2, Biome (Rome), and zero-config build tooling for rapid project setup.'
    capabilities = ['Parcel 2 configuration', 'Biome formatter & linter', 'Transformer plugins', 'Glob-based targeting', 'Multi-output bundles', 'Asset optimization', 'Hot reloading', 'Workspaces support']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-parcel.md'

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


def create() -> LibParcelBot:
    return LibParcelBot()
