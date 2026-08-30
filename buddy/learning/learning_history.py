"""Append-only learning history and native-capability trend calculations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def append_event(path: str | Path, event: dict[str, Any]) -> None:
    """Append one sanitized learning event; never rewrite prior evidence."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def summarize(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {"events": 0, "verified": 0, "promoted": 0, "native_verified": 0, "external_assisted": 0}
    events = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]
    verified = [e for e in events if e.get("verified")]
    native = [e for e in verified if e.get("native_success") and not e.get("external_assistance")]
    external = [e for e in verified if e.get("external_assistance")]
    return {
        "events": len(events),
        "verified": len(verified),
        "promoted": sum(bool(e.get("promote")) for e in events),
        "native_verified": len(native),
        "external_assisted": len(external),
        "native_solve_rate": len(native) / len(verified) if verified else 0.0,
        "external_assistance_rate": len(external) / len(verified) if verified else 0.0,
    }


def capability_trend(path: str | Path, capability_id: str) -> dict[str, Any]:
    """Summarize verified progress for one capability without mutating history."""
    target = Path(path)
    if not target.exists():
        return {"capability_id": capability_id, "verified": 0, "native_verified": 0, "promoted": False}
    events = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]
    matching = [e for e in events if e.get("capability_id") == capability_id]
    verified = [e for e in matching if e.get("verified")]
    native = [e for e in verified if e.get("native_success") and not e.get("external_assistance")]
    return {
        "capability_id": capability_id,
        "verified": len(verified),
        "native_verified": len(native),
        "promoted": any(bool(e.get("promote")) for e in matching),
        "latest_verified": verified[-1] if verified else None,
    }
