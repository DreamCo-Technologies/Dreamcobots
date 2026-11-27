import hashlib
import json
import unittest
from unittest.mock import MagicMock, patch

from buddy.datasets.postgres_catalog import (
    PostgresCatalogError, PostgresDatasetCatalog, division_schema,
)


def manifest(**overrides):
    value = {
        "dataset_id": "demo.dataset", "version": 1, "name": "Demo",
        "owner": "DreamCo", "license": "CC-BY-4.0",
        "license_url": "https://example.org/license", "source_url": "https://example.org/data",
        "data_plane": "licensed_training", "rights_status": "VERIFIED",
        "training_approved": True, "rights_evidence": "review-123",
        "primary_masterbot_id": 1, "content_sha256": "a" * 64,
    }
    value.update(overrides)
    return value


class PostgresCatalogTests(unittest.TestCase):
    def test_schema_is_canonical(self):
        self.assertEqual(division_schema(1), "dreamco_division_001")
        self.assertEqual(division_schema(65), "dreamco_division_065")

    def test_rejects_invalid_division_and_identifier(self):
        for value in (0, 66, True, "1"):
            with self.assertRaises(PostgresCatalogError):
                division_schema(value)
        with self.assertRaises(PostgresCatalogError):
            PostgresDatasetCatalog(dsn="postgresql://safe", masterbot_id=1, connect=lambda *_a, **_k: None).get(1, "x; DROP TABLE", 1)

    def test_requires_division_scoped_dsn(self):
        catalog = PostgresDatasetCatalog(masterbot_id=1, connect=MagicMock(), dsn_resolver=lambda _id: None)
        with self.assertRaisesRegex(PostgresCatalogError, "DSN_MASTERBOT_001"):
            catalog.register(1, manifest())

    def test_direct_dsn_requires_fixed_division_identity(self):
        with self.assertRaisesRegex(PostgresCatalogError, "bound to one canonical"):
            PostgresDatasetCatalog(dsn="postgresql://shared", connect=MagicMock())

    def test_adapter_cannot_cross_division_boundary(self):
        connect = MagicMock()
        catalog = PostgresDatasetCatalog(dsn="postgresql://division-001", masterbot_id=1, connect=connect)
        with self.assertRaisesRegex(PostgresCatalogError, "different MasterBot"):
            catalog.get(2, "demo.dataset", 1)
        connect.assert_not_called()

    def test_environment_resolver_uses_division_specific_dsn(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = ("demo.dataset", 1, "b" * 64)
        connection = MagicMock()
        connection.cursor.return_value.__enter__.return_value = cursor
        connect = MagicMock()
        connect.return_value.__enter__.return_value = connection
        with patch.dict("os.environ", {"DREAMCO_POSTGRES_DSN_MASTERBOT_001":"postgresql://division-001"}, clear=True):
            catalog = PostgresDatasetCatalog(masterbot_id=1, connect=connect)
            catalog.register(1, manifest())
        self.assertEqual(connect.call_args.args[0], "postgresql://division-001")

    def test_get_uses_division_specific_environment_dsn(self):
        payload = manifest(training_approved=False)
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        cursor = MagicMock()
        cursor.fetchone.return_value = (payload, digest)
        connection = MagicMock()
        connection.cursor.return_value.__enter__.return_value = cursor
        connect = MagicMock()
        connect.return_value.__enter__.return_value = connection
        with patch.dict("os.environ", {"DREAMCO_POSTGRES_DSN_MASTERBOT_001":"postgresql://division-001"}, clear=True):
            catalog = PostgresDatasetCatalog(masterbot_id=1, connect=connect)
            result = catalog.get(1, "demo.dataset", 1)
        self.assertEqual(result["dataset_id"], "demo.dataset")
        self.assertEqual(connect.call_args.args[0], "postgresql://division-001")

    def test_training_manifest_requires_rights_and_owner(self):
        for changed in (
            {"rights_status": "UNVERIFIED"},
            {"rights_evidence": ""},
            {"primary_masterbot_id": 2},
            {"data_plane": "public_reference_and_retrieval"},
        ):
            with self.subTest(changed=changed), self.assertRaises(PostgresCatalogError):
                PostgresDatasetCatalog(dsn="postgresql://safe", masterbot_id=1, connect=lambda *_a, **_k: None).register(1, manifest(**changed))

    def test_register_persists_metadata_and_redacts_credentials(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = ("demo.dataset", 1, "b" * 64)
        connection = MagicMock()
        connection.cursor.return_value.__enter__.return_value = cursor
        connect = MagicMock()
        connect.return_value.__enter__.return_value = connection
        catalog = PostgresDatasetCatalog(dsn="postgresql://secret", masterbot_id=1, connect=connect)
        result = catalog.register(1, manifest(token="never-store", raw_data="never-store"))
        self.assertEqual(result["status"], "PERSISTED")
        self.assertFalse(result["credentials_emitted"])
        scope_args = cursor.execute.call_args_list[0].args
        self.assertIn("set_config('dreamco.masterbot_id'", scope_args[0])
        self.assertEqual(scope_args[1], ("1",))
        args = cursor.execute.call_args.args
        self.assertIn('"dreamco_division_001".dataset_catalog', args[0])
        self.assertNotIn("never-store", args[1][3])

    def test_register_rejects_immutable_version_conflict(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        connection = MagicMock()
        connection.cursor.return_value.__enter__.return_value = cursor
        connect = MagicMock()
        connect.return_value.__enter__.return_value = connection
        catalog = PostgresDatasetCatalog(dsn="postgresql://safe", masterbot_id=1, connect=connect)
        with self.assertRaises(PostgresCatalogError):
            catalog.register(1, manifest())

    def test_get_verifies_manifest_hash(self):
        payload = manifest(training_approved=False)
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        cursor = MagicMock()
        cursor.fetchone.return_value = (payload, digest)
        connection = MagicMock()
        connection.cursor.return_value.__enter__.return_value = cursor
        connect = MagicMock()
        connect.return_value.__enter__.return_value = connection
        result = PostgresDatasetCatalog(dsn="postgresql://safe", masterbot_id=1, connect=connect).get(1, "demo.dataset", 1)
        self.assertEqual(result["dataset_id"], "demo.dataset")
        scope_args = cursor.execute.call_args_list[0].args
        self.assertIn("set_config('dreamco.masterbot_id'", scope_args[0])
        self.assertEqual(scope_args[1], ("1",))

    def test_get_rejects_tampered_manifest(self):
        payload = manifest(training_approved=False)
        cursor = MagicMock()
        cursor.fetchone.return_value = (payload, "0" * 64)
        connection = MagicMock()
        connection.cursor.return_value.__enter__.return_value = cursor
        connect = MagicMock()
        connect.return_value.__enter__.return_value = connection
        with self.assertRaises(PostgresCatalogError):
            PostgresDatasetCatalog(dsn="postgresql://safe", masterbot_id=1, connect=connect).get(1, "demo.dataset", 1)


if __name__ == "__main__":
    unittest.main()
