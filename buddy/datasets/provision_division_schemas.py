"""Guarded PostgreSQL provisioning for DreamCo's 65 division schemas.

Default operation is a read-only plan. Applying DDL requires an explicit CLI
flag, an operator approval reference, a matching resource-map hash, a separate
environment opt-in, and 65 pre-existing non-login, non-superuser owner roles.
The tool never creates database roles or grants application-role membership.
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

from buddy.datasets.postgres_probe import DEFAULT_RESOURCE_MAP, PostgresProbeError, load_expected_namespaces

NAMESPACE_PATTERN = re.compile(r"^dreamco_division_[0-9]{3}$")
ALLOW_APPLY_ENV = "DREAMCO_ALLOW_DIVISION_SCHEMA_PROVISIONING"


class DivisionProvisioningError(RuntimeError):
    """Provisioning request failed a safety or database precondition."""


def _inspect(cursor: Any, namespaces: list[str]) -> dict[str, Any]:
    cursor.execute(
        "SELECT rolname, rolsuper, rolcanlogin, pg_catalog.pg_has_role(current_user, rolname, 'MEMBER') "
        "FROM pg_catalog.pg_roles WHERE rolname = ANY(%s)",
        (namespaces,),
    )
    roles = {
        row[0]: {"superuser": bool(row[1]), "can_login": bool(row[2]), "operator_is_member": bool(row[3])}
        for row in cursor.fetchall()
    }
    cursor.execute(
        "SELECT n.nspname, r.rolname FROM pg_catalog.pg_namespace AS n "
        "JOIN pg_catalog.pg_roles AS r ON r.oid = n.nspowner "
        "WHERE n.nspname = ANY(%s)",
        (namespaces,),
    )
    owners = {row[0]: row[1] for row in cursor.fetchall()}
    missing_roles = sorted(set(namespaces) - set(roles))
    unsafe_roles = sorted(name for name, flags in roles.items() if flags["superuser"] or flags["can_login"])
    owner_mismatches = sorted(name for name, owner in owners.items() if owner != name)
    return {
        "roles": roles,
        "existing_schema_owners": owners,
        "missing_owner_roles": missing_roles,
        "unsafe_owner_roles": unsafe_roles,
        "missing_owner_memberships": sorted(
            name for name in set(namespaces) - set(owners)
            if name in roles and not roles[name]["operator_is_member"]
        ),
        "schema_owner_mismatches": owner_mismatches,
        "missing_schemas": sorted(set(namespaces) - set(owners)),
    }


def provision_division_schemas(
    *,
    dsn: str | None = None,
    resource_map_path: str | Path = DEFAULT_RESOURCE_MAP,
    apply: bool = False,
    approval_id: str | None = None,
    expected_resource_map_sha256: str | None = None,
    connect: Callable[..., Any] | None = None,
    allow_apply: bool | None = None,
) -> dict[str, Any]:
    """Plan or apply schema creation; never creates roles or application grants."""
    try:
        namespaces, map_hash = load_expected_namespaces(resource_map_path)
    except PostgresProbeError as exc:
        raise DivisionProvisioningError(str(exc)) from exc

    if apply:
        if not approval_id or not approval_id.strip():
            raise DivisionProvisioningError("An operator approval reference is required for --apply")
        if expected_resource_map_sha256 != map_hash:
            raise DivisionProvisioningError("Expected resource-map SHA-256 does not match the current map")
        permitted = os.environ.get(ALLOW_APPLY_ENV) == "1" if allow_apply is None else allow_apply
        if not permitted:
            raise DivisionProvisioningError(f"Set {ALLOW_APPLY_ENV}=1 in the protected execution environment to permit DDL")

    configured_dsn = dsn if dsn is not None else (os.environ.get("DREAMCO_POSTGRES_DSN") or os.environ.get("DATABASE_URL"))
    if not configured_dsn:
        return {
            "schema": "dreamco.division_schema_provisioning_evidence.v1",
            "status": "BLOCKED",
            "reason": "POSTGRES_DSN_NOT_CONFIGURED",
            "expected_division_schemas": len(namespaces),
            "resource_map_sha256": map_hash,
            "ddl_executed": False,
            "credentials_emitted": False,
        }

    if connect is None:
        try:
            import psycopg
        except ImportError as exc:
            raise DivisionProvisioningError("Install psycopg to enable PostgreSQL schema provisioning") from exc
        connect = psycopg.connect

    try:
        with connect(configured_dsn, connect_timeout=5, options="-c statement_timeout=10000 -c lock_timeout=5000") as connection:
            with connection.cursor() as cursor:
                inventory = _inspect(cursor, namespaces)
                blocked = any(inventory[key] for key in (
                    "missing_owner_roles", "unsafe_owner_roles", "missing_owner_memberships", "schema_owner_mismatches"
                ))
                if blocked:
                    status = "BLOCKED"
                elif not apply:
                    status = "PLAN_READY"
                elif not inventory["missing_schemas"]:
                    status = "ALREADY_PROVISIONED"
                else:
                    for namespace in inventory["missing_schemas"]:
                        # Names have already passed a strict identifier allowlist.
                        cursor.execute(f'CREATE SCHEMA "{namespace}" AUTHORIZATION "{namespace}"')
                        cursor.execute(f'REVOKE ALL ON SCHEMA "{namespace}" FROM PUBLIC')
                    status = "PROVISIONED"
    except DivisionProvisioningError:
        raise
    except Exception as exc:
        # Driver exceptions may include connection details. Do not leak them.
        raise DivisionProvisioningError(f"PostgreSQL provisioning failed: {type(exc).__name__}") from exc

    return {
        "schema": "dreamco.division_schema_provisioning_evidence.v1",
        "status": status,
        "probed_at": datetime.now(timezone.utc).isoformat(),
        "expected_division_schemas": len(namespaces),
        "resource_map_sha256": map_hash,
        "approval_id": approval_id if apply else None,
        "inventory": {
            "preexisting_owner_roles": len(inventory["roles"]),
            "missing_owner_roles": inventory["missing_owner_roles"],
            "unsafe_owner_roles": inventory["unsafe_owner_roles"],
            "missing_owner_memberships": inventory["missing_owner_memberships"],
            "existing_schemas": len(inventory["existing_schema_owners"]),
            "missing_schemas": inventory["missing_schemas"],
            "schema_owner_mismatches": inventory["schema_owner_mismatches"],
        },
        "ddl_executed": bool(apply and status == "PROVISIONED"),
        "roles_created": False,
        "application_role_memberships_granted": False,
        "credentials_emitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource-map", default=str(DEFAULT_RESOURCE_MAP))
    parser.add_argument("--apply", action="store_true", help="Apply schema DDL; default is read-only planning")
    parser.add_argument("--approval-id", help="Operator approval reference required with --apply")
    parser.add_argument("--expected-resource-map-sha256", help="Pin the exact resource map reviewed by the operator")
    parser.add_argument("--output", help="Optional evidence JSON output path")
    args = parser.parse_args()
    try:
        evidence = provision_division_schemas(
            resource_map_path=args.resource_map,
            apply=args.apply,
            approval_id=args.approval_id,
            expected_resource_map_sha256=args.expected_resource_map_sha256,
        )
    except DivisionProvisioningError as exc:
        evidence = {
            "schema": "dreamco.division_schema_provisioning_evidence.v1",
            "status": "ERROR",
            "reason": str(exc),
            "ddl_executed": False,
            "credentials_emitted": False,
        }
    rendered = json.dumps(evidence, indent=2, sort_keys=True)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\\n", encoding="utf-8")
    print(rendered)
    return 0 if evidence["status"] in {"PLAN_READY", "PROVISIONED", "ALREADY_PROVISIONED"} else (2 if evidence["status"] == "BLOCKED" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
