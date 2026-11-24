import unittest
from tools.build_daily_lesson_plan import build_plan


def crosswalk_fixture():
    core_names = ["DreamCyber", "DreamCodeLab", "DreamRealEstate"] + [f"DreamCore{i}" for i in range(4, 46)]
    supplemental_names = ["DreamFood"] + [f"DreamSupplemental{i}" for i in range(2, 11)]
    domains = []
    for index, name in enumerate(core_names, 1):
        domains.append({"domain_id": name.casefold(), "domain_name": name, "masterbot_id": index,
                        "mapping_status": "proposed_exact_name_match", "review_required": True})
    for name in supplemental_names:
        domains.append({"domain_id": name.casefold(), "domain_name": name, "masterbot_id": None,
                        "mapping_status": "unresolved", "review_required": True})
    return {"domains": domains}


class DailyLessonPlanTests(unittest.TestCase):
    def setUp(self):
        self.crosswalk = crosswalk_fixture()

    def build_queues(self):
        rows = []
        for domain in self.crosswalk["domains"]:
            rows.append({
                "domain_id": domain["domain_id"],
                "items": [{
                    "video_id": f"video-{domain['domain_id']}-{ordinal}",
                    "title": f"Study candidate {domain['domain_id']}-{ordinal}",
                    "url": f"https://www.youtube.com/watch?v={domain['domain_id']}-{ordinal}",
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
            "domain_count": 55,
            "catalog_video_count": 1650,
            "source_inventory_status": "complete",
            "source_inventory": {"complete": True, "expected_entry_count": 1650, "observed_entry_count": 1650},
            "domains": rows,
        }

    def test_five_daily_slots_for_each_domain_division(self):
        plan = build_plan(self.crosswalk, "2026-11-24")
        self.assertEqual(plan["domain_count"], 55)
        self.assertEqual(plan["masterbot_count"], 65)
        self.assertEqual(plan["shared_platform_masterbot_count"], 20)
        self.assertEqual(plan["target_lessons_per_domain"], 5)
        self.assertEqual(plan["daily_target"], 275)
        self.assertEqual(len(plan["slots"]), 275)
        self.assertTrue(all(x["status"] == "queued_not_created" for x in plan["slots"]))
        self.assertEqual(plan["created_lessons"], 0)

    def test_daily_slots_reference_five_rights_gated_candidates_per_domain(self):
        plan = build_plan(self.crosswalk, "2026-11-24", queues=self.build_queues())
        self.assertEqual(len(plan["slots"]), 275)
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
            build_plan(self.crosswalk, "2026-11-24", queues=queues)
        queues = self.build_queues()
        queues["domains"][0]["items"][0]["training_eligible"] = True
        with self.assertRaisesRegex(ValueError, "rights-review-only"):
            build_plan(self.crosswalk, "2026-11-24", queues=queues)

    def test_rejects_incomplete_or_duplicate_domain_crosswalk(self):
        with self.assertRaisesRegex(ValueError, "55 domain"):
            build_plan({"domains": self.crosswalk["domains"][:-1]}, "2026-11-24")
        broken = {"domains": list(self.crosswalk["domains"])}
        broken["domains"][-1] = {**broken["domains"][-1], "domain_id": broken["domains"][0]["domain_id"]}
        with self.assertRaisesRegex(ValueError, "unique"):
            build_plan(broken, "2026-11-24")

    def test_rejects_invalid_date_and_quota(self):
        with self.assertRaisesRegex(ValueError, "ISO date"):
            build_plan(self.crosswalk, "tomorrow")
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            build_plan(self.crosswalk, "2026-11-24", 0)


if __name__ == "__main__":
    unittest.main()
