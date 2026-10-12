"""Auto-generated sandbox bot from bots/crash-reporter-bot.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class CrashReporterBotBot(CompiledBot):
    slug = 'crash-reporter-bot'
    display_name = 'Crash Reporter Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Aggregates crash reports from Sentry, Crashlytics, and Bugsnag, deduplicates issues, and prioritizes fixes by revenue impact.'
    capabilities = ['Multi-platform crash aggregation', 'Deduplication engine', 'Revenue impact scoring', 'Affected-user counting', 'Stack trace analysis', 'Auto GitHub issue creation', 'Release regression detection', 'Error trend alerting']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/crash-reporter-bot.md'

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


def create() -> CrashReporterBotBot:
    return CrashReporterBotBot()
