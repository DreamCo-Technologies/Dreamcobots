"""Auto-generated sandbox bot from bots/lib-matplotlib.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibMatplotlibBot(CompiledBot):
    slug = 'lib-matplotlib'
    display_name = 'Data Visualization Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Matplotlib, Seaborn, Plotly, and Altair for scientific and interactive data visualization.'
    capabilities = ['Matplotlib subplots & axes', 'Custom style sheets', 'Seaborn statistical plots', 'Plotly interactive charts', 'Altair declarative grammar', 'Geographic visualization', 'Animation with FuncAnimation', 'Dashboard integration']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-matplotlib.md'

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


def create() -> LibMatplotlibBot:
    return LibMatplotlibBot()
