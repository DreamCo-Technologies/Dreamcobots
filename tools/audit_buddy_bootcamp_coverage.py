#!/usr/bin/env python3
"""Audit whether canonical Bootcamp source tracks are actually represented.

This is an inventory/coverage gate, not a course-completion or mastery claim.
It reads tracked manifests, reports gaps, and exits non-zero on structural errors.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TRACKS = {
    "huggingface": "config/buddy-huggingface-full-learning-map.json",
    "onet": "config/buddy-onet-content-model-curriculum.json",
    "freecodecamp": "buddy/bootcamp/sources/freecodecamp/catalog.json",
    "freecodecamp_path": "config/freecodecamp-complete-learning-path.json",
    "tokenizer": "config/buddy-tokenizer-training-curriculum.json",
    "tolkien": "config/buddy-tolkien-study-track.json",
    "masterbots": "config/masterbot-65-registry.json",
    "division_crosswalk": "config/generated/masterbot-55-domain-crosswalk.json",
}

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value

def audit(root: Path = ROOT) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema": "dreamco.bootcamp_coverage_audit.v1",
        "status": "inventory_only",
        "completion_claim": False,
        "tracks": {},
        "errors": [],
        "warnings": [],
    }
    docs: dict[str, dict[str, Any]] = {}
    for name, relative in TRACKS.items():
        path = root / relative
        if not path.is_file():
            result["errors"].append(f"missing required manifest: {relative}")
            continue
        try:
            docs[name] = load(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            result["errors"].append(f"invalid {relative}: {exc}")

    hf = docs.get("huggingface", {})
    courses = hf.get("official_courses", [])
    modules = hf.get("ecosystem_modules", [])
    result["tracks"]["huggingface"] = {
        "manifest": TRACKS["huggingface"],
        "course_records": len(courses) if isinstance(courses, list) else 0,
        "ecosystem_module_records": len(modules) if isinstance(modules, list) else 0,
        "declared_course_count": hf.get("course_count"),
        "declared_module_count": hf.get("ecosystem_module_count"),
        "status": "cataloged_not_studied",
    }
    if not isinstance(courses, list) or not courses:
        result["errors"].append("Hugging Face official_courses must be a non-empty array")
    if isinstance(courses, list) and hf.get("course_count") != len(courses):
        result["warnings"].append("Hugging Face declared course_count differs from records")
    if isinstance(modules, list) and hf.get("ecosystem_module_count") != len(modules):
        result["warnings"].append("Hugging Face declared ecosystem_module_count differs from records")

    onet = docs.get("onet", {})
    areas = onet.get("content_model_areas", [])
    result["tracks"]["onet"] = {
        "manifest": TRACKS["onet"],
        "content_model_area_records": len(areas) if isinstance(areas, list) else 0,
        "status": onet.get("status", "unknown"),
        "task_guides_generated": False,
    }
    if not isinstance(areas, list) or not areas:
        result["errors"].append("O*NET content_model_areas must be a non-empty array")
    result["warnings"].append("O*NET manifest coverage does not prove every occupation/task guide exists")

    fcc = docs.get("freecodecamp", {})
    videos = fcc.get("videos", [])
    result["tracks"]["freecodecamp"] = {
        "manifest": TRACKS["freecodecamp"],
        "inventory_status": fcc.get("inventory_status", "unknown"),
        "declared_video_count": fcc.get("video_count"),
        "video_records": len(videos) if isinstance(videos, list) else 0,
        "status": "cataloged_not_studied",
        "transcripts_complete": False,
        "study_guides_complete": False,
    }
    if not isinstance(videos, list):
        result["errors"].append("freeCodeCamp videos must be an array")
    if fcc.get("inventory_status") != "complete":
        result["warnings"].append("freeCodeCamp channel inventory is not marked complete")
    if isinstance(videos, list) and fcc.get("video_count") != len(videos):
        result["warnings"].append("freeCodeCamp declared video_count differs from video records")

    fcc_path = docs.get("freecodecamp_path", {})
    result["tracks"]["freecodecamp_path"] = {
        "manifest": TRACKS["freecodecamp_path"],
        "coverage_status": fcc_path.get("scope", {}).get("coverage_status", "unknown"),
        "status": "roadmap_only_unless_lessons_and_assessments_are_linked",
    }

    for name in ("tokenizer", "tolkien"):
        doc = docs.get(name, {})
        result["tracks"][name] = {
            "manifest": TRACKS[name],
            "status": doc.get("status", "unknown"),
            "curriculum_records": len(doc.get("curriculum", [])) if isinstance(doc.get("curriculum"), list) else 0,
            "training_executed": False,
        }
        result["warnings"].append(f"{name} curriculum presence does not prove training or mastery")

    registry = docs.get("masterbots", {})
    bots = registry.get("divisions", [])
    result["tracks"]["masterbots"] = {
        "manifest": TRACKS["masterbots"],
        "declared_count": registry.get("canonical_count"),
        "records": len(bots) if isinstance(bots, list) else 0,
        "status": "registry_inventory",
    }
    if registry.get("canonical_count") != 65 or not isinstance(bots, list) or len(bots) != 65:
        result["errors"].append("MasterBot registry must contain exactly 65 canonical records")

    crosswalk = docs.get("division_crosswalk", {})
    domains = crosswalk.get("domains", [])
    result["tracks"]["division_crosswalk"] = {
        "manifest": TRACKS["division_crosswalk"],
        "declared_divisions": crosswalk.get("counts", {}).get("domain_divisions"),
        "domain_records": len(domains) if isinstance(domains, list) else 0,
        "status": crosswalk.get("status", "unknown"),
        "owner_approved": sum(1 for row in domains if isinstance(row, dict) and row.get("owner_approval") is True) if isinstance(domains, list) else 0,
    }
    if crosswalk.get("counts", {}).get("domain_divisions") != 55:
        result["errors"].append("Division crosswalk must declare 55 canonical divisions")
    if not isinstance(domains, list) or len(domains) != 55:
        result["errors"].append("Division crosswalk must contain exactly 55 domain records")
    if crosswalk.get("status") != "approved":
        result["warnings"].append("55-division ownership crosswalk is not approved; do not infer primary ownership")

    result["status"] = "structural_errors" if result["errors"] else ("coverage_gaps_present" if result["warnings"] else "inventory_passed")
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(args.root.resolve())
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1 if report["errors"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
