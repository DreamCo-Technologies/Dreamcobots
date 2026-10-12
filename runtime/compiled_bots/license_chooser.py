"""Auto-generated sandbox bot from bots/license-chooser.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LicenseChooserBot(CompiledBot):
    slug = 'license-chooser'
    display_name = 'License Chooser'
    division = 'DreamLicensing'
    tier = 'pro'
    mission = 'Helps pick SPDX/CC style licenses.'
    capabilities = ['license']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/license-chooser.md'

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


def create() -> LicenseChooserBot:
    return LicenseChooserBot()
