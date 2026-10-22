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

    def test_forget_deletes_private_records(self):
        task, result = self.completed()
        self.learn(task, result)
        self.assertEqual(self.bridge.store.forget("alice"), 1)
        self.assertEqual(self.bridge.coach("alice", "technical")["observations"], 0)


if __name__ == "__main__":
    unittest.main()
