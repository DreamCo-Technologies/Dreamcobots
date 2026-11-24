from __future__ import annotations

import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from unittest.mock import MagicMock, Mock

from buddy.datasets.postgres_probe import PostgresProbeError, load_expected_namespaces, main, probe_postgres


def resource_map(path: Path, *, count: int = 65, duplicate: bool = False) -> Path:
    rows = []
    for index in range(count):
        suffix = 1 if duplicate and index == 64 else index + 1
        rows.append({"masterbot_id": index + 1, "logical_database_namespace": f"dreamco_division_{suffix:03d}"})
    path.write_text(json.dumps({"routes": rows}), encoding="utf-8")
    return path



class CursorContext:
    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc, tb):
        return False


class ConnectionContext:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self, cursor):
        self.cursor_context = CursorContext(cursor)

    def cursor(self):
        return self.cursor_context


class PostgresProbeTests(unittest.TestCase):
    def test_missing_dsn_is_blocked_without_connecting(self):
        connect = MagicMock()
        result = probe_postgres(dsn="", connect=connect)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["credentials_emitted"])
        connect.assert_not_called()

    def test_requires_exactly_65_unique_safe_namespaces(self):
        with tempfile.TemporaryDirectory() as temp:
            too_few = resource_map(Path(temp) / "few.json", count=64)
            with self.assertRaises(PostgresProbeError):
                load_expected_namespaces(too_few)
            duplicate = resource_map(Path(temp) / "duplicate.json", duplicate=True)
            with self.assertRaises(PostgresProbeError):
                load_expected_namespaces(duplicate)

    def test_success_verifies_all_namespaces_using_read_only_probe(self):
        with tempfile.TemporaryDirectory() as temp:
            mapping = resource_map(Path(temp) / "map.json")
            cursor = MagicMock()
            cursor.fetchone.return_value = ("dreamco", "dreamco_probe")
            cursor.fetchall.return_value = [(f"dreamco_division_{i:03d}",) for i in range(1, 66)]
            connection = FakeConnection(cursor)
            connect = MagicMock(return_value=ConnectionContext(connection))

            result = probe_postgres(dsn="postgresql://redacted", resource_map_path=mapping, connect=connect)

            self.assertEqual(result["status"], "CONNECTED_SCHEMAS_VERIFIED")
            self.assertEqual(result["verified_division_namespaces"], 65)
            self.assertFalse(result["checks"]["schema_creation_performed"])
            self.assertFalse(result["checks"]["application_data_modified"])
            self.assertNotIn("redacted", json.dumps(result))
            self.assertEqual(cursor.execute.call_args_list[0].args[0], "SET TRANSACTION READ ONLY")
            self.assertEqual(connect.call_args.kwargs["connect_timeout"], 5)

    def test_missing_namespace_is_incomplete_not_provisioned(self):
        with tempfile.TemporaryDirectory() as temp:
            mapping = resource_map(Path(temp) / "map.json")
            cursor = MagicMock()
            cursor.fetchone.return_value = ("dreamco", "probe")
            cursor.fetchall.return_value = [(f"dreamco_division_{i:03d}",) for i in range(1, 65)]
            connection = FakeConnection(cursor)
            connect = MagicMock(return_value=ConnectionContext(connection))

            result = probe_postgres(dsn="postgresql://secret", resource_map_path=mapping, connect=connect)

            self.assertEqual(result["status"], "CONNECTED_SCHEMA_INCOMPLETE")
            self.assertEqual(result["verified_division_namespaces"], 64)
            self.assertEqual(result["missing_division_namespaces"], ["dreamco_division_065"])

    def test_cli_output_file_is_valid_json_with_a_real_newline(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "evidence.json"
            with patch("sys.argv", ["postgres_probe", "--output", str(output)]), patch.dict("os.environ", {"DREAMCO_POSTGRES_DSN": "", "DATABASE_URL": ""}):
                self.assertEqual(main(), 2)
            raw = output.read_text(encoding="utf-8")
            self.assertTrue(raw.endswith("\n"))
            self.assertFalse(raw.endswith("\\n"))
            self.assertEqual(json.loads(raw)["status"], "BLOCKED")

    def test_connection_errors_do_not_leak_dsn_or_exception_text(self):
        def fail(*args, **kwargs):
            raise RuntimeError("failed to connect using postgresql://private-password")
        with tempfile.TemporaryDirectory() as temp:
            mapping = resource_map(Path(temp) / "map.json")
            with self.assertRaises(PostgresProbeError) as caught:
                probe_postgres(dsn="postgresql://private-password", resource_map_path=mapping, connect=fail)
            self.assertNotIn("private-password", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
