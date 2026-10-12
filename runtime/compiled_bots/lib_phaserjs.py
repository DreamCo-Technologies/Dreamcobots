"""Auto-generated sandbox bot from bots/lib-phaserjs.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibPhaserjsBot(CompiledBot):
    slug = 'lib-phaserjs'
    display_name = 'Phaser.js Browser Game Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Phaser 3 for 2D browser game development with physics, tilemaps, and multiplayer.'
    capabilities = ['Phaser 3 scene lifecycle', 'Arcade & Matter physics', 'Tilemap & Tiled integration', 'Sprite animation', 'Game object pooling', 'Asset preloading', 'State machine patterns', 'Socket.io multiplayer']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-phaserjs.md'

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


def create() -> LibPhaserjsBot:
    return LibPhaserjsBot()
