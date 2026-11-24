"""Build lane-isolated DreamCo Bootcamp training candidates from original lessons.

This tool creates candidate artifacts only. It never approves rights, registers
training data, downloads sources, invokes a teacher, or starts model training.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data/dreamco_training/bootcamp/core_lessons.v1.jsonl"
REGISTRY = ROOT / "config/masterbot-65-registry.json"
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "phone": re.compile(r"(?<!\d)(?:\+1[ .-]?)?(?:\(?\d{3}\)?[ .-]?)\d{3}[ .-]?\d{4}(?!\d)"),
    "ssn": re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
}
SECRET_PATTERNS = [
    re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,})\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
REQUIRED_AUTHORING = {
    "status": "DRAFT_REQUIRES_HUMAN_REVIEW",
    "owner_claim": "PENDING_ASSIGNMENT_REVIEW",
    "training_permission": "NOT_GRANTED",
}


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_rows(rows: list[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        for row in rows
    )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at line {line_number}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"JSONL line {line_number} must be an object")
        rows.append(value)
    return rows


def build_candidate(
    examples: list[dict[str, Any]],
    masterbot_id: int,
    registry: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    divisions = {int(item["id"]): item["name"] for item in registry.get("divisions", [])}
    if masterbot_id not in divisions:
        raise ValueError("masterbot_id must exist in the canonical 65-MasterBot registry")
    if len(divisions) != 65:
        raise ValueError("canonical registry must contain exactly 65 MasterBots")
    if len(examples) < 3:
        raise ValueError("at least three seed examples are required")
    ids: set[str] = set()
    content_fingerprints: set[str] = set()
    modules: set[str] = set()
    counts = {"train": 0, "validation": 0, "test": 0}
    rows = []
    for example in examples:
        example_id = str(example.get("example_id", "")).strip()
        if not example_id or example_id in ids:
            raise ValueError("example IDs must be non-empty and unique")
        ids.add(example_id)
        module_id = str(example.get("module_id", "")).strip()
        if not module_id:
            raise ValueError(f"{example_id}: module_id is required")
        modules.add(module_id)
        split = example.get("split")
        if split not in counts:
            raise ValueError(f"{example_id}: invalid split")
        prompt = str(example.get("prompt", "")).strip()
        response = str(example.get("response", "")).strip()
        if len(prompt) < 20 or len(response) < 40:
            raise ValueError(f"{example_id}: prompt or response is too short")
        rubric = example.get("rubric")
        tags = example.get("tags")
        if not isinstance(rubric, list) or len(rubric) < 2 or not all(isinstance(x, str) and len(x.strip()) >= 5 for x in rubric):
            raise ValueError(f"{example_id}: at least two meaningful rubric checks are required")
        if not isinstance(tags, list) or not tags or not all(isinstance(x, str) and x.strip() for x in tags):
            raise ValueError(f"{example_id}: at least one subject tag is required")
        if not isinstance(example.get("source"), dict) or example["source"].get("external_text_included") is not False:
            raise ValueError(f"{example_id}: seed data must not include unreviewed external text")
        if example.get("authoring") != REQUIRED_AUTHORING:
            raise ValueError(f"{example_id}: authoring and rights must remain pending human review")
        inspected = json.dumps(example, ensure_ascii=False)
        if any(pattern.search(inspected) for pattern in PII_PATTERNS.values()) or any(pattern.search(inspected) for pattern in SECRET_PATTERNS):
            raise ValueError(f"{example_id}: PII or secret pattern detected")
        fingerprint = hashlib.sha256((prompt.casefold() + "\\0" + response.casefold()).encode("utf-8")).hexdigest()
        if fingerprint in content_fingerprints:
            raise ValueError(f"{example_id}: duplicate prompt/response content detected")
        content_fingerprints.add(fingerprint)
        row = {
            "masterbot_id": masterbot_id,
            "split": split,
            "task_id": example_id,
            "text": f"### Instruction:\n{prompt}\n### Response:\n{response}",
            "prompt": prompt,
            "expected": response,
            "rubric": rubric,
            "module_id": module_id,
            "tags": tags,
            "source": example["source"],
            "authoring": example["authoring"],
            "target_scope": example.get("target_scope", "shared_foundation_candidate"),
        }
        rows.append(row)
        counts[split] += 1
    if any(count == 0 for count in counts.values()):
        raise ValueError("train, validation, and test must all be non-empty")
    if len(modules) < 10:
        raise ValueError("Bootcamp seed corpus must span at least ten distinct modules")
    if len(rows) != len(ids):
        raise ValueError("duplicate example detected")
    payload_bytes = _canonical_rows(rows)
    split_hashes = {
        f"{split}_sha256": _sha_bytes(_canonical_rows([row for row in rows if row["split"] == split]))
        for split in ("train", "validation", "test")
    }
    manifest = {
        "schema": "dreamco.first_party_training_candidate.v1",
        "dataset_id": f"dreamco.bootcamp.core.v1.masterbot-{masterbot_id:03d}",
        "dataset_version": "1.0.0",
        "dataset_name": "DreamCo Bootcamp Core Lessons",
        "source_id": "dreamco.bootcamp.core.v1",
        "owner_or_creator": "DreamCo Technologies - proposed, pending assignment review",
        "primary_masterbot_id": masterbot_id,
        "primary_masterbot_name": divisions[masterbot_id],
        "source_file": "data/dreamco_training/bootcamp/core_lessons.v1.jsonl",
        "source_sha256": _sha_bytes(_canonical_rows(examples)),
        "candidate_sha256": _sha_bytes(payload_bytes),
        "split_manifest": split_hashes,
        "split_counts": counts,
        "example_count": len(rows),
        "module_count": len(modules),
        "module_ids": sorted(modules),
        "data_plane": "dreamco_owned_training",
        "rights_status": "PENDING_HUMAN_REVIEW",
        "training_approved": False,
        "human_review_required": True,
        "owner_assignment_review_required": True,
        "external_text_included": False,
        "contains_private_holdout": False,
        "weights_trained": False,
        "training_started": False,
        "eligible_for_training": False,
        "sharing": {
            "shared_foundation_source": True,
            "materialize_per_division": True,
            "raw_private_data_shared": False,
            "private_holdouts_shared": False,
            "weights_or_checkpoints_shared": False,
            "collaboration_requires_owner_grant": True,
        },
        "notice": "Candidate generation only. No rights approval, ingestion, training, or model ownership claim is made.",
    }
    return rows, manifest


def build_dataset_card(manifest: dict[str, Any], candidate_path: str) -> dict[str, Any]:
    return {
        "dataset_id": manifest["dataset_id"],
        "name": manifest["dataset_name"],
        "owner": "DreamCo Technologies - pending assignment review",
        "license": "DREAMCO_INTERNAL_OWNED",
        "license_url": "https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/config/buddy-training-data-provenance-policy.json",
        "license_url_status": "INTERNAL_POLICY_REFERENCE_NOT_A_PUBLIC_LICENSE",
        "source": "dreamco_authored",
        "source_id": manifest["source_id"],
        "ai_training_allowed": False,
        "content_rights_verified": False,
        "owner_assignment_verified": False,
        "contributor_rights_verified": False,
        "owner_approval_id": "",
        "source_url": "https://github.com/DreamCo-Technologies/Dreamcobots",
        "data_plane": "dreamco_owned_training",
        "rights_status": "PENDING_HUMAN_REVIEW",
        "rights_evidence": "",
        "training_approved": False,
        "holdout": False,
        "primary_masterbot_id": manifest["primary_masterbot_id"],
        "collaborating_masterbot_ids": [],
        "split_manifest": manifest["split_manifest"],
        "content_sha256": manifest["candidate_sha256"],
        "candidate_data_path": candidate_path,
        "privacy_review": "NOT_STARTED",
        "human_review_required": True,
        "owner_assignment_review_required": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--masterbot-id", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest-out", type=Path, required=True)
    parser.add_argument("--card-out", type=Path, required=True)
    args = parser.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    examples = load_jsonl(args.source)
    rows, manifest = build_candidate(examples, args.masterbot_id, registry)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
    args.card_out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(_canonical_rows(rows))
    manifest["candidate_path"] = str(args.out)
    manifest["candidate_sha256"] = _sha_bytes(args.out.read_bytes())
    card = build_dataset_card(manifest, str(args.out))
    args.manifest_out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.card_out.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "dataset_id": manifest["dataset_id"],
        "examples": manifest["example_count"],
        "modules": manifest["module_count"],
        "split_counts": manifest["split_counts"],
        "training_approved": False,
        "training_started": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
