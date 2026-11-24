import unittest
from tools.build_daily_lesson_plan import build_plan


class DailyLessonPlanTests(unittest.TestCase):
    def setUp(self):
        self.registry = {"divisions": [
            {"id": i, "name": f"Division{i}"} for i in range(1, 66)
        ]}

    def test_five_daily_slots_for_each_division(self):
        plan = build_plan(self.registry, "2026-11-24")
        self.assertEqual(plan["division_count"], 65)
        self.assertEqual(plan["target_lessons_per_division"], 5)
        self.assertEqual(plan["daily_target"], 325)
        self.assertEqual(len(plan["slots"]), 325)
        self.assertTrue(all(x["status"] == "queued_not_created" for x in plan["slots"]))
        self.assertEqual(plan["created_lessons"], 0)

    def build_queues(self):
        rows = []
        for division_id in range(1, 66):
            rows.append({
                "division_id": division_id,
                "items": [{
                    "video_id": f"video-{division_id}-{ordinal}",
                    "title": f"Study candidate {division_id}-{ordinal}",
                    "url": f"https://www.youtube.com/watch?v=video-{division_id}-{ordinal}",
                    "categories": ["python_and_automation"],
                    "priority_score": 10 - ordinal,
                    "assignment_status": "queued_not_studied",
                    "rights_status": "review_required",
                    "media_download_allowed": False,
                    "transcript_ingestion_allowed": False,
                    "training_eligible": False,
                } for ordinal in range(1, 31)],
            })
        return {
            "schema": "dreamco.freecodecamp_division_learning_queues.v1",
            "division_count": 65,
            "catalog_video_count": 1950,
            "source_inventory_status": "complete",
            "source_inventory": {
                "complete": True,
                "expected_entry_count": 1950,
                "observed_entry_count": 1950,
            },
            "divisions": rows,
        }

    def test_daily_slots_reference_five_rights_gated_candidates_per_division(self):
        queues = self.build_queues()
        plan = build_plan(self.registry, "2026-11-24", queues=queues)
        self.assertEqual(len(plan["slots"]), 325)
        self.assertTrue(all("candidate" in slot for slot in plan["slots"]))
        self.assertTrue(all(slot["candidate"]["rights_status"] == "review_required" for slot in plan["slots"]))
        self.assertTrue(all(slot["candidate"]["training_eligible"] is False for slot in plan["slots"]))
        self.assertTrue(all(slot["candidate"]["transcript_ingestion_allowed"] is False for slot in plan["slots"]))
        self.assertEqual(plan["created_lessons"], 0)
        self.assertEqual(plan["validated_lessons"], 0)

    def test_daily_plan_rejects_partial_or_unsafe_queue_candidates(self):
        queues = self.build_queues()
        queues["source_inventory_status"] = "partial"
        with self.assertRaisesRegex(ValueError, "verified complete"):
            build_plan(self.registry, "2026-11-24", queues=queues)
        queues = self.build_queues()
        queues["divisions"][0]["items"][0]["training_eligible"] = True
        with self.assertRaisesRegex(ValueError, "rights-review-only"):
            build_plan(self.registry, "2026-11-24", queues=queues)

    def test_rejects_incomplete_or_duplicate_registry(self):
        with self.assertRaisesRegex(ValueError, "65 divisions"):
            build_plan({"divisions": self.registry["divisions"][:-1]}, "2026-11-24")
        broken = {"divisions": list(self.registry["divisions"])}
        broken["divisions"][-1] = {"id": 64, "name": "Duplicate"}
        with self.assertRaisesRegex(ValueError, "unique"):
            build_plan(broken, "2026-11-24")

    def test_rejects_invalid_date_and_quota(self):
        with self.assertRaisesRegex(ValueError, "ISO date"):
            build_plan(self.registry, "tomorrow")
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            build_plan(self.registry, "2026-11-24", 0)


if __name__ == "__main__":
    unittest.main()
