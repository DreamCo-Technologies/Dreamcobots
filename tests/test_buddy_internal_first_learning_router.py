from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from buddy.learning.buddy_knowledge_router import ROOT, route_buddy_learning_query, _supporting_guide


class BuddyInternalFirstLearningRouterTests(unittest.TestCase):
    def test_query_routes_to_internal_bootcamp_instead_of_a_model(self):
        result = route_buddy_learning_query("React 19", root=ROOT, limit=10)
        self.assertEqual(result["route"], "internal_bootcamp_lesson")
        self.assertTrue(any(row["lesson_id"] == "candidate-discovery-seed-react-19" for row in result["course_lessons"]))
        self.assertFalse(result["external_discovery_performed"])
        self.assertFalse(result["external_model_routing_performed"])
        self.assertTrue(result["study_required"])
        self.assertFalse(result["mastery_awarded"])
        self.assertTrue(all(row["completion_status"] == "queued_not_studied" for row in result["course_lessons"]))

    def test_huggingface_onet_and_freecodecamp_tracks_are_reachable_internally(self):
        cases = [
            ("hugging face transformers", {"hugging-face", "huggingface-full"}),
            ("onet occupations skills", {"onet"}),
            ("freecodecamp javascript algorithms", {"freecodecamp", "freecodecamp-video-catalog"}),
        ]
        for query, expected_tracks in cases:
            with self.subTest(query=query):
                result = route_buddy_learning_query(query, root=ROOT, limit=25)
                self.assertEqual(result["route"], "internal_bootcamp_lesson")
                self.assertTrue(
                    any(row["track_id"] in expected_tracks for row in result["course_lessons"]),
                    [row["track_id"] for row in result["course_lessons"]],
                )
                self.assertFalse(result["external_model_routing_performed"])

    def test_approved_guide_is_retrieved_before_course_matching(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            guide_path = root / "data/buddy-library-study-guides/guide.json"
            guide_path.parent.mkdir(parents=True)
            guide = {"library": {"canonical_id": "demo", "name": "Demo"}, "status": "approved_for_study"}
            guide_path.write_text(json.dumps(guide), encoding="utf-8")
            with patch("buddy.learning.buddy_knowledge_router.search_internal_library_knowledge", return_value={
                "matches": [{"canonical_id": "demo", "guide_path": "data/buddy-library-study-guides/guide.json"}],
                "seed_candidate_matches": [],
                "knowledge_gap": None,
            }), patch("buddy.learning.buddy_knowledge_router._course_matches") as course_matcher:
                result = route_buddy_learning_query("demo API", root=root)
            self.assertEqual(result["route"], "internal_approved_guide")
            self.assertEqual(result["guide_documents"][0]["library"]["canonical_id"], "demo")
            course_matcher.assert_not_called()
            self.assertFalse(result["external_model_routing_performed"])

    def test_missing_knowledge_stays_internal_and_is_not_persisted_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("buddy.learning.buddy_knowledge_router.search_internal_library_knowledge", return_value={
                "matches": [], "seed_candidate_matches": [], "knowledge_gap": {"status": "internal_knowledge_gap"},
            }), patch("buddy.learning.buddy_knowledge_router._course_matches", return_value=[]):
                result = route_buddy_learning_query("unmapped capability zqv 9842", root=root)
            self.assertEqual(result["route"], "internal_knowledge_gap")
            self.assertIsNone(result["gap_event"])
            self.assertTrue(result["external_discovery_available"])
            self.assertFalse(result["external_discovery_performed"])
            self.assertFalse(result["external_model_routing_performed"])
            self.assertFalse((root / "data/buddy-library-knowledge-gaps.jsonl").exists())

    def test_numeric_only_reference_does_not_match_unrelated_approved_guides(self):
        result = route_buddy_learning_query("qzxv 9481", root=ROOT)
        self.assertEqual(result["route"], "internal_knowledge_gap")
        self.assertFalse(result["external_discovery_performed"])
        self.assertFalse(result["external_model_routing_performed"])
        self.assertFalse(result["mastery_awarded"])

    def test_gap_persistence_requires_explicit_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("buddy.learning.buddy_knowledge_router.search_internal_library_knowledge", return_value={
                "matches": [], "seed_candidate_matches": [], "knowledge_gap": {"status": "internal_knowledge_gap"},
            }), patch("buddy.learning.buddy_knowledge_router._course_matches", return_value=[]):
                result = route_buddy_learning_query("unmapped capability zqv 9842", root=root, record_gap=True)
            self.assertEqual(result["gap_event"]["status"], "open")
            self.assertEqual(result["gap_event"]["query"], "[redacted]")
            self.assertFalse(result["gap_event"]["external_routing_performed"])
            self.assertTrue((root / "data/buddy-library-knowledge-gaps.jsonl").is_file())

    def test_invalid_query_and_limit_are_rejected(self):
        with self.assertRaises(ValueError):
            route_buddy_learning_query(" ")
        with self.assertRaises(ValueError):
            route_buddy_learning_query("python", limit=0)
        with self.assertRaises(ValueError):
            route_buddy_learning_query("x" * 1001)


    def test_course_route_includes_local_supporting_guide_excerpt(self):
        result = route_buddy_learning_query("hugging face transformers", root=ROOT, limit=25)
        self.assertEqual(result["route"], "internal_bootcamp_lesson")
        available = [
            row for row in result["course_lessons"]
            if row["internal_guide"]["status"] == "supporting_guide_available"
        ]
        self.assertTrue(available)
        self.assertTrue(all(row["internal_guide"]["sha256"] for row in available))
        self.assertTrue(all(row["internal_guide"]["excerpt"] for row in available))
        self.assertTrue(all(row["internal_guide"]["lesson_specific_guide_complete"] is False for row in available))
        self.assertGreater(result["supporting_guide_count"], 0)
        self.assertFalse(result["external_discovery_performed"])
        self.assertFalse(result["external_discovery_available"])
        self.assertFalse(result["external_model_routing_performed"])

    def test_supporting_guide_reader_blocks_paths_outside_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            outside = Path(tmp) / "secret.md"
            outside.write_text("private fixture", encoding="utf-8")
            blocked = _supporting_guide("../secret.md", root)
            missing = _supporting_guide("docs/missing.md", root)
            self.assertEqual(blocked["status"], "blocked_path")
            self.assertEqual(missing["status"], "not_in_repository")
            self.assertEqual(blocked["excerpt"], "")

if __name__ == "__main__":
    unittest.main()
