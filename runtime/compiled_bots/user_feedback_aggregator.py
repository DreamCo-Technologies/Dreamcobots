"""Auto-generated sandbox bot from bots/user-feedback-aggregator.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class UserFeedbackAggregatorBot(CompiledBot):
    slug = 'user-feedback-aggregator'
    display_name = 'User Feedback Aggregator Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Collects, tags, and synthesizes user feedback from reviews, support tickets, surveys, and social mentions.'
    capabilities = ['Multi-source feedback collection', 'AI topic tagging', 'Sentiment classification', 'Feature request clustering', 'Pain point prioritization', 'CSAT/NPS tracking', 'Survey automation', 'Intercom/Zendesk integration']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/user-feedback-aggregator.md'

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


def create() -> UserFeedbackAggregatorBot:
    return UserFeedbackAggregatorBot()
