import json
import unittest
from pathlib import Path
from tools.build_dreamco_training_factory import FILES, build_factory_plan, _load, _hash

class DreamCoTrainingFactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configs = {name: _load(path) for name, path in FILES.items()}

    def test_builds_65_isolated_lanes_and_all_taxonomy_tasks(self):
        plan = build_factory_plan(self.configs, {k: _hash(v) for k, v in FILES.items()})
        self.assertEqual(plan["coverage"]["masterbots"], 65)
        self.assertEqual(plan["coverage"]["task_families"], 37)
        self.assertEqual(plan["coverage"]["division_task_assignments"], 2405)
        self.assertEqual(len(plan["lanes"]), 65)
        for lane in plan["lanes"]:
            self.assertEqual(len(lane["task_families"]), 37)
            self.assertFalse(lane["training_approved"])
            self.assertEqual(lane["training_status"], "NOT_RUN")
            self.assertIn("evaluation_only_holdout", lane["dataset_planes"]["isolated"])

    def test_rejects_duplicate_or_missing_task_ids(self):
        configs = json.loads(json.dumps(self.configs))
        configs["tasks"]["task_families"][1]["id"] = configs["tasks"]["task_families"][0]["id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            build_factory_plan(configs)

    def test_rejects_route_drift(self):
        configs = json.loads(json.dumps(self.configs))
        configs["taxonomy_routes"]["routes"].pop()
        with self.assertRaisesRegex(ValueError, "65 routes"):
            build_factory_plan(configs)

    def test_no_data_or_training_is_claimed(self):
        plan = build_factory_plan(self.configs)
        self.assertEqual(plan["truth_boundary"]["weights_trained"], False)
        self.assertEqual(plan["truth_boundary"]["plan_generation_does_not_create_examples"], True)
        self.assertEqual(plan["status"], "PLAN_GENERATED_NO_DATA_INGESTED_NO_TRAINING_RUN")

if __name__ == "__main__":
    unittest.main()
