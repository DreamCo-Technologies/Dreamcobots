#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITES = ROOT / "config" / "repository-test-suites.json"
POLICY = ROOT / "config" / "benchmark-mastery-distillation-policy.json"
OUT = ROOT / "config" / "generated" / "benchmark-mastery-distillation-plan.json"
REPORT = ROOT / "reports" / "BENCHMARK_MASTERY_DISTILLATION.md"


def stable_worker_id(suite_id: str) -> str:
    digest = hashlib.sha256(suite_id.encode()).hexdigest()[:12]
    return f"benchmark-master-{suite_id}-{digest}"


def main() -> int:
    suites = json.loads(SUITES.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    gap_policy = policy["gap_closure_policy"]
    rows = []
    for index, suite in enumerate(suites.get("suites", []), start=1):
        suite_id = suite["id"]
        worker_id = stable_worker_id(suite_id)
        rows.append({
            "suite_id": suite_id,
            "suite_name": suite["name"],
            "area": suite.get("area"),
            "level": suite.get("level"),
            "worker": {
                "id": worker_id,
                "type": "task_scoped_benchmark_master",
                "status": "active_when_suite_is_scheduled",
                "expires_after_suite": True,
                "parallel_slot": ((index - 1) % policy["parallel_policy"]["maximum_parallel_workers"]) + 1,
                "single_writer_per_owner": True,
            },
            "mastery": {
                "state": "unknown",
                "scope_is_revision_specific": True,
                "requirements": policy["mastered_requires"],
                "regression_revokes_mastery": True,
            },
            "gap_closure": {
                "required": gap_policy["required_for_every_suite"],
                "review_standard": gap_policy["review_standard"],
                "status": "ready_to_measure",
                "loop": gap_policy["loop"],
                "steps": gap_policy["required_steps"],
                "repair_priorities": gap_policy["repair_priorities"],
                "prohibited_shortcuts": gap_policy["prohibited_shortcuts"],
                "shared_fix_rule": gap_policy["shared_fix_rule"],
                "blocked_rule": gap_policy["blocked_rule"],
                "targeted_tests": suite.get("tests", []),
                "targeted_scripts": suite.get("scripts", []),
                "acceptance_boundary": suite.get("boundary"),
                "promotion_requires_passing_evidence": True,
            },
            "evidence": {
                "sources": suite.get("sources", []),
                "tests": suite.get("tests", []),
                "scripts": suite.get("scripts", []),
                "boundary": suite.get("boundary"),
            },
            "distillation": {
                "state": "candidate_after_mastery",
                "teacher": "best verified route for this suite",
                "student": "cheaper/smaller/local route that satisfies the same required capabilities",
                "methods": policy["distillation_policy"]["methods"],
                "acceptance": policy["distillation_policy"]["acceptance"],
                "promotion_rule": policy["distillation_policy"]["promotion_rule"],
                "rollback_rule": policy["distillation_policy"]["regression_rule"],
            },
            "cost_controls": policy["cost_efficiency"],
        })

    payload = {
        "schema": "dreamco.benchmark_mastery_distillation_plan.v2",
        "suite_count": len(rows),
        "worker_count": len(rows),
        "gap_closure_path_count": len(rows),
        "all_suites_have_gap_closure_path": all(row["gap_closure"]["required"] for row in rows),
        "gap_closure_review_standard": gap_policy["review_standard"],
        "maximum_parallel_workers": policy["parallel_policy"]["maximum_parallel_workers"],
        "one_worker_per_suite": policy["parallel_policy"]["one_worker_per_benchmark_suite"],
        "workers_are_task_scoped": True,
        "all_workers_active_simultaneously": False,
        "scheduling_rule": "queue every suite; run up to the maximum parallel worker limit; inactive workers consume no runtime",
        "truth_boundary": policy["truth_boundary"],
        "suites": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Benchmark Mastery & Distillation",
        "",
        f"- Benchmark suites: **{len(rows)}**",
        f"- Task-scoped Benchmark Masters: **{len(rows)}**",
        f"- Gap-closure paths: **{len(rows)}**",
        f"- Review standard: **{gap_policy['review_standard']}**",
        f"- Maximum concurrent workers: **{payload['maximum_parallel_workers']}**",
        "- Idle workers consume no runtime.",
        "- Every suite has a measure -> diagnose -> repair -> retest -> compare path.",
        "- A reviewed repair path is not a passing result; mastery still requires benchmark evidence.",
        "- Mastery is revision-specific and revoked on regression.",
        "- Distillation is promoted only when the cheaper/student route preserves the benchmark quality floor.",
        "",
    ]
    for row in rows:
        lines += [
            f"## {row['suite_name']}",
            f"- Worker: `{row['worker']['id']}`",
            f"- Area: {row['area']}",
            f"- State: {row['mastery']['state']}",
            f"- Gap closure: {row['gap_closure']['status']} ({row['gap_closure']['review_standard']})",
            f"- Loop: {row['gap_closure']['loop']}",
            f"- Distillation: {row['distillation']['state']}",
            "",
        ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"ok": True, "suites": len(rows), "workers": len(rows), "gap_paths": len(rows), "max_parallel": payload["maximum_parallel_workers"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
