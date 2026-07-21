from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List


@dataclass
class TrafficSplit:
    stable_percent: int
    canary_percent: int


@dataclass
class DeploymentStage:
    name: str
    traffic: TrafficSplit
    error_threshold: float = 0.05
    latency_threshold_ms: int = 1200
    completed: bool = False


@dataclass
class DeploymentPlan:
    bot_id: str
    old_version: str
    new_version: str
    stages: List[DeploymentStage]
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = 'pending'


class RollingDeployment:
    def __init__(self, health_check: Callable[[str, str, int], Dict[str, float]]) -> None:
        self.health_check = health_check
        self.deployments: Dict[str, DeploymentPlan] = {}
        self.events: list[dict] = []

    def build_plan(self, bot_id: str, old_version: str, new_version: str) -> DeploymentPlan:
        stages = [
            DeploymentStage('stage-5', TrafficSplit(95, 5)),
            DeploymentStage('stage-25', TrafficSplit(75, 25)),
            DeploymentStage('stage-50', TrafficSplit(50, 50)),
            DeploymentStage('stage-100', TrafficSplit(0, 100)),
        ]
        plan = DeploymentPlan(bot_id=bot_id, old_version=old_version, new_version=new_version, stages=stages)
        self.deployments[bot_id] = plan
        return plan

    def deploy(self, bot_id: str, old_version: str, new_version: str) -> DeploymentPlan:
        plan = self.build_plan(bot_id, old_version, new_version)
        plan.status = 'running'
        for stage in plan.stages:
            metrics = self.health_check(bot_id, new_version, stage.traffic.canary_percent)
            self.events.append({'bot_id': bot_id, 'stage': stage.name, 'metrics': metrics})
            if self._should_rollback(stage, metrics):
                self.rollback(plan, metrics)
                return plan
            stage.completed = True
        plan.status = 'completed'
        return plan

    def _should_rollback(self, stage: DeploymentStage, metrics: Dict[str, float]) -> bool:
        error_rate = metrics.get('error_rate', 0.0)
        latency_ms = metrics.get('latency_ms', 0.0)
        healthy = metrics.get('healthy_instances', 1.0) >= metrics.get('required_instances', 1.0)
        return error_rate > stage.error_threshold or latency_ms > stage.latency_threshold_ms or not healthy

    def rollback(self, plan: DeploymentPlan, metrics: Dict[str, float]) -> None:
        plan.status = 'rolled_back'
        self.events.append(
            {
                'bot_id': plan.bot_id,
                'action': 'rollback',
                'restored_version': plan.old_version,
                'reason': f"error spike={metrics.get('error_rate', 0.0):.3f}",
            }
        )

    def summarize(self, bot_id: str) -> Dict[str, object]:
        plan = self.deployments[bot_id]
        return {
            'bot_id': bot_id,
            'from': plan.old_version,
            'to': plan.new_version,
            'status': plan.status,
            'completed_stages': [stage.name for stage in plan.stages if stage.completed],
        }
