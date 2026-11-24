import unittest
from buddy.models.division_model_registry import load_division_model_registry,validate_division_model_registry,get_division_model_identity

class DivisionModelRegistryTests(unittest.TestCase):
 def test_all_65_divisions_have_independent_model_identities(self):
  payload=load_division_model_registry()
  self.assertEqual(payload["canonical_division_count"],65)
  self.assertEqual(len(payload["divisions"]),65)
  self.assertEqual(len({x["model_name"] for x in payload["divisions"]}),65)
  self.assertEqual(len({x["artifacts"]["weights_path"] for x in payload["divisions"]}),65)
  self.assertEqual(len({x["artifacts"]["checkpoints_path"] for x in payload["divisions"]}),65)
  self.assertEqual(len({x["tokenizer"]["artifact_path"] for x in payload["divisions"]}),65)
 def test_identity_contains_versioned_artifacts_and_runtime_gate(self):
  model=get_division_model_identity(1)
  self.assertEqual(model["model_name"],"dreamco/dreamfinance-mini")
  self.assertEqual(model["model_version"],"0.1.0")
  self.assertIn("checkpoints",model["artifacts"]["checkpoints_path"])
  self.assertFalse(model["runtime_policy"]["production_serving_enabled"])
  self.assertEqual(model["model_status"],"SPECIFIED_NOT_TRAINED")
 def test_validator_rejects_shared_weights_directory(self):
  payload=load_division_model_registry()
  payload["divisions"][1]["artifacts"]["weights_path"]=payload["divisions"][0]["artifacts"]["weights_path"]
  with self.assertRaisesRegex(ValueError,"weights_path"): validate_division_model_registry(payload)
 def test_validator_rejects_fabricated_training_state(self):
  payload=load_division_model_registry()
  payload["divisions"][0]["model_status"]="TRAINED"
  with self.assertRaisesRegex(ValueError,"fabricate"): validate_division_model_registry(payload)

if __name__=="__main__": unittest.main()
