"""Auto-generated sandbox bot from bots/research-analyst.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class ResearchAnalystBot(CompiledBot):
    slug = 'research-analyst'
    display_name = 'Research Analyst Agent'
    division = 'CommandCore'
    tier = 'pro'
    mission = 'Produces structured source-backed research packets from approved sources, clearly separating evidence, inference, uncertainty, and unresolved questions.'
    capabilities = ['Multi-source research planning', 'Citation tracking', 'Evidence tables', 'Trend analysis', 'Competitive intelligence', 'Literature review support', 'Data synthesis', 'Fact verification workflow']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/research-analyst.md'

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


def create() -> ResearchAnalystBot:
    return ResearchAnalystBot()
