"""Validate DreamCo-authored lessons without copying source material."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

REQUIRED = ("schema", "lesson_id", "division_id", "title", "learning_objectives",
            "original_explanation", "worked_examples", "practice", "assessment",
            "authorship", "provenance", "rights")

def validate_lesson(item: dict) -> list[str]:
    errors = [f"missing required field: {key}" for key in REQUIRED if key not in item]
    if errors:
        return errors
    if item["schema"] != "dreamco.original_lesson.v1":
        errors.append("unsupported lesson schema")
    if not isinstance(item["division_id"], int) or not 1 <= item["division_id"] <= 65:
        errors.append("division_id must be between 1 and 65")
    if len(item["learning_objectives"]) < 2:
        errors.append("at least two learning objectives required")
    if len(item["original_explanation"].strip()) < 80:
        errors.append("original explanation must be at least 80 characters")
    if not item["worked_examples"]:
        errors.append("at least one worked example required")
    if len(item["practice"]) < 2:
        errors.append("at least two practice tasks required")
    assessment = item["assessment"]
    if len(assessment.get("questions", [])) < 3 or len(assessment.get("answer_key", [])) < 3:
        errors.append("assessment requires three questions and answer explanations")
    authorship = item["authorship"]
    if not authorship.get("authoring_entity", "").strip():
        errors.append("authorship must identify the authoring entity")
    if len(authorship.get("human_contribution", "").strip()) < 20:
        errors.append("authorship must record meaningful human contribution")
    if authorship.get("human_owner_confirmation") not in {"pending", "confirmed", "not_applicable"}:
        errors.append("invalid human owner confirmation status")
    if not authorship.get("created_at"):
        errors.append("authorship must include a creation timestamp")
    provenance = item["provenance"]
    parsed = urlparse(provenance.get("source_url", ""))
    if parsed.scheme != "https" or not parsed.netloc:
        errors.append("provenance must include an HTTPS source URL")
    rights = item["rights"]
    if rights.get("source_material_copied") is not False:
        errors.append("lesson must be original; source_material_copied must be false")
    if rights.get("training_allowed") is not False:
        errors.append("lesson training remains disabled until separate approval")
    if rights.get("review_status") not in {"pending", "approved", "restricted", "rejected"}:
        errors.append("invalid rights review status")
    if not rights.get("owner_label", "").strip():
        errors.append("rights record must identify the claimed owner label")
    if rights.get("ownership_claim_status") not in {"pending_review", "confirmed", "disputed"}:
        errors.append("invalid ownership claim status")
    if rights.get("third_party_material_included") is not False:
        errors.append("original lesson package must not include third-party material")
    if rights.get("ownership_claim_status") == "confirmed" and authorship.get("human_owner_confirmation") != "confirmed":
        errors.append("confirmed ownership requires human owner confirmation")
    if provenance.get("source_usage") not in {"inspiration_only", "authorized_reference", "public_metadata_only"}:
        errors.append("invalid source usage")
    return errors

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson", type=Path)
    args = parser.parse_args()
    item = json.loads(args.lesson.read_text(encoding="utf-8"))
    errors = validate_lesson(item)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"VALID original DreamCo lesson: {item['lesson_id']} (division {item['division_id']})")

if __name__ == "__main__":
    main()
