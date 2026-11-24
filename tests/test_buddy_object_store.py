import io
import os
import unittest
from unittest.mock import patch

from buddy.storage.object_store import (
    ObjectStoreError,
    run_division_object_store_healthcheck,
    run_object_store_healthcheck,
)


class FakeS3:
    def __init__(self, *, versioning=True, encryption=True, public=True, retention=30):
        self.versioning = versioning
        self.encryption = encryption
        self.public = public
        self.retention = retention
        self.objects = {}
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

    def put_object(self, Bucket, Key, Body):
        self.sequence += 1
        self.objects[(Bucket, Key)] = Body
        return {"VersionId": f"v{self.sequence}"}

    def head_object(self, Bucket, Key):
        body = self.objects[(Bucket, Key)]
        return {"ServerSideEncryption": "AES256", "ContentLength": len(body)}

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


if __name__ == "__main__":
    unittest.main()
