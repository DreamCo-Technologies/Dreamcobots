"""Auto-generated sandbox bot from bots/lib-threejs.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibThreejsBot(CompiledBot):
    slug = 'lib-threejs'
    display_name = 'Three.js & WebGL Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Three.js, WebGL, R3F (React Three Fiber), and interactive 3D web experiences.'
    capabilities = ['Scene graph architecture', 'Mesh & geometry creation', 'Material & shader design', 'Lighting systems', 'Animation (GSAP/mixer)', 'Post-processing effects', 'Physics (Rapier/Cannon)', 'GLTF model loading']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-threejs.md'

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


def create() -> LibThreejsBot:
    return LibThreejsBot()
