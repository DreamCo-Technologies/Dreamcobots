"""Auto-generated sandbox bot from bots/crewai-agent.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class CrewaiAgentBot(CompiledBot):
    slug = 'crewai-agent'
    display_name = 'CrewAI Team Orchestrator'
    division = 'DreamAgents'
    tier = 'pro'
    mission = 'Multi-agent team orchestrator inspired by CrewAI. Creates teams of specialized agents with roles, goals, and backstories that collaborate like a real team to complete complex projects.'
    capabilities = ['Agent role definition', 'Goal assignment', 'Backstory creation', 'Team collaboration', 'Task delegation', 'Sequential processing', 'Hierarchical teams', 'Tool sharing']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/crewai-agent.md'

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


def create() -> CrewaiAgentBot:
    return CrewaiAgentBot()
