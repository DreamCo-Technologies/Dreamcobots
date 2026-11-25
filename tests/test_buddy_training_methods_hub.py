import unittest
from buddy.bootcamp.training_methods_hub import METHODS, PROVIDERS, TrainingRequest, propose


class TrainingHubTests(unittest.TestCase):
    def test_methods_cover_retrieval_token_and_weight_training(self):
        for name in ("rag", "skill_pack", "tokenizer_training", "continued_pretraining",
                     "lora", "qlora", "sft", "dpo", "grpo", "distillation"):
            self.assertIn(name, METHODS)

    def test_zero_budget_has_local_and_free_options_only(self):
        result = propose(TrainingRequest("rag", 0, True, True))
        ids = {row["id"] for row in result["providers"]}
        self.assertIn("local_cpu", ids)
        self.assertIn("colab", ids)
        self.assertNotIn("runpod", ids)
        self.assertFalse(result["training_started"])
        self.assertFalse(result["purchase_or_paid_request_started"])

    def test_rag_requires_content_rights_but_not_model_license(self):
        self.assertFalse(propose(TrainingRequest("rag", 0, False, True))["eligible_for_review"])
        result = propose(TrainingRequest("rag", 0, True, True, False))
        self.assertTrue(result["eligible_for_review"])
        self.assertFalse(result["requires_model_license"])

    def test_weight_methods_require_rights_owner_and_model_license(self):
        self.assertFalse(propose(TrainingRequest("sft", 0, False, True, True))["eligible_for_review"])
        self.assertFalse(propose(TrainingRequest("sft", 0, True, False, True))["eligible_for_review"])
        self.assertFalse(propose(TrainingRequest("sft", 0, True, True, False))["eligible_for_review"])
        self.assertTrue(propose(TrainingRequest("sft", 0, True, True, True))["eligible_for_review"])

    def test_tokenizer_training_requires_content_rights_but_not_base_model_license(self):
        result = propose(TrainingRequest("tokenizer_training", 0, True, True, False))
        self.assertTrue(result["eligible_for_review"])
        self.assertTrue(result["requires_content_rights"])
        self.assertFalse(result["requires_model_license"])

    def test_invalid_inputs(self):
        requests = [
            TrainingRequest("invalid", 0, True, True),
            TrainingRequest("rag", -1, True, True),
            TrainingRequest("rag", float("nan"), True, True),
            TrainingRequest("rag", float("inf"), True, True),
            TrainingRequest("rag", True, True, True),
            TrainingRequest("rag", 0, 1, True),
        ]
        for request in requests:
            with self.subTest(request=request):
                with self.assertRaises(ValueError):
                    propose(request)

    def test_no_provider_claimed_live_or_priced(self):
        self.assertGreater(len(PROVIDERS), 8)
        result = propose(TrainingRequest("rag", 20, True, True))
        self.assertTrue(all(not row["availability_verified"] for row in result["providers"]))
        self.assertTrue(all(not row["price_verified"] for row in result["providers"]))
        self.assertTrue(result["approval_required"])
        self.assertFalse(result["training_started"])


if __name__ == "__main__":
    unittest.main()
