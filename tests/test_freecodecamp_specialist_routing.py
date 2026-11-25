from __future__ import annotations

import unittest

from buddy.learning.course_track_registry import (
    load_course_lessons,
    resources_for_division,
    resources_for_masterbot,
)


class FreeCodeCampSpecialistRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lessons = load_course_lessons()
        cls.by_video = {
            lesson.lesson_id.removeprefix("fcc-video-"): lesson
            for lesson in cls.lessons
            if lesson.track_id == "freecodecamp-video-catalog"
        }

    def test_algorithmic_trading_routes_to_dreamfinance_not_unrelated_divisions(self):
        lesson = self.by_video["zH2Mg782XhA"]
        self.assertIn("DreamFinance", lesson.division_targets)
        self.assertNotIn("DreamAgents", lesson.division_targets)
        self.assertGreaterEqual(len(lesson.implementation_steps), 10)
        self.assertIn("paper", lesson.assessment.lower())
        finance = {row.name for row in resources_for_division("DreamFinance")}
        agents = {row.name for row in resources_for_division("DreamAgents")}
        self.assertIn(lesson.title, finance)
        self.assertNotIn(lesson.title, agents)

    def test_multi_agent_pr_reviewer_routes_to_agent_and_engineering_divisions(self):
        lesson = self.by_video["iqRcGCah0Kw"]
        self.assertIn("DreamAgents", lesson.division_targets)
        self.assertIn("CommandCore", lesson.division_targets)
        self.assertIn("independent-verifier", lesson.agent_tags)
        self.assertTrue(lesson.buddy_demo)

    def test_openclaw_and_self_healing_cicd_have_original_demonstration_steps(self):
        openclaw = self.by_video["n1sfrc-RjyM"]
        cicd = self.by_video["vj68el9hRvU"]
        self.assertIn("DreamAgents", openclaw.division_targets)
        self.assertIn("DreamCyber", openclaw.division_targets)
        self.assertIn("DreamAIInfra", cicd.division_targets)
        self.assertGreaterEqual(len(openclaw.implementation_steps), 10)
        self.assertGreaterEqual(len(cicd.implementation_steps), 10)

    def test_every_cataloged_typescript_video_gets_specialist_routing(self):
        typescript = [row for row in self.by_video.values() if "typescript" in row.title.casefold()]
        self.assertGreaterEqual(len(typescript), 20)
        self.assertTrue(all(row.division_targets for row in typescript))
        self.assertTrue(all("DreamCodeLab" in row.division_targets for row in typescript))


    def test_agentic_ai_machine_learning_and_mlops_courses_have_demonstrable_paths(self):
        agentic = self.by_video["Zy7EXDONlTY"]
        ml = self.by_video["i_LwzRVP7bg"]
        from_scratch = self.by_video["vDDjtwQDw2k"]
        mlops = self.by_video["tVskbekONlw"]
        for lesson in (agentic, ml, from_scratch, mlops):
            self.assertEqual(lesson.content_status, "original_implementation_brief")
            self.assertGreaterEqual(len(lesson.implementation_steps), 8)
            self.assertTrue(lesson.buddy_demo)
        self.assertIn("DreamAgents", agentic.division_targets)
        self.assertIn("DreamAIInfra", ml.division_targets)
        self.assertIn("DreamScience", from_scratch.division_targets)
        self.assertIn("MLflow", mlops.tool_tags)
        infra = {row.name for row in resources_for_division("DreamAIInfra")}
        agents = {row.name for row in resources_for_division("DreamAgents")}
        self.assertIn(mlops.title, infra)
        self.assertIn(agentic.title, agents)


    def test_subject_category_routing_covers_courses_without_keywords_in_the_title(self):
        mcp_security = self.by_video["gYXLRMycVMk"]
        computer_vision = self.by_video["Q5U-b6gRTaY"]
        self.assertEqual(mcp_security.content_status, "original_implementation_brief")
        self.assertIn("DreamAgents", mcp_security.division_targets)
        self.assertEqual(computer_vision.content_status, "original_implementation_brief")
        self.assertIn("DreamAIInfra", computer_vision.division_targets)
        self.assertGreaterEqual(len(mcp_security.implementation_steps), 8)
        self.assertGreaterEqual(len(computer_vision.implementation_steps), 8)

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
        trade_resources = {row.name for row in resources_for_masterbot("DreamTrade")}
        self.assertIn(self.by_video["zH2Mg782XhA"].title, trade_resources)


if __name__ == "__main__":
    unittest.main()
