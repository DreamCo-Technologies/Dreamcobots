import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_division_model_fleet as fleet

class DivisionModelFleetTests(unittest.TestCase):
    def test_generates_one_independent_profile_per_masterbot(self):
        profiles = fleet.build_profiles()
        self.assertEqual(len(profiles), 65)
        self.assertEqual(len({p["division_model_id"] for p in profiles}), 65)
        self.assertTrue(all(p["independence_contract"]["division_owned_task_runner"] for p in profiles))
        self.assertTrue(all(p["independence_contract"]["buddy_is_coordinator_not_hidden_solver"] for p in profiles))

    def test_profiles_do_not_claim_training_or_mastery(self):
        for profile in fleet.build_profiles():
            self.assertEqual(profile["model_identity"]["status"], "PROFILE_ONLY_NOT_TRAINED")
            self.assertFalse(profile["training"]["weights_trained"])
            self.assertEqual(profile["promotion"]["status"], "BLOCKED_NO_EVIDENCE")
            self.assertFalse(profile["promotion"]["automatic_production_update"])

    def test_domain_crosswalk_is_explicitly_unresolved(self):
        self.assertTrue(all(p["domain_crosswalk"]["primary_domain_id"] is None for p in fleet.build_profiles()))

if __name__ == "__main__":
    unittest.main()
