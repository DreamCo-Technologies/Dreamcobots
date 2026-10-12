"""Auto-generated sandbox bot from bots/integration-runbook.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class IntegrationRunbookBot(CompiledBot):
    slug = 'integration-runbook'
    display_name = 'Integration Runbook'
    division = 'DreamIntegrations'
    tier = 'free'
    mission = 'Integration runbooks.'
    capabilities = ['runbook']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/integration-runbook.md'

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


def create() -> IntegrationRunbookBot:
    return IntegrationRunbookBot()
