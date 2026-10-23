import unittest
from buddy.bootcamp.training_methods_hub import METHODS, PROVIDERS, TrainingRequest, propose

class TrainingHubTests(unittest.TestCase):
    def test_methods_cover_token_and_weight_training(self):
        for name in ("tokenizer_training", "continued_pretraining", "lora", "qlora", "sft", "dpo", "grpo", "distillation", "rag"):
            self.assertIn(name, METHODS)

    def test_zero_budget_has_free_options(self):
        result = propose(TrainingRequest("rag", 0, False, False))
        self.assertTrue(any(x["id"] == "colab" for x in result["providers"]))
        self.assertFalse(result["training_started"])

    def test_weights_require_rights_and_approval(self):
        self.assertFalse(propose(TrainingRequest("sft", 0, False, True))["eligible_for_review"])
        self.assertTrue(propose(TrainingRequest("sft", 0, True, True, True))["eligible_for_review"])

    def test_invalid_inputs(self):
        for req in (TrainingRequest("invalid", 0, True, True), TrainingRequest("rag", -1, True, True)):
            with self.assertRaises(ValueError):
                propose(req)

    def test_no_provider_claimed_live(self):
        self.assertGreater(len(PROVIDERS), 8)
        self.assertTrue(all(not x["availability_verified"] for x in propose(TrainingRequest("rag", 20, False, False))["providers"]))

if __name__ == "__main__":
    unittest.main()
