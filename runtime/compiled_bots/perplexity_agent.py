"""Auto-generated sandbox bot from bots/perplexity-agent.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class PerplexityAgentBot(CompiledBot):
    slug = 'perplexity-agent'
    display_name = 'Perplexity Search Agent'
    division = 'DreamAgents'
    tier = 'pro'
    mission = 'AI search agent inspired by Perplexity Comet. Actively searches, browses, and synthesizes web information to complete research tasks with cited, verified answers.'
    capabilities = ['Active web search', 'Source verification', 'Citation generation', 'Multi-hop reasoning', 'Real-time data', 'Answer synthesis', 'Follow-up questions', 'Topic exploration']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/perplexity-agent.md'

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


def create() -> PerplexityAgentBot:
    return PerplexityAgentBot()
