"""Auto-generated sandbox bot from bots/devin-agent.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class DevinAgentBot(CompiledBot):
    slug = 'devin-agent'
    display_name = 'Devin Software Engineer Agent'
    division = 'DreamAgents'
    tier = 'elite'
    mission = "Fully autonomous software engineer agent inspired by Cognition's Devin. Takes task descriptions and autonomously writes code, runs tests, debugs issues, and creates pull requests."
    capabilities = ['Autonomous coding', 'Test writing', 'Bug fixing', 'PR creation', 'Full IDE access', 'Terminal commands', 'Browser debugging', 'API integration']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/devin-agent.md'

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


def create() -> DevinAgentBot:
    return DevinAgentBot()
