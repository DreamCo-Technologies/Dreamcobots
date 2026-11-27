"""Deterministic registered runner for continuous-learning evidence jobs.

This runner validates learning decisions and emits evidence without pretending to
perform model-weight training. Real trainers can be registered behind the same
contract later.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from continuous_learning_controller import LearningEvent, EventType, evaluate_event


def _required_bool(item: dict, key: str) -> bool:
    value = item.get(key)
    if type(value) is not bool:
        raise ValueError(f"{key} must be a JSON boolean")
    return value


def _optional_bool(item: dict, key: str, default: bool = False) -> bool:
    if key not in item:
        return default
    value = item[key]
    if type(value) is not bool:
        raise ValueError(f"{key} must be a JSON boolean")
    return value


def _text(item: dict, key: str) -> str:
    value = item.get(key, "")
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def _evidence_refs(item: dict) -> tuple[str, ...]:
    refs = item.get("evidence_refs", [])
    if not isinstance(refs, list) or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
        raise ValueError("evidence_refs must be a list of non-empty strings")
    return tuple(refs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.events).read_text(encoding="utf-8"))
    events = payload.get("events", [])
    if not isinstance(events, list):
        raise ValueError("events must be a JSON array")

    results = []
    for item in events:
        if not isinstance(item, dict):
            raise ValueError("each learning event must be a JSON object")
        event = LearningEvent(
            event_id=_text(item, "event_id"),
            event_type=EventType(_text(item, "event_type")),
            capability=_text(item, "capability"),
            success=_required_bool(item, "success"),
            verified=_required_bool(item, "verified"),
            regression_passed=_required_bool(item, "regression_passed"),
            safety_passed=_required_bool(item, "safety_passed"),
            external_assistance=_optional_bool(item, "external_assistance"),
            evidence_refs=_evidence_refs(item),
            run_id=_text(item, "run_id"),
            commit_sha=_text(item, "commit_sha"),
            baseline_ref=_text(item, "baseline_ref"),
            holdout_ref=_text(item, "holdout_ref"),
            regression_ref=_text(item, "regression_ref"),
            safety_ref=_text(item, "safety_ref"),
        )
        decision = evaluate_event(event)
        results.append({
            "event_id": event.event_id,
            "capability": event.capability,
            "learn": decision.learn,
            "promote": decision.promote,
            "reason": decision.reason,
            "evidence_refs": list(event.evidence_refs),
            "run_id": event.run_id,
            "commit_sha": event.commit_sha,
            "baseline_ref": event.baseline_ref,
            "holdout_ref": event.holdout_ref,
            "regression_ref": event.regression_ref,
            "safety_ref": event.safety_ref,
        })

    Path(args.out).write_text(json.dumps({
        "schema": "dreamco.continuous_learning.evidence.v1",
        "events_processed": len(results),
        "promotions": sum(result["promote"] for result in results),
        "results": results,
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
