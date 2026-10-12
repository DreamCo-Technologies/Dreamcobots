"""Auto-generated sandbox bot from bots/expense-reporter.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class ExpenseReporterBot(CompiledBot):
    slug = 'expense-reporter'
    display_name = 'Expense Report Manager'
    division = 'DreamAdmin'
    tier = 'pro'
    mission = 'Manages expense reports with receipt scanning and policy compliance checking.'
    capabilities = ['Receipt OCR scanning', 'Policy compliance validation', 'Approval routing automation', 'Reimbursement tracking tools', 'Budget category allocation', 'Spending analytics dashboard', 'Advanced analytics dashboard', 'Priority email support']
    autonomy_ceiling = 'plan_only'
    source = 'bots/expense-reporter.md'

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


def create() -> ExpenseReporterBot:
    return ExpenseReporterBot()
