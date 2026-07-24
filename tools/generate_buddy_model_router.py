#!/usr/bin/env python3
"""Publish Buddy's free-first model connector policy for the static chat UI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "buddy-model-router.json"
WEB_OUT = ROOT / "website" / "data" / "buddy-model-router.js"


def build_public_policy() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    connectors = source.get("connectors", [])
    ids = [item.get("id") for item in connectors]
    if len(ids) != len(set(ids)) or not all(isinstance(item, str) and item for item in ids):
        raise ValueError("Model connector ids must be unique non-empty strings")
    if not any(item.get("id") == "buddy_native" and item.get("mode") == "free" for item in connectors):
        raise ValueError("Buddy Native must remain the default free route")
    return {
        "schema": source["schema"],
        "defaultMode": source["default_mode"],
        "policy": source["policy"],
        "connectors": [
            {
                "id": item["id"],
                "label": item["label"],
                "mode": item["mode"],
                "availability": item["availability"],
                "taskTypes": item["task_types"],
                "customModelIdAllowed": bool(
                    source["policy"].get("custom_model_ids_allowed_for_connected_providers")
                ),
            }
            for item in connectors
        ],
    }


def output_text() -> str:
    return f"window.BUDDY_MODEL_ROUTER={json.dumps(build_public_policy(), separators=(',', ':'))};\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = output_text()
    if args.check:
        if not WEB_OUT.exists() or WEB_OUT.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"Generated output is stale: {WEB_OUT.relative_to(ROOT)}")
    else:
        WEB_OUT.parent.mkdir(parents=True, exist_ok=True)
        WEB_OUT.write_text(expected, encoding="utf-8")
    public = build_public_policy()
    print(json.dumps({
        "ok": True,
        "connectors": len(public["connectors"]),
        "free": sum(item["mode"] == "free" for item in public["connectors"]),
        "premium": sum(item["mode"] == "premium" for item in public["connectors"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
