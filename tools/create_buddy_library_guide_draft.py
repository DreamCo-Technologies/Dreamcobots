"""Create a rights-pending original study-guide skeleton for a discovered library.

This tool writes a draft only. It does not fetch source, infer license rights,
download packages, execute code, authorize training or mark a guide approved.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not result or len(result) > 100:
        raise ValueError("library identifier must produce a 1-100 character slug")
    return result


def build_draft(
    *,
    canonical_id: str,
    name: str,
    ecosystem: str,
    official_homepage: str,
    documentation_url: str,
    version_reviewed: str = "not-yet-reviewed",
    root: Path = ROOT,
) -> Path:
    for label, value in (("canonical_id", canonical_id), ("name", name), ("ecosystem", ecosystem)):
        if not value.strip():
            raise ValueError(f"{label} is required")
    if not official_homepage.startswith("https://") or not documentation_url.startswith("https://"):
        raise ValueError("official homepage and documentation URL must use HTTPS")
    file_name = slug(canonical_id) + ".json"
    directory = root / "data/buddy-library-study-guides"
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / file_name
    if destination.exists():
        raise FileExistsError(f"study guide already exists: {destination}")
    today = date.today().isoformat()
    guide: dict[str, Any] = {
        "schema_version": "dreamco.buddy_library_study_guide.v1",
        "library": {
            "canonical_id": canonical_id,
            "name": name,
            "ecosystem": ecosystem,
            "artifact_type": "library",
            "official_homepage": official_homepage,
            "official_documentation": [documentation_url],
            "version_reviewed": version_reviewed,
            "latest_version_checked_at": today,
            "maintenance_status": "unknown",
            "license": "unknown_pending_review",
            "supported_platforms": [],
        },
        "provenance": {
            "sources": [{
                "url": documentation_url,
                "source_type": "candidate_first_party_documentation",
                "accessed_at": today,
                "revision_or_version": version_reviewed,
                "license_or_terms_note": "Rights and terms review pending; this draft does not grant reuse or training permission.",
            }],
            "reviewed_at": today,
            "reviewer": "not_reviewed",
        },
        "learning_map": {
            "prerequisites": [],
            "objectives": ["TODO: write measurable original learning objectives after source review."],
            "concepts": [{
                "name": "TODO",
                "explanation": "Replace with an original explanation grounded in reviewed official documentation.",
                "limitations": ["Not yet researched."],
            }],
        },
        "api_inventory": {
            "inventory_method": "not_yet_reviewed",
            "coverage": "unknown",
            "entries": [],
        },
        "use_cases": [{
            "category": "experimental",
            "scenario": "TODO: identify a real use case and supporting evidence.",
            "implementation_pattern": "TODO: author an original implementation pattern.",
            "tradeoffs": ["Not yet researched."],
            "evidence": [documentation_url],
            "confidence": "hypothesis",
        }],
        "architecture_patterns": [],
        "security": {
            "threats": ["Not yet researched."],
            "safe_defaults": ["Do not execute untrusted package code."],
            "secret_handling": "Not yet researched.",
            "supply_chain": ["Review package provenance, dependencies and license before use."],
            "sandbox_required": True,
        },
        "performance": {"profiling_methods": [], "scaling_limits": ["Not yet researched."], "cost_model": "Not yet researched."},
        "practice": {
            "worked_examples": [{
                "goal": "TODO: add a verified worked example.",
                "steps": ["Complete after source review."],
                "verification": ["Add deterministic tests."],
            }],
            "exercises": [
                {"difficulty": level, "prompt": "TODO: author an original exercise.", "acceptance_criteria": ["TODO"], "tests": ["TODO"]}
                for level in ("beginner", "intermediate", "advanced")
            ],
            "projects": [{
                "name": "TODO: capstone project",
                "deliverable": "An original project demonstrating the library's core capabilities.",
                "rubric": ["Correctness", "Security", "Tests", "Documentation"],
            }],
            "debugging_playbook": [{
                "symptom": "TODO: add a verified failure mode.",
                "likely_causes": ["Not yet researched."],
                "diagnosis": ["Reproduce in an isolated environment."],
                "fix": ["Only add a fix after verification."],
                "prevention": ["Add a regression test."],
            }],
        },
        "crosswalks": {
            "onet_tasks": [],
            "onet_skills": [],
            "huggingface_tasks": [],
            "benchmarks": [],
            "dreamco_divisions": [],
            "masterbot_lanes": [],
            "revenue_playbooks": [],
        },
        "innovation": [],
        "evaluation": {
            "target_benchmark": "TODO: define a task-matched benchmark.",
            "holdout": "TODO: define an unseen holdout.",
            "regression": "TODO: define regression coverage.",
            "evidence_state": "discovered",
            "run_ids": [],
        },
        "rights": {
            "documentation_access": "unknown",
            "derivative_summary_permission": "pending",
            "evaluation_permission": "pending",
            "training_permission": "pending",
            "download_permission": "pending",
            "evidence_reference": "No permission is inferred from discovery.",
        },
        "status": "review_required",
    }
    destination.write_text(json.dumps(guide, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--canonical-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--ecosystem", required=True)
    parser.add_argument("--homepage", required=True)
    parser.add_argument("--docs-url", required=True)
    parser.add_argument("--version", default="not-yet-reviewed")
    args = parser.parse_args()
    path = build_draft(
        canonical_id=args.canonical_id, name=args.name, ecosystem=args.ecosystem,
        official_homepage=args.homepage, documentation_url=args.docs_url,
        version_reviewed=args.version, root=args.root,
    )
    print(path.relative_to(args.root).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
