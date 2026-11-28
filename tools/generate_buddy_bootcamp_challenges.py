#!/usr/bin/env python3
"""Generate rights-gated, original Buddy Bootcamp challenge specifications from task seeds.

This creates challenge *specifications*, not model training data or a trained model.
Source task text is only admitted when a source-specific rights manifest explicitly
approves commercial and training use. Evaluation-only material is never accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_MANIFEST_PATH = ROOT / "config/buddy-bootcamp-100-resource-manifest.json"

OUTPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Buddy occupational workflow challenge response",
    "type": "object",
    "additionalProperties": False,
    "required": ["task_summary", "steps", "required_tools", "safety_checks", "completion_criteria"],
    "properties": {
        "task_summary": {"type": "string", "minLength": 1},
        "steps": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False,
            "required": ["step", "action", "verification"], "properties": {
                "step": {"type": "integer", "minimum": 1},
                "action": {"type": "string", "minLength": 1},
                "verification": {"type": "string", "minLength": 1}}}},
        "required_tools": {"type": "array", "items": {"type": "string"}},
        "safety_checks": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "completion_criteria": {"type": "array", "minItems": 1, "items": {"type": "string"}}
    }
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: each row must be an object")
        yield row


def validate_rights(rights: dict[str, Any], source_id: str, source_license: str) -> None:
    required = {
        "source_id": source_id,
        "license_id": source_license,
        "commercial_use_approved": True,
        "training_use_approved": True,
        "evaluation_only": False,
        "privacy_review_status": "APPROVED",
        "review_status": "APPROVED",
    }
    for key, expected in required.items():
        if rights.get(key) != expected:
            raise ValueError(f"rights manifest gate failed: {key} must equal {expected!r}")
    if not rights.get("reviewer") or not rights.get("reviewed_at") or not rights.get("evidence_uri"):
        raise ValueError("rights manifest must record reviewer, reviewed_at and evidence_uri")


def normalize_text(value: Any, field: str, max_length: int = 3000) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if not text:
        raise ValueError(f"source row is missing {field}")
    if len(text) > max_length:
        raise ValueError(f"{field} exceeds {max_length} characters")
    return text


def build_challenge(row: dict[str, Any], division: dict[str, Any], rights: dict[str, Any],
                    source_id: str, source_license: str, ordinal: int) -> dict[str, Any]:
    task_id = normalize_text(row.get("task_id") or row.get("task_id_onet") or row.get("id"), "task_id", 160)
    task_statement = normalize_text(row.get("task_statement") or row.get("task"), "task_statement")
    occupation_code = normalize_text(row.get("occupation_code") or row.get("onet_soc_code"), "occupation_code", 80)
    occupation_title = normalize_text(row.get("occupation_title") or row.get("occupation"), "occupation_title", 300)
    source_record = {
        "source_id": source_id,
        "source_license_id": source_license,
        "source_task_id": task_id,
        "occupation_code": occupation_code,
        "occupation_title": occupation_title,
        "source_task_sha256": hashlib.sha256(task_statement.encode("utf-8")).hexdigest(),
        "rights_manifest_sha256": hashlib.sha256(canonical_json(rights).encode("utf-8")).hexdigest(),
        "source_url": row.get("source_url"),
    }
    challenge_seed = f"{division['id']}|{source_id}|{task_id}|{source_record['source_task_sha256']}"
    challenge_id = "BUDDY-" + hashlib.sha256(challenge_seed.encode()).hexdigest()[:16].upper()
    prompt = (
        "You are completing an original DreamCo Buddy Bootcamp occupational workflow challenge. "
        "Use the task seed below to produce a safe, auditable workflow plan. Do not assume access "
        "to tools or data that are not explicitly available. State verification steps and identify "
        "safety, privacy, authorization, and escalation checks.\n\n"
        f"Occupation: {occupation_title} ({occupation_code})\n"
        f"Occupational task seed: {task_statement}\n\n"
        "Return JSON only, conforming exactly to the supplied response schema."
    )
    pytest_contract = {
        "grader": "json_schema",
        "schema": OUTPUT_SCHEMA,
        "assertions": [
            "response parses as JSON",
            "response validates against the response schema",
            "step numbers are consecutive starting at 1",
            "every step has a non-empty action and verification",
            "safety_checks is non-empty",
            "completion_criteria is non-empty",
        ],
        "hidden_tests_required_before_mastery": True,
        "public_schema_is_not_a_blind_holdout": True,
    }
    return {
        "schema": "dreamco.buddy_bootcamp_challenge.v1",
        "challenge_id": challenge_id,
        "ordinal": ordinal,
        "division": {
            "id": division["id"],
            "slug": division.get("slug"),
            "name": division["name"],
            "masterbot_targets": division.get("masterbot_targets", []),
        },
        "source": source_record,
        "rights": {
            "status": "APPROVED_FOR_THIS_SOURCE_AND_PURPOSE",
            "rights_manifest_sha256": source_record["rights_manifest_sha256"],
            "does_not_transfer_ownership_of_source_material": True,
        },
        "challenge": {"kind": "occupational_workflow_planning", "prompt": prompt},
        "response_schema": OUTPUT_SCHEMA,
        "pytest_contract": pytest_contract,
        "provenance": {
            "generator": "tools/generate_buddy_bootcamp_challenges.py",
            "generator_version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "originality_boundary": "DreamCo-authored framing, schema and grading contract; source task seed remains subject to its upstream rights.",
            "training_split": "candidate_training_only_after_separate_dataset_release_approval",
            "holdout_split": "NEVER_GENERATE_FROM_THIS_TOOL",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-jsonl", type=Path, required=True,
                        help="Staged task seed JSONL; expected fields task_id, task_statement, occupation_code, occupation_title")
    parser.add_argument("--rights-manifest", type=Path, required=True,
                        help="Source-specific rights approval JSON; see docs/buddy-bootcamp-resource-foundry.md")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-license-id", required=True)
    parser.add_argument("--division-id", type=int, required=True)
    parser.add_argument("--output-jsonl", type=Path, required=True)
    parser.add_argument("--max-tasks", type=int, default=100)
    args = parser.parse_args()
    if args.max_tasks < 1 or args.max_tasks > 10000:
        raise ValueError("--max-tasks must be between 1 and 10000")
    rights = read_json(args.rights_manifest)
    validate_rights(rights, args.source_id, args.source_license_id)
    resource_manifest = read_json(RESOURCE_MANIFEST_PATH)
    divisions = resource_manifest.get("canonical_divisions", [])
    division = next((item for item in divisions if item.get("id") == args.division_id), None)
    if division is None:
        raise ValueError(f"division id {args.division_id} is not in the canonical 55-domain-division registry")
    output = []
    seen = set()
    for row in read_jsonl(args.input_jsonl):
        if len(output) >= args.max_tasks:
            break
        challenge = build_challenge(row, division, rights, args.source_id, args.source_license_id, len(output) + 1)
        if challenge["challenge_id"] in seen:
            raise ValueError(f"duplicate source task generated challenge {challenge['challenge_id']}")
        seen.add(challenge["challenge_id"])
        output.append(challenge)
    if not output:
        raise ValueError("no valid source tasks were provided")
    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    args.output_jsonl.write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in output), encoding="utf-8")
    print(json.dumps({"status": "CHALLENGES_GENERATED", "count": len(output),
                      "division": division, "source_id": args.source_id,
                      "rights_manifest_sha256": hashlib.sha256(canonical_json(rights).encode()).hexdigest(),
                      "output": str(args.output_jsonl)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
