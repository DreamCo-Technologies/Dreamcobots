"""Run the CommandCore-to-Buddy-Bootcamp routing and scheduler smoke check."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from buddy.fleet_runtime.router import complete_learning
from buddy.learning.runtime_bridge import BuddyLearningBridge, PrivateLearningStore
from dreamco_platform.automation.task_runner import BuddyTaskRunner
from buddy.learning.course_track_registry import plan_next_for_division, resources_for_division
from buddy.learning.buddy_knowledge_router import route_buddy_learning_query
from buddy.learning.study_resource_scheduler import Capability

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "config/generated/commandcore-bootcamp-smoke.json"
QUERY = "CommandCore capability-aware routing and approval-aware orchestration"


def run_smoke(root: Path = ROOT) -> dict[str, Any]:
    portfolio = json.loads((root / "App_bots/CommandCore.json").read_text(encoding="utf-8"))
    division = json.loads((root / "config/divisions/commandcore.json").read_text(encoding="utf-8"))
    route = route_buddy_learning_query(QUERY, root=root, limit=10, record_gap=False)
    if route.get("route") != "internal_bootcamp_lesson":
        raise AssertionError(f"CommandCore did not route to internal Bootcamp: {route.get('route')}")
    matches = [
        row for row in route.get("course_lessons", [])
        if row.get("track_id") == "dreamco-division-specialist"
        and "CommandCore" in row.get("division_targets", [])
    ]
    if len(matches) != 6:
        raise AssertionError(f"expected six CommandCore lessons, found {len(matches)}")
    if any(row.get("source_url") for row in route.get("course_lessons", [])):
        raise AssertionError("learner route exposed an external source URL")

    plan = plan_next_for_division(
        "CommandCore",
        [Capability("workflow planning", "planning_and_orchestration", score=0.1, failed_benchmarks=1)],
        root,
    )
    if not plan or plan.get("track_id") != "dreamco-division-specialist":
        raise AssertionError("CommandCore scheduler did not select its DreamCo specialist course")
    for field in ("exercise_ids", "project_ids", "assessment_ids", "retraining_policy_id"):
        if not plan.get(field):
            raise AssertionError(f"CommandCore study plan is missing {field}")
    if plan.get("model_weight_training_authorized") is not False:
        raise AssertionError("draft curriculum must not authorize model-weight training")

    def forbidden_fallback() -> str:
        raise AssertionError("learning task fell through to a model/offline fallback")

    completion = complete_learning(
        QUERY,
        {"mode": "offline_only"},
        forbidden_fallback,
        {"DREAMCO_FLEET_LIVE_MODEL": "1", "OPENROUTER_API_KEY": "smoke-test-not-used"},
    )
    if completion.get("mode") != "internal_bootcamp_study" or completion.get("model") is not None:
        raise AssertionError("Fleet learning completion did not stop at internal Bootcamp")

    resources = resources_for_division("CommandCore", root)
    if len(resources) < 6 or any(resource.url for resource in resources):
        raise AssertionError("CommandCore scheduler resources are incomplete or externally routed")

    with tempfile.TemporaryDirectory(prefix="dreamco-commandcore-smoke-") as temp_dir:
        store = PrivateLearningStore(Path(temp_dir) / "learning.db")
        # PrivateLearningStore opens and closes a SQLite connection per operation.
        # It has no persistent connection handle or close() method.
        bridge = BuddyLearningBridge(store, BuddyTaskRunner())
        queue = bridge.bootcamp_learning_queue(division="CommandCore", limit=10)
        if queue.get("track_ids") != ["dreamco-division-specialist"] or queue.get("available_count") != 6:
            raise AssertionError("CommandCore runtime bridge did not expose its six DreamCo lessons")
        if any(item.get("source_url") for item in queue.get("items", [])):
            raise AssertionError("CommandCore runtime bridge exposed an external learner URL")
        if any(not item.get("exercise_ids") or not item.get("project_ids") or not item.get("assessment_ids")
               for item in queue.get("items", [])):
            raise AssertionError("CommandCore runtime bridge omitted exercises, projects, or assessments")

    return {
        "schema": "dreamco.commandcore_bootcamp_smoke.v1",
        "status": "PASS",
        "smoke_scope": "commandcore_internal_bootcamp_routing_and_scheduler",
        "division": "CommandCore",
        "division_manifest_status": division.get("status", "unknown"),
        "source_profile_count": len(portfolio.get("bots", [])),
        "course_track_id": "dreamco-division-specialist",
        "course_lesson_count": len(matches),
        "runtime_queue_lesson_count": queue["returned_count"],
        "runtime_queue_track_ids": queue["track_ids"],
        "exercise_ids": plan["exercise_ids"],
        "project_ids": plan["project_ids"],
        "assessment_ids": plan["assessment_ids"],
        "retraining_policy_id": plan["retraining_policy_id"],
        "learner_external_routing": False,
        "model_fallback_used": False,
        "model_weight_training_authorized": False,
        "capability_runtime_status": "not_verified",
        "mastery_status": "not_claimed",
        "certification_status": "not_certified",
        "notes": (
            "This smoke verifies CommandCore's internal Bootcamp route and scheduler contract. "
            "It does not execute every declared CommandCore capability or establish runtime mastery."
        ),
    }


def main() -> int:
    report = run_smoke()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
