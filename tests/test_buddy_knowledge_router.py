"""Focused regression tests for Buddy's internal-first knowledge routing."""
from __future__ import annotations

import unittest

from buddy.learning.buddy_knowledge_router import route_buddy_learning_query


class BuddyKnowledgeRouterTests(unittest.TestCase):
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
        self.assertFalse(route["external_discovery_performed"])
        self.assertFalse(route["external_model_routing_performed"])
        self.assertFalse(route["mastery_awarded"])

    def test_track_specific_query_prioritizes_its_named_curriculum_track(self):
        route = route_buddy_learning_query("hugging face transformers", limit=25)
        self.assertEqual(route["route"], "internal_bootcamp_lesson")
        self.assertTrue(any(
            row["track_id"] in {"hugging-face", "huggingface-full"}
            for row in route["course_lessons"]
        ))
        self.assertFalse(route["external_model_routing_performed"])
        self.assertFalse(route["mastery_awarded"])


if __name__ == "__main__":
    unittest.main()
