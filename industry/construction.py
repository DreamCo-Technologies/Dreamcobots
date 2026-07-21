"""
Construction AI module for Dreamcobots platform.

Provides AI-powered construction planning, project scheduling, resource
management, safety compliance checking, cost estimation, and progress reporting.
"""

import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ConstructionProject:
    """Represents a construction project."""
    project_id: str
    name: str
    client: str
    location: str
    start_date: date
    estimated_end_date: date
    budget: float
    status: str = "planning"   # 'planning', 'active', 'on_hold', 'complete'
    progress_percent: float = 0.0
    phases: List[str] = field(default_factory=list)


@dataclass
class ResourceAllocation:
    """Tracks resource assignment to a project."""
    resource_id: str
    project_id: str
    resource_type: str   # 'labour', 'equipment', 'material'
    quantity: float
    unit: str            # e.g. 'workers', 'hours', 'tonnes'
    cost_per_unit: float

    @property
    def total_cost(self) -> float:
        """Return total cost for this allocation."""
        return round(self.quantity * self.cost_per_unit, 2)


@dataclass
class SafetyCheck:
    """Records a safety compliance check for a project."""
    check_id: str
    project_id: str
    category: str        # e.g. 'PPE', 'scaffolding', 'electrical'
    passed: bool
    notes: str = ""
    check_date: date = field(default_factory=date.today)


# ---------------------------------------------------------------------------
# ConstructionAI bot
# ---------------------------------------------------------------------------

class ConstructionAI(BotBase):
    """
    AI-powered construction planning and management bot.

    Manages project lifecycles, schedules phases, allocates resources,
    enforces safety compliance, estimates costs, and generates progress reports.

    Args:
        autonomy: Autonomy level.
        scaling: Scaling level.
    """

    # Standard overhead rate applied to raw material/labour costs
    OVERHEAD_RATE = 0.15

    def __init__(
        self,
        autonomy: AutonomyLevel = AutonomyLevel.SEMI_AUTONOMOUS,
        scaling: ScalingLevel = ScalingLevel.MODERATE,
    ) -> None:
        super().__init__("ConstructionAI", autonomy, scaling)
        self._projects: Dict[str, ConstructionProject] = {}
        self._resources: List[ResourceAllocation] = []
        self._safety_checks: List[SafetyCheck] = []

    # ------------------------------------------------------------------
    # Project management
    # ------------------------------------------------------------------

    def create_project(self, project: ConstructionProject) -> ConstructionProject:
        """Register a new construction project."""
        self._projects[project.project_id] = project
        return project

    def get_project(self, project_id: str) -> Optional[ConstructionProject]:
        """Return a project or None."""
        return self._projects.get(project_id)

    def update_progress(self, project_id: str, progress_percent: float) -> bool:
        """Update completion percentage for a project. Returns True if found."""
        project = self._projects.get(project_id)
        if not project:
            return False
        project.progress_percent = max(0.0, min(100.0, progress_percent))
        if project.progress_percent >= 100.0:
            project.status = "complete"
        return True

    def list_projects(self, status: Optional[str] = None) -> List[ConstructionProject]:
        """Return all (or status-filtered) projects."""
        if status:
            return [p for p in self._projects.values() if p.status == status]
        return list(self._projects.values())

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------

    def generate_phase_schedule(
        self,
        project_id: str,
        phases: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Distribute project phases evenly across the project timeline.

        Args:
            project_id: Target project.
            phases: Ordered list of phase names.

        Returns:
            List of phase schedule dicts with start and end dates.
        """
        project = self._projects.get(project_id)
        if not project:
            return []

        total_days = (project.estimated_end_date - project.start_date).days
        phase_duration = max(1, total_days // max(len(phases), 1))
        schedule = []
        current = project.start_date
        for phase in phases:
            end = current + timedelta(days=phase_duration)
            schedule.append({"phase": phase, "start": current.isoformat(), "end": end.isoformat()})
            current = end

        project.phases = phases
        return schedule

    # ------------------------------------------------------------------
    # Resource allocation
    # ------------------------------------------------------------------

    def allocate_resource(
        self,
        project_id: str,
        resource_type: str,
        quantity: float,
        unit: str,
        cost_per_unit: float,
    ) -> ResourceAllocation:
        """Allocate a resource to a project."""
        allocation = ResourceAllocation(
            resource_id=str(uuid.uuid4()),
            project_id=project_id,
            resource_type=resource_type,
            quantity=quantity,
            unit=unit,
            cost_per_unit=cost_per_unit,
        )
        self._resources.append(allocation)
        return allocation

    def get_project_resources(self, project_id: str) -> List[ResourceAllocation]:
        """Return all resources allocated to a project."""
        return [r for r in self._resources if r.project_id == project_id]

    # ------------------------------------------------------------------
    # Cost estimation
    # ------------------------------------------------------------------

    def estimate_total_cost(self, project_id: str) -> Dict[str, float]:
        """
        Estimate total project cost including overhead.

        Returns:
            Dict with raw_cost, overhead, and total_cost.
        """
        resources = self.get_project_resources(project_id)
        raw_cost = sum(r.total_cost for r in resources)
        overhead = round(raw_cost * self.OVERHEAD_RATE, 2)
        return {
            "raw_cost": round(raw_cost, 2),
            "overhead": overhead,
            "total_cost": round(raw_cost + overhead, 2),
        }

    # ------------------------------------------------------------------
    # Safety compliance
    # ------------------------------------------------------------------

    def record_safety_check(
        self,
        project_id: str,
        category: str,
        passed: bool,
        notes: str = "",
    ) -> SafetyCheck:
        """Record a safety compliance check for a project."""
        check = SafetyCheck(
            check_id=str(uuid.uuid4()),
            project_id=project_id,
            category=category,
            passed=passed,
            notes=notes,
        )
        self._safety_checks.append(check)
        return check

    def get_safety_summary(self, project_id: str) -> Dict[str, Any]:
        """Return safety check statistics for a project."""
        checks = [c for c in self._safety_checks if c.project_id == project_id]
        passed = sum(1 for c in checks if c.passed)
        failed = sum(1 for c in checks if not c.passed)
        return {
            "total_checks": len(checks),
            "passed": passed,
            "failed": failed,
            "compliance_rate": round(passed / len(checks) * 100, 2) if checks else 0.0,
        }

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def generate_report(self) -> Dict[str, Any]:
        """Generate an overall construction portfolio report."""
        active = [p for p in self._projects.values() if p.status == "active"]
        complete = [p for p in self._projects.values() if p.status == "complete"]
        avg_progress = (
            sum(p.progress_percent for p in self._projects.values()) / len(self._projects)
            if self._projects else 0.0
        )
        return {
            "total_projects": len(self._projects),
            "active_projects": len(active),
            "completed_projects": len(complete),
            "average_progress_percent": round(avg_progress, 2),
            "total_resource_allocations": len(self._resources),
            "total_safety_checks": len(self._safety_checks),
        }

    # ------------------------------------------------------------------
    # Task runner
    # ------------------------------------------------------------------

    def _run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "")
        if task_type == "update_progress":
            ok = self.update_progress(task.get("project_id", ""), float(task.get("progress", 0)))
            return {"status": "ok" if ok else "error", "message": "progress updated" if ok else "project not found"}
        if task_type == "estimate_cost":
            costs = self.estimate_total_cost(task.get("project_id", ""))
            return {"status": "ok", **costs}
        return super()._run_task(task)
