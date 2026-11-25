import json
import tempfile
import unittest
from pathlib import Path

from buddy.learning.dreamco_summary_source import (
    append_progress_event, execute_study_plan, resources_for_division, select_next_for_division,
)
from buddy.learning.permissioned_study_worker import StudyAuthorization
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
            "source": {"source_id": "example/guide", "url": "https://example.org/guide", "revision": "rev-1"},
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
        self.assertEqual(plan["source"]["source_id"], "example/guide")
        self.assertEqual(plan["source"]["url"], "https://example.org/guide")
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

    def test_progress_is_append_only_jsonl_and_idempotent(self):
        event = append_progress_event(
            self.progress, asset_id="asset-001", division="DreamAI",
            event_type="study_started", evidence_ref="evidence:1", source_revision="rev-1", organization_path=self.organization
        )
        lines = self.progress.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(json.loads(lines[0])["event_id"], event["event_id"])
        duplicate = append_progress_event(self.progress, asset_id="asset-001", division="DreamAI", event_type="study_started", evidence_ref="evidence:1", source_revision="rev-1", organization_path=self.organization)
        self.assertEqual(len(self.progress.read_text(encoding="utf-8").splitlines()), 1)
        self.assertEqual(duplicate["event_id"], event["event_id"])

    def test_training_events_require_explicit_permission(self):
        with self.assertRaises(PermissionError):
            append_progress_event(
                self.progress, asset_id="asset-001", division="DreamAI",
                event_type="training_run_started", evidence_ref="run:1", organization_path=self.organization
            )
        payload = json.loads(self.organization.read_text(encoding="utf-8"))
        payload["packages"][0]["training"]["weight_training_eligible"] = True
        payload["packages"][0]["rights"]["training_permission"] = True
        self.organization.write_text(json.dumps(payload), encoding="utf-8")
        append_progress_event(
            self.progress, asset_id="asset-001", division="DreamAI",
            event_type="training_run_started", evidence_ref="run:3", organization_path=self.organization
        )


    def test_approved_summary_executes_read_only_and_records_evidence(self):
        plan = select_next_for_division(
            "DreamAI", [Capability(name="AI", category="DreamAI")], self.organization
        )
        selected_source = plan["source"]
        self.assertEqual(selected_source["url"], "https://example.org/guide")
        authorization = StudyAuthorization(
            source_name=selected_source["source_id"],
            source_url=selected_source["url"],
            review_status="approved",
            allowed_operations=frozenset({"open_official_page"}),
            evidence_ref="rights-review-1",
        )
        result = execute_study_plan(
            plan,
            authorization,
            lambda selected, context: {
                "evidence_ref": "study-run:1",
                "lesson_status": "verified_pass",
                "independent_evaluator_id": "independent-test-runner",
                "lesson_evidence_ref": "lesson:1",
                "knowledge_check_evidence_ref": "quiz:1",
                "knowledge_check_score": 0.95,
                "exercise_status": "verified_pass",
                "exercise_evidence_ref": "exercise:1",
                "capstone_evidence_ref": "capstone-submit:1",
                "capstone_status": "verified_pass",
                "capstone_pass_evidence_ref": "capstone-pass:1",
            },
            self.root / "workspace",
            self.progress,
            self.organization,
        )
        self.assertEqual(result["completion_status"], "lesson_completed_with_evidence")
        self.assertFalse(result["model_training_performed"])
        self.assertTrue(result["temporary_workspace_erased"])
        events = [json.loads(line) for line in self.progress.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([x["event_type"] for x in events], ["study_started", "lesson_completed", "knowledge_check_submitted", "exercise_passed", "capstone_submitted", "capstone_passed"])
        self.assertEqual(events[2]["score"], 0.95)

    def test_summary_execution_rejects_mismatched_rights_and_write_operations(self):
        plan = select_next_for_division(
            "DreamAI", [Capability(name="AI", category="DreamAI")], self.organization
        )
        selected_source = plan["source"]
        mismatched = StudyAuthorization(
            source_name=selected_source["source_id"],
            source_url=selected_source["url"],
            review_status="approved",
            allowed_operations=frozenset({"open_official_page"}),
            evidence_ref="wrong-evidence",
        )
        with self.assertRaises(PermissionError):
            execute_study_plan(plan, mismatched, lambda *_: {}, self.root / "workspace", self.progress, self.organization)
        write_access = StudyAuthorization(
            source_name=selected_source["source_id"],
            source_url=selected_source["url"],
            review_status="approved",
            allowed_operations=frozenset({"open_official_page", "download_media"}),
            evidence_ref="rights-review-1",
        )
        with self.assertRaises(PermissionError):
            execute_study_plan(plan, write_access, lambda *_: {}, self.root / "workspace", self.progress, self.organization)

    def test_mastery_cannot_be_self_reported(self):
        with self.assertRaises(PermissionError):
            append_progress_event(
                self.progress, asset_id="asset-001", division="DreamAI",
                event_type="mastery_awarded", evidence_ref="claim:1", organization_path=self.organization
            )


if __name__ == "__main__":
    unittest.main()
