#!/usr/bin/env python3
"""Validate every Buddy study-resource catalog and expansion boundary."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "config"
POLICY = CATALOG_DIR / "buddy-study-resource-policy.json"
EXPANSION = CATALOG_DIR / "buddy-study-resources-1101-1200-expansion.json"


def validate_catalogs(root: Path = ROOT) -> dict:
    config = root / "config"
    policy_path = config / "buddy-study-resource-policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    files = sorted(config.glob("buddy-study-resources-*.json"))
    if not files:
        raise ValueError("no Buddy study-resource catalogs found")

    ids: dict[int, str] = {}
    urls: dict[str, str] = {}
    total = 0
    per_file = {}
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("resources")
        if not isinstance(rows, list):
            raise ValueError(f"resources must be a list: {path.name}")
        per_file[path.name] = len(rows)
        for row in rows:
            if not isinstance(row, list) or len(row) < 6:
                raise ValueError(f"resource rows must have at least six fields: {path.name}")
            resource_id, name, category, url = row[:4]
            if not isinstance(resource_id, int):
                raise ValueError(f"resource ID must be an integer: {path.name}")
            if not all(str(value).strip() for value in (name, category, url, row[4], row[5])):
                raise ValueError(f"resource fields cannot be blank: {path.name} ID {resource_id}")
            if not str(url).startswith("https://"):
                raise ValueError(f"resource URL must use HTTPS: {path.name} ID {resource_id}")
            canonical_url = str(url).strip().rstrip("/").lower()
            if resource_id in ids:
                raise ValueError(f"duplicate resource ID {resource_id}: {ids[resource_id]} and {path.name}")
            if canonical_url in urls:
                raise ValueError(f"duplicate resource URL {canonical_url}: {urls[canonical_url]} and {path.name}")
            ids[resource_id] = path.name
            urls[canonical_url] = path.name
            total += 1

    if EXPANSION.exists():
        expansion = json.loads(EXPANSION.read_text(encoding="utf-8"))
        rows = expansion.get("resources", [])
        expected = list(range(1101, 1201))
        actual = [row[0] for row in rows]
        if actual != expected:
            raise ValueError("resource expansion IDs must be exactly 1101-1200 in order")
        for flag in ("automatic_download", "automatic_transcript_download", "automatic_training_approval"):
            if expansion.get(flag) is not False:
                raise ValueError(f"study expansion must keep {flag}=false")
        tracks = expansion.get("specialized_study_tracks", [])
        if not isinstance(tracks, list):
            raise ValueError("specialized_study_tracks must be a list")
        for track in tracks:
            if track.get("track_id") == "tolkien":
                rights = track.get("rights_and_safety") or {}
                lessons = track.get("lesson_sequence") or []
                source_ids = track.get("source_ids") or []
                if len(lessons) != 8 or not source_ids:
                    raise ValueError("Tolkien study track requires eight lessons and source references")
                if any(source_id not in {row[0] for row in rows} for source_id in source_ids):
                    raise ValueError("Tolkien study track references unknown study resources")
                for flag in (
                    "primary_tolkien_texts_training_eligible",
                    "copyrighted_text_or_audio_ingestion_authorized",
                    "transcript_or_audiobook_download_authorized",
                    "invented_language_or_script_reproduction_authorized",
                    "character_setting_or_story_derivative_generation_authorized",
                    "model_weight_training_authorized",
                ):
                    if rights.get(flag) is not False:
                        raise ValueError(f"Tolkien rights gate must keep {flag}=false")
                if rights.get("unknown_rights_status") != "BLOCKED":
                    raise ValueError("Tolkien study track must block unknown rights")
            if track.get("track_id") == "database-and-dataset-engineering":
                rights = track.get("rights_and_safety") or {}
                lessons = track.get("lesson_sequence") or []
                source_ids = track.get("source_ids") or []
                if len(lessons) != 10 or not source_ids:
                    raise ValueError("database and dataset track requires ten lessons and source references")
                if any(source_id not in {row[0] for row in rows} for source_id in source_ids):
                    raise ValueError("database and dataset track references unknown study resources")
                for flag in (
                    "production_database_access_authorized",
                    "live_database_writes_authorized",
                    "production_migrations_authorized",
                    "bulk_dataset_download_authorized",
                    "private_or_paid_dataset_ingestion_authorized",
                    "model_weight_training_authorized",
                ):
                    if rights.get(flag) is not False:
                        raise ValueError(f"database/dataset rights gate must keep {flag}=false")
                if rights.get("unknown_rights_status") != "BLOCKED":
                    raise ValueError("database and dataset track must block unknown rights")
    else:
        raise ValueError("required study resource expansion 1101-1200 is missing")

    minimum = int(policy.get("minimum_operational_count", 0))
    target = int(policy.get("target_count", minimum))
    if total < minimum:
        raise ValueError(f"study resources below operational floor: {total} < {minimum}")
    if total > target:
        raise ValueError(f"study resources exceed configured target: {total} > {target}")

    return {
        "ok": True,
        "catalog_count": len(files),
        "resource_count": total,
        "unique_ids": len(ids),
        "unique_urls": len(urls),
        "expansion_1101_1200": 100,
        "per_file": per_file,
    }


def main() -> int:
    print(json.dumps(validate_catalogs(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
