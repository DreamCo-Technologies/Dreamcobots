import json
import tempfile
import unittest
from pathlib import Path

from tools.build_freecodecamp_routes import build_routes, validate
from buddy.learning.freecodecamp_source import resources_for_division, select_next_for_division, plan_next_lesson\nfrom buddy.learning.study_resource_scheduler import Capability

class FreeCodeCampSourceRouteTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {
            "schema": "dreamco.freecodecamp_catalog.v1",
            "generated_at": "2026-11-24T00:00:00+00:00",
            "rights_policy": {"media_download_enabled": False, "transcript_ingestion_enabled": False, "model_training_requires_review": True},
            "categories": [{"id": x} for x in ["python_and_automation", "cybersecurity_and_privacy", "other_or_unclassified"]],
            "videos": [
                {"video_id": "v1", "title": "Python", "url": "https://www.youtube.com/watch?v=v1", "categories": ["python_and_automation"], "rights_status": "review_required", "learning_status": "not_studied"},
                {"video_id": "v2", "title": "Unclassified", "url": "https://www.youtube.com/watch?v=v2", "categories": ["other_or_unclassified"], "rights_status": "review_required", "learning_status": "not_studied},
            ],
        }
        self.registry = {"divisions": [{"id": i, "name": "DreamCyber" if i == 1 else f"DreamDivision{i}"} for i in range(1, 66)]}

    def test_every_video_is_discoverable_by_all_65_divisions(self):
        result = build_routes(self.catalog, self.registry)
        validate(result)
        self.assertEqual(result["catalog_video_count"], 2)
        self.assertTrue(all(x["available_video_count"] == 2 for x in result["divisions"]))
        self.assertTrue(all(x["shared_catalog_access"] for x in result["divisions"]))

    def test_specialty_tags_create_recommendation_routes(self):
        result = build_routes(self.catalog, self.registry)
        python = next(x for x in result["videos"] if x["video_id"] == "v1")
        self.assertEqual(python["specialty_division_ids"], [])
        cyber = next(x for x in result["videos"] if x["video_id"] == "v2")
        self.assertEqual(cyber["routing_status"], "unclassified_review")

    def test_training_media_and_transcript_gates_remain_closed(self):
        result = build_routes(self.catalog, self.registry)
        for video in result["videos"]:
            self.assertFalse(video["model_training_allowed"])
            self.assertFalse(video["media_download_allowed"])
            self.assertFalse(video["transcript_ingestion_allowed"])
            self.assertEqual(video["rights_status"], "review_required")

    def test_rejects_missing_division_or_duplicate_video(self):
        with self.assertRaisesRegex(ValueError, "65 divisions"):
            build_routes(self.catalog, {"divisions": self.registry["divisions"][:64]})
        broken = dict(self.catalog)
        broken["videos"] = [*self.catalog["videos"], self.catalog["videos"][0]]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate(build_routes(broken, self.registry))

    def test_runtime_returns_all_video_candidates_for_each_division(self):
        payload = build_routes(self.catalog, self.registry)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routes.json"
            path.write_text(json.dumps(payload))
            for division_id in range(1, 66):
                self.assertEqual(len(resources_for_division(division_id, path)), 2)

    def test_plan_next_lesson_contains_official_url_and_evidence_steps(self):
        payload = build_routes(self.catalog, self.registry)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routes.json"
            path.write_text(json.dumps(payload))
            plan = plan_next_lesson(1, Capability(name="python", category="python_and_automation"), path=path)
            self.assertIsNotNone(plan)
            self.assertEqual(plan["source"], "freeCodeCamp.org")
            self.assertTrue(plan["source_url"].startswith("https://www.youtube.com/"))
            self.assertIn("practice_in_sandbox", plan["steps"])
            self.assertIn("run_targeted_benchmark", plan["steps"])
            self.assertEqual(plan["completion_status"], "queued_not_studied")
            self.assertFalse(plan["model_training_allowed"])

    def test_runtime_scheduler_selects_candidate_and_validates_division(self):
        payload = build_routes(self.catalog, self.registry)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routes.json"
            path.write_text(json.dumps(payload))
            resource = select_next_for_division(1, [], path=path)
            self.assertIsNotNone(resource)
            with self.assertRaisesRegex(ValueError, "between 1 and 65"):
                resources_for_division(66, path)

if __name__ == "__main__":
    unittest.main()
