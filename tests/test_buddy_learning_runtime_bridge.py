"""Integration tests: task runner -> private learning -> coaching -> SOP -> dashboard."""
import tempfile
import unittest
from pathlib import Path

from buddy.learning.runtime_bridge import BuddyLearningBridge, PrivateLearningStore
from dreamco_platform.automation.task_runner import BuddyTaskRunner


class ReadOnlyAdapter:
    name = "offline"
    def execute(self, task):
        return {"verified": True}


class FakeCapabilityAdapter:
    id = "fixture"
    revision = "1"
    def discover(self):
        from buddy.capabilities.runtime import Action
        return (Action("inspect", "Inspect a local fixture", "read_only"),)


class RuntimeBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = str(Path(self.temp.name) / "private.db")
        self.runner = BuddyTaskRunner()
        self.bridge = BuddyLearningBridge(PrivateLearningStore(self.path), self.runner)

    def completed(self, owner="alice"):
        task = self.runner.schedule(owner_user_id=owner, bot_slug="test-bot",
                                    objective="Verify this authorized offline test task")
        result = self.runner.run_due(ReadOnlyAdapter(), now=task.run_at + .01)[0]
        self.assertEqual(result["status"], "completed")
        return task, result

    def learn(self, task, result, **changes):
        params = dict(tenant_id=task.owner_user_id, task_id=task.task_id,
                      domain="technical", workflow="test-first", source_revision="r1",
                      result=result, capture_consent=True, redacted=True,
                      outcome_verified=True)
        params.update(changes)
        return self.bridge.learn_from_result(**params)

    def test_persistence_across_instances_and_dashboard(self):
        task, result = self.completed()
        self.learn(task, result)
        other = BuddyLearningBridge(PrivateLearningStore(self.path), self.runner)
        self.assertEqual(other.dashboard("alice", "technical")["learning_observations"], 1)
        self.assertEqual(other.dashboard("bob", "technical")["learning_observations"], 0)
        self.assertEqual(other.dashboard("alice", "technical")["task_counts"]["completed"], 1)

    def test_cannot_learn_from_other_tenant(self):
        task, result = self.completed("alice")
        with self.assertRaises(PermissionError):
            self.learn(task, result, tenant_id="bob")

    def test_consent_and_verified_result_required(self):
        task, result = self.completed()
        with self.assertRaises(PermissionError):
            self.learn(task, result, capture_consent=False)
        with self.assertRaises(ValueError):
            self.learn(task, result, outcome_verified=False)
        with self.assertRaises(ValueError):
            self.learn(task, {"status": "failed"})

    def test_coaching_and_sop_require_evidence(self):
        self.assertEqual(self.bridge.sop_candidates("alice", "technical"), [])
        for _ in range(3):
            task, result = self.completed()
            self.learn(task, result)
        self.assertEqual(len(self.bridge.sop_candidates("alice", "technical")), 1)
        self.assertEqual(self.bridge.sop_candidates("alice", "technical")[0]["steps"], [])
        self.assertFalse(self.bridge.coach("alice", "technical")["automated"])

    def test_library_knowledge_is_internal_first_and_network_off_by_default(self):
        result = self.bridge.library_knowledge("React", external_discovery=False)
        self.assertEqual(result["route"], "internal_knowledge_gap")
        self.assertTrue(result["internal"]["seed_candidate_matches"])
        self.assertFalse(result["external_discovery_performed"])
        self.assertFalse(result["external_model_call_performed"])

    def test_library_coverage_reports_guides_and_discovery_backlog_separately(self):
        report = self.bridge.library_coverage()
        self.assertEqual(report["seed_candidate_count"], 531)
        self.assertEqual(report["ecosystem_count"], 38)
        self.assertGreaterEqual(report["review_required_guide_count"], 1)
        self.assertFalse(report["worldwide_completeness_claimed"])

    def test_library_learning_queue_serves_internal_curriculum_without_mastery_claims(self):
        queue = self.bridge.library_learning_queue(
            division="DreamCodeLab", query="React", limit=10
        )
        self.assertEqual(queue["schema"], "dreamco.buddy_library_learning_queue.v1")
        self.assertGreaterEqual(queue["available_count"], 1)
        self.assertTrue(any("React" in item["title"] for item in queue["items"]))
        self.assertTrue(all(item["completion_status"] == "queued_not_studied" for item in queue["items"]))
        self.assertTrue(all(item["mastery_awarded"] is False for item in queue["items"]))
        self.assertFalse(queue["external_model_call_performed"])

    def test_library_learning_queue_contains_all_seed_and_ecosystem_lanes(self):
        queue = self.bridge.library_learning_queue(division="DreamCodeLab", limit=100)
        self.assertGreaterEqual(queue["available_count"], 569)
        self.assertEqual(queue["returned_count"], 100)

    def test_library_learning_queue_supports_masterbot_lanes(self):
        queue = self.bridge.library_learning_queue(
            masterbot="DreamCodeLab", query="React", limit=5
        )
        self.assertEqual(queue["masterbot"], "DreamCodeLab")
        self.assertGreaterEqual(queue["returned_count"], 1)

    def test_library_learning_queue_requires_exactly_one_owner(self):
        with self.assertRaises(ValueError):
            self.bridge.library_learning_queue(query="React")
        with self.assertRaises(ValueError):
            self.bridge.library_learning_queue(division="DreamCodeLab", masterbot="DreamCodeLab")
        with self.assertRaises(ValueError):
            self.bridge.library_learning_queue(division="DreamCodeLab", limit=101)

    def test_library_gap_persistence_requires_redaction(self):
        with self.assertRaises(PermissionError):
            self.bridge.library_knowledge("React", persist_gap=True, query_is_redacted=False)
        result = self.bridge.library_knowledge(
            "React", persist_gap=True, query_is_redacted=True, gap_root=Path(self.temp.name)
        )
        self.assertTrue(result["gap_recorded"])
        self.assertTrue((Path(self.temp.name) / ".dreamco/library-knowledge-gaps.jsonl").exists())

    def test_adapter_registration_requires_review(self):
        adapter = FakeCapabilityAdapter()
        with self.assertRaises(PermissionError):
            self.bridge.discover_adapter(adapter, evidence_id="e1", tested=False, approved=True)
        self.bridge.discover_adapter(adapter, evidence_id="e1", tested=True, approved=True)
        self.assertEqual(self.bridge.capabilities.propose("inspect", ["inspect"])["missing"], [])

    def test_model_route_uses_measured_holdout(self):
        result = self.bridge.model_route_report("alice", "technical", [
            {"model": "model-a", "baseline": [.5]*3, "candidate": [.9]*3, "holdout": [.8]*3},
            {"model": "model-b", "baseline": [.5]*3, "candidate": [.6]*3, "holdout": [.2]*3},
        ])
        self.assertEqual(result["eligible"][0]["model"], "model-a")
        self.assertFalse(result["provider_called"])

    def test_supervised_project_proposal_does_not_schedule(self):
        proposal = self.bridge.propose_supervised_project("alice", "test-bot",
                                                         "Complete a long running project")
        self.assertFalse(proposal["scheduled"])
        self.assertEqual(self.runner.dashboard()["tasks"], [])

    def test_private_database_uses_restricted_file_permissions(self):
        self.assertTrue(Path(self.path).parent.is_dir())
        if __import__("os").name == "posix":
            self.assertEqual(Path(self.path).stat().st_mode & 0o777, 0o600)

    def test_forget_deletes_private_records(self):
        task, result = self.completed()
        self.learn(task, result)
        self.assertEqual(self.bridge.store.forget("alice"), 1)
        self.assertEqual(self.bridge.coach("alice", "technical")["observations"], 0)


if __name__ == "__main__":
    unittest.main()
