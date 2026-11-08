#!/usr/bin/env python3
"""Read-only validation of Buddy's research-only open-weight shortlist.

This validates registry syntax and deliberately blocked status, not actual
licenses, model weights, training rights, safety, or hardware compatibility.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

SCHEMA = "dreamco.buddy_open_weight_candidate_research.v1"
STATUS = "research_only_no_download_or_training"
FIELDS = {
    "id", "advertised_parameter_class", "model_card_url",
    "license_label_observed", "candidate_role", "relative_compute_expectation",
    "source_checked_date", "exact_revision_commit", "license_notice_review_receipt",
    "commercial_rights_reviewed", "derivative_weight_rights_reviewed",
    "redistribution_obligations_reviewed", "hardware_preflight_receipt",
    "local_latency_ms", "local_quality_score", "independent_holdout_receipt",
    "model_downloaded", "model_trained", "production_ready",
}
FALSE_FIELDS = {
    "commercial_rights_reviewed", "derivative_weight_rights_reviewed",
    "redistribution_obligations_reviewed", "model_downloaded", "model_trained",
    "production_ready",
}
NULL_FIELDS = {
    "exact_revision_commit", "license_notice_review_receipt",
    "hardware_preflight_receipt", "local_latency_ms", "local_quality_score",
    "independent_holdout_receipt",
}
DECISION_FIELDS = {
    "selected_for_training", "training_authorized",
    "model_promotion_authorized", "release_authorized", "required_before_training",
}
MODEL_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
PARAMS = re.compile(r"[0-9]+(?:\.[0-9]+)?[MB]\Z")
LICENSE = re.compile(r"[A-Za-z0-9][A-Za-z0-9.+-]{1,63}\Z")


class CandidateError(ValueError):
    """Invalid or overclaiming research-only registry."""


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise CandidateError("duplicate JSON key")
        result[key] = value
    return result


def _no_constant(value: str) -> None:
    raise CandidateError("nonfinite JSON constant: " + value)


def parse(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_unique_keys,
                          parse_constant=_no_constant)
    except json.JSONDecodeError as exc:
        raise CandidateError("invalid candidate registry JSON") from exc


def _date(value: Any) -> dt.date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise CandidateError("invalid ISO date")
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise CandidateError("invalid ISO date") from exc


def _text(value: Any) -> bool:
    return isinstance(value, str) and 1 <= len(value) <= 1000 and bool(value.strip())


def validate(data: Any) -> dict:
    if not isinstance(data, dict) or set(data) != {
        "schema", "status", "as_of_date", "notes", "candidates", "decision"
    }:
        raise CandidateError("invalid top-level fields")
    if data["schema"] != SCHEMA or data["status"] != STATUS:
        raise CandidateError("research-only schema/status required")
    as_of = _date(data["as_of_date"])
    if not isinstance(data["notes"], list) or not data["notes"] or len(data["notes"]) > 30 or not all(_text(x) for x in data["notes"]):
        raise CandidateError("invalid research notes")
    candidates = data["candidates"]
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 20:
        raise CandidateError("invalid candidate list")
    seen = set()
    for candidate in candidates:
        if not isinstance(candidate, dict) or set(candidate) != FIELDS:
            raise CandidateError("invalid candidate fields")
        model_id = candidate["id"]
        if not isinstance(model_id, str) or not MODEL_ID.fullmatch(model_id):
            raise CandidateError("invalid model identifier")
        normalized = unicodedata.normalize("NFKC", model_id).casefold()
        if normalized in seen:
            raise CandidateError("duplicate normalized model identifier")
        seen.add(normalized)
        if candidate["model_card_url"] != "https://huggingface.co/" + model_id:
            raise CandidateError("model card URL must match model identifier")
        if not isinstance(candidate["advertised_parameter_class"], str) or not PARAMS.fullmatch(candidate["advertised_parameter_class"]):
            raise CandidateError("invalid advertised parameter class")
        if not isinstance(candidate["license_label_observed"], str) or not LICENSE.fullmatch(candidate["license_label_observed"]):
            raise CandidateError("invalid observed license label")
        for field in ("candidate_role", "relative_compute_expectation"):
            if not _text(candidate[field]):
                raise CandidateError("invalid " + field)
        if _date(candidate["source_checked_date"]) > as_of:
            raise CandidateError("source check date after registry date")
        for field in FALSE_FIELDS:
            if candidate[field] is not False:
                raise CandidateError("research-only candidate cannot assert " + field)
        for field in NULL_FIELDS:
            if candidate[field] is not None:
                raise CandidateError("research-only candidate cannot assert " + field)
    decision = data["decision"]
    if not isinstance(decision, dict) or set(decision) != DECISION_FIELDS:
        raise CandidateError("invalid decision fields")
    if decision["selected_for_training"] is not None:
        raise CandidateError("research-only registry cannot select training model")
    for field in ("training_authorized", "model_promotion_authorized", "release_authorized"):
        if decision[field] is not False:
            raise CandidateError("research-only registry cannot authorize " + field)
    requirements = decision["required_before_training"]
    if not isinstance(requirements, list) or not requirements or len(requirements) > 40 or not all(_text(x) for x in requirements):
        raise CandidateError("invalid pretraining requirements")
    return {
        "schema": "dreamco.buddy_open_weight_candidate_preflight.v1",
        "status": "research_only_no_training",
        "candidate_count": len(candidates),
        "candidate_ids": [x["id"] for x in candidates],
        "model_card_metadata_verified": False,
        "commercial_and_derivative_rights_verified": False,
        "hardware_latency_quality_measured": False,
        "independent_holdouts_completed": False,
        "training_authorized": False,
        "production_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = validate(parse(args.registry.read_text(encoding="utf-8")))
    except (OSError, CandidateError, TypeError, ValueError) as exc:
        parser.exit(2, "Candidate registry preflight blocked: " + str(exc) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
