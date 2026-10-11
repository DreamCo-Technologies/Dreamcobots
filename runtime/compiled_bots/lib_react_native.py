"""Auto-generated sandbox bot from bots/lib-react-native.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibReactNativeBot(CompiledBot):
    slug = 'lib-react-native'
    display_name = 'React Native Expert Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in React Native, Expo, and native module integration for iOS and Android app development.'
    capabilities = ['React Native component patterns', 'Expo managed & bare workflow', 'Navigation (React Navigation)', 'Native module bridging', 'Async Storage & MMKV', 'Platform-specific code', 'Push notification setup', 'Deep linking']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-react-native.md'

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


def create() -> LibReactNativeBot:
    return LibReactNativeBot()
