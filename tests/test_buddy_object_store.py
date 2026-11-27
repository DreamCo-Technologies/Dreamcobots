import hashlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from buddy.storage.object_store import (
    ObjectStoreError,
    run_division_object_store_healthcheck,
    run_object_store_healthcheck,
    upload_approved_division_dataset,
)


class FakeS3:
    def __init__(self, *, versioning=True, encryption=True, public=True, retention=30):
        self.versioning = versioning
        self.encryption = encryption
        self.public = public
        self.retention = retention
        self.objects = {}
        self.metadata = {}
        self.copies = []
        self.sequence = 0

    def get_bucket_versioning(self, Bucket):
        return {"Status": "Enabled" if self.versioning else "Suspended"}

    def get_bucket_encryption(self, Bucket):
        rules = (
            [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
            if self.encryption
            else []
        )
        return {"ServerSideEncryptionConfiguration": {"Rules": rules}}

    def get_public_access_block(self, Bucket):
        keys = ("BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets")
        return {"PublicAccessBlockConfiguration": {key: self.public for key in keys}}

    def get_bucket_lifecycle_configuration(self, Bucket):
        rules = [{"Expiration": {"Days": self.retention}}] if self.retention else []
        return {"Rules": rules}

    def put_object(self, Bucket, Key, Body, Metadata=None):
        self.sequence += 1
        data = Body.read() if hasattr(Body, "read") else Body
        self.objects[(Bucket, Key)] = data
        self.metadata[(Bucket, Key)] = Metadata or {}
        return {"VersionId": f"v{self.sequence}"}

    def head_object(self, Bucket, Key, VersionId=None):
        body = self.objects[(Bucket, Key)]
        return {"ServerSideEncryption": "AES256", "ContentLength": len(body), "Metadata": self.metadata.get((Bucket, Key), {})}

    def get_object(self, Bucket, Key, VersionId=None):
        return {"Body": io.BytesIO(self.objects[(Bucket, Key)])}

    def copy_object(self, Bucket, Key, CopySource):
        source = (CopySource["Bucket"], CopySource["Key"])
        self.objects[(Bucket, Key)] = self.objects[source]
        self.copies.append((source, (Bucket, Key)))
        self.sequence += 1
        return {"VersionId": f"v{self.sequence}"}


class ObjectStoreHealthTests(unittest.TestCase):
    def test_configuration_without_canary_is_not_reported_healthy_or_written(self):
        client = FakeS3()
        evidence = run_object_store_healthcheck(
            client=client,
            primary_bucket="dreamco-primary",
            backup_bucket="dreamco-backup",
        )
        self.assertEqual(evidence["status"], "CONFIGURED_NOT_VALIDATED")
        self.assertEqual(evidence["backup_restore_test"], "NOT_RUN")
        self.assertEqual(client.objects, {})
        self.assertFalse(evidence["credentials_emitted"])

    def test_canary_proves_primary_backup_and_restore_readback(self):
        client = FakeS3()
        evidence = run_object_store_healthcheck(
            client=client,
            primary_bucket="dreamco-primary",
            backup_bucket="dreamco-backup",
            allow_canary=True,
        )
        self.assertEqual(evidence["status"], "HEALTHY")
        self.assertEqual(evidence["backup_restore_test"], "PASS")
        self.assertTrue(evidence["encryption_at_rest"])
        self.assertTrue(evidence["versioning_enabled"])
        self.assertTrue(evidence["public_access_blocked"])
        self.assertEqual(len(client.copies), 2)
        primary = client.objects[("dreamco-primary", evidence["primary_canary_key"])]
        backup = client.objects[("dreamco-backup", evidence["backup_canary_key"])]
        restored = client.objects[("dreamco-primary", evidence["restore_canary_key"])]
        self.assertEqual(primary, backup)
        self.assertEqual(backup, restored)
        self.assertFalse(evidence["credentials_emitted"])
        self.assertFalse(evidence["canary_payload_contains_secrets"])

    def test_environment_opt_in_enables_only_the_generated_canary(self):
        client = FakeS3()
        with patch.dict(os.environ, {"DREAMCO_ALLOW_OBJECT_STORE_CANARY": "1"}, clear=True):
            evidence = run_object_store_healthcheck(
                client=client,
                primary_bucket="dreamco-primary",
                backup_bucket="dreamco-backup",
            )
        self.assertEqual(evidence["status"], "HEALTHY")
        self.assertEqual(evidence["backup_restore_test"], "PASS")

    def test_missing_security_or_backup_retention_fails_closed(self):
        clients = (
            FakeS3(versioning=False),
            FakeS3(encryption=False),
            FakeS3(public=False),
            FakeS3(retention=0),
        )
        for client in clients:
            with self.subTest(client=client):
                evidence = run_object_store_healthcheck(
                    client=client,
                    primary_bucket="dreamco-primary",
                    backup_bucket="dreamco-backup",
                    allow_canary=True,
                )
                self.assertEqual(evidence["status"], "BLOCKED")
                self.assertEqual(evidence["backup_restore_test"], "NOT_RUN")
                self.assertEqual(client.objects, {})

    def test_distinct_valid_buckets_are_required(self):
        with self.assertRaisesRegex(ObjectStoreError, "distinct_valid"):
            run_object_store_healthcheck(
                client=FakeS3(),
                primary_bucket="dreamco-primary",
                backup_bucket="dreamco-primary",
            )

    def test_invalid_s3_bucket_name_forms_are_rejected(self):
        for invalid in ("dreamco..primary", "dreamco.-backup", "192.168.1.1"):
            with self.subTest(bucket=invalid):
                with self.assertRaisesRegex(ObjectStoreError, "distinct_valid"):
                    run_object_store_healthcheck(
                        client=FakeS3(),
                        primary_bucket=invalid,
                        backup_bucket="dreamco-backup",
                    )

    def test_invalid_prefix_is_rejected_before_any_write(self):
        client = FakeS3()
        with self.assertRaisesRegex(ObjectStoreError, "prefix_is_invalid"):
            run_object_store_healthcheck(
                client=client,
                primary_bucket="dreamco-primary",
                backup_bucket="dreamco-backup",
                prefix="../escape",
                allow_canary=True,
            )
        self.assertEqual(client.objects, {})

    def test_prefix_rejects_ambiguous_slash_forms(self):
        for invalid in ("/absolute", "prefix/", "prefix//nested"):
            with self.subTest(prefix=invalid):
                with self.assertRaisesRegex(ObjectStoreError, "prefix_is_invalid"):
                    run_object_store_healthcheck(
                        client=FakeS3(),
                        primary_bucket="dreamco-primary",
                        backup_bucket="dreamco-backup",
                        prefix=invalid,
                        allow_canary=True,
                    )

    def test_division_healthcheck_uses_isolated_prefix(self):
        evidence = run_division_object_store_healthcheck(
            7,
            client=FakeS3(),
            primary_bucket="dreamco-primary",
            backup_bucket="dreamco-backup",
            allow_canary=True,
        )
        self.assertEqual(evidence["masterbot_id"], 7)
        self.assertIn("/divisions/007/", evidence["primary_canary_key"])

    def test_invalid_division_id_is_rejected(self):
        for value in (0, 66, True, "7"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ObjectStoreError, "masterbot_id"):
                    run_division_object_store_healthcheck(
                        value,
                        client=FakeS3(),
                        primary_bucket="dreamco-primary",
                        backup_bucket="dreamco-backup",
                    )

    def test_bucket_and_prefix_inputs_must_be_strings(self):
        with self.assertRaisesRegex(ObjectStoreError, "must_be_strings"):
            run_object_store_healthcheck(
                client=FakeS3(),
                primary_bucket=123,
                backup_bucket="dreamco-backup",
            )

    def test_canary_flag_must_be_boolean(self):
        with self.assertRaisesRegex(ObjectStoreError, "allow_canary_must_be_boolean"):
            run_object_store_healthcheck(
                client=FakeS3(),
                primary_bucket="dreamco-primary",
                backup_bucket="dreamco-backup",
                allow_canary="yes",
            )


    def _approved_dataset_card(self, source: Path) -> dict:
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        return {
            "dataset_id": "finance.dataset", "version": 1, "content_sha256": digest,
            "training_approved": True, "rights_status": "VERIFIED",
            "data_plane": "dreamco_owned_training", "holdout": False,
            "training_status": "APPROVED_PENDING_TRAINING",
            "rights_evidence": "approved-authorship-register:finance-fixture",
            "owner_approval_id": "OWNER-APPROVAL-FINANCE-001", "primary_masterbot_id": 41,
            "quality": {"quality_status": "STRUCTURE_CHECKS_PASSED", "pii_review_required": False},
            "split_manifest": {"train_sha256": "a" * 64, "validation_sha256": "b" * 64, "test_sha256": "c" * 64},
        }

    def test_upload_persists_only_registered_rights_approved_dataset(self):
        client = FakeS3()
        payload = b'{"masterbot_id":41,"text":"safe"}\\n'
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "train.jsonl"
            source.write_bytes(payload)
            card = self._approved_dataset_card(source)
            with patch.dict(os.environ, {"DREAMCO_ALLOW_DATASET_OBJECT_UPLOAD": "1"}, clear=True):
                evidence = upload_approved_division_dataset(41, card, str(source), "UPLOAD-APPROVAL-2026-001", client=client, bucket="dreamco-primary")
        self.assertEqual(evidence["status"], "PERSISTED")
        self.assertEqual(evidence["training_status"], "APPROVED_PENDING_TRAINING")
        self.assertFalse(evidence["weights_trained"])
        self.assertFalse(evidence["credentials_emitted"])
        self.assertIn("/divisions/041/", evidence["object_key"])
        self.assertEqual(client.objects[("dreamco-primary", evidence["object_key"])], payload)
        self.assertEqual(client.metadata[("dreamco-primary", evidence["object_key"])]["owner-approval-ref"], "OWNER-APPROVAL-FINANCE-001")

    def test_upload_requires_opt_in_and_rights_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "train.jsonl"
            source.write_bytes(b"safe dataset")
            card = self._approved_dataset_card(source)
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(ObjectStoreError, "ALLOW_DATASET_OBJECT_UPLOAD"):
                    upload_approved_division_dataset(41, card, str(source), "UPLOAD-001", client=FakeS3(), bucket="dreamco-primary")
            with patch.dict(os.environ, {"DREAMCO_ALLOW_DATASET_OBJECT_UPLOAD": "1"}, clear=True):
                with self.assertRaisesRegex(ObjectStoreError, "training_approval_required"):
                    upload_approved_division_dataset(41, {**card, "training_approved": False}, str(source), "UPLOAD-001", client=FakeS3(), bucket="dreamco-primary")
                holdout = {**card, "holdout": True, "data_plane": "evaluation_only_holdout"}
                with self.assertRaisesRegex(ObjectStoreError, "training_eligible_data_plane"):
                    upload_approved_division_dataset(41, holdout, str(source), "UPLOAD-001", client=FakeS3(), bucket="dreamco-primary")

    def test_upload_requires_matching_owner_hash_and_split_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "train.jsonl"
            source.write_bytes(b"safe dataset")
            card = self._approved_dataset_card(source)
            with patch.dict(os.environ, {"DREAMCO_ALLOW_DATASET_OBJECT_UPLOAD": "1"}, clear=True):
                with self.assertRaisesRegex(ObjectStoreError, "primary_masterbot_mismatch"):
                    upload_approved_division_dataset(42, card, str(source), "UPLOAD-001", client=FakeS3(), bucket="dreamco-primary")
                with self.assertRaisesRegex(ObjectStoreError, "content_hash_mismatch"):
                    upload_approved_division_dataset(41, {**card, "content_sha256": "0" * 64}, str(source), "UPLOAD-001", client=FakeS3(), bucket="dreamco-primary")
                with self.assertRaisesRegex(ObjectStoreError, "split_manifest_hashes_required"):
                    upload_approved_division_dataset(41, {**card, "split_manifest": {}}, str(source), "UPLOAD-001", client=FakeS3(), bucket="dreamco-primary")

    def test_upload_requires_upload_approval_and_secure_bucket(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "train.jsonl"
            source.write_bytes(b"safe dataset")
            card = self._approved_dataset_card(source)
            with patch.dict(os.environ, {"DREAMCO_ALLOW_DATASET_OBJECT_UPLOAD": "1"}, clear=True):
                with self.assertRaisesRegex(ObjectStoreError, "upload_approval_id_required"):
                    upload_approved_division_dataset(41, card, str(source), " ", client=FakeS3(), bucket="dreamco-primary")
                with self.assertRaisesRegex(ObjectStoreError, "bucket_security_configuration_incomplete"):
                    upload_approved_division_dataset(41, card, str(source), "UPLOAD-001", client=FakeS3(encryption=False), bucket="dreamco-primary")
if __name__ == "__main__":
    unittest.main()
