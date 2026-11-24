import unittest

from tools.validate_buddy_continuous_study_policy import validate


def fixture():
    return {
        "schema": "dreamco.buddy_continuous_study_policy.v1",
        "schedule": {
            "mode": "continuous_24x7_with_resource_governors",
            "daily_lesson_slots_per_division": 5,
            "division_count": 65,
            "daily_planned_slots": 325,
        },
        "mastery": {
            "require_holdout_for_mastery": True,
            "regression_must_pass": True,
        },
        "resource_governors": {
            "paid_compute_requires_separate_approval": True,
            "pause_when_no_authorized_work_exists": True,
        },
        "source_permissions": {
            "transcript_download_default": False,
            "media_download_default": False,
            "model_training_default": False,
            "unknown_rights": "BLOCKED",
        },
        "model_build": {
            "target_parameters_per_division": 45000000,
            "no_claim_of_gpt5_equivalence": True,
        },
    }


class ContinuousStudyPolicyTests(unittest.TestCase):
    def test_valid_policy(self):
        registry = {"divisions": [{"id": i} for i in range(1, 66)]}
        self.assertEqual(validate(fixture(), registry), [])

    def test_rejects_wrong_slot_count(self):
        policy = fixture()
        policy["schedule"]["daily_planned_slots"] = 320
        registry = {"divisions": [{"id": i} for i in range(1, 66)]}
        self.assertIn(
            "daily_planned_slots must equal per-division slots times registry size",
            validate(policy, registry),
        )

    def test_rejects_unknown_rights_or_auto_training(self):
        policy = fixture()
        policy["source_permissions"]["model_training_default"] = True
        policy["source_permissions"]["unknown_rights"] = "ALLOW"
        registry = {"divisions": [{"id": i} for i in range(1, 66)]}
        errors = validate(policy, registry)
        self.assertIn("model_training_default must remain false by default", errors)
        self.assertIn("unknown rights must be blocked", errors)

    def test_rejects_missing_divisions_and_gpt5_claim(self):
        policy = fixture()
        policy["model_build"]["no_claim_of_gpt5_equivalence"] = False
        registry = {"divisions": [{"id": i} for i in range(1, 64)]}
        errors = validate(policy, registry)
        self.assertIn("canonical registry must contain exactly 65 divisions", errors)
        self.assertIn("parameter count must not be presented as GPT-5 equivalence", errors)


if __name__ == "__main__":
    unittest.main()
