import json
import tempfile
import unittest
from pathlib import Path

from buddy.learning.dreamco_summary_source import (
    append_progress_event, resources_for_division, select_next_for_division,
)
from buddy.learning.study_resource_scheduler import Capability


class DreamCoSummarySourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.organization = self.root / "organization.json"
        self.progress = self.root / "progress.jsonl"
        package = {
            "asset_id": "asset-001",
            "division_ids": ["DreamAI"],
            "source": {"url": "https://example.org/guide", "revision": "rev-1"},
            "rights": {
                "study_permission": True,
                "summary_derivative_permission": True,
                "evaluation_permission": True,
                "training_permission": False,
                "evidence_ref": "rights-review-1",
            },
            "summary": {"executive_overview": "A DreamCo authored summary."},
            "study_path": {"sequence": [{"step": 1, "type": "read"}]},
            "assessment": {"knowledge_check_count": 5},
            "ownership": {"artifact_owner": "DreamCo-Technologies"},
            "training": {"weight_training_eligible": False},
        }
        self.organization.write_text(json.dumps({
            "schema": "dreamco.buddy_learning_organization.v1",
            "packages": [package],
            "division_curricula": [{"division": "DreamAI"}],
        }), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_summary_package_enters_existing_study_scheduler(self):
        resources = resources_for_division("DreamAI", self.organization)
        self.assertEqual(len(resources), 1)
        plan = select_next_for_division(
            "DreamAI", [Capability(name="AI", category="DreamAI")], self.organization
        )
        self.assertEqual(plan["asset_id"], "asset-001")
        self.assertEqual(plan["completion_status"], "queued_not_studied")
        self.assertEqual(len(plan["study_path"]["sequence"]), 1)
        self.assertFalse(plan["weight_training_eligible"])

    def test_unknown_division_and_missing_rights_fail_closed(self):
        with self.assertRaises(ValueError):
            resources_for_division("Unknown", self.organization)
        payload = json.loads(self.organization.read_text(encoding="utf-8"))
        payload["packages"][0]["rights"]["study_permission"] = False
        self.organization.write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual(resources_for_division("DreamAI", self.organization), [])

    def test_progress_is_append_only_jsonl_and_idempotency_is_not_assumed(self):
        event = append_progress_event(
            self.progress, asset_id="asset-001", division="DreamAI",
            event_type="study_started", evidence_ref="evidence:1", source_revision="rev-1"
        )
        lines = self.progress.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(json.loads(lines[0])["event_id"], event["event_id"])
        duplicate = append_progress_event(self.progress, asset_id="asset-001", division="DreamAI", event_type="study_started", evidence_ref="evidence:1", source_revision="rev-1")
        self.assertEqual(len(self.progress.read_text(encoding="utf-8").splitlines()), 1)
        self.assertEqual(duplicate["event_id"], event["event_id"])

    def test_training_events_require_explicit_permission(self):
        with self.assertRaises(PermissionError):
            append_progress_event(
                self.progress, asset_id="asset-001", division="DreamAI",
                event_type="training_run_started", evidence_ref="run:1"
            )
        with self.assertRaises(PermissionError):
            append_progress_event(
                self.progress, asset_id="asset-001", division="DreamAI",
                event_type="training_run_started", evidence_ref="run:2", organization_path=self.organization
            )
        payload = json.loads(self.organization.read_text(encoding="utf-8"))
        payload["packages"][0]["training"]["weight_training_eligible"] = True
        payload["packages"][0]["rights"]["training_permission"] = True
        self.organization.write_text(json.dumps(payload), encoding="utf-8")
        append_progress_event(
            self.progress, asset_id="asset-001", division="DreamAI",
            event_type="training_run_started", evidence_ref="run:3", organization_path=self.organization
        )

    def test_mastery_cannot_be_self_reported(self):
        with self.assertRaises(PermissionError):
            append_progress_event(
                self.progress, asset_id="asset-001", division="DreamAI",
                event_type="mastery_awarded", evidence_ref="claim:1"
            )


if __name__ == "__main__":
    unittest.main()
