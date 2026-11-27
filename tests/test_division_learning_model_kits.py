import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools/build_division_learning_model_kits.py"
spec = importlib.util.spec_from_file_location("division_learning_model_kits", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DivisionLearningModelKitTests(unittest.TestCase):
    def test_generates_exactly_195_manifests_for_65_lanes(self):
        manifests = module.build_manifests()
        self.assertEqual(len(manifests), 195)
        self.assertEqual(len({path.split("/")[3] for path in manifests}), 65)
        self.assertEqual(
            {Path(path).name for path in manifests},
            {"nano_18m.json", "core_120m.json", "master_teacher.json"},
        )

    def test_each_lane_has_all_three_untrained_tiers(self):
        manifests = module.build_manifests()
        by_lane = {}
        for path, payload in manifests.items():
            lane = payload["division"]["lane_id"]
            by_lane.setdefault(lane, set()).add(payload["kit"]["id"])
            self.assertFalse(payload["kit"]["weights_present"])
            self.assertFalse(payload["kit"]["training_authorized"])
            self.assertFalse(payload["release"]["marketplace_eligible"])
            self.assertFalse(payload["release"]["production_eligible"])
        self.assertEqual(len(by_lane), 65)
        self.assertTrue(all(len(tiers) == 3 for tiers in by_lane.values()))

    def test_teacher_size_is_not_invented(self):
        manifests = module.build_manifests()
        teacher = [p for p in manifests.values() if p["kit"]["id"] == "master_teacher"]
        self.assertEqual(len(teacher), 65)
        self.assertTrue(all(p["kit"]["target_parameters"] is None for p in teacher))
        self.assertTrue(all(p["status"] == "ARCHITECTURE_AND_SIZE_TO_BE_DEFINED" for p in teacher))

    def test_crosswalk_does_not_grant_domain_ownership(self):
        manifests = module.build_manifests()
        self.assertTrue(all(
            p["division"]["domain_mapping_status"] == "REVIEW_REQUIRED_NOT_AUTHORIZED"
            for p in manifests.values()
        ))

    def test_write_and_check_are_deterministic(self):
        manifests = module.build_manifests()
        with tempfile.TemporaryDirectory() as tmp:
            original_root = module.ROOT
            original_out = module.OUT
            try:
                module.ROOT = Path(tmp)
                module.OUT = module.ROOT / "config/generated/division-learning-model-kits"
                module.write_manifests(manifests)
                self.assertEqual(module.check_manifests(manifests), [])
                first = (module.ROOT / next(iter(manifests))).read_text(encoding="utf-8")
                module.write_manifests(manifests)
                second = (module.ROOT / next(iter(manifests))).read_text(encoding="utf-8")
                self.assertEqual(first, second)
            finally:
                module.ROOT = original_root
                module.OUT = original_out


if __name__ == "__main__":
    unittest.main()
