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
