"""Auto-generated sandbox bot from bots/client-intake-care.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class ClientIntakeCareBot(CompiledBot):
    slug = 'client-intake-care'
    display_name = 'Client Intake & Consultation'
    division = 'DreamPersonalCare'
    tier = 'pro'
    mission = 'Manages client intake for personal care services with consultation and allergy tracking.'
    capabilities = ['Digital intake form builder', 'Consultation note management', 'Allergy and sensitivity tracking', 'Before/after photo logging', 'Consent form collection', 'Treatment history archive', 'Advanced analytics dashboard', 'Priority email support']
    autonomy_ceiling = 'plan_only'
    source = 'bots/client-intake-care.md'

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


def create() -> ClientIntakeCareBot:
    return ClientIntakeCareBot()
