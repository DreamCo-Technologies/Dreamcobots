#!/usr/bin/env python3
"""Validate Buddy's connector registry and publish its public-safe catalog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.connections import AuthMethod


SOURCE = ROOT / "config" / "buddy-connector-registry.json"
PUBLIC = ROOT / "website" / "data" / "buddy-connection-catalog.json"
ALLOWED_STATUSES = {"adapter_ready", "configuration_required", "user_handoff"}


def load_source() -> dict[str, Any]:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    if payload.get("schema") != "dreamco.buddy_connector_registry.v1":
        raise ValueError("Unsupported Buddy connector registry schema.")
    return payload


def build_public_catalog(payload: dict[str, Any]) -> dict[str, Any]:
    methods = payload.get("auth_methods", [])
    gates = payload.get("user_presence_gates", [])
    contracts = payload.get("connector_contracts", [])
    expected_methods = {method.value for method in AuthMethod}
    method_ids = [str(item.get("id", "")) for item in methods]
    if set(method_ids) != expected_methods or len(method_ids) != len(set(method_ids)):
        raise ValueError("Connector registry must define every auth method exactly once.")
    if any(item.get("status") not in ALLOWED_STATUSES for item in methods):
        raise ValueError("Connector registry contains an unsupported adapter status.")
    if len(gates) < 7 or len({item.get("id") for item in gates}) != len(gates):
        raise ValueError("Connector registry must define unique user-presence gates.")
    if len(contracts) < 6 or len({item.get("id") for item in contracts}) != len(contracts):
        raise ValueError("Connector registry must define unique connector contracts.")

    summary = payload.get("summary", {})
    if summary.get("raw_credentials_accepted") is not False:
        raise ValueError("Buddy connector registry must reject raw credentials.")

    return {
        "schema": "dreamco.public_buddy_connection_catalog.v1",
        "summary": {
            **summary,
            "auth_method_count": len(methods),
            "user_presence_gate_count": len(gates),
            "connector_contract_count": len(contracts),
        },
        "auth_methods": methods,
        "user_presence_gates": gates,
        "connector_contracts": contracts,
        "public_contract": {
            "mode": "connection_planner",
            "live_authentication": False,
            "live_account_creation": False,
            "raw_secrets_collected": False,
            "stored_browser_data": ["plan status", "app label", "official host", "timestamp"],
            "backend_required_for": [
                "token exchange",
                "secret resolution",
                "live API calls",
                "connection revocation",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate the committed catalog.")
    args = parser.parse_args()

    catalog = build_public_catalog(load_source())
    rendered = json.dumps(catalog, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not PUBLIC.exists() or PUBLIC.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Buddy connection catalog is missing or out of date.")
    else:
        PUBLIC.parent.mkdir(parents=True, exist_ok=True)
        PUBLIC.write_text(rendered, encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "auth_methods": catalog["summary"]["auth_method_count"],
                "user_presence_gates": catalog["summary"]["user_presence_gate_count"],
                "connector_contracts": catalog["summary"]["connector_contract_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
