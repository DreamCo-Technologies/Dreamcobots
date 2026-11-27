import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.validate_dreamco_resource_registry import validate


def sample(**updates):
    item = {
        "id": "X",
        "name": "source",
        "category": "test",
        "resource_type": "dataset",
        "acquisition_status": "NOT_ACQUIRED",
        "license_status": "UNVERIFIED",
        "commercial_training_permission": "NOT_ESTABLISHED",
        "quarantine_status": "BLOCKED_PENDING_REVIEW",
        "source_provenance_required": True,
        "sha256_required": True,
    }
    item.update(updates)
    return item


def approved_sample(root):
    snapshot = root / "data" / "source.jsonl"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_text('{"example":"synthetic"}\n', encoding="utf-8")
    digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    return sample(
        acquisition_status="ACQUIRED",
        license_status="VERIFIED",
        commercial_training_permission="APPROVED",
        quarantine_status="APPROVED_FOR_TRAINING",
        license_evidence="reviewed-license-record",
        source_url="https://example.org/data",
        snapshot_path="data/source.jsonl",
        snapshot_sha256=digest,
        reviewed_by="reviewer",
        privacy_review="PASSED",
        retention_evidence="approved-retention-record",
    )


class ResourceRegistryTests(unittest.TestCase):
    def test_unknown_rights_are_validly_blocked(self):
        self.assertEqual(validate({"resource_count": 1, "resources": [sample()]}, expected_count=1), [])

    def test_training_approval_without_evidence_is_rejected(self):
        item = sample(
            acquisition_status="ACQUIRED",
            license_status="VERIFIED",
            commercial_training_permission="APPROVED",
            quarantine_status="APPROVED_FOR_TRAINING",
        )
        self.assertTrue(validate({"resource_count": 1, "resources": [item]}, expected_count=1))

    def test_training_approval_requires_snapshot_rights_privacy_and_retention_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item = approved_sample(root)
            self.assertEqual(validate({"resource_count": 1, "resources": [item]}, expected_count=1, root=root), [])

    def test_missing_privacy_or_retention_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item = approved_sample(root)
            item.pop("privacy_review")
            item.pop("retention_evidence")
            errors = validate({"resource_count": 1, "resources": [item]}, expected_count=1, root=root)
            self.assertTrue(any("privacy/PII review" in error for error in errors))
            self.assertTrue(any("approval evidence incomplete" in error for error in errors))

    def test_snapshot_hash_must_match_local_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item = approved_sample(root)
            item["snapshot_sha256"] = "0" * 64
            self.assertTrue(any(
                "snapshot hash does not match" in error
                for error in validate({"resource_count": 1, "resources": [item]}, expected_count=1, root=root)
            ))

    def test_snapshot_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item = approved_sample(root)
            item["snapshot_path"] = "../source.jsonl"
            self.assertTrue(any(
                "snapshot_path must resolve" in error
                for error in validate({"resource_count": 1, "resources": [item]}, expected_count=1, root=root)
            ))

    def test_rights_approval_alone_does_not_open_quarantine(self):
        item = sample(license_status="VERIFIED", license_evidence="license", commercial_training_permission="APPROVED")
        self.assertTrue(validate({"resource_count": 1, "resources": [item]}, expected_count=1))

    def test_registry_rejects_wrong_count(self):
        self.assertTrue(validate({"resource_count": 0, "resources": []}))


if __name__ == "__main__":
    unittest.main()
