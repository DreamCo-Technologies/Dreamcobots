"""Auto-generated sandbox bot from bots/lib-java-spring.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibJavaSpringBot(CompiledBot):
    slug = 'lib-java-spring'
    display_name = 'Java Spring Boot Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Spring Boot 3, Spring Security, JPA, and enterprise Java application architecture.'
    capabilities = ['Spring Boot 3 auto-configuration', 'Spring Security OAuth2', 'JPA/Hibernate ORM', 'Spring Data repositories', 'REST template & WebClient', 'Spring Batch', 'Spring Cache', 'Actuator monitoring']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-java-spring.md'

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


def create() -> LibJavaSpringBot:
    return LibJavaSpringBot()
