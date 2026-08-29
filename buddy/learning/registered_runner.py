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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.events).read_text())
    events = payload.get("events", [])
    results = []
    for item in events:
        event = LearningEvent(
            event_id=item["event_id"],
            event_type=EventType(item["event_type"]),
            capability=item["capability"],
            success=bool(item["success"]),
            verified=bool(item["verified"]),
            regression_passed=bool(item["regression_passed"]),
            safety_passed=bool(item["safety_passed"]),
            external_assistance=bool(item.get("external_assistance", False)),
        )
        decision = evaluate_event(event)
        results.append({"event_id": event.event_id, "capability": event.capability,
                        "learn": decision.learn, "promote": decision.promote,
                        "reason": decision.reason})

    Path(args.out).write_text(json.dumps({
        "schema": "dreamco.continuous_learning.evidence.v1",
        "events_processed": len(results),
        "promotions": sum(r["promote"] for r in results),
        "results": results,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
