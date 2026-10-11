"""Auto-generated sandbox bot from bots/lib-terraform.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibTerraformBot(CompiledBot):
    slug = 'lib-terraform'
    display_name = 'Terraform IaC Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in Terraform, Terragrunt, and OpenTofu for multi-cloud infrastructure as code.'
    capabilities = ['Resource graph design', 'Module composition patterns', 'State management & backends', 'Workspace strategies', 'Terragrunt DRY patterns', 'Policy as code (Sentinel/OPA)', 'Import existing resources', 'Terraform testing (Terratest)']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-terraform.md'

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


def create() -> LibTerraformBot:
    return LibTerraformBot()
