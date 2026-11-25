from __future__ import annotations

import json
import unittest
from pathlib import Path

from buddy.learning.course_track_registry import (
    load_course_lessons,
    resources_for_division,
)

ROOT = Path(__file__).resolve().parents[1]


class FreeCodeCampSpecialistRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lessons = load_course_lessons()
        cls.by_video = {
            lesson.source_video_id: lesson
            for lesson in cls.lessons
            if lesson.track_id == "freecodecamp-video-catalog"
        }
        cls.paths_by_video = {
            lesson.source_video_id: lesson
            for lesson in cls.lessons
            if lesson.track_id == "freecodecamp-specialist-learning-paths"
        }

    def test_algorithmic_trading_routes_to_dreamfinance_not_unrelated_divisions(self):
        metadata = self.by_video["zH2Mg782XhA"]
        lesson = self.paths_by_video["zH2Mg782XhA"]
        self.assertEqual(metadata.content_status, "metadata_only")
        self.assertIn("DreamFinance", metadata.division_targets)
        self.assertEqual(lesson.content_status, "original_implementation_brief")
        self.assertIn("DreamFinance", lesson.division_targets)
        self.assertNotIn("DreamAgents", lesson.division_targets)
        self.assertGreaterEqual(len(lesson.implementation_steps), 10)
        self.assertIn("paper", lesson.assessment.lower())
        study_ready = {row.name for row in resources_for_division("DreamFinance")}
        self.assertNotIn(lesson.title, study_ready)
        self.assertNotIn(metadata.title, study_ready)

    def test_multi_agent_pr_reviewer_routes_to_agent_and_engineering_divisions(self):
        lesson = self.paths_by_video["iqRcGCah0Kw"]
        self.assertIn("DreamAgents", lesson.division_targets)
        self.assertIn("CommandCore", lesson.division_targets)
        self.assertIn("independent-verifier", lesson.agent_tags)
        self.assertTrue(lesson.buddy_demo)

    def test_openclaw_and_self_healing_cicd_have_original_demonstration_steps(self):
        openclaw = self.paths_by_video["n1sfrc-RjyM"]
        cicd = self.paths_by_video["vj68el9hRvU"]
        self.assertIn("DreamAgents", openclaw.division_targets)
        self.assertIn("DreamCyber", openclaw.division_targets)
        self.assertIn("DreamAIInfra", cicd.division_targets)
        self.assertGreaterEqual(len(openclaw.implementation_steps), 10)
        self.assertGreaterEqual(len(cicd.implementation_steps), 10)

    def test_every_cataloged_typescript_video_gets_specialist_routing(self):
        typescript = [row for row in self.by_video.values() if "typescript" in row.title.casefold()]
        self.assertGreaterEqual(len(typescript), 20)
        self.assertTrue(all(row.content_status == "metadata_only" for row in typescript))
        self.assertTrue(all("DreamCodeLab" in row.division_targets for row in typescript))
        self.assertTrue(all(row.source_video_id in self.paths_by_video for row in typescript))

    def test_agentic_ai_machine_learning_and_mlops_courses_have_demonstrable_paths(self):
        agentic = self.paths_by_video["Zy7EXDONlTY"]
        ml = self.paths_by_video["i_LwzRVP7bg"]
        from_scratch = self.paths_by_video["vDDjtwQDw2k"]
        mlops = self.paths_by_video["tVskbekONlw"]
        for lesson in (agentic, ml, from_scratch, mlops):
            self.assertEqual(lesson.content_status, "original_implementation_brief")
            self.assertGreaterEqual(len(lesson.implementation_steps), 8)
            self.assertTrue(lesson.buddy_demo)
        self.assertIn("DreamAgents", agentic.division_targets)
        self.assertIn("DreamAIInfra", ml.division_targets)
        self.assertIn("DreamScience", from_scratch.division_targets)
        self.assertIn("MLflow", mlops.tool_tags)
        self.assertNotIn(mlops.title, {row.name for row in resources_for_division("DreamAIInfra")})

    def test_subject_category_routing_covers_courses_without_keywords_in_the_title(self):
        mcp_security = self.by_video["gYXLRMycVMk"]
        computer_vision = self.by_video["Q5U-b6gRTaY"]
        self.assertEqual(mcp_security.content_status, "metadata_only")
        self.assertIn("DreamAgents", mcp_security.division_targets)
        self.assertEqual(computer_vision.content_status, "metadata_only")
        self.assertIn("DreamAIInfra", computer_vision.division_targets)
        self.assertGreaterEqual(len(self.paths_by_video["gYXLRMycVMk"].implementation_steps), 8)
        self.assertGreaterEqual(len(self.paths_by_video["Q5U-b6gRTaY"].implementation_steps), 8)

    def test_every_cataloged_machine_learning_agentic_and_devops_video_is_routed(self):
        catalog = json.loads((ROOT / "buddy/bootcamp/sources/freecodecamp/catalog.json").read_text(encoding="utf-8"))
        checks = [
            ("machine_learning_and_deep_learning", "DreamAIInfra"),
            ("ai_agents_and_mcp", "DreamAgents"),
            ("cloud_devops_and_ci_cd", "DreamOps"),
        ]
        for category, division in checks:
            rows = [row for row in catalog["videos"] if category in row.get("categories", [])]
            self.assertTrue(rows, category)
            for row in rows:
                metadata = self.by_video[row["video_id"]]
                path = self.paths_by_video[row["video_id"]]
                self.assertEqual(metadata.content_status, "metadata_only", row["video_id"])
                self.assertIn(division, metadata.division_targets, row["video_id"])
                self.assertEqual(path.content_status, "original_implementation_brief", row["video_id"])
                self.assertIn(division, path.division_targets, row["video_id"])

    def test_course_overrides_reference_real_divisions_and_masterbot_lanes(self):
        canonical = {
            name for row in self.lessons for name in row.division_targets
        }
        masterbots = {
            name for row in self.lessons for name in row.masterbot_targets
        }
        self.assertIn("DreamFinance", canonical)
        self.assertIn("DreamAgents", canonical)
        self.assertIn("DreamQuality", masterbots)
        self.assertIn("DreamTrade", self.paths_by_video["zH2Mg782XhA"].masterbot_targets)


if __name__ == "__main__":
    unittest.main()
