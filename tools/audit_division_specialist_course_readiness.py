#!/usr/bin/env python3
"""Audit domain-specific lessons for all canonical divisions and MasterBot lanes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/masterbot-65-registry.json"
CROSSWALK = ROOT / "config/generated/masterbot-55-domain-crosswalk.json"
COURSE = ROOT / "config/buddy-25m-cpu-llm-course.json"
ARTIFACTS = ROOT / "config/buddy-division-specialist-course-artifacts.json"
OUTPUT = ROOT / "config/generated/division-specialist-course-readiness.json"

REQUIRED_MODULES = (
    "domain_overview", "core_skills", "tools_and_libraries", "task_playbooks",
    "safety_and_rights", "sandbox_lab", "assessment", "capstone",
)


def audit(registry: dict[str, Any], crosswalk: dict[str, Any],
          course: dict[str, Any], artifacts_doc: dict[str, Any],
          *, root: Path = ROOT) -> dict[str, Any]:
    if crosswalk.get("schema") != "dreamco.masterbot_domain_crosswalk.v1":
        raise ValueError("unsupported MasterBot/division crosswalk schema")
    if course.get("schema") != "dreamco.buddy_25m_cpu_llm_course.v1":
        raise ValueError("unsupported Buddy shared-foundation course schema")
    if artifacts_doc.get("schema") != "dreamco.buddy_division_specialist_course_artifacts.v1":
        raise ValueError("unsupported specialist course artifact schema")

    bots = registry.get("divisions")
    domains = crosswalk.get("domains")
    mapped_bots = crosswalk.get("masterbots")
    if not isinstance(bots, list) or len(bots) != 65:
        raise ValueError("canonical MasterBot registry must contain exactly 65 lanes")
    if not isinstance(domains, list) or len(domains) != 55:
        raise ValueError("canonical division crosswalk must contain exactly 55 domains")
    if not isinstance(mapped_bots, list) or len(mapped_bots) != 65:
        raise ValueError("crosswalk must contain exactly 65 MasterBot lanes")
    bot_ids = [str(row.get("id")) for row in bots if isinstance(row, dict)]
    domain_ids = [row.get("domain_id") for row in domains if isinstance(row, dict)]
    mapped_ids = [str(row.get("masterbot_id")) for row in mapped_bots if isinstance(row, dict)]
    if len(bot_ids) != 65 or len(set(bot_ids)) != 65:
        raise ValueError("MasterBot registry IDs must be present and unique")
    if len(domain_ids) != 55 or any(not isinstance(x, str) or not x for x in domain_ids) or len(set(domain_ids)) != 55:
        raise ValueError("division IDs must be present and unique")
    if len(mapped_ids) != 65 or set(mapped_ids) != set(bot_ids):
        raise ValueError("crosswalk MasterBot IDs must exactly match the canonical registry")

    delivery = course.get("delivery", {})
    if len(delivery.get("division_assignments", [])) != 55:
        raise ValueError("shared foundation must be assigned to all 55 divisions")
    if len(delivery.get("masterbot_assignments", [])) != 65:
        raise ValueError("shared foundation must be assigned to all 65 MasterBot lanes")

    targets = (
        [("division", row["domain_id"], row.get("owner_approval") is True) for row in domains]
        + [("masterbot", str(row["masterbot_id"]), row.get("owner_approval") is True) for row in mapped_bots]
    )
    canonical = {(kind, target_id): approved for kind, target_id, approved in targets}
    artifact_rows = artifacts_doc.get("artifacts", [])
    if not isinstance(artifact_rows, list):
        raise ValueError("artifacts must be an array")
    artifact_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in artifact_rows:
        if not isinstance(row, dict):
            raise ValueError("artifact entries must be objects")
        key = (row.get("target_type"), str(row.get("target_id", "")), row.get("module_id"))
        if key[0] not in {"division", "masterbot"} or key[1] == "" or key[2] not in REQUIRED_MODULES:
            raise ValueError(f"invalid specialist course artifact identity: {key}")
        if (key[0], key[1]) not in canonical:
            raise ValueError(f"artifact references non-canonical target: {key[:2]}")
        if key in artifact_by_key:
            raise ValueError(f"duplicate specialist course artifact: {key}")
        artifact_by_key[key] = row

    rows = []
    missing_by_module = {module: 0 for module in REQUIRED_MODULES}
    ready_count = 0
    owner_pending_count = sum(1 for approved in canonical.values() if not approved)
    for kind, target_id, owner_approved in targets:
        modules = []
        for module_id in REQUIRED_MODULES:
            artifact = artifact_by_key.get((kind, target_id, module_id), {})
            guide_path = artifact.get("guide_path")
            guide_exists = False
            if isinstance(guide_path, str) and guide_path.startswith("docs/bootcamp/specialist/"):
                candidate = (root / guide_path).resolve()
                try:
                    candidate.relative_to(root.resolve())
                except ValueError:
                    pass
                else:
                    guide_exists = candidate.is_file()
            exercises = artifact.get("exercises")
            objectives = artifact.get("learning_objectives")
            citations = artifact.get("citations")
            ready = all((
                guide_exists,
                isinstance(objectives, list) and len(objectives) >= 3,
                isinstance(exercises, list) and len(exercises) >= 2,
                isinstance(artifact.get("assessment"), dict),
                isinstance(citations, list) and len(citations) > 0
                    and all(isinstance(c, dict) and c.get("url") and c.get("accessed_at") and c.get("rights_evidence_ref") for c in citations),
                artifact.get("rights_review") == "approved",
                artifact.get("human_review") == "approved",
            ))
            if ready:
                ready_count += 1
            else:
                missing_by_module[module_id] += 1
            modules.append({
                "module_id": module_id,
                "status": "ready_for_study_review" if ready else "not_ready",
                "guide_exists": guide_exists,
                "learning_objective_count": len(objectives) if isinstance(objectives, list) else 0,
                "exercise_count": len(exercises) if isinstance(exercises, list) else 0,
                "assessment_recorded": isinstance(artifact.get("assessment"), dict),
                "citation_count": len(citations) if isinstance(citations, list) else 0,
                "rights_review": artifact.get("rights_review", "pending"),
                "human_review": artifact.get("human_review", "pending"),
            })
        rows.append({
            "target_type": kind,
            "target_id": target_id,
            "owner_approved": owner_approved,
            "specialist_routing_allowed": owner_approved,
            "ready_module_count": sum(m["status"] == "ready_for_study_review" for m in modules),
            "modules": modules,
        })

    required_count = len(targets) * len(REQUIRED_MODULES)
    return {
        "schema": "dreamco.division_specialist_course_readiness.v1",
        "division_count": len(domains),
        "masterbot_count": len(bots),
        "target_count": len(targets),
        "required_module_count": required_count,
        "ready_module_count": ready_count,
        "not_ready_module_count": required_count - ready_count,
        "owner_pending_target_count": owner_pending_count,
        "specialist_routing_authorized_target_count": sum(1 for approved in canonical.values() if approved),
        "missing_by_module": missing_by_module,
        "status": "ready_for_study_review" if ready_count == required_count else "specialist_curriculum_gaps",
        "targets": rows,
        "mastery_claim": False,
        "production_claim": False,
        "truth_boundary": "The shared 18-module foundation and 55/65 assignments do not substitute for domain-specific specialist courses. Readiness requires actual authored guides, exercises, assessments, dated rights-evidenced citations, rights review and human review. This report does not prove study, competence, mastery, certification or production readiness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    documents = [json.loads(path.read_text(encoding="utf-8")) for path in (REGISTRY, CROSSWALK, COURSE, ARTIFACTS)]
    report = audit(*documents)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "status", "division_count", "masterbot_count", "required_module_count",
        "ready_module_count", "not_ready_module_count", "owner_pending_target_count",
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
