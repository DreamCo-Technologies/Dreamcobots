import unittest

from tools.validate_buddy_continuous_study_policy import validate


def crosswalk_fixture():
    domains = []
    for index in range(1, 46):
        domains.append({"domain_id": f"core-{index}", "mapping_status": "proposed_exact_name_match"})
    for index in range(1, 11):
        domains.append({"domain_id": f"supplemental-{index}", "mapping_status": "unresolved"})
    return {"domains": domains}


def fixture():
    return {
        "schema": "dreamco.buddy_continuous_study_policy.v1",
        "schedule": {
            "mode": "continuous_24x7_with_resource_governors",
            "domain_count": 55,
            "masterbot_count": 65,
            "shared_platform_masterbot_count": 20,
            "daily_lesson_slots_per_domain": 5,
            "daily_planned_slots": 275,
        },
        "mastery": {"require_holdout_for_mastery": True, "regression_must_pass": True},
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
    def test_valid_policy_separates_domains_from_shared_masterbots(self):
        self.assertEqual(validate(fixture(), crosswalk_fixture()), [])

    def test_rejects_wrong_slot_count(self):
        policy = fixture()
        policy["schedule"]["daily_planned_slots"] = 320
        self.assertIn(
            "daily_planned_slots must equal per-domain slots times the 55 domain profiles",
            validate(policy, crosswalk_fixture()),
        )

    def test_rejects_wrong_domain_and_masterbot_counts(self):
        policy = fixture()
        policy["schedule"]["domain_count"] = 65
        policy["schedule"]["shared_platform_masterbot_count"] = 10
        errors = validate(policy, crosswalk_fixture())
        self.assertIn("domain_count must be 55; shared-platform MasterBots are not divisions", errors)
        self.assertIn("65 MasterBots must remain separate from the 55 domain divisions", errors)

    def test_rejects_unknown_rights_or_auto_training(self):
        policy = fixture()
        policy["source_permissions"]["model_training_default"] = True
        policy["source_permissions"]["unknown_rights"] = "ALLOW"
        errors = validate(policy, crosswalk_fixture())
        self.assertIn("model_training_default must remain false by default", errors)
        self.assertIn("unknown rights must be blocked", errors)

    def test_rejects_missing_domains_and_gpt5_claim(self):
        policy = fixture()
        policy["model_build"]["no_claim_of_gpt5_equivalence"] = False
        errors = validate(policy, {"domains": crosswalk_fixture()["domains"][:54]})
        self.assertIn("canonical crosswalk must contain exactly 55 domain divisions", errors)
        self.assertIn("parameter count must not be presented as GPT-5 equivalence", errors)

    def test_rejects_changed_45_10_mapping_counts(self):
        domains = crosswalk_fixture()
        domains["domains"][0]["mapping_status"] = "unresolved"
        errors = validate(fixture(), domains)
        self.assertIn("crosswalk must preserve 45 original core domains", errors)
        self.assertIn("crosswalk must preserve 10 supplemental domains pending owner review", errors)


if __name__ == "__main__":
    unittest.main()
