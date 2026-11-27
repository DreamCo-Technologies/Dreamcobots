"""Build original DreamCo curricula for all canonical divisions."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _unique(values: list[Any]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _profile_values(profiles: list[dict[str, Any]], key: str) -> list[str]:
    values: list[Any] = []
    for profile in profiles:
        value = profile.get(key, [])
        if isinstance(value, list):
            if key == "tasks":
                values.extend(
                    task.get("title", "") if isinstance(task, dict) else task
                    for task in value
                )
            elif key == "benchmarks":
                values.extend(
                    benchmark.get("label", "") if isinstance(benchmark, dict) else benchmark
                    for benchmark in value
                )
            else:
                values.extend(value)
    return _unique(values)


def build_division_curricula(root: Path = ROOT) -> dict[str, Any]:
    """Return 55 source-backed, DreamCo-authored curriculum drafts in memory."""
    taxonomy = _read(root / "config/dreamco-universal-capability-taxonomy.json")
    reconciliation = _read(root / "config/generated/division-reconciliation.json")
    crosswalk = _read(root / "config/generated/masterbot-55-domain-crosswalk.json")
    masterbot_registry = _read(root / "config/masterbot-65-registry.json")

    divisions = reconciliation.get("domain_divisions", [])
    if len(divisions) != 55:
        raise ValueError(f"expected 55 canonical divisions, found {len(divisions)}")
    cross_by_id = {row.get("domain_id"): row for row in crosswalk.get("domains", [])}
    masterbot_names = {
        int(row["id"]): str(row["name"])
        for row in masterbot_registry.get("divisions", [])
        if row.get("id") is not None and row.get("name")
    }
    if len(cross_by_id) != 55 or len(masterbot_names) != 65:
        raise ValueError("DreamCo curricula require the canonical 55-domain and 65-MasterBot registries")

    portfolios: dict[str, tuple[str, dict[str, Any]]] = {}
    for path in sorted((root / "App_bots").glob("*.json")):
        payload = _read(path)
        division_name = str(payload.get("division", "")).strip()
        if division_name and isinstance(payload.get("bots"), list):
            portfolios[division_name] = (path.relative_to(root).as_posix(), payload)

    actor_modes = [row["id"] for row in taxonomy["actor_modes"]]
    capability_domains = [row["id"] for row in taxonomy["capability_domains"]]
    artifacts: list[dict[str, Any]] = []

    for division in sorted(divisions, key=lambda row: str(row.get("id", ""))):
        division_id = str(division["id"])
        division_name = str(division["name"])
        portfolio_entry = portfolios.get(division_name)
        if portfolio_entry is None:
            raise ValueError(f"missing DreamCo source portfolio for {division_name}")
        source_path, portfolio = portfolio_entry
        if str(portfolio.get("division", "")) != division_name:
            raise ValueError(f"source portfolio division mismatch for {division_name}")
        profiles = portfolio.get("bots", [])
        if not profiles:
            raise ValueError(f"division {division_name} has no specialist bot profiles")

        capabilities = _profile_values(profiles, "capabilities")
        task_titles = _profile_values(profiles, "tasks")
        tools = _profile_values(profiles, "toolsNeeded")
        benchmark_labels = _profile_values(profiles, "benchmarks")
        learning_plan = _profile_values(profiles, "learningPlan")
        agent_slugs = _unique([profile.get("slug", "") for profile in profiles])
        task_focus = task_titles[:3] or [f"representative {division_name} workflow"]
        capability_focus = capabilities[:6] or [f"{division_name} specialist capability"]
        tool_focus = tools[:8]
        mapping = cross_by_id.get(division_id, {})
        masterbot_targets: list[str] = []
        primary_masterbot = mapping.get("masterbot_name")
        if primary_masterbot:
            masterbot_targets.append(str(primary_masterbot))
        for masterbot_id in division.get("shared_platform_masterbot_ids", []):
            name = masterbot_names.get(int(masterbot_id))
            if name:
                masterbot_targets.append(name)
        masterbot_targets = _unique(masterbot_targets)
        operations = _unique(division.get("capability_operations", []) or taxonomy["capability_operations"])
        slug = _slug(division_name)
        course_id = f"dreamco-{slug}-specialist-v1"
        exercise_ids = [f"{slug}-{row['id'].lower()}" for row in taxonomy["exercise_types"]]
        project_ids = [f"{slug}-{row['id'].lower()}" for row in taxonomy["project_types"]]
        assessment_ids = [f"{slug}-{row['id'].lower()}" for row in taxonomy["assessment_types"]]
        lessons: list[dict[str, Any]] = []
        modules: list[dict[str, Any]] = []

        for module in taxonomy["curriculum_modules"]:
            module_id = str(module["id"])
            lesson_id = f"{slug}-{module_id.lower()}"
            focus_text = ", ".join(capability_focus[:4])
            task_text = "; ".join(task_focus[:2])
            tool_text = ", ".join(tool_focus[:4]) if tool_focus else "approved DreamCo sandbox tools"
            lesson = {
                "id": lesson_id,
                "title": f"{division_name}: {module['title']}",
                "objective": (
                    f"Demonstrate {module['title'].lower()} for {division_name} by applying "
                    f"{focus_text} to a real division task while stating assumptions, constraints, "
                    "acceptance criteria, and required evidence."
                ),
                "practice": (
                    f"Work in a synthetic, isolated sandbox on a representative {division_name} task "
                    f"such as {task_text}. Select only approved tools ({tool_text}), record each step, "
                    "and stop before any live external action or irreversible change."
                ),
                "assessment": (
                    f"Complete a new {division_name} scenario without copying the practice input. "
                    "Submit the task brief, plan, execution trace, output, verification evidence, "
                    "safety decisions, and a short explanation of remaining uncertainty."
                ),
                "benchmark": (
                    f"{division_name} {module['category']} benchmark: at least 80% task accuracy, "
                    "at least 80% unseen-holdout accuracy, and a 100% safety-gate pass."
                ),
                "category": module["category"],
                "division_targets": [division_name],
                "masterbot_targets": masterbot_targets,
                "capability_tags": _unique(capability_focus + module.get("capability_domains", [])),
                "tool_tags": tool_focus,
                "agent_tags": agent_slugs,
                "learning_modes": module.get("actor_modes", actor_modes),
                "implementation_steps": operations,
                "buddy_demo": (
                    f"Use synthetic {division_name} inputs to demonstrate {module['title'].lower()}; "
                    "capture a reproducible trace and do not claim mastery from a successful explanation alone."
                ),
                "source_url": "",
                "guide_path": "",
                "content_status": "authored",
                "learner_visible": True,
                "review_status": "draft_needs_owner_review",
                "training_eligibility": "internal_sandbox_practice_only",
                "exercise_ids": exercise_ids,
                "project_ids": project_ids,
                "assessment_ids": assessment_ids,
                "retraining_policy_id": f"{slug}-targeted-retraining-v1",
            }
            lessons.append(lesson)
            modules.append({
                "id": module_id,
                "title": module["title"],
                "category": module["category"],
                "capability_domains": module.get("capability_domains", []),
                "actor_modes": module.get("actor_modes", actor_modes),
                "lesson_ids": [lesson_id],
                "exercise_ids": [item for item in exercise_ids if item.startswith(f"{slug}-{module_id.lower()}")],
                "assessment_ids": assessment_ids,
                "status": "draft_generated_needs_owner_review",
            })

        exercises: list[dict[str, Any]] = []
        for template in taxonomy["exercise_types"]:
            exercise_id = f"{slug}-{template['id'].lower()}"
            exercises.append({
                "id": exercise_id,
                "title": f"{division_name}: {template['title']}",
                "category": template["category"],
                "module_id": template["module_id"],
                "objective": (
                    f"Practice {template['title'].lower()} using {division_name} capabilities "
                    f"({', '.join(capability_focus[:4])})."
                ),
                "task_prompt": (
                    f"Given a synthetic {division_name} request involving {task_focus[0]}, produce a "
                    "structured plan, identify actor responsibilities, and define observable acceptance criteria."
                ),
                "required_capabilities": capability_focus[:5],
                "tool_tags": tool_focus,
                "actor_modes": template.get("actor_modes", actor_modes),
                "expected_evidence": [
                    "task statement and assumptions",
                    "step-by-step plan and actor assignment",
                    "sandbox output and verification trace",
                    "risk and permission decisions",
                    "measured result and unresolved gaps",
                ],
                "sandbox_only": True,
                "status": "draft_generated_needs_owner_review",
            })

        projects = [
            {
                "id": project_ids[0],
                "title": f"{division_name}: End-to-end specialist workflow",
                "brief": (
                    f"Design and demonstrate a complete {division_name} workflow around {task_focus[0]}. "
                    "Include intake, research, planning, execution, verification, and handoff."
                ),
                "deliverables": ["workflow specification", "sandbox implementation", "test suite", "evidence report"],
                "acceptance_criteria": ["reproducible run", "measurable output", "safety checks passed", "rollback plan"],
                "actor_modes": actor_modes,
                "sandbox_only": True,
            },
            {
                "id": project_ids[1],
                "title": f"{division_name}: Human-AI-robot collaboration challenge",
                "brief": (
                    f"Design a safe collaborative workflow for {division_name} that assigns work among "
                    "a human, an AI model, and a robot where physical execution is applicable."
                ),
                "deliverables": ["actor responsibility matrix", "handoff protocol", "failure escalation map", "holdout results"],
                "acceptance_criteria": ["clear human approval points", "no unauthorized actuation", "verified handoffs", "measured holdout performance"],
                "actor_modes": ["human_ai", "human_robot", "ai_robot", "human_ai_robot"],
                "sandbox_only": True,
            },
        ]

        assessments: list[dict[str, Any]] = []
        for template in taxonomy["assessment_types"]:
            assessment_id = f"{slug}-{template['id'].lower()}"
            assessments.append({
                "id": assessment_id,
                "title": f"{division_name}: {template['title']}",
                "kind": template["kind"],
                "instructions": (
                    f"Evaluate an unseen {division_name} task related to {task_focus[0]}. "
                    "Require the learner to show process, output, verification, and safety evidence."
                ),
                "pass_threshold": template["pass_threshold"],
                "rubric": {
                    "task_accuracy": 0.4,
                    "process_quality": 0.2,
                    "verification_evidence": 0.2,
                    "safety_and_permissions": 0.2,
                },
                "safety_gate_required": True,
                "unseen_inputs_required": template["kind"] == "holdout",
                "mastery_awarded": False,
            })

        artifacts.append({
            "schema": "dreamco.division_specialist_curriculum.v1",
            "course_id": course_id,
            "ownership_class": "dreamco_owned",
            "title": f"{division_name} Specialist Bootcamp",
            "version": "1.0.0",
            "division": {
                "id": division_id,
                "name": division_name,
                "domain_tier": division.get("domain_tier", "canonical_domain"),
                "primary_masterbot": primary_masterbot,
                "masterbot_mapping_status": mapping.get("mapping_status", "unresolved"),
            },
            "source_portfolio": source_path,
            "source_profile_count": len(profiles),
            "source_profile_slugs": agent_slugs,
            "focus_capabilities": capability_focus,
            "source_task_inventory": task_titles,
            "source_tool_inventory": tools,
            "source_benchmark_inventory": benchmark_labels,
            "source_learning_plan": learning_plan,
            "masterbot_targets": masterbot_targets,
            "actor_modes": actor_modes,
            "capability_domains": capability_domains,
            "capability_operations": operations,
            "modules": modules,
            "lessons": lessons,
            "exercises": exercises,
            "projects": projects,
            "assessments": assessments,
            "retraining_policy": {
                "id": f"{slug}-targeted-retraining-v1",
                "trigger": "any_required_assessment_or_benchmark_failure",
                "steps": taxonomy["retraining_policy"]["steps"],
                "failure_routes": {
                    category: next(
                        lesson["id"] for lesson in lessons if lesson["category"] == category
                    )
                    for category in taxonomy["retraining_policy"]["failure_routes"]
                    if any(lesson["category"] == category for lesson in lessons)
                },
                "repeat_assessment": "new_unseen_input_after_targeted_practice",
                "mastery_awarded_on_failure": False,
            },
            "mastery_policy": taxonomy["mastery_policy"],
            "status": "draft_generated_needs_owner_review",
            "review_status": "owner_review_required",
            "training_eligibility": "internal_sandbox_practice_only",
            "model_weight_training_authorized": False,
            "certification_status": "not_certified",
            "external_source_routing": False,
            "source_references": [
                "config/dreamco-universal-capability-taxonomy.json",
                "config/generated/division-reconciliation.json",
                "config/generated/masterbot-55-domain-crosswalk.json",
                source_path,
            ],
        })

    if len(artifacts) != 55:
        raise ValueError(f"generated {len(artifacts)} division curricula; expected 55")
    return {
        "schema": "dreamco.division_specialist_curriculum_catalog.v1",
        "status": "draft_generated_needs_owner_review",
        "counts": {
            "divisions": len(artifacts),
            "lessons": sum(len(row["lessons"]) for row in artifacts),
            "exercises": sum(len(row["exercises"]) for row in artifacts),
            "projects": sum(len(row["projects"]) for row in artifacts),
            "assessments": sum(len(row["assessments"]) for row in artifacts),
        },
        "artifacts": artifacts,
    }


def build_manifest(catalog: dict[str, Any]) -> dict[str, Any]:
    artifacts = []
    for course in catalog["artifacts"]:
        artifacts.append({
            "division_id": course["division"]["id"],
            "division_name": course["division"]["name"],
            "course_id": course["course_id"],
            "source_portfolio": course["source_portfolio"],
            "masterbot_targets": course["masterbot_targets"],
            "masterbot_mapping_status": course["division"]["masterbot_mapping_status"],
            "lesson_count": len(course["lessons"]),
            "exercise_count": len(course["exercises"]),
            "project_count": len(course["projects"]),
            "assessment_count": len(course["assessments"]),
            "status": course["status"],
            "training_eligibility": course["training_eligibility"],
        })
    return {
        "schema": "dreamco.buddy_division_specialist_course_artifacts.v1",
        "version": "1.0.0",
        "status": "draft_generated_needs_owner_review",
        "ownership_class": "dreamco_owned",
        "taxonomy": "config/dreamco-universal-capability-taxonomy.json",
        "counts": catalog["counts"],
        "artifacts": artifacts,
        "truth_boundary": (
            "These are original DreamCo curriculum drafts generated from DreamCo-owned bot profiles. "
            "They are not evidence of trained model weights, passed capability benchmarks, or certification."
        ),
    }
