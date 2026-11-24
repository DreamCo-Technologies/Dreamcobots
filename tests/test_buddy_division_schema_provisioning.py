from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from buddy.datasets.provision_division_schemas import (
    DivisionProvisioningError,
    provision_division_schemas,
)


def resource_map(path: Path) -> Path:
    rows = [
        {"masterbot_id": i, "logical_database_namespace": f"dreamco_division_{i:03d}"}
        for i in range(1, 66)
    ]
    path.write_text(json.dumps({"routes": rows}), encoding="utf-8")
    return path


def db_mocks(*, missing_roles=None, unsafe_roles=None, no_membership=None, existing_schemas=None, wrong_owners=None):
    missing_roles = set(missing_roles or [])
    unsafe_roles = set(unsafe_roles or [])
    no_membership = set(no_membership or [])
    existing_schemas = set(existing_schemas or [])
    wrong_owners = dict(wrong_owners or {})
    cursor = MagicMock()
    roles = [
        (f"dreamco_division_{i:03d}", False, i in unsafe_roles, i not in no_membership)
        for i in range(1, 66)
        if i not in missing_roles
    ]
    owners = [
        (name, wrong_owners.get(name, name))
        for name in sorted(existing_schemas)
    ]
    cursor.fetchall.side_effect = [roles, owners]
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    connect = MagicMock()
    connect.return_value.__enter__.return_value = connection
    return connect, cursor


class DivisionSchemaProvisioningTests(unittest.TestCase):
    def test_default_without_dsn_is_blocked_and_never_executes_ddl(self):
        connect = Mock()
        result = provision_division_schemas(dsn="", connect=connect)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["ddl_executed"])
        connect.assert_not_called()

    def test_dry_run_reports_missing_owner_roles_and_never_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            mapping = resource_map(Path(temp) / "map.json")
            connect, cursor = db_mocks(missing_roles={65})
            result = provision_division_schemas(dsn="postgresql://test", resource_map_path=mapping, connect=connect)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(result["inventory"]["missing_owner_roles"], ["dreamco_division_065"])
            self.assertEqual(cursor.execute.call_count, 2)

    def test_dry_run_is_ready_only_when_all_65_safe_roles_exist(self):
        with tempfile.TemporaryDirectory() as temp:
            mapping = resource_map(Path(temp) / "map.json")
            connect, cursor = db_mocks(existing_schemas={"dreamco_division_001"})
            result = provision_division_schemas(dsn="postgresql://test", resource_map_path=mapping, connect=connect)
            self.assertEqual(result["status"], "PLAN_READY")
            self.assertEqual(result["inventory"]["preexisting_owner_roles"], 65)
            self.assertFalse(result["ddl_executed"])
            self.assertEqual(cursor.execute.call_count, 2)

    def test_blocks_when_operator_is_not_member_of_missing_schema_owner_role(self):
        with tempfile.TemporaryDirectory() as temp:
            mapping = resource_map(Path(temp) / "map.json")
            connect, _ = db_mocks(no_membership={65})
            result = provision_division_schemas(dsn="postgresql://test", resource_map_path=mapping, connect=connect)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(result["inventory"]["missing_owner_memberships"], ["dreamco_division_065"])

    def test_rejects_login_or_superuser_owner_roles_and_owner_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            mapping = resource_map(Path(temp) / "map.json")
            connect, _ = db_mocks(unsafe_roles={3}, existing_schemas={"dreamco_division_001"},
                                  wrong_owners={"dreamco_division_001": "postgres"})
            result = provision_division_schemas(dsn="postgresql://test", resource_map_path=mapping, connect=connect)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(result["inventory"]["unsafe_owner_roles"], ["dreamco_division_003"])
            self.assertEqual(result["inventory"]["schema_owner_mismatches"], ["dreamco_division_001"])

    def test_apply_requires_approval_map_pin_and_explicit_environment_opt_in(self):
        with tempfile.TemporaryDirectory() as temp:
            mapping = resource_map(Path(temp) / "map.json")
            with self.assertRaises(DivisionProvisioningError):
                provision_division_schemas(dsn="postgresql://test", resource_map_path=mapping, apply=True,
                                           approval_id=None, expected_resource_map_sha256="x", allow_apply=True)
            with self.assertRaises(DivisionProvisioningError):
                provision_division_schemas(dsn="postgresql://test", resource_map_path=mapping, apply=True,
                                           approval_id="APPROVAL-1", expected_resource_map_sha256="wrong", allow_apply=True)
            with self.assertRaises(DivisionProvisioningError):
                provision_division_schemas(dsn="postgresql://test", resource_map_path=mapping, apply=True,
                                           approval_id="APPROVAL-1", expected_resource_map_sha256="x", allow_apply=False)

    def test_apply_creates_only_missing_schemas_and_revokes_public(self):
        with tempfile.TemporaryDirectory() as temp:
            mapping = resource_map(Path(temp) / "map.json")
            connect, cursor = db_mocks(existing_schemas={"dreamco_division_001"})
            import hashlib
            map_hash = hashlib.sha256(mapping.read_bytes()).hexdigest()
            result = provision_division_schemas(
                dsn="postgresql://test", resource_map_path=mapping, apply=True,
                approval_id="APPROVAL-1", expected_resource_map_sha256=map_hash,
                connect=connect, allow_apply=True,
            )
            self.assertEqual(result["status"], "PROVISIONED")
            self.assertTrue(result["ddl_executed"])
            self.assertEqual(cursor.execute.call_count, 2 + (64 * 2))
            self.assertIn('CREATE SCHEMA "dreamco_division_002" AUTHORIZATION "dreamco_division_002"',
                          [call.args[0] for call in cursor.execute.call_args_list])
            self.assertFalse(result["roles_created"])
            self.assertFalse(result["application_role_memberships_granted"])


if __name__ == "__main__":
    unittest.main()
