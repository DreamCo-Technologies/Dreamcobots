"""Shared DreamCo event envelope contract utilities."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

CONTRACT_PATH = Path(__file__).resolve().parents[2] / "config" / "shared_event_contract.json"


def load_event_contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def validate_event_envelope(event: dict[str, Any], contract: dict[str, Any] | None = None) -> bool:
    if not isinstance(event, dict):
        raise ValueError("event envelope must be a dict")

    contract_data = contract or load_event_contract()
    required_fields = contract_data.get("required_fields", [])
    for field in required_fields:
        if field not in event:
            raise ValueError(f"missing required field: {field}")

    event_type = event.get("event_type")
    if not isinstance(event_type, str) or "." not in event_type:
        raise ValueError("event_type must follow <family>.<subtype>")

    bot_id = event.get("bot_id")
    if not isinstance(bot_id, str) or not bot_id.strip():
        raise ValueError("bot_id must be a non-empty string")

    intent = event.get("intent")
    if not isinstance(intent, str) or not intent.strip():
        raise ValueError("intent must be a non-empty string")

    timestamp = event.get("timestamp")
    if not isinstance(timestamp, str):
        raise ValueError("timestamp must be an ISO-8601 string")
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be an ISO-8601 string") from exc

    status = event.get("status")
    status_values = contract_data.get("status_values", [])
    if status not in status_values:
        raise ValueError(f"status must be one of: {', '.join(status_values)}")

    correlation_id = event.get("correlation_id")
    if not isinstance(correlation_id, str) or not correlation_id.strip():
        raise ValueError("correlation_id must be a non-empty string")

    return True
