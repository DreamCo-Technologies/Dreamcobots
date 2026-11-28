"""Focused regression tests for Buddy's internal-first knowledge routing."""
from __future__ import annotations

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from buddy.learning.buddy_knowledge_router import route_buddy_learning_query


class BuddyKnowledgeRouterTests(unittest.TestCase):
    def test_division_specific_query_prioritizes_its_dreamco_curriculum(self):
        route = route_buddy_learning_query(
            "CommandCore capability-aware routing and approval-aware orchestration",
            limit=25,
        )
        self.assertEqual(route["route"], "internal_bootcamp_lesson")
        self.assertTrue(any(
            row["track_id"] == "dreamco-division-specialist"
            and "CommandCore" in row["division_targets"]
            for row in route["course_lessons"]
        ))
        self.assertTrue(all(not row["source_url"] for row in route["course_lessons"]))
        self.assertFalse(route["external_discovery_performed"])
        self.assertFalse(route["external_model_routing_performed"])
        self.assertFalse(route["mastery_awarded"])


    def test_external_provider_tracks_are_not_exposed_to_learner_routes(self):
        route = route_buddy_learning_query("Hugging Face FreeCodeCamp O*NET course materials", limit=25)
        external_tracks = {
            "onet", "hugging-face", "freecodecamp", "huggingface-full",
            "freecodecamp-video-catalog", "freecodecamp-specialist-learning-paths",
            "freecodecamp-metadata-triage",
        }
        self.assertFalse(any(row["track_id"] in external_tracks for row in route["course_lessons"]))
        self.assertTrue(all(not row["source_url"] for row in route["course_lessons"]))
        self.assertFalse(route["external_discovery_performed"])
        self.assertFalse(route["external_model_routing_performed"])

    def test_approved_internal_guide_precedes_exact_unverified_seed_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "guides").mkdir()
            (root / "guides/react.json").write_text('{"title":"Approved React guide"}', encoding="utf-8")
            library = {
                "matches": [{"guide_path": "guides/react.json", "score": 1.0}],
                "seed_candidate_matches": [{
                    "candidate_id": "seed-react-19",
                    "name": "React 19",
                    "status": "seed_candidate_unverified",
                }],
                "knowledge_gap": None,
            }
            candidate_lesson = [{
                "lesson_id": "candidate-discovery-seed-react-19",
                "internal_guide": {"status": "not_in_repository"},
            }]
            with patch(
                "buddy.learning.buddy_knowledge_router.search_internal_library_knowledge",
                return_value=library,
            ), patch(
                "buddy.learning.buddy_knowledge_router._exact_seed_candidate_ids",
                return_value={"candidate-discovery-seed-react-19"},
            ), patch(
                "buddy.learning.buddy_knowledge_router._course_matches",
                return_value=candidate_lesson,
            ):
                route = route_buddy_learning_query("React 19", root=root)

        self.assertEqual(route["route"], "internal_approved_guide")
        self.assertEqual(route["answer_source"], "dreamco_approved_library_guides")
        self.assertEqual(route["course_lessons"], [])
        self.assertEqual(route["guide_documents"], [{"title": "Approved React guide"}])
        self.assertFalse(route["mastery_awarded"])


    def test_external_research_is_not_available_from_the_learner_route(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch(
                "buddy.learning.buddy_knowledge_router.search_internal_library_knowledge",
                return_value={
                    "matches": [],
                    "seed_candidate_matches": [],
                    "knowledge_gap": {"status": "internal_knowledge_gap"},
                },
            ), patch(
                "buddy.learning.buddy_knowledge_router._course_matches",
                return_value=[],
            ):
                route = route_buddy_learning_query(
                    "unmapped capability zebra quartz violet",
                    root=Path(directory),
                )
        self.assertFalse(route["external_discovery_available"])
        self.assertFalse(route["external_discovery_requires_explicit_opt_in"])
        self.assertFalse(route["external_discovery_performed"])
        self.assertFalse(route["external_model_routing_performed"])
        self.assertIn("do not route learners to external course websites", route["next_action"])

    def test_exact_seed_candidate_routes_to_its_bootcamp_discovery_lesson(self):
        route = route_buddy_learning_query("React 19")

        self.assertEqual(route["route"], "internal_bootcamp_lesson")
        self.assertEqual(route["answer_source"], "dreamco_bootcamp_candidate_discovery")
        self.assertTrue(
            any(
                row["lesson_id"] == "candidate-discovery-seed-react-19"
                for row in route["course_lessons"]
            )
        )
        self.assertTrue(route["candidate_verification_required"])
        self.assertFalse(route["external_discovery_requires_explicit_opt_in"])
        self.assertIn("do not route learners to external course websites", route["next_action"])
        self.assertFalse(route["external_discovery_performed"])
        self.assertFalse(route["external_model_routing_performed"])
        self.assertFalse(route["mastery_awarded"])


if __name__ == "__main__":
    unittest.main()
