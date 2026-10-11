"""Auto-generated sandbox bot from bots/payout-reconciler.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class PayoutReconcilerBot(CompiledBot):
    slug = 'payout-reconciler'
    display_name = 'Payout Reconciler'
    division = 'DreamAffiliate'
    tier = 'pro'
    mission = 'Reconcile reports; no live payouts.'
    capabilities = ['reconcile']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/payout-reconciler.md'

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


def create() -> PayoutReconcilerBot:
    return PayoutReconcilerBot()
