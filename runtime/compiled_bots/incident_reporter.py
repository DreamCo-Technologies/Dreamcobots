"""Auto-generated sandbox bot from bots/incident-reporter.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class IncidentReporterBot(CompiledBot):
    slug = 'incident-reporter'
    display_name = 'Incident Report Generator'
    division = 'DreamProtection'
    tier = 'free'
    mission = 'Generates standardized incident reports with photo documentation and witness details.'
    capabilities = ['Report template builder', 'Photo attachment system', 'Witness information capture', 'Incident classification engine', 'Report distribution automation', 'Basic analytics', 'Email support', 'Community access']
    autonomy_ceiling = 'plan_only'
    source = 'bots/incident-reporter.md'

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


def create() -> IncidentReporterBot:
    return IncidentReporterBot()
