import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/human-ai-robot-collaboration-taxonomy.json"


class HumanAIRobotTaxonomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CONFIG.read_text(encoding="utf-8"))

    def test_schema_and_required_participants(self):
        self.assertEqual(self.data["schema"], "dreamco.human_ai_robot_collaboration_taxonomy.v1")
        ids = {item["id"] for item in self.data["allocation_agents"]}
        self.assertTrue({"human", "ai", "robot", "human_ai", "human_robot", "ai_robot", "human_ai_robot"} <= ids)

    def test_unknowns_fail_closed(self):
        self.assertEqual(self.data["coverage_policy"]["unknown_capability_defaults_to"], "not_assessed")
        self.assertTrue(self.data["coverage_policy"]["no_unverified_autonomy"])

    def test_task_records_preserve_accountability_and_evidence(self):
        required = set(self.data["task_record_required_fields"])
        self.assertTrue({"recommended_allocation", "human_responsibility", "safety_controls", "fallback_plan", "evidence"} & required)
        self.assertIn("human", {item["id"] for item in self.data["allocation_agents"]})

    def test_examples_are_labeled_as_illustrative(self):
        self.assertGreaterEqual(len(self.data["initial_task_examples"]), 3)
        self.assertIn("not a completed scan", self.data["truth_boundary"])


if __name__ == "__main__":
    unittest.main()
