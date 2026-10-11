"""Auto-generated sandbox bot from bots/lib-prisma.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibPrismaBot(CompiledBot):
    slug = 'lib-prisma'
    display_name = 'Prisma ORM Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Prisma ORM, schema design, migrations, relations, and Prisma Client optimization.'
    capabilities = ['Prisma schema design', 'Relation modeling (1:N, M:N)', 'Migration workflow', 'Prisma Client queries', 'Aggregation & raw SQL', 'Prisma Studio', 'Seeding strategies', 'Soft delete patterns']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-prisma.md'

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


def create() -> LibPrismaBot:
    return LibPrismaBot()
