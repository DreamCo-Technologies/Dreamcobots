"""Coverage matrix for the canonical 65-MasterBot registry; never invent O*NET mappings."""
from __future__ import annotations

import json
from pathlib import Path


def build_matrix(registry_path: str | Path, curriculum_path: str | Path | None = None) -> dict:
    registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    divisions = registry.get("divisions", [])
    ids = [item.get("id") for item in divisions]
    if len(divisions) != 65 or sorted(ids) != list(range(1, 66)):
        raise ValueError("canonical MasterBot registry must contain unique IDs 1..65")

    curricula_by_id: dict[str, dict] = {}
    curricula_by_name: dict[str, dict] = {}
    if curriculum_path and Path(curriculum_path).exists():
        data = json.loads(Path(curriculum_path).read_text(encoding="utf-8"))
        items = data.get("divisions", data.get("artifacts", []))
        if not isinstance(items, list):
            raise ValueError("curriculum manifest divisions/artifacts must be a list")
        curricula_by_id = {
            str(item["division_id"]): item
            for item in items
            if item.get("division_id") is not None
        }
        curricula_by_name = {
            str(item["division_name"]).casefold(): item
            for item in items
            if item.get("division_name")
        }

    rows = []
    for division in sorted(divisions, key=lambda item: item["id"]):
        curriculum = (
            curricula_by_id.get(str(division["id"]))
            or curricula_by_name.get(str(division["name"]).casefold())
            or {}
        )
        task_codes = curriculum.get("onet_task_codes", [])
        if not isinstance(task_codes, list):
            task_codes = []
        verified = curriculum.get("onet_mapping_status") == "verified" and bool(task_codes)
        owner_reviewed = curriculum.get("owner_reviewed") is True
        rows.append({
            "division_id": division["id"],
            "division_name": division["name"],
            "curriculum_status": curriculum.get("status", "not_yet_mapped"),
            "onet_task_codes": task_codes,
            "onet_mapping_status": "verified" if verified else "unverified_not_mapped",
            "tools": curriculum.get("tools", []),
            "competencies": curriculum.get("competencies", []),
            "readiness": "OWNER_REVIEWED" if owner_reviewed else "BLOCKED_UNTIL_OWNER_REVIEW",
        })

    return {
        "schema": "dreamco.bootcamp_division_matrix.v1",
        "canonical_registry": "config/masterbot-65-registry.json",
        "division_count": 65,
        "mapped_curricula": sum(row["curriculum_status"] not in ("not_yet_mapped", "") for row in rows),
        "verified_onet_mappings": sum(row["onet_mapping_status"] == "verified" for row in rows),
        "ready_divisions": sum(row["readiness"] == "OWNER_REVIEWED" for row in rows),
        "truth_boundary": "No O*NET task code is inferred from a division name. Unverified mappings remain explicitly unmapped.",
        "divisions": rows,
    }
