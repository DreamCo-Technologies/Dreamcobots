"""Read-only PostgreSQL connectivity and division-schema verification.

This module never creates schemas, migrates tables, or writes application data.
It uses DREAMCO_POSTGRES_DSN from the environment and emits credential-free
evidence suitable for an operator-reviewed provisioning workflow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESOURCE_MAP = ROOT / "config/generated/division-resource-readiness-map.json"
NAMESPACE_PATTERN = re.compile(r"^dreamco_division_[0-9]{3}$")


class PostgresProbeError(RuntimeError):
    """A safe PostgreSQL probe could not be completed."""


def load_expected_namespaces(resource_map_path: str | Path = DEFAULT_RESOURCE_MAP) -> tuple[list[str], str]:
    path = Path(resource_map_path)
    raw = path.read_bytes()
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PostgresProbeError("Division resource map is not valid JSON") from exc
    routes = payload.get("routes")
    if not isinstance(routes, list) or len(routes) != 65:
        raise PostgresProbeError("Expected exactly 65 MasterBot resource routes")
    namespaces: list[str] = []
    for route in routes:
        namespace = route.get("logical_database_namespace") if isinstance(route, dict) else None
        if not isinstance(namespace, str) or not NAMESPACE_PATTERN.fullmatch(namespace):
            raise PostgresProbeError("Resource map contains an invalid logical database namespace")
        namespaces.append(namespace)
    if len(set(namespaces)) != 65:
        raise PostgresProbeError("Division database namespaces must be unique")
    return sorted(namespaces), hashlib.sha256(raw).hexdigest()


def probe_postgres(
    *,
    dsn: str | None = None,
    resource_map_path: str | Path = DEFAULT_RESOURCE_MAP,
    connect: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Run read-only SELECT probes and verify expected schemas already exist."""
    configured_dsn = dsn if dsn is not None else os.environ.get("DREAMCO_POSTGRES_DSN")
    if not configured_dsn:
        return {
            "schema": "dreamco.postgres_probe_evidence.v1",
            "status": "BLOCKED",
            "reason": "DREAMCO_POSTGRES_DSN_NOT_CONFIGURED",
            "credentials_emitted": False,
        }

    namespaces, resource_map_sha256 = load_expected_namespaces(resource_map_path)
    if connect is None:
        try:
            import psycopg
        except ImportError as exc:
            raise PostgresProbeError("Install psycopg to enable PostgreSQL connectivity probes") from exc
        connect = psycopg.connect

    try:
        with connect(
            configured_dsn,
            connect_timeout=5,
            options="-c default_transaction_read_only=on -c statement_timeout=5000",
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute("SELECT current_database(), current_user")
                identity = cursor.fetchone()
                cursor.execute(
                    "SELECT nspname FROM pg_catalog.pg_namespace WHERE nspname = ANY(%s)",
                    (namespaces,),
                )
                found = {row[0] for row in cursor.fetchall()}
    except Exception as exc:
        # Exception text can contain a DSN. Never copy it into evidence.
        raise PostgresProbeError(f"PostgreSQL probe failed: {type(exc).__name__}") from exc

    missing = sorted(set(namespaces) - found)
    return {
        "schema": "dreamco.postgres_probe_evidence.v1",
        "status": "CONNECTED_SCHEMAS_VERIFIED" if not missing else "CONNECTED_SCHEMA_INCOMPLETE",
        "probed_at": datetime.now(timezone.utc).isoformat(),
        "database_identity": {
            "database": str(identity[0]),
            "role": str(identity[1]),
        },
        "expected_division_namespaces": len(namespaces),
        "verified_division_namespaces": len(found),
        "missing_division_namespaces": missing,
        "resource_map_sha256": resource_map_sha256,
        "checks": {
            "connection": "PASS",
            "read_only_transaction": "PASS",
            "namespace_inventory": "PASS" if not missing else "INCOMPLETE",
            "schema_creation_performed": False,
            "application_data_modified": False,
        },
        "credentials_emitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource-map", default=str(DEFAULT_RESOURCE_MAP))
    parser.add_argument("--output", help="Optional evidence JSON output path")
    args = parser.parse_args()
    try:
        evidence = probe_postgres(resource_map_path=args.resource_map)
    except PostgresProbeError as exc:
        evidence = {
            "schema": "dreamco.postgres_probe_evidence.v1",
            "status": "ERROR",
            "reason": str(exc),
            "credentials_emitted": False,
        }
    rendered = json.dumps(evidence, indent=2, sort_keys=True)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\\n", encoding="utf-8")
    print(rendered)
    return 0 if evidence["status"] == "CONNECTED_SCHEMAS_VERIFIED" else (2 if evidence["status"] == "BLOCKED" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
