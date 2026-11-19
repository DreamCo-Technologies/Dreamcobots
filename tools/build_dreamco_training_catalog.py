#!/usr/bin/env python3
"""Build a provenance-aware index of DreamCo's existing training resources.

This indexes repository manifests and counts records. It does not download,
copy, scrape, or train on third-party content.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/dreamco_training/catalog.json"


def load_json(relative: str):
    path = ROOT / relative
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def main() -> int:
    catalog = load_json("data/dreamco_training/catalog.json")
    if not catalog:
        raise SystemExit("Missing canonical catalog template")
    datasets = load_json("website/data/free-datasets.json") or {}
    platforms = load_json("website/data/open-platforms.json") or {}
    courses = load_json("benchmarks/study_courses/course_catalog.json") or {}
    lesson_library = load_json("data/dreamco_training/lessons/universal_task_mastery_lessons_v1.json") or {}
    original_lessons = lesson_library.get("lessons", [])
    study_packs = []
    for path in sorted((ROOT / "study_packs").glob("*/index.json")):
        pack = json.loads(path.read_text(encoding="utf-8"))
        study_packs.append({
            "pack_id": pack.get("pack_id", path.parent.name),
            "title": pack.get("title", path.parent.name),
            "path": str(path.relative_to(ROOT)),
            "lesson_count": len(pack.get("lessons", [])),
            "train_allowed": bool(pack.get("train_allowed", False)),
            "ownership": "per_pack_manifest_review_required",
        })
    packages = []
    package_root = ROOT / "data/dreamco_knowledge/packages"
    if package_root.exists():
        for manifest_path in sorted(package_root.glob("*/*/manifest.json")):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            packages.append({
                "sku_id": manifest.get("sku_id"),
                "version": manifest.get("version"),
                "title": manifest.get("title"),
                "path": str(manifest_path.relative_to(ROOT)),
                "license_gate_status": manifest.get("license_gate_status", "unknown"),
                "release_level": manifest.get("release_level", "unknown"),
                "ownership": "mixed_per_asset_review_required",
            })
    catalog["totals"] = {
        "source_manifests": len(catalog.get("source_manifests", [])),
        "external_dataset_pointers": len(datasets.get("datasets", [])),
        "platform_resource_pointers": len(platforms.get("resources", [])),
        "courses": len(courses.get("courses", [])),
        "study_packs": len(study_packs),
        "versioned_data_packages": len(packages),
        "dreamco_original_training_records": 0,
        "dreamco_original_lesson_drafts": len(original_lessons),
        "train_eligible_assets": 0,
    }
    catalog["external_dataset_index"] = [
        {
            "id": row.get("name"),
            "url": row.get("href"),
            "declared_license": row.get("license"),
            "category": row.get("category"),
            "listed_train_flag": row.get("train", False),
            "ownership": "third_party_reference_only",
            "ingested": False,
            "training_eligibility": "must_reverify_license_and_asset",
        }
        for row in datasets.get("datasets", [])
    ]
    catalog["platform_index"] = [
        {
            "name": row.get("name"),
            "url": row.get("href"),
            "category": row.get("category"),
            "declared_license": row.get("license"),
            "ownership": "third_party_reference_only",
        }
        for row in platforms.get("resources", [])
    ]
    catalog["course_index"] = [
        {
            "id": row.get("id"),
            "domain": row.get("domain"),
            "name": row.get("name"),
            "ownership": "dreamco_owned_course_metadata",
            "lesson_content_status": "not_inferred_from_catalog_entry",
        }
        for row in courses.get("courses", [])
    ]
    catalog["original_lesson_index"] = [
        {
            "lesson_id": row.get("lesson_id"),
            "module_id": row.get("module_id"),
            "title": row.get("title"),
            "domain": row.get("domain"),
            "skills": row.get("skills", []),
            "review_status": lesson_library.get("review_status", "unknown"),
            "training_eligibility": lesson_library.get("training_eligibility", "unknown"),
            "ownership": lesson_library.get("ownership_class", "unknown"),
        }
        for row in original_lessons
    ]
    catalog["lesson_library_status"] = lesson_library.get("review_status", "not_present")
    catalog["study_pack_index"] = study_packs
    catalog["data_package_index"] = packages
    catalog["generation_status"] = "indexed_from_repository_manifests"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(catalog["totals"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
