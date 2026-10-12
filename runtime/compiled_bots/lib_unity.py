"""Auto-generated sandbox bot from bots/lib-unity.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibUnityBot(CompiledBot):
    slug = 'lib-unity'
    display_name = 'Unity Game Dev Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Unity, C#, game architecture patterns, physics, UI, and mobile game publishing.'
    capabilities = ['MonoBehaviour patterns', 'ScriptableObject architecture', 'Unity Physics system', 'UI Toolkit & Canvas', 'Coroutine & async patterns', 'Addressable Assets', 'Unity Netcode (multiplayer)', 'Mobile optimization']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-unity.md'

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


def create() -> LibUnityBot:
    return LibUnityBot()
