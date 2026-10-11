"""Auto-generated sandbox bot from bots/buddy-self-teacher.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class BuddySelfTeacherBot(CompiledBot):
    slug = 'buddy-self-teacher'
    display_name = 'Buddy Self-Teaching Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Continuously learns new coding libraries, reads official documentation, runs experiments, and updates all DreamCodeLab bots with new knowledge.'
    capabilities = ['Documentation ingestion & parsing', 'Code example extraction', 'API change detection', 'Self-experiment with new libraries', 'Knowledge graph updates', 'Bot prompt auto-updating', 'Release note analysis', 'RFC & proposal tracking']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/buddy-self-teacher.md'

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


def create() -> BuddySelfTeacherBot:
    return BuddySelfTeacherBot()
