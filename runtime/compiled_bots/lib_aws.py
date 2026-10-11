"""Auto-generated sandbox bot from bots/lib-aws.md.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class LibAwsBot(CompiledBot):
    slug = 'lib-aws'
    display_name = 'AWS SDK & Cloud Bot'
    division = 'DreamCodeLab'
    tier = 'pro'
    mission = 'Expert in AWS services: Lambda, S3, DynamoDB, RDS, SQS, SNS, Cognito, and CDK infrastructure.'
    capabilities = ['Lambda function patterns', 'S3 operations & presigned URLs', 'DynamoDB design patterns', 'SQS/SNS messaging', 'API Gateway configuration', 'Cognito auth flows', 'CloudFormation & CDK', 'ECS Fargate deployment']
    autonomy_ceiling = 'sandbox_execute'
    source = 'bots/lib-aws.md'

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


def create() -> LibAwsBot:
    return LibAwsBot()
