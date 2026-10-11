"""Auto-generated sandbox bot from bots/lib-axios.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibAxiosBot(CompiledBot):
    slug = 'lib-axios'
    display_name = 'HTTP & Fetch Library Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Axios, fetch API, ky, and got for HTTP request management, interceptors, retry logic, and API clients.'
    capabilities = ['Request/response interceptors', 'Retry with exponential backoff', 'Request cancellation (AbortController)', 'Multipart file upload', 'Response caching strategies', 'Authentication middleware', 'Rate limiting client-side', 'Streaming response handling']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-axios.md'

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


def create() -> LibAxiosBot:
    return LibAxiosBot()
