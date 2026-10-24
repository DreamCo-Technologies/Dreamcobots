"""Deterministic registered runner for continuous-learning evidence jobs.

This runner validates learning decisions and emits evidence without pretending to
perform model-weight training. Real trainers can be registered behind the same
contract later.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .continuous_learning_controller import LearningEvent, EventType, evaluate_event
except ImportError:
    from continuous_learning_controller import LearningEvent, EventType, evaluate_event


def process_events(events: list) -> list:
    if not isinstance(events, list):
        raise ValueError("events must be a list")
    ids = [item.get("event_id") for item in events if isinstance(item, dict)]
    if len(ids) != len(events) or any(not isinstance(i, str) or not i.strip() for i in ids):
        raise ValueError("every event requires a nonempty string identity")
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate event IDs")
    results = []
    for item in events:
        capability = item.get("capability")
        if not isinstance(capability, str) or not capability.strip():
            raise ValueError(f"{item['event_id']}: capability must be a nonempty string")
        flags = {}
        for name in ("success", "verified", "regression_passed", "safety_passed", "external_assistance"):
            value = item.get(name, False)
            if type(value) is not bool:
                raise ValueError(f"{item['event_id']}: {name} must be a boolean")
            flags[name] = value
        event = LearningEvent(event_id=item["event_id"], event_type=EventType(item["event_type"]),
                              capability=item["capability"], **flags)
        decision = evaluate_event(event)
        results.append({"event_id": event.event_id, "capability": event.capability,
                        "learn": decision.learn, "promote": decision.promote, "reason": decision.reason})
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.events).read_text())
    # Missing/misspelled event envelopes must not create a false zero-event receipt.
    if not isinstance(payload, dict) or "events" not in payload:
        raise ValueError("input must contain an explicit events list")
    results = process_events(payload["events"])

    Path(args.out).write_text(json.dumps({
        "schema": "dreamco.continuous_learning.evidence.v1",
        "events_processed": len(results),
        "weights_trained": False,
        "production_ready": False,
        "promotions": sum(r["promote"] for r in results),
        "results": results,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
