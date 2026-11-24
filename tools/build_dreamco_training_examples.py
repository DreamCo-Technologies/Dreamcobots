"""Build review-gated, original DreamCo training candidates from verified work."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/masterbot-65-registry.json"
ALLOWED_TYPES = {
    "verified_commit", "verified_test", "approved_pr", "approved_workflow",
    "verified_bug_fix", "original_lesson", "approved_synthetic",
}
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "phone": re.compile(r"(?<!\d)(?:\+1[ .-]?)?(?:\(?\d{3}\)?[ .-]?)\d{3}[ .-]?\d{4}(?!\d)"),
    "ssn": re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
}
SECRET_PATTERNS = {
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "generic_secret_assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*['\"]?[^\s'\"]{12,}"
    ),
}


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _safe_source_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def _split_manifest(rows: list[dict]) -> dict[str, Any]:
    manifest: dict[str, Any] = {}
    for split in ("train", "validation", "test"):
        serialized = "".join(_canonical(row) + "\n" for row in rows if row["split"] == split)
        manifest[split] = {
            "row_count": sum(row["split"] == split for row in rows),
            "sha256": _sha(serialized),
        }
    manifest["all_rows_sha256"] = _sha("".join(_canonical(row) + "\n" for row in rows))
    return manifest


def build(events: list[dict], masterbot_registry: Path = REGISTRY) -> dict:
    registry = json.loads(masterbot_registry.read_text(encoding="utf-8"))
    valid = {int(item["id"]): item["name"] for item in registry.get("divisions", [])}
    accepted: list[dict] = []
    rejected: list[dict] = []
    seen_ids: set[str] = set()
    seen_content: set[str] = set()

    for event in events:
        if not isinstance(event, dict):
            rejected.append({"event_id": "", "reason": "source record must be a JSON object"})
            continue
        event_id = _text(event.get("event_id"))
        if not event_id or event_id in seen_ids:
            rejected.append({"event_id": event_id, "reason": "missing or duplicate source event ID"})
            continue
        seen_ids.add(event_id)

        source_url = _text(event.get("source_url"))
        evidence_type = _text(event.get("evidence_type"))
        task = _text(event.get("task"))
        lesson = _text(event.get("verified_lesson"))
        owner = event.get("primary_masterbot_id")

        if not _safe_source_url(source_url) or evidence_type not in ALLOWED_TYPES:
            rejected.append({"event_id": event_id, "reason": "missing valid HTTPS evidence source or approved evidence type"})
            continue
        if not (
            event.get("verified") is True
            and event.get("human_reviewed") is True
            and event.get("training_allowed") is True
            and event.get("rights_status") == "VERIFIED"
        ):
            rejected.append({"event_id": event_id, "reason": "verification, human review, explicit training permission, or rights verification missing"})
            continue
        if not (
            event.get("contains_secrets") is False
            and event.get("contains_personal_data") is False
            and event.get("third_party_content_included") is False
        ):
            rejected.append({"event_id": event_id, "reason": "secrets, personal data, or third-party content is not allowed"})
            continue
        if isinstance(owner, bool) or not isinstance(owner, int) or owner not in valid or len(task) < 12 or len(lesson) < 30:
            rejected.append({"event_id": event_id, "reason": "invalid MasterBot owner or insufficient original task/lesson"})
            continue

        source_text = _canonical(event)
        if any(pattern.search(source_text) for pattern in PII_PATTERNS.values()):
            rejected.append({"event_id": event_id, "reason": "personal-data pattern detected"})
            continue
        if any(pattern.search(source_text) for pattern in SECRET_PATTERNS.values()):
            rejected.append({"event_id": event_id, "reason": "credential or private-key pattern detected"})
            continue

        criteria_raw = event.get("acceptance_criteria")
        evidence_raw = event.get("test_evidence")
        if not isinstance(criteria_raw, list) or not isinstance(evidence_raw, list):
            rejected.append({"event_id": event_id, "reason": "acceptance criteria and test evidence must be arrays"})
            continue
        criteria = [_text(item) for item in criteria_raw if _text(item)]
        evidence = [_text(item) for item in evidence_raw if _text(item)]
        if not criteria or not evidence:
            rejected.append({"event_id": event_id, "reason": "acceptance criteria and verified test evidence are required"})
            continue

        content_key = _sha(_canonical([owner, task.casefold(), lesson.casefold(), criteria, evidence]))
        if content_key in seen_content:
            rejected.append({"event_id": event_id, "reason": "duplicate task/lesson content detected"})
            continue
        seen_content.add(content_key)
        accepted.append({
            "event_id": event_id, "source_url": source_url, "evidence_type": evidence_type,
            "masterbot_id": owner, "masterbot": valid[owner], "task": task, "lesson": lesson,
            "criteria": criteria, "test_evidence": evidence, "source_event_sha256": _sha(source_text),
        })

    if len(accepted) < 3:
        raise ValueError(
            "At least three independently verified, rights-cleared, non-duplicate work records "
            f"are required; found {len(accepted)}"
        )
    owners = {item["masterbot_id"] for item in accepted}
    if len(owners) != 1:
        raise ValueError("Build one dataset per MasterBot lane; mixed-division datasets are rejected")

    accepted.sort(key=lambda item: _sha(item["event_id"]))
    rows = []
    for index, event in enumerate(accepted):
        split = "test" if index == len(accepted) - 1 else "validation" if index == len(accepted) - 2 else "train"
        instruction = f"How should {event['masterbot']} handle this verified task: {event['task']}?"
        response = " ".join([
            event["lesson"],
            "Acceptance criteria: " + "; ".join(event["criteria"]) + ".",
            "Verified evidence: " + "; ".join(event["test_evidence"]) + ".",
        ])
        row = {
            "text": "### Instruction:\n" + instruction + "\n### Response:\n" + response,
            "split": split,
            "masterbot_id": event["masterbot_id"],
            "source_event_id": event["event_id"],
            "source_url": event["source_url"],
            "source_event_sha256": event["source_event_sha256"],
            "evidence_type": event["evidence_type"],
            "derivation": "original_synthesis_from_verified_DreamCo_work",
        }
        row["example_id"] = _sha(_canonical(row))
        rows.append(row)

    return {
        "schema": "dreamco.original_training_candidate.v2",
        "generated_by": "DreamCo verified-work example builder",
        "accepted_source_events": len(accepted),
        "rejected_source_events": rejected,
        "rows": rows,
        "split_manifest": _split_manifest(rows),
        "primary_masterbot_ids": sorted(owners),
        "training_approved": False,
        "rights_status": "PENDING_FINAL_DATASET_CARD_REVIEW",
        "source_files_copied": False,
        "third_party_text_copied": False,
        "weights_trained": False,
        "notice": (
            "Candidate examples are original syntheses, not automatically training-approved. "
            "A human must review source permissions, the dataset card, split quality, ownership, "
            "privacy, and quality before registration or training. Hashes establish integrity, "
            "not correctness or legal permission."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--card-out", required=True)
    parser.add_argument("--name", default="DreamCo Verified Engineering Lessons")
    parser.add_argument("--license-url", required=True)
    parser.add_argument("--masterbot-id", required=True, type=int)
    args = parser.parse_args()

    events = [
        json.loads(line)
        for line in Path(args.events).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    events = [event for event in events if event.get("primary_masterbot_id") == args.masterbot_id]
    result = build(events)

    output_path = Path(args.out)
    card_path = Path(args.card_out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    card_path.parent.mkdir(parents=True, exist_ok=True)
    serialized_rows = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in result["rows"])
    output_path.write_text(serialized_rows, encoding="utf-8")
    card = {
        "schema": "dreamco.dataset_card_candidate.v2",
        "name": args.name,
        "owner": "DreamCo Technologies",
        "license": "DreamCo internal authored synthesis - pending human review",
        "license_url": args.license_url,
        "source_url": "https://github.com/DreamCo-Technologies/Dreamcobots",
        "data_plane": "dreamco_owned_training",
        "rights_status": "PENDING_HUMAN_REVIEW",
        "training_approved": False,
        "primary_masterbot_id": args.masterbot_id,
        "collaborating_masterbot_ids": [],
        "split_manifest": result["split_manifest"],
        "source_event_count": result["accepted_source_events"],
        "candidate_data_path": str(output_path),
        "candidate_file_sha256": _sha(serialized_rows),
        "review_required": True,
        "weights_trained": False,
    }
    card_path.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "accepted_events": result["accepted_source_events"],
        "rejected_events": len(result["rejected_source_events"]),
        "examples": len(result["rows"]),
        "training_approved": False,
        "weights_trained": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
