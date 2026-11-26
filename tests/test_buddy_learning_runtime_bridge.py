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
        self.assertTrue(all(
            item["completion_status"] == (
                "queued_not_studied" if item["content_status"] == "authored"
                else "metadata_only" if item["content_status"] == "metadata_only"
                else "authoring_backlog"
            )
            for item in queue["items"]
        ))
        self.assertTrue(all(
            item["study_allowed"] is (item["content_status"] == "authored")
            for item in queue["items"]
        ))
        self.assertTrue(all(
            item["authoring_required"] is (item["content_status"] in {"authoring_backlog", "metadata_only"})
            for item in queue["items"]
        ))
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





    def test_onet_outlines_are_discoverable_as_internal_authoring_backlog(self):
        queue = self.bridge.bootcamp_learning_queue(
            division="DreamCodeLab", query="worker requirements", limit=20
        )
        matches = [item for item in queue["items"] if item["track_id"] == "onet"]
        self.assertTrue(matches)
        self.assertTrue(all(item["completion_status"] == "authoring_backlog" for item in matches))
        self.assertTrue(all(item["study_allowed"] is False for item in matches))
        self.assertTrue(all(item["authoring_required"] is True for item in matches))
        self.assertTrue(all(item["mastery_awarded"] is False for item in matches))

    def test_freecodecamp_video_metadata_is_not_presented_as_study_content(self):
        queue = self.bridge.bootcamp_learning_queue(
            division="DreamCodeLab", query="fcc-video", limit=100
        )
        video_items = [item for item in queue["items"] if item["track_id"] == "freecodecamp-video-catalog"]
        self.assertTrue(video_items)
        self.assertTrue(all(item["completion_status"] == "metadata_only" for item in video_items))
        self.assertTrue(all(item["study_allowed"] is False for item in video_items))
        self.assertTrue(all(item["authoring_required"] is True for item in video_items))
        self.assertTrue(all(item["mastery_awarded"] is False for item in video_items))

    def test_benchmark_guide_work_items_are_discoverable_in_internal_queue(self):
        queue = self.bridge.bootcamp_learning_queue(
            division="DreamCodeLab", query="long_context", limit=20
        )
        matches = [item for item in queue["items"] if item["track_id"] == "benchmark-guides"]
        self.assertTrue(matches)
        self.assertTrue(all(item["completion_status"] == "authoring_backlog" for item in matches))
        self.assertTrue(all(item["study_allowed"] is False for item in matches))
        self.assertTrue(all(item["authoring_required"] is True for item in matches))
        self.assertTrue(all(item["mastery_awarded"] is False for item in matches))

    def test_workforce_playbooks_appear_as_authoring_backlog_not_study_ready(self):
        queue = self.bridge.bootcamp_learning_queue(
            division="DreamCodeLab", query="government grants", limit=20
        )
        self.assertGreater(queue["authoring_backlog_count"], 0)
        self.assertEqual(queue["study_ready_count"], 0)
        self.assertTrue(queue["items"])
        self.assertTrue(all(item["completion_status"] == "authoring_backlog" for item in queue["items"]))
        self.assertTrue(all(item["study_allowed"] is False for item in queue["items"]))
        self.assertTrue(all(item["authoring_required"] is True for item in queue["items"]))
        self.assertTrue(all(item["mastery_awarded"] is False for item in queue["items"]))

    def test_forget_deletes_private_records(self):
        task, result = self.completed()
        self.learn(task, result)
        self.assertEqual(self.bridge.store.forget("alice"), 1)
        self.assertEqual(self.bridge.coach("alice", "technical")["observations"], 0)


    def test_bootcamp_learning_queue_exposes_all_internal_tracks(self):
        queue = self.bridge.bootcamp_learning_queue(division="DreamCodeLab", limit=100)
        self.assertEqual(queue["schema"], "dreamco.buddy_bootcamp_learning_queue.v1")
        self.assertGreater(queue["catalog_lesson_count"], 2000)
        self.assertEqual(queue["returned_count"], 100)
        self.assertTrue({"onet", "hugging-face", "huggingface-full", "freecodecamp",
                         "freecodecamp-video-catalog", "tokenizer"}.issubset(set(queue["track_ids"])))
        self.assertTrue(all(item["completion_status"] in {"queued_not_studied", "metadata_only", "authoring_backlog"} for item in queue["items"]))
        self.assertTrue(all(item["mastery_awarded"] is False for item in queue["items"]))
        self.assertTrue(all(item["study_allowed"] is (item["content_status"] == "authored") for item in queue["items"]))
        self.assertTrue(all(item["authoring_required"] is (item["content_status"] in {"metadata_only", "authoring_backlog", "original_implementation_brief"}) for item in queue["items"]))
        self.assertTrue(all(item["mastery_awarded"] is False for item in queue["items"]))
        self.assertFalse(queue["external_discovery_performed"])
        self.assertFalse(queue["external_model_call_performed"])

    def test_bootcamp_learning_queue_filters_and_supports_masterbot_lanes(self):
        queue = self.bridge.bootcamp_learning_queue(
            masterbot="DreamCodeLab", query="hf-llm-course", limit=10
        )
        self.assertEqual(queue["masterbot"], "DreamCodeLab")
        self.assertGreaterEqual(queue["returned_count"], 1)
        self.assertIn("huggingface-full", queue["track_ids"])
        self.assertTrue(all(item["lesson_id"] == "hf-llm-course" for item in queue["items"]))

    def test_bootcamp_learning_queue_requires_exactly_one_owner_and_bounded_query(self):
        with self.assertRaises(ValueError):
            self.bridge.bootcamp_learning_queue(query="python")
        with self.assertRaises(ValueError):
            self.bridge.bootcamp_learning_queue(division="DreamCodeLab", masterbot="DreamCodeLab")
        with self.assertRaises(ValueError):
            self.bridge.bootcamp_learning_queue(division="DreamCodeLab", limit=101)
        with self.assertRaises(ValueError):
            self.bridge.bootcamp_learning_queue(division="DreamCodeLab", query="x" * 1001)


    def test_specialist_learning_paths_are_scoped_and_demonstrable(self):
        finance = self.bridge.bootcamp_learning_queue(
            division="DreamFinance", query="algorithmic trading", limit=10
        )
        agents = self.bridge.bootcamp_learning_queue(
            division="DreamAgents", query="algorithmic trading", limit=10
        )
        trade = self.bridge.bootcamp_learning_queue(
            masterbot="DreamTrade", query="algorithmic trading", limit=10
        )
        finance_items = [item for item in finance["items"] if item.get("source_video_id") == "zH2Mg782XhA"]
        agent_items = [item for item in agents["items"] if item.get("source_video_id") == "zH2Mg782XhA"]
        trade_items = [item for item in trade["items"] if item.get("source_video_id") == "zH2Mg782XhA"]
        self.assertTrue(any(item["track_id"] == "freecodecamp-specialist-learning-paths" for item in finance_items))
        self.assertFalse(agent_items)
        self.assertTrue(any(item["track_id"] == "freecodecamp-specialist-learning-paths" for item in trade_items))
        path = next(item for item in finance_items if item["track_id"] == "freecodecamp-specialist-learning-paths")
        self.assertGreaterEqual(len(path["implementation_steps"]), 10)
        self.assertTrue(path["buddy_demo"])
        self.assertFalse(path["study_allowed"])
        self.assertTrue(path["authoring_required"])
        self.assertEqual(path["completion_status"], "authoring_backlog")



    def test_query_ranks_exact_specialist_title_before_broad_shared_matches(self):
        def lesson(resource_id, title, objective, *, division_targets=()):
            return CourseLesson(
                resource_id=resource_id, lesson_id=f"fixture-{resource_id}", track_id="fixture-track",
                title=title, category="finance", objective=objective,
                practice="Build a safe, deterministic practice project.",
                assessment="Verify the result with independent tests.",
                benchmark="Task-matched holdout and regression.",
                source_url="https://example.org/course", guide_path="fixture",
                rights_mode="metadata_only", delivery="metadata_only",
                content_status="metadata_only", division_targets=tuple(division_targets),
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


    def test_video_catalog_is_filtered_by_division_categories_and_shared_foundation(self):
        def video(resource_id, title, categories, *, division_targets=()):
            return CourseLesson(
                resource_id=resource_id, lesson_id=f"video-{resource_id}", track_id="freecodecamp-video-catalog",
                title=title, category="video", objective="Original metadata-only learning candidate.",
                practice="Verify source rights before authoring.", assessment="Require an independent project assessment.",
                benchmark="Task-matched holdout and regression.", source_url="https://www.youtube.com/watch?v=fixture",
                guide_path="metadata-only", rights_mode="metadata_only", delivery="metadata_only",
                content_status="metadata_only", division_targets=tuple(division_targets),
                source_video_id=f"fixture-{resource_id}", video_categories=tuple(categories),
            )

        lessons = [
            video(1, "Shared Python foundations", ["python_and_automation"]),
            video(2, "Finance database design", ["databases_and_sql"]),
            video(3, "Unrelated CSS animation", ["html_css_and_accessibility"]),
            video(4, "Explicit finance specialist override", ["html_css_and_accessibility"], division_targets=("DreamFinance",)),
            video(5, "Cybersecurity specialist route", ["cybersecurity_and_privacy"], division_targets=("DreamCyber",)),
            video(6, "Spring Boot Java service", ["java_and_jvm"]),
        ]
        with patch("buddy.learning.runtime_bridge.resources_for_division", return_value=[]), \
             patch("buddy.learning.runtime_bridge.load_course_lessons", return_value=lessons):
            result = self.bridge.bootcamp_learning_queue(division="DreamFinance", limit=100)
        ids = {item["source_video_id"] for item in result["items"]}
        self.assertEqual(ids, {"fixture-1", "fixture-2", "fixture-4", "fixture-6"})
        self.assertTrue(all(item["video_categories"] for item in result["items"]))


    def test_learning_queue_paginates_without_dropping_later_lessons(self):
        lessons = [
            CourseLesson(
                resource_id=index, lesson_id=f"pagination-{index}", track_id="shared-fixture",
                title=f"Shared curriculum lesson {index}", category="foundation",
                objective="Study and practice a foundational skill.", practice="Complete a guided exercise.",
                assessment="Pass the independent check.", benchmark="Regression benchmark.",
                source_url="https://example.org/lesson", guide_path="fixture", rights_mode="original",
                delivery="original", content_status="authored",
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


    def test_all_55_divisions_receive_subject_relevant_video_pages(self):
        root = Path(__file__).resolve().parents[1]
        crosswalk = json.loads((root / "config/generated/masterbot-55-domain-crosswalk.json").read_text(encoding="utf-8"))
        profiles = json.loads((root / "config/freecodecamp-division-category-profiles.json").read_text(encoding="utf-8"))
        shared = set(profiles["shared_foundation_categories"])
        lessons = load_course_lessons()
        with patch("buddy.learning.runtime_bridge.resources_for_division", return_value=[]), \
             patch("buddy.learning.runtime_bridge.load_course_lessons", return_value=lessons):
            for domain in crosswalk["domains"]:
                domain_name = domain["domain_name"]
                allowed = shared | set(profiles["domain_categories"][domain["domain_id"]])
                result = self.bridge.bootcamp_learning_queue(
                    division=domain_name, query="freecodecamp", limit=100, offset=0
                )
                video_items = [item for item in result["items"] if item["source_video_id"]]
                self.assertTrue(video_items, domain_name)
                self.assertGreaterEqual(result["total_count"], 100, domain_name)
                self.assertTrue(result["has_more"], domain_name)
                for item in video_items:
                    if item["track_id"] == "freecodecamp-metadata-triage":
                        self.assertIn(domain_name, item["division_targets"], domain_name)
                    else:
                        self.assertTrue(
                            set(item["video_categories"]) & allowed or domain_name in item["division_targets"],
                            f"irrelevant video leaked into {domain_name}: {item['source_video_id']}",
                        )

    def test_unclassified_video_triage_is_visible_only_to_review_lanes(self):
        # This policy test must remain valid when the live catalog is fully classified.
        source_video_id = "synthetic-unclassified-video"
        source_title = "Synthetic classification review video"
        catalog_video = CourseLesson(
            resource_id=1, lesson_id="synthetic-video", track_id="freecodecamp-video-catalog",
            title=source_title, category="video", objective="classification review",
            practice="Create an original practice brief.", assessment="Verify classification.",
            benchmark="Independent classification check.", source_url="https://www.freecodecamp.org/",
            guide_path="metadata-only", rights_mode="metadata_only", delivery="metadata_only",
            content_status="metadata_only", division_targets=("DreamEducation",),
            masterbot_targets=("DreamDiscovery",), learning_modes=("metadata_review",),
            source_video_id=source_video_id,
        )
        triage_video = CourseLesson(
            resource_id=2, lesson_id="synthetic-triage", track_id="freecodecamp-metadata-triage",
            title=f"Metadata triage: {source_title}", category="video", objective="classification review",
            practice="Classify metadata and check rights before authoring.",
            assessment="A human reviewer verifies classification and rights.",
            benchmark="Independent metadata review.", source_url="https://www.freecodecamp.org/",
            guide_path="metadata-only", rights_mode="metadata_only", delivery="metadata_only",
            content_status="metadata_only", division_targets=("DreamEducation",),
            masterbot_targets=("DreamDiscovery",),
            learning_modes=("metadata_review", "guided_classification", "rights_check", "human_review"),
            implementation_steps=("Inspect title and description.", "Verify rights.", "Request human review."),
            buddy_demo="Show a metadata-only classification walkthrough.",
            source_video_id=source_video_id,
        )
        with patch("buddy.learning.runtime_bridge.load_course_lessons", return_value=[catalog_video, triage_video]):
            education = self.bridge.bootcamp_learning_queue(
                division="DreamEducation", query="classification review", limit=10
            )
            finance = self.bridge.bootcamp_learning_queue(
                division="DreamFinance", query="classification review", limit=10
            )
            discovery = self.bridge.bootcamp_learning_queue(
                masterbot="DreamDiscovery", query="classification review", limit=10
            )
            education_items = [item for item in education["items"] if item["track_id"] == "freecodecamp-metadata-triage"]
            finance_items = [item for item in finance["items"] if item["track_id"] == "freecodecamp-metadata-triage"]
            discovery_items = [item for item in discovery["items"] if item["track_id"] == "freecodecamp-metadata-triage"]
            self.assertTrue(education_items)
            self.assertFalse(finance_items)
            self.assertTrue(discovery_items)
            item = education_items[0]
            self.assertEqual(item["content_status"], "metadata_only")
            self.assertEqual(item["completion_status"], "metadata_only")
            self.assertFalse(item["study_allowed"])
            self.assertTrue(item["authoring_required"])
            self.assertTrue(item["implementation_steps"])
            self.assertTrue(item["buddy_demo"])
            self.assertEqual(set(item["learning_modes"]), {
                "metadata_review", "guided_classification", "rights_check", "human_review"
            })
            source_title = item["title"].split(": ", 1)[1]
            education_metadata = self.bridge.bootcamp_learning_queue(
                division="DreamEducation", query=source_title, limit=10
            )
            finance_metadata = self.bridge.bootcamp_learning_queue(
                division="DreamFinance", query=source_title, limit=10
            )
            self.assertTrue(any(
                row["track_id"] == "freecodecamp-video-catalog"
                and row["source_video_id"] == item["source_video_id"]
                for row in education_metadata["items"]
            ))
            self.assertFalse(any(
                row.get("source_video_id") == item["source_video_id"]
                for row in finance_metadata["items"]
            ))

if __name__ == "__main__":
    unittest.main()
