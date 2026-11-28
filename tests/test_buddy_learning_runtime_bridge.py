"""Integration tests: task runner -> private learning -> coaching -> SOP -> dashboard."""
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from buddy.learning.runtime_bridge import BuddyLearningBridge, PrivateLearningStore
from buddy.learning.course_track_registry import CourseLesson, load_course_lessons
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

    def test_library_knowledge_never_performs_external_discovery(self):
        result = self.bridge.library_knowledge("React", external_discovery=True)
        self.assertEqual(result["route"], "internal_knowledge_gap")
        self.assertFalse(result["external_discovery_performed"])
        self.assertFalse(result["external_model_call_performed"])

    def test_library_coverage_reports_guides_and_discovery_backlog_separately(self):
        report = self.bridge.library_coverage()
        self.assertEqual(report["seed_candidate_count"], 531)
        self.assertEqual(report["ecosystem_count"], 38)
        self.assertGreaterEqual(report["review_required_guide_count"], 1)
        self.assertFalse(report["worldwide_completeness_claimed"])

    def test_library_learning_queue_serves_dreamco_curriculum_with_owner_review_gate(self):
        queue = self.bridge.library_learning_queue(
            division="DreamCodeLab", query="task", limit=10
        )
        self.assertEqual(queue["schema"], "dreamco.buddy_library_learning_queue.v1")
        self.assertEqual(queue["available_count"], 6)
        self.assertEqual(queue["returned_count"], 6)
        self.assertTrue(all(item["track_id"] == "dreamco-division-specialist" for item in queue["items"]))
        self.assertTrue(all(item["source_url"] == "" for item in queue["items"]))
        self.assertTrue(all(item["completion_status"] == "queued_for_owner_review" for item in queue["items"]))
        self.assertTrue(all(item["study_allowed"] is False for item in queue["items"]))
        self.assertTrue(all(item["authoring_required"] is True for item in queue["items"]))
        self.assertTrue(all(item["exercise_ids"] and item["project_ids"] and item["assessment_ids"] for item in queue["items"]))
        self.assertTrue(all(item["retraining_policy_id"] for item in queue["items"]))
        self.assertTrue(all(item["mastery_awarded"] is False for item in queue["items"]))
        self.assertFalse(queue["external_discovery_performed"])
        self.assertFalse(queue["external_model_call_performed"])

    def test_library_learning_queue_is_bounded_to_the_dreamco_division_course(self):
        queue = self.bridge.library_learning_queue(division="DreamCodeLab", limit=100)
        self.assertEqual(queue["available_count"], 6)
        self.assertEqual(queue["returned_count"], 6)
        self.assertEqual(queue["items"][0]["track_id"], "dreamco-division-specialist")

    def test_library_learning_queue_supports_masterbot_lanes(self):
        queue = self.bridge.library_learning_queue(
            masterbot="CommandCore", query="approval-aware routing", limit=5
        )
        self.assertEqual(queue["masterbot"], "CommandCore")
        self.assertGreaterEqual(queue["returned_count"], 1)
        self.assertTrue(all(item["track_id"] == "dreamco-division-specialist" for item in queue["items"]))
        self.assertTrue(all("CommandCore" in item["masterbot_targets"] for item in queue["items"]))

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





    def test_external_provider_tracks_are_not_exposed_to_the_bootcamp_queue(self):
        queue = self.bridge.bootcamp_learning_queue(division="DreamCodeLab", limit=100)
        external_ids = {
            "onet", "hugging-face", "freecodecamp", "huggingface-full",
            "freecodecamp-video-catalog", "freecodecamp-specialist-learning-paths",
            "freecodecamp-metadata-triage",
        }
        self.assertFalse(any(item["track_id"] in external_ids for item in queue["items"]))
        self.assertTrue(all(item["source_url"] == "" for item in queue["items"]))
        self.assertEqual(queue["track_ids"], ["dreamco-division-specialist"])

    def test_external_metadata_is_not_presented_as_a_dreamco_lesson(self):
        queue = self.bridge.bootcamp_learning_queue(division="DreamCodeLab", query="video metadata", limit=100)
        self.assertFalse(any(item.get("source_video_id") for item in queue["items"]))
        self.assertTrue(all(item["source_url"] == "" for item in queue["items"]))

    def test_division_benchmark_lessons_include_assessments_and_retraining(self):
        queue = self.bridge.bootcamp_learning_queue(
            division="DreamCodeLab", query="benchmark", limit=20
        )
        self.assertTrue(queue["items"])
        self.assertTrue(all(item["assessment_ids"] for item in queue["items"]))
        self.assertTrue(all(item["retraining_policy_id"] for item in queue["items"]))
        self.assertTrue(all(item["mastery_awarded"] is False for item in queue["items"]))

    def test_generated_curriculum_stays_in_owner_review_until_approved(self):
        queue = self.bridge.bootcamp_learning_queue(division="DreamCodeLab", limit=20)
        self.assertEqual(queue["study_ready_count"], 0)
        self.assertEqual(queue["authoring_backlog_count"], 6)
        self.assertTrue(all(item["review_status"] == "draft_needs_owner_review" for item in queue["items"]))
        self.assertTrue(all(item["training_eligibility"] == "internal_sandbox_practice_only" for item in queue["items"]))
        self.assertTrue(all(item["completion_status"] == "queued_for_owner_review" for item in queue["items"]))
        self.assertTrue(all(item["study_allowed"] is False for item in queue["items"]))
        self.assertTrue(all(item["authoring_required"] is True for item in queue["items"]))
        self.assertTrue(all(item["mastery_awarded"] is False for item in queue["items"]))

    def test_forget_deletes_private_records(self):
        task, result = self.completed()
        self.learn(task, result)
        self.assertEqual(self.bridge.store.forget("alice"), 1)
        self.assertEqual(self.bridge.coach("alice", "technical")["observations"], 0)


    def test_bootcamp_learning_queue_exposes_only_dreamco_owned_curriculum(self):
        queue = self.bridge.bootcamp_learning_queue(division="DreamCodeLab", limit=100)
        self.assertEqual(queue["schema"], "dreamco.buddy_bootcamp_learning_queue.v1")
        self.assertEqual(queue["catalog_lesson_count"], 330)
        self.assertEqual(queue["available_count"], 6)
        self.assertEqual(queue["returned_count"], 6)
        self.assertEqual(queue["track_ids"], ["dreamco-division-specialist"])
        self.assertTrue(all(item["completion_status"] == "queued_for_owner_review" for item in queue["items"]))
        self.assertTrue(all(item["study_allowed"] is False for item in queue["items"]))
        self.assertTrue(all(item["authoring_required"] is True for item in queue["items"]))
        self.assertTrue(all(item["exercise_ids"] and item["project_ids"] and item["assessment_ids"] for item in queue["items"]))
        self.assertTrue(all(item["mastery_awarded"] is False for item in queue["items"]))
        self.assertFalse(queue["external_discovery_performed"])
        self.assertFalse(queue["external_model_call_performed"])

    def test_bootcamp_learning_queue_filters_and_supports_masterbot_lanes(self):
        queue = self.bridge.bootcamp_learning_queue(
            masterbot="CommandCore", query="approval-aware routing", limit=10
        )
        self.assertEqual(queue["masterbot"], "CommandCore")
        self.assertGreaterEqual(queue["returned_count"], 1)
        self.assertEqual(queue["track_ids"], ["dreamco-division-specialist"])
        self.assertTrue(all("CommandCore" in item["masterbot_targets"] for item in queue["items"]))
        self.assertTrue(all(item["source_url"] == "" for item in queue["items"]))

    def test_bootcamp_learning_queue_requires_exactly_one_owner_and_bounded_query(self):
        with self.assertRaises(ValueError):
            self.bridge.bootcamp_learning_queue(query="python")
        with self.assertRaises(ValueError):
            self.bridge.bootcamp_learning_queue(division="DreamCodeLab", masterbot="DreamCodeLab")
        with self.assertRaises(ValueError):
            self.bridge.bootcamp_learning_queue(division="DreamCodeLab", limit=101)
        with self.assertRaises(ValueError):
            self.bridge.bootcamp_learning_queue(division="DreamCodeLab", query="x" * 1001)


    def test_division_and_masterbot_curricula_are_scoped_and_demonstrable(self):
        finance = self.bridge.bootcamp_learning_queue(division="DreamFinance", limit=10)
        agents = self.bridge.bootcamp_learning_queue(division="DreamAgents", limit=10)
        commandcore = self.bridge.bootcamp_learning_queue(masterbot="CommandCore", limit=10)
        self.assertEqual(len(finance["items"]), 6)
        self.assertEqual(len(agents["items"]), 6)
        self.assertTrue(all("DreamFinance" in item["division_targets"] for item in finance["items"]))
        self.assertTrue(all("DreamAgents" in item["division_targets"] for item in agents["items"]))
        self.assertTrue(all("CommandCore" in item["masterbot_targets"] for item in commandcore["items"]))
        for queue in (finance, agents, commandcore):
            self.assertEqual(queue["track_ids"], ["dreamco-division-specialist"])
            self.assertTrue(all(item["exercise_ids"] and item["project_ids"] and item["assessment_ids"] for item in queue["items"]))
            self.assertTrue(all(item["source_url"] == "" for item in queue["items"]))

    def test_query_ranks_exact_specialist_title_before_broad_shared_matches(self):
        def lesson(resource_id, title, objective, *, division_targets=()):
            return CourseLesson(
                resource_id=resource_id, lesson_id=f"fixture-{resource_id}", track_id="dreamco-division-specialist",
                title=title, category="finance", objective=objective,
                practice="Build a safe, deterministic practice project.",
                assessment="Verify the result with independent tests.",
                benchmark="Task-matched holdout and regression.",
                source_url="", guide_path="docs/DREAMCO_UNIVERSAL_CAPABILITY_TAXONOMY.md",
                rights_mode="dreamco_original_internal", delivery="internal_bootcamp",
                content_status="authored", division_targets=tuple(division_targets or ("DreamFinance",)),
                learner_visible=True, review_status="approved",
                training_eligibility="internal_sandbox_practice_only",
            )

        broad_matches = [
            lesson(i, f"General finance topic {i}", "Discuss trading operations and portfolio vocabulary.")
            for i in range(1, 13)
        ]
        exact_match = lesson(
            99, "Algorithmic Trading with Risk Controls",
            "Build and verify an algorithmic trading research sandbox.",
            division_targets=("DreamFinance",),
        )
        with patch("buddy.learning.runtime_bridge.resources_for_division", return_value=[]), \
             patch("buddy.learning.runtime_bridge.load_course_lessons", return_value=broad_matches + [exact_match]):
            result = self.bridge.bootcamp_learning_queue(
                division="DreamFinance", query="algorithmic trading", limit=1
            )
        self.assertEqual(result["returned_count"], 1)
        self.assertEqual(result["items"][0]["title"], "Algorithmic Trading with Risk Controls")


    def test_all_55_divisions_receive_six_dreamco_owned_lessons(self):
        root = Path(__file__).resolve().parents[1]
        crosswalk = json.loads((root / "config/generated/masterbot-55-domain-crosswalk.json").read_text(encoding="utf-8"))
        for domain in crosswalk["domains"]:
            division = domain["domain_name"]
            with self.subTest(division=division):
                queue = self.bridge.bootcamp_learning_queue(division=division, limit=10)
                self.assertEqual(queue["available_count"], 6)
                self.assertEqual(queue["track_ids"], ["dreamco-division-specialist"])
                self.assertEqual(queue["study_ready_count"], 0)
                self.assertEqual(queue["authoring_backlog_count"], 6)
                self.assertTrue(all(division in item["division_targets"] for item in queue["items"]))
                self.assertTrue(all(item["source_url"] == "" for item in queue["items"]))
                self.assertTrue(all(item["exercise_ids"] and item["project_ids"] and item["assessment_ids"] for item in queue["items"]))

    def test_external_metadata_tracks_are_filtered_before_learner_routing(self):
        external = CourseLesson(
            resource_id=1, lesson_id="external-reference", track_id="freecodecamp-video-catalog",
            title="External metadata record", category="metadata", objective="Not learner content.",
            practice="Internal rights review only.", assessment="Not an assessment.",
            benchmark="Not a learner benchmark.", source_url="https://example.org/video",
            guide_path="", rights_mode="metadata_only", delivery="internal_authoring_reference",
            content_status="metadata_only", learner_visible=False,
        )
        internal = CourseLesson(
            resource_id=2, lesson_id="dreamco-commandcore", track_id="dreamco-division-specialist",
            title="CommandCore: Task Understanding", category="task_understanding",
            objective="Understand a CommandCore task.", practice="Practice in an isolated sandbox.",
            assessment="Verify a new CommandCore task.", benchmark="Holdout benchmark.",
            source_url="", guide_path="docs/DREAMCO_UNIVERSAL_CAPABILITY_TAXONOMY.md",
            rights_mode="dreamco_original_internal", delivery="internal_bootcamp",
            content_status="authored", division_targets=("CommandCore",),
            learner_visible=True, review_status="draft_needs_owner_review",
            training_eligibility="internal_sandbox_practice_only",
        )
        with patch("buddy.learning.runtime_bridge.resources_for_division", return_value=[]), \
             patch("buddy.learning.runtime_bridge.load_course_lessons", return_value=[external, internal]):
            queue = self.bridge.bootcamp_learning_queue(division="CommandCore", limit=10)
        self.assertEqual(queue["track_ids"], ["dreamco-division-specialist"])
        self.assertEqual([item["lesson_id"] for item in queue["items"]], ["dreamco-commandcore"])
        self.assertTrue(all(item["source_url"] == "" for item in queue["items"]))
    def test_learning_queue_paginates_without_dropping_later_lessons(self):
        lessons = [
            CourseLesson(
                resource_id=index, lesson_id=f"pagination-{index}", track_id="dreamco-division-specialist",
                title=f"Shared curriculum lesson {index}", category="foundation",
                objective="Study and practice a foundational skill.", practice="Complete a guided exercise.",
                assessment="Pass the independent check.", benchmark="Regression benchmark.",
                source_url="", guide_path="docs/DREAMCO_UNIVERSAL_CAPABILITY_TAXONOMY.md", rights_mode="dreamco_original_internal",
                delivery="internal_bootcamp", content_status="authored",
                division_targets=("DreamFinance",), learner_visible=True, review_status="approved",
                training_eligibility="internal_sandbox_practice_only",
            )
            for index in range(205)
        ]
        with patch("buddy.learning.runtime_bridge.resources_for_division", return_value=[]), \
             patch("buddy.learning.runtime_bridge.load_course_lessons", return_value=lessons):
            first = self.bridge.bootcamp_learning_queue(division="DreamFinance", limit=100, offset=0)
            second = self.bridge.bootcamp_learning_queue(division="DreamFinance", limit=100, offset=100)
            third = self.bridge.bootcamp_learning_queue(division="DreamFinance", limit=100, offset=200)
        self.assertEqual(first["total_count"], 205)
        self.assertEqual(first["returned_count"], 100)
        self.assertTrue(first["has_more"])
        self.assertEqual(first["next_offset"], 100)
        self.assertEqual(second["offset"], 100)
        self.assertEqual(second["next_offset"], 200)
        self.assertEqual(third["returned_count"], 5)
        self.assertFalse(third["has_more"])
        ids = [item["lesson_id"] for page in (first, second, third) for item in page["items"]]
        self.assertEqual(len(ids), 205)
        self.assertEqual(len(set(ids)), 205)



if __name__ == "__main__":
    unittest.main()
