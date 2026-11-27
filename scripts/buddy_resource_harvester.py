"""Rights-aware, offline-first resource intake for all Institute divisions.

This tool stages candidate material for review. It never writes training corpora,
development fixtures, private holdouts, or model checkpoints. Hashes prove file
identity, not authorship, originality, or permission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "dreamco-institute-academic-catalog.json"
DEFAULT_SOURCE_MANIFEST = ROOT / "config" / "buddy-resource-sources.json"
ALLOWED_RIGHTS = {"DREAMCO_ORIGINAL", "APPROVED_FOR_TRAINING"}
ALLOWED_TYPES = {"local_markdown", "cached_jsonl"}
SECRET_MARKERS = (
    "-----BEGIN PRIVATE KEY-----",
    "ghp_", "github_pat_", "sk-proj-", "sk_live_", "AKIA",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def load_divisions(path: Path = CATALOG) -> dict[str, str]:
    catalog = load_object(path)
    if catalog.get("schema") != "dreamco.institute.academic_catalog.v1":
        raise ValueError("unsupported Institute academic catalog schema")
    divisions: dict[str, str] = {}
    for college in catalog.get("colleges", []):
        college_id = college.get("id")
        for division in college.get("divisions", []):
            if not isinstance(division, str) or not division:
                raise ValueError("catalog contains an invalid division ID")
            if division in divisions:
                raise ValueError(f"division appears more than once in academic catalog: {division}")
            divisions[division] = str(college_id)
    if len(divisions) != 55:
        raise ValueError(f"expected 55 canonical academic divisions; found {len(divisions)}")
    return divisions


def safe_repo_path(raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        raise ValueError("source paths must be repository-relative")
    resolved = (ROOT / candidate).resolve()
    if resolved != ROOT and ROOT not in resolved.parents:
        raise ValueError("source path escapes repository root")
    if not resolved.is_file():
        raise FileNotFoundError(f"source file does not exist: {raw}")
    return resolved


def check_text_safety(text: str, source: str) -> None:
    if any(marker in text for marker in SECRET_MARKERS):
        raise PermissionError(f"possible credential material detected in {source}; quarantine source manually")


def make_record(division: str, college: str, source: dict[str, Any],
                prompt: str, completion: str, source_hash: str,
                ordinal: int) -> dict[str, Any]:
    if len(prompt.strip()) < 12 or len(completion.strip()) < 12:
        raise ValueError("resource prompt and completion must each contain at least 12 characters")
    check_text_safety(prompt + "\n" + completion, str(source.get("path", "cached-record")))
    identity = json.dumps(
        {"division": division, "prompt": prompt.strip(), "completion": completion.strip()},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")
    return {
        "schema": "dreamco.resource_candidate.v1",
        "division_id": division,
        "college_id": college,
        "prompt": prompt.strip(),
        "completion": completion.strip(),
        "provenance": {
            "source_type": source["source_type"],
            "source_path": source["path"],
            "source_sha256": source_hash,
            "rights_status": source["rights_status"],
            "license_id": source.get("license_id"),
            "evidence_reference": source["evidence_reference"],
            "approved_for_training": source["approved_for_training"],
            "approved_for_evaluation": source.get("approved_for_evaluation", False),
            "record_ordinal": ordinal,
        },
        "record_sha256": sha256_bytes(identity),
        "status": "QUARANTINED_PENDING_REVIEW",
        "routing": "NOT_ASSIGNED",
    }


def markdown_records(path: Path, division: str, college: str,
                     source: dict[str, Any], source_hash: str) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    check_text_safety(raw, str(path.relative_to(ROOT)))
    sections = re.split(r"(?m)(?=^#{1,3}\s+)", raw)
    records = []
    for index, section in enumerate(sections):
        content = section.strip()
        if len(content) < 50:
            continue
        lines = content.splitlines()
        heading = lines[0].lstrip("#").strip() if lines[0].startswith("#") else path.stem
        body = "\n".join(lines[1:]).strip() if lines[0].startswith("#") else content
        if len(body) < 30:
            continue
        records.append(make_record(
            division, college, source,
            f"Explain and apply the DreamCo {division} specification: {heading}",
            body[:4000], source_hash, index,
        ))
    return records


def cached_jsonl_records(path: Path, division: str, college: str,
                         source: dict[str, Any], source_hash: str) -> list[dict[str, Any]]:
    records = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        item = json.loads(line)
        if not isinstance(item, dict):
            raise ValueError(f"{path}:{index + 1} must be a JSON object")
        if item.get("division_id") not in (None, division):
            raise ValueError(f"{path}:{index + 1} has a mismatched division_id")
        prompt, completion = item.get("prompt"), item.get("completion")
        if not isinstance(prompt, str) or not isinstance(completion, str):
            raise ValueError(f"{path}:{index + 1} needs string prompt and completion")
        records.append(make_record(division, college, source, prompt, completion, source_hash, index))
    return records


def load_sources(path: Path, divisions: dict[str, str]) -> list[dict[str, Any]]:
    payload = load_object(path)
    if payload.get("schema") != "dreamco.buddy_resource_sources.v1":
        raise ValueError("unsupported resource source manifest schema")
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise ValueError("source manifest must contain a sources array")
    seen = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("each source entry must be an object")
        division = source.get("division_id")
        if division not in divisions:
            raise ValueError(f"source references unknown division: {division}")
        if source.get("source_type") not in ALLOWED_TYPES:
            raise ValueError(f"unsupported source_type for {division}")
        if source.get("rights_status") not in ALLOWED_RIGHTS:
            raise PermissionError(f"source for {division} is not rights-cleared for training")
        if source.get("approved_for_training") is not True:
            raise PermissionError(f"source for {division} lacks explicit training approval")
        if not isinstance(source.get("evidence_reference"), str) or not source["evidence_reference"].strip():
            raise ValueError(f"source for {division} needs a rights evidence reference")
        if source.get("source_type") == "cached_jsonl" and source.get("approved_for_evaluation") is True:
            raise PermissionError("training-intake sources cannot be auto-approved as benchmark fixtures")
        key = (division, source.get("path"))
        if key in seen:
            raise ValueError(f"duplicate source declaration: {key}")
        seen.add(key)
    return sources


def run(source_manifest: Path, output_dir: Path, dry_run: bool = False) -> dict[str, Any]:
    divisions = load_divisions()
    sources = load_sources(source_manifest, divisions)
    staged: dict[str, list[dict[str, Any]]] = {key: [] for key in divisions}
    rejected: list[dict[str, str]] = []
    for source in sources:
        division = source["division_id"]
        try:
            path = safe_repo_path(source["path"])
            digest = sha256_file(path)
            if source.get("expected_sha256") and source["expected_sha256"].lower() != digest:
                raise ValueError("source SHA-256 differs from the pinned manifest hash")
            if source["source_type"] == "local_markdown":
                records = markdown_records(path, division, divisions[division], source, digest)
            else:
                records = cached_jsonl_records(path, division, divisions[division], source, digest)
            staged[division].extend(records)
        except (OSError, ValueError, PermissionError, json.JSONDecodeError) as exc:
            rejected.append({"division_id": division, "path": str(source.get("path", "")),
                             "reason": f"{type(exc).__name__}: {exc}"})

    summary = []
    for division in sorted(divisions):
        records = staged[division]
        # Stable ordering and deduplication; never split into train/dev/holdout here.
        unique = {item["record_sha256"]: item for item in records}
        ordered = [unique[key] for key in sorted(unique)]
        summary.append({"division_id": division, "college_id": divisions[division],
                        "staged_candidates": len(ordered)})
        if not dry_run and ordered:
            target = output_dir / division / "quarantine.jsonl"
            target.parent.mkdir(parents=True, exist_ok=True)
            # Replace atomically; no append-based split drift or accidental holdout mutation.
            temp = target.with_suffix(".jsonl.tmp")
            temp.write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n"
                                    for item in ordered), encoding="utf-8")
            temp.replace(target)

    report = {
        "schema": "dreamco.buddy.resource_intake_report.v1",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "canonical_divisions": len(divisions),
        "sources_declared": len(sources),
        "records_staged": sum(item["staged_candidates"] for item in summary),
        "rejected_sources": rejected,
        "divisions": summary,
        "status": "REVIEW_REQUIRED" if sources else "NO_SOURCES_CONFIGURED",
        "training_corpora_written": False,
        "development_suites_written": False,
        "private_holdouts_written": False,
        "holdout_seals_modified": False,
        "model_weights_modified": False,
        "network_calls_made": False,
    }
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "resource_intake_report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "resource_staging")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        report = run(args.source_manifest, args.output_dir, args.dry_run)
    except (OSError, ValueError, PermissionError, json.JSONDecodeError) as exc:
        print(f"RESOURCE INTAKE BLOCKED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "status": report["status"],
        "canonical_divisions": report["canonical_divisions"],
        "sources_declared": report["sources_declared"],
        "records_staged": report["records_staged"],
        "rejected_sources": len(report["rejected_sources"]),
    }, indent=2))
    return 1 if report["rejected_sources"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
