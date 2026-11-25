from __future__ import annotations

import unittest

from buddy.learning.course_track_registry import (
    load_course_lessons,
    plan_next_for_division,
    resources_for_division,
    resources_for_masterbot,
)
from buddy.learning.study_resource_scheduler import Capability


class BuddyCourseTrackRegistryTests(unittest.TestCase):
    def test_all_tracks_are_exposed_as_ordered_course_lessons(self):
        lessons = load_course_lessons()
        self.assertEqual(len(lessons), sum(1 for _ in lessons))
        self.assertEqual(len({lesson.resource_id for lesson in lessons}), len(lessons))
        self.assertEqual(len({(lesson.track_id, lesson.lesson_id) for lesson in lessons}), len(lessons))
        expected = {"tolkien", "tokenizer", "cpu-first-llm", "onet", "hugging-face", "freecodecamp", "huggingface-full", "freecodecamp-video-catalog"}
        self.assertEqual({lesson.track_id for lesson in lessons}, expected)

    def test_every_canonical_division_receives_the_shared_course_queue(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1]
        crosswalk = json.loads((root / "config/generated/masterbot-55-domain-crosswalk.json").read_text(encoding="utf-8"))
        expected = len(load_course_lessons())
        for row in crosswalk["domains"]:
            with self.subTest(division=row["domain_name"]):
                self.assertEqual(len(resources_for_division(row["domain_name"])), expected)

    def test_every_masterbot_lane_receives_shared_foundations(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1]
        registry = json.loads((root / "config/masterbot-65-registry.json").read_text(encoding="utf-8"))
        expected = len(load_course_lessons())
        for row in registry["divisions"]:
            with self.subTest(masterbot=row["name"]):
                self.assertEqual(len(resources_for_masterbot(row["name"])), expected)

    def test_huggingface_full_map_includes_all_official_courses_and_ecosystem_modules(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "config/buddy-huggingface-full-learning-map.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["official_courses"]), 12)
        self.assertEqual(len(data["ecosystem_modules"]), 18)
        self.assertEqual(data["task_family_count"], 37)
        self.assertTrue(any(c["id"] == "hf-context-course" for c in data["official_courses"]))
        deep_rl = next(c for c in data["official_courses"] if c["id"] == "hf-deep-rl-course")
        self.assertEqual(deep_rl["status"], "available_low_maintenance")
        self.assertTrue(all(not c["training_data_authorized"] for c in data["official_courses"]))

    def test_freecodecamp_video_inventory_is_queued_but_truthfully_partial(self):
        from pathlib import Path
        import json
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / "buddy/bootcamp/sources/freecodecamp/catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["video_count"], len(catalog["videos"]))
        self.assertEqual(catalog["inventory"]["observed_entry_count"], len(catalog["videos"]))
        self.assertFalse(catalog["inventory"]["complete"])
        self.assertEqual(catalog["inventory_status"], "partial")
        lessons = [lesson for lesson in load_course_lessons() if lesson.track_id == "freecodecamp-video-catalog"]
        self.assertEqual(len(lessons), len(catalog["videos"]))
        self.assertTrue(all(lesson.rights_mode == "metadata_only_until_item_level_permissions" for lesson in lessons))
        self.assertTrue(all(lesson.source_url.startswith("https://www.youtube.com/watch?v=") for lesson in lessons))

    def test_course_scheduler_returns_queued_lesson_not_mastery(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        plan = plan_next_for_division(
            "DreamAIInfra",
            [Capability("LLM architecture", "ai_ml", score=0.1, failed_benchmarks=2)],
            root,
        )
        self.assertIsNotNone(plan)
        self.assertEqual(plan["completion_status"], "queued_not_studied")
        self.assertFalse(plan["mastery_awarded"])
        self.assertFalse(plan["model_weight_training_authorized"])
        self.assertFalse(plan["paid_compute_authorized"])
        self.assertTrue(plan["assessment"])
        self.assertTrue(plan["benchmark"])

    def test_unknown_division_is_rejected(self):
        with self.assertRaises(ValueError):
            resources_for_division("not-a-canonical-division")


if __name__ == "__main__":
    unittest.main()
