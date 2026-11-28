"""Command-line interface for validating rules and evaluating fixture observations."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .engine import Observation, WatchRule, evaluate


def _read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _atomic_write(path: str, payload: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{destination.name}.", dir=str(destination.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="Validate a JSON rule catalog.")
    validate.add_argument("--rules", required=True)
    run = sub.add_parser("evaluate", help="Evaluate normalized observation fixtures.")
    run.add_argument("--rules", required=True)
    run.add_argument("--observations", required=True, help="JSON object mapping rule IDs to arrays.")
    run.add_argument("--state", required=True)
    run.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    raw_rules = _read_json(args.rules)
    if not isinstance(raw_rules, list):
        parser.error("Rule catalog must be a JSON array.")
    rules = [WatchRule.from_dict(row) for row in raw_rules]
    if args.command == "validate":
        print(json.dumps({"valid": True, "rule_count": len(rules)}, sort_keys=True))
        return 0

    raw_observations = _read_json(args.observations)
    if not isinstance(raw_observations, dict):
        parser.error("Observation fixture must be an object keyed by rule ID.")
    observations = {
        rule_id: [Observation.from_dict(row) for row in rows]
        for rule_id, rows in raw_observations.items()
        if isinstance(rows, list)
    }
    state_path = Path(args.state)
    previous = _read_json(str(state_path)) if state_path.exists() else {}
    alerts, state = evaluate(rules, observations, previous)
    _atomic_write(args.state, state)
    _atomic_write(args.output, {"schema": "dreamco.watchtower.alerts.v1", "alerts": [alert.__dict__ for alert in alerts]})
    print(json.dumps({"alert_count": len(alerts), "state": str(state_path), "output": args.output}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
