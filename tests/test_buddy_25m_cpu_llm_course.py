from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Buddy25MCpuLLMCourseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course = json.loads((ROOT / "config/buddy-25m-cpu-llm-course.json").read_text(encoding="utf-8"))
        cls.model_units = json.loads((ROOT / "config/buddy-gpt-style-model-training-units.json").read_text(encoding="utf-8"))
        cls.division_map = json.loads((ROOT / "config/buddy-ai-model-course-division-map.json").read_text(encoding="utf-8"))
        cls.onet = json.loads((ROOT / "config/buddy-onet-content-model-curriculum.json").read_text(encoding="utf-8"))

    def test_course_has_all_18_ordered_modules_and_full_video_chapters(self):
        self.assertEqual(len(self.course["modules"]), 18)
        self.assertEqual([m["id"] for m in self.course["modules"]], [f"LLM25-{i:02d}" for i in range(1, 19)])
        self.assertGreaterEqual(len(self.course["course_video_chapters"]), 18)
        self.assertTrue(all(m["objective"] and m["practice"] and m["transfer_task"] and m["benchmark"] for m in self.course["modules"]))

    def test_every_canonical_division_and_masterbot_lane_receives_shared_foundation(self):
        self.assertEqual(len(self.course["delivery"]["division_assignments"]), 55)
        self.assertEqual(len(self.course["delivery"]["masterbot_assignments"]), 65)
        self.assertTrue(all(d["delivery"] == "shared_ai_model_literacy_foundation" for d in self.course["delivery"]["division_assignments"]))
        self.assertTrue(all(b["shared_foundation"] for b in self.course["delivery"]["masterbot_assignments"]))
        self.assertTrue(self.course["delivery"]["specialist_routes_require_reviewed_ownership"])

    def test_course_source_rights_and_compute_are_not_overstated(self):
        self.assertTrue(all(not source["training_data_authorized"] for source in self.course["sources"] if "training_data_authorized" in source))
        self.assertFalse(self.course["safety_and_compute"]["paid_compute_authorized"])
        self.assertFalse(self.course["safety_and_compute"]["model_weight_updates_authorized"])
        self.assertTrue(self.course["mastery"]["reading_is_not_mastery"])

    def test_model_training_units_cover_all_25m_course_additions(self):
        self.assertEqual(len(self.model_units["units"]), 20)
        self.assertEqual(self.model_units["course_integration"]["module_count"], 18)
        self.assertEqual(self.model_units["division_coverage"]["canonical_divisions"], 55)
        self.assertEqual(self.model_units["division_coverage"]["masterbot_lanes"], 65)

    def test_course_source_catalog_is_link_only_and_complete(self):
        self.assertEqual(self.resources["resource_count"], 42)
        self.assertEqual(len(self.resources["resources"]), 42)
        self.assertTrue(all(row["url"].startswith("https://") for row in self.resources["resources"]))
        self.assertFalse(self.resources["automatic_download"])
        self.assertFalse(self.resources["automatic_transcript_download"])
        self.assertFalse(self.resources["automatic_training_approval"])

    def test_onet_covers_six_content_model_areas_and_all_divisions(self):
        self.assertEqual(len(self.onet["content_model_areas"]), 6)
        self.assertEqual(self.onet["official_release_snapshot"]["release"], "31.0")
        self.assertEqual(self.onet["official_release_snapshot"]["row_counts"]["occupations"], 1016)
        self.assertGreaterEqual(len(self.onet["source_files"]), 20)
        self.assertIn("CC BY 4.0", self.onet["source"]["license"])
        self.assertEqual(len(self.onet["division_delivery"]["division_crosswalk"]), 55)
        self.assertEqual(len(self.onet["division_delivery"]["masterbot_lanes"]), 65)
        self.assertGreaterEqual(len(self.onet["subject_inventory"]), 25)
        self.assertTrue(self.onet["ai_task_suitability"]["required_task_fields"])
        self.assertIn("not_assessed", [x["id"] for x in self.onet["ai_task_suitability"]["classes"]])


if __name__ == "__main__":
    unittest.main()
