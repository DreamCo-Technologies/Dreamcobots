import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.build_buddy_teacher_authoring_queue import asset_key, build_work_orders


class BuddyTeacherAuthoringQueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bundles = self.root / "bundles"
        self.bundles.mkdir()
        self.item = {
            "source_type": "github_repository",
            "source_id": "owner/repo",
            "url": "https://github.com/owner/repo",
            "revision": "abc123",
            "status": "guide_authoring_eligible",
            "rights_evidence_ref": "rights-review-1",
        }
        self.queue = {"schema": "dreamco.buddy_source_study_queue.v1", "queue": [self.item]}

    def tearDown(self):
        self.temp.cleanup()

    def test_rights_pending_sources_never_get_authoring_work_orders(self):
        item = {**self.item, "status": "rights_pending"}
        result = build_work_orders({"schema": self.queue["schema"], "queue": [item]}, self.bundles)
        order = result["work_orders"][0]
        self.assertEqual(order["status"], "blocked_rights_pending")
        self.assertIn("not explicitly rights-cleared", order["blocked_reasons"][0])

    def test_missing_full_source_bundle_blocks_metadata_only_item(self):
        result = build_work_orders(self.queue, self.bundles)
        self.assertEqual(result["work_orders"][0]["status"], "blocked_source_bundle_missing")

    def test_valid_bundle_creates_teacher_work_order_but_not_approved_guide(self):
        key = asset_key(self.item)
        content = ("Authorized full source content with section locators. " * 20).encode()
        content_path = self.bundles / f"{key}.content.md"
        content_path.write_bytes(content)
        manifest = {
            "schema": "dreamco.authorized_source_bundle.v1",
            "source": {k: self.item[k] for k in ("source_type", "source_id", "url", "revision")},
            "rights": {
                "study_permission": True,
                "summary_derivative_permission": True,
                "evaluation_permission": True,
                "evidence_ref": "rights-review-1",
            },
            "content_sha256": hashlib.sha256(content).hexdigest(),
        }
        (self.bundles / f"{key}.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        result = build_work_orders(self.queue, self.bundles)
        order = result["work_orders"][0]
        self.assertEqual(order["status"], "ready_for_teacher_authoring")
        self.assertEqual(order["teacher"], "ChatGPT/GPT-6")
        self.assertEqual(order["student"], "Buddy")
        self.assertIn("needs_review", " ".join(order["instructions"]))
        self.assertEqual(result["counts"]["ready_for_teacher_authoring"], 1)

    def test_hash_or_revision_mismatch_blocks_work_order(self):
        key = asset_key(self.item)
        content = b"Authorized content " * 40
        (self.bundles / f"{key}.content.md").write_bytes(content)
        manifest = {
            "schema": "dreamco.authorized_source_bundle.v1",
            "source": {**{k: self.item[k] for k in ("source_type", "source_id", "url", "revision")}, "revision": "wrong"},
            "rights": {
                "study_permission": True,
                "summary_derivative_permission": True,
                "evaluation_permission": True,
                "evidence_ref": "rights-review-1",
            },
            "content_sha256": "0" * 64,
        }
        (self.bundles / f"{key}.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        order = build_work_orders(self.queue, self.bundles)["work_orders"][0]
        self.assertEqual(order["status"], "blocked_bundle_validation_failed")
        self.assertTrue(any("revision" in reason for reason in order["blocked_reasons"]))
        self.assertTrue(any("hash mismatch" in reason for reason in order["blocked_reasons"]))

    def test_wrong_queue_schema_fails_closed(self):
        with self.assertRaises(ValueError):
            build_work_orders({"schema": "wrong", "queue": []}, self.bundles)


if __name__ == "__main__":
    unittest.main()
