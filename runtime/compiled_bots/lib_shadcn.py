"""Auto-generated sandbox bot from bots/lib-shadcn.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibShadcnBot(CompiledBot):
    slug = 'lib-shadcn'
    display_name = 'shadcn/ui & Radix Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in shadcn/ui, Radix UI primitives, and accessible component design systems.'
    capabilities = ['shadcn/ui customization', 'Radix primitive composition', 'Accessible component patterns', 'Theme token system', 'Dark mode implementation', 'Form components (react-hook-form)', 'Data table patterns', 'Command palette']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-shadcn.md'

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


def create() -> LibShadcnBot:
    return LibShadcnBot()
