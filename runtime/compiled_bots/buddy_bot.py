"""Auto-generated sandbox bot from bots/buddy-bot.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class BuddyBotBot(CompiledBot):
    slug = 'buddy-bot'
    display_name = 'Buddy Bot'
    division = 'CommandCore'
    tier = 'elite'
    mission = 'Primary DreamCo interface and governed task router. Buddy interprets user goals, selects relevant bots and models, prepares or executes bounded workflows through configured tools, and requires approval for high-impact external actions.'
    capabilities = ['Natural-language task routing', 'Cross-bot orchestration', 'Model selection planning', 'Code and app workflow assistance', 'Tool and connector selection', 'Evidence-aware task planning', 'Approval-aware execution', 'User-job completion tracking']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/buddy-bot.md'

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


def create() -> BuddyBotBot:
    return BuddyBotBot()
