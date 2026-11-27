import unittest
from buddy.bootcamp.model_capability_parity import validate_capability_evidence, select_learner_model_path, ALLOWED_STATUSES

class ModelCapabilityParityTests(unittest.TestCase):
    def valid(self, **overrides):
        row={"capability_id":"vision","implementation_ref":"src/vision","acceptance_test_ref":"tests/vision","safety_test_ref":"tests/vision_safety","evidence_ref":"artifacts/run-1","status":"live_verified","repetitions":3,"hidden_holdout_pass":True,"safety_pass":True}
        row.update(overrides)
        return row

    def test_live_verified_requires_three_runs_holdout_and_safety(self):
        self.assertTrue(validate_capability_evidence(self.valid())["verified"])
        for changes in ({"repetitions":2},{"hidden_holdout_pass":False},{"safety_pass":False}):
            with self.assertRaises(ValueError):
                validate_capability_evidence(self.valid(**changes))

    def test_missing_references_and_unknown_status_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_capability_evidence(self.valid(evidence_ref=""))
        with self.assertRaises(ValueError):
            validate_capability_evidence(self.valid(status="frontier"))

    def test_unsupported_requires_reason_and_does_not_claim_verified(self):
        with self.assertRaises(ValueError):
            validate_capability_evidence(self.valid(status="unsupported"))
        result=validate_capability_evidence(self.valid(status="unsupported",reason="hardware unavailable"))
        self.assertFalse(result["verified"])

    def test_model_path_distinguishes_product_from_training_weights(self):
        registry={"learner_model_paths":[
            {"id":"model-powered-product","label":"Product","result":"No weights"},
            {"id":"fine_tuned_model","label":"Fine tune","result":"Adapter"}
        ]}
        self.assertEqual(select_learner_model_path("model-powered-product",registry)["result"],"No weights")
        with self.assertRaises(ValueError):
            select_learner_model_path("mystery",registry)

    def test_status_registry_is_closed_and_explicit(self):
        self.assertIn("live_verified",ALLOWED_STATUSES)
        self.assertIn("unsupported",ALLOWED_STATUSES)

if __name__ == "__main__":
    unittest.main()
