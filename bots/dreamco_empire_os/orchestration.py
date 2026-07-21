"""
DreamCo Empire OS — Orchestration Module

Manages multiple AI bots working together in synchronised autonomous
pipelines. Defines workflows, execution order, dependencies, and
real-time visualisation of inter-bot data flow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from framework import GlobalAISourcesFlow  # noqa: F401


class PipelineStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class PipelineStep:
    """A single step within an orchestration pipeline."""
    step_id: str
    bot_name: str
    action: str
    depends_on: list = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Optional[dict] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


@dataclass
class Pipeline:
    """An ordered collection of bot pipeline steps."""
    pipeline_id: str
    name: str
    description: str
    steps: list = field(default_factory=list)
    status: PipelineStatus = PipelineStatus.DRAFT
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    run_count: int = 0


class Orchestration:
    """
    Orchestration — design and execute multi-bot collaborative pipelines.

    Supports sequential and dependency-aware execution, real-time step
    status tracking, and pipeline analytics.
    """

    def __init__(self) -> None:
        self._pipelines: dict[str, Pipeline] = {}
        self._run_log: list = []

    # ------------------------------------------------------------------
    # Pipeline management
    # ------------------------------------------------------------------

    def create_pipeline(self, pipeline_id: str, name: str, description: str = "") -> dict:
        """Create a new (empty) pipeline."""
        pipeline = Pipeline(pipeline_id=pipeline_id, name=name, description=description)
        self._pipelines[pipeline_id] = pipeline
        return _pipeline_to_dict(pipeline)

    def add_step(
        self,
        pipeline_id: str,
        step_id: str,
        bot_name: str,
        action: str,
        depends_on: Optional[list] = None,
    ) -> dict:
        """Add a step to an existing pipeline."""
        pipeline = self._get(pipeline_id)
        step = PipelineStep(
            step_id=step_id,
            bot_name=bot_name,
            action=action,
            depends_on=depends_on or [],
        )
        pipeline.steps.append(step)
        return {"pipeline_id": pipeline_id, "step_id": step_id, "bot_name": bot_name, "action": action}

    def activate_pipeline(self, pipeline_id: str) -> dict:
        """Mark pipeline as active and ready to run."""
        pipeline = self._get(pipeline_id)
        pipeline.status = PipelineStatus.ACTIVE
        return {"pipeline_id": pipeline_id, "status": pipeline.status.value}

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run_pipeline(self, pipeline_id: str) -> dict:
        """
        Execute all steps in the pipeline respecting dependency order.

        Steps with unresolved dependencies are skipped. All steps are
        simulated (marked done) to allow dry-run orchestration testing.
        """
        pipeline = self._get(pipeline_id)
        pipeline.status = PipelineStatus.ACTIVE
        pipeline.started_at = datetime.now(timezone.utc).isoformat()
        pipeline.run_count += 1

        completed_steps: set = set()
        step_results = []

        for step in pipeline.steps:
            deps_met = all(dep in completed_steps for dep in step.depends_on)
            if not deps_met:
                step.status = StepStatus.SKIPPED
                step_results.append({"step_id": step.step_id, "status": StepStatus.SKIPPED.value})
                continue

            step.status = StepStatus.RUNNING
            step.started_at = datetime.now(timezone.utc).isoformat()
            step.result = {"bot": step.bot_name, "action": step.action, "output": "success"}
            step.status = StepStatus.DONE
            step.finished_at = datetime.now(timezone.utc).isoformat()
            completed_steps.add(step.step_id)
            step_results.append({"step_id": step.step_id, "status": StepStatus.DONE.value, "bot": step.bot_name})

        all_done = all(s.status in (StepStatus.DONE, StepStatus.SKIPPED) for s in pipeline.steps)
        pipeline.status = PipelineStatus.COMPLETED if all_done else PipelineStatus.FAILED
        pipeline.finished_at = datetime.now(timezone.utc).isoformat()

        run_entry = {
            "pipeline_id": pipeline_id,
            "name": pipeline.name,
            "status": pipeline.status.value,
            "steps": step_results,
            "started_at": pipeline.started_at,
            "finished_at": pipeline.finished_at,
        }
        self._run_log.append(run_entry)
        return run_entry

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_pipeline(self, pipeline_id: str) -> dict:
        return _pipeline_to_dict(self._get(pipeline_id))

    def list_pipelines(self) -> list:
        return [_pipeline_to_dict(p) for p in self._pipelines.values()]

    def get_run_log(self, limit: int = 20) -> list:
        return self._run_log[-limit:]

    def get_summary(self) -> dict:
        pipelines = list(self._pipelines.values())
        return {
            "total_pipelines": len(pipelines),
            "active": sum(1 for p in pipelines if p.status == PipelineStatus.ACTIVE),
            "completed": sum(1 for p in pipelines if p.status == PipelineStatus.COMPLETED),
            "total_runs": sum(p.run_count for p in pipelines),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get(self, pipeline_id: str) -> Pipeline:
        if pipeline_id not in self._pipelines:
            raise KeyError(f"Pipeline '{pipeline_id}' not found.")
        return self._pipelines[pipeline_id]


def _pipeline_to_dict(p: Pipeline) -> dict:
    return {
        "pipeline_id": p.pipeline_id,
        "name": p.name,
        "description": p.description,
        "status": p.status.value,
        "step_count": len(p.steps),
        "steps": [
            {
                "step_id": s.step_id,
                "bot_name": s.bot_name,
                "action": s.action,
                "depends_on": s.depends_on,
                "status": s.status.value,
            }
            for s in p.steps
        ],
        "run_count": p.run_count,
        "created_at": p.created_at,
        "started_at": p.started_at,
        "finished_at": p.finished_at,
    }
