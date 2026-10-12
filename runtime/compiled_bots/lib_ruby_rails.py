"""Auto-generated sandbox bot from bots/lib-ruby-rails.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibRubyRailsBot(CompiledBot):
    slug = 'lib-ruby-rails'
    display_name = 'Ruby on Rails Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Rails 7+, Hotwire, ActiveRecord, Sidekiq, and full-stack Ruby web development.'
    capabilities = ['Rails MVC conventions', 'ActiveRecord associations', 'Hotwire Turbo & Stimulus', 'ActionCable WebSocket', 'Devise authentication', 'Sidekiq background jobs', 'Capybara system tests', 'Rails engines']
    autonomy_ceiling = 'plan_only'
    source = 'bots/lib-ruby-rails.md'

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


def create() -> LibRubyRailsBot:
    return LibRubyRailsBot()
