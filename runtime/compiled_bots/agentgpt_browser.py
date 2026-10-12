"""Auto-generated sandbox bot from bots/agentgpt-browser.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class AgentgptBrowserBot(CompiledBot):
    slug = 'agentgpt-browser'
    display_name = 'AgentGPT Browser Agent'
    division = 'DreamAgents'
    tier = 'free'
    mission = 'Browser-based autonomous agent inspired by AgentGPT. Deploy autonomous agents directly from the browser with no coding required. Just type a goal and watch it work.'
    capabilities = ['Browser-based execution', 'No-code setup', 'Goal-driven automation', 'Web search integration', 'Task breakdown', 'Progress visualization', 'Result compilation', 'Simple interface']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/agentgpt-browser.md'

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


def create() -> AgentgptBrowserBot:
    return AgentgptBrowserBot()
