import unittest
from tools.build_freecodecamp_division_queues import build_queues, validate

class FreeCodeCampDivisionQueueTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {
            "schema": "dreamco.freecodecamp_catalog.v1",
            "rights_policy": {"media_download_enabled": False, "transcript_ingestion_enabled": False, "model_training_requires_review": True},
            "categories": [{"id": x} for x in ["computer_science_and_fundamentals", "python_and_automation", "cybersecurity_and_privacy", "databases_and_sql", "javascript_and_typescript"]],
            "videos": [
                {"video_id": "a", "title": "Python foundations", "url": "https://www.youtube.com/watch?v=a", "categories": ["python_and_automation"]},
                {"video_id": "b", "title": "Cybersecurity basics", "url": "https://www.youtube.com/watch?v=b", "categories": ["cybersecurity_and_privacy"]},
                {"video_id": "c", "title": "Computer science foundations", "url": "https://www.youtube.com/watch?v=c", "categories": ["computer_science_and_fundamentals"]},
            ],
        }
        self.registry = {"divisions": [{"id": i, "name": name} for i, name in enumerate(["DreamCyber", "DreamCodeLab", "DreamFood"] * 22, 1)][:65]}

    def test_builds_unique_queue_for_all_65_divisions(self):
        result = build_queues(self.catalog, self.registry, limit=10)
        validate(result)
        self.assertEqual(result["division_count"], 65)
        self.assertEqual(len({x["division_id"] for x in result["divisions"]}), 65)

    def test_domain_hints_route_specialist_content(self):
        result = build_queues(self.catalog, self.registry, limit=10)
        cyber = result["divisions"][0]
        self.assertIn("cybersecurity_and_privacy", cyber["target_categories"])
        self.assertTrue(any("cybersecurity_and_privacy" in x["categories"] for x in cyber["items"]))

    def test_unmapped_division_gets_foundation_queue_and_pending_status(self):
        result = build_queues(self.catalog, self.registry, limit=10)
        food = next(x for x in result["divisions"] if x["division_name"] == "DreamFood")
        self.assertEqual(food["queue_status"], "foundation_only_owner_mapping_pending")
        self.assertTrue(all(x["assignment_status"] == "queued_not_studied" for x in food["items"]))

    def test_no_queue_item_is_authorized_for_training_or_media_ingestion(self):
        result = build_queues(self.catalog, self.registry, limit=10)
        for division in result["divisions"]:
            for item in division["items"]:
                self.assertFalse(item["training_eligible"])
                self.assertFalse(item["media_download_allowed"])
                self.assertFalse(item["transcript_ingestion_allowed"])
                self.assertEqual(item["rights_status"], "review_required")

    def test_rejects_wrong_division_count_and_claims_of_learning(self):
        with self.assertRaisesRegex(ValueError, "65-division"):
            build_queues(self.catalog, {"divisions": self.registry["divisions"][:64]})
        result = build_queues(self.catalog, self.registry, limit=10)
        result["divisions"][0]["items"][0]["assignment_status"] = "mastered"
        with self.assertRaisesRegex(ValueError, "cannot claim study"):
            validate(result)

if __name__ == "__main__":
    unittest.main()
