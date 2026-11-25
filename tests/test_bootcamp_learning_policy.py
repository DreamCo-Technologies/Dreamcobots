import unittest
from buddy.bootcamp.learning_policy import evaluate_bootcamp_learning_use

class FirstPartyBootcampLearningPolicyTests(unittest.TestCase):
    def base(self):
        return {"scope":"first_party_dreamco","ownership_confirmed":True,
                "contains_unlicensed_third_party_material":False,"learner_submitted":False,
                "contains_personal_data":False,"contains_secrets":False,"safety_review_passed":True}

    def test_dreamco_owned_course_asset_needs_no_repeated_consent(self):
        result=evaluate_bootcamp_learning_use(self.base())
        self.assertTrue(result["eligible"])
        self.assertIn("internal_model_training",result["allowed_uses"])

    def test_external_material_is_not_covered_by_standing_authorization(self):
        asset=self.base(); asset["scope"]="external"
        result=evaluate_bootcamp_learning_use(asset)
        self.assertFalse(result["eligible"])
        self.assertTrue(result["requires_separate_permission"])

    def test_third_party_material_and_learner_submissions_are_excluded(self):
        for key in ("contains_unlicensed_third_party_material","learner_submitted"):
            asset=self.base(); asset[key]=True
            self.assertFalse(evaluate_bootcamp_learning_use(asset)["eligible"])

    def test_privacy_secrets_and_safety_gates_remain(self):
        for key in ("contains_personal_data","contains_secrets"):
            asset=self.base(); asset[key]=True
            self.assertFalse(evaluate_bootcamp_learning_use(asset)["eligible"])
        asset=self.base(); asset["safety_review_passed"]=False
        self.assertFalse(evaluate_bootcamp_learning_use(asset)["eligible"])

    def test_ownership_must_be_confirmed(self):
        asset=self.base(); asset["ownership_confirmed"]=False
        self.assertFalse(evaluate_bootcamp_learning_use(asset)["eligible"])

if __name__ == "__main__":
    unittest.main()
