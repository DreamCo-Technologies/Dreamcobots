"""Auto-generated sandbox bot from bots/code-review-ai.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class CodeReviewAiBot(CompiledBot):
    slug = 'code-review-ai'
    display_name = 'AI Code Reviewer'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Reviews code with best practice enforcement and security vulnerability detection.'
    capabilities = ['Best practice enforcement', 'Security vulnerability scanning', 'Performance issue detection', 'Style consistency checking', 'Suggestion prioritization', 'PR summary generation', 'Advanced analytics dashboard', 'Priority email support']
    autonomy_ceiling = 'plan_only'
    source = 'bots/code-review-ai.md'

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


def create() -> CodeReviewAiBot:
    return CodeReviewAiBot()
