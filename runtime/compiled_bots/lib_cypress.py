"""Auto-generated sandbox bot from bots/lib-cypress.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibCypressBot(CompiledBot):
    slug = 'lib-cypress'
    display_name = 'Cypress Testing Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Cypress for E2E, component testing, network stubbing, and real browser automation.'
    capabilities = ['Cypress E2E test design', 'Component testing', 'Network stub/intercept', 'Custom command library', 'Fixtures management', 'Viewport testing', 'CI integration (GitHub Actions)', 'Dashboard reporting']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-cypress.md'

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


def create() -> LibCypressBot:
    return LibCypressBot()
