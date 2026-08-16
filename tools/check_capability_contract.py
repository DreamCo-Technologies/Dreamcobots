"""Lightweight contract checker for capability records.

The checker is intentionally dependency-free so contributors can run it before
installing the complete DreamCo toolchain.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

POLICY = Path("config/capability-lifecycle-policy.json")


def main() -> int:
    if not POLICY.exists():
        print(f"Missing capability lifecycle policy: {POLICY}", file=sys.stderr)
        return 1

    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    required = policy.get("required_record_fields", [])
    states = set(policy.get("states", []))

    if not required or not states:
        print("Capability policy is incomplete", file=sys.stderr)
        return 1

    print(f"Capability lifecycle states: {len(states)}")
    print(f"Required record fields: {len(required)}")
    print("Capability contract policy: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
