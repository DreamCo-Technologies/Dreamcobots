from __future__ import annotations

import unittest
from unittest.mock import patch

from buddy.fleet_runtime.router import complete, complete_learning


class FleetInternalBootcampRoutingTests(unittest.TestCase):
    def test_learning_completion_returns_internal_guide_without_model_fallback(self):
        route = {
            "route": "internal_approved_guide",
            "guide_documents": [{"library": {"name": "Demo"}}],
        }
        with patch("buddy.learning.buddy_knowledge_router.route_buddy_learning_query", return_value=route) as lookup:
            result = complete_learning("demo library", {}, lambda: self.fail("offline should not be called"))
        self.assertEqual(result["mode"], "internal_knowledge")
        self.assertIsNone(result["model"])
        self.assertEqual(result["learning_route"], route)
        lookup.assert_called_once()

    def test_learning_completion_returns_bootcamp_lesson_before_model_fallback(self):
        route = {
            "route": "internal_bootcamp_lesson",
            "course_lessons": [{"title": "Study React 19"}],
        }
        with patch("buddy.learning.buddy_knowledge_router.route_buddy_learning_query", return_value=route):
            result = complete_learning("React 19", {}, lambda: self.fail("offline should not be called"),
                                       {"DREAMCO_FLEET_LIVE_MODEL": "1", "OPENROUTER_API_KEY": "test"})
        self.assertEqual(result["mode"], "internal_bootcamp_study")
        self.assertIsNone(result["model"])
        self.assertEqual(result["learning_route"], route)

    def test_learning_gap_does_not_call_live_model_without_explicit_fallback(self):
        route = {"route": "internal_knowledge_gap", "knowledge_gap": {"status": "internal_knowledge_gap"}}
        with patch("buddy.learning.buddy_knowledge_router.route_buddy_learning_query", return_value=route):
            result = complete_learning("unmapped subject", {}, lambda: "local gap response",
                                       {"DREAMCO_FLEET_LIVE_MODEL": "1", "OPENROUTER_API_KEY": "test"})
        self.assertEqual(result["mode"], "offline_deterministic")
        self.assertEqual(result["fallback_reason"], "internal_knowledge_gap_external_fallback_disabled")
        self.assertEqual(result["learning_route"], route)

    def test_explicit_external_fallback_only_occurs_after_internal_gap(self):
        route = {"route": "internal_knowledge_gap", "knowledge_gap": {"status": "internal_knowledge_gap"}}
        with patch("buddy.learning.buddy_knowledge_router.route_buddy_learning_query", return_value=route):
            result = complete("unmapped subject", {
                "internal_bootcamp_first": True,
                "allow_external_learning_fallback": True,
                "mode": "offline_only",
            }, lambda: "offline after gap")
        self.assertEqual(result["mode"], "offline_deterministic")
        self.assertEqual(result["learning_route"], route)
        self.assertEqual(result["text"], "offline after gap")

    def test_general_fleet_completion_is_unchanged_without_learning_flag(self):
        with patch("buddy.learning.buddy_knowledge_router.route_buddy_learning_query") as lookup:
            result = complete("ordinary task", {"mode": "offline_only"}, lambda: "offline")
        lookup.assert_not_called()
        self.assertEqual(result["mode"], "offline_deterministic")
        self.assertEqual(result["text"], "offline")


if __name__ == "__main__":
    unittest.main()
