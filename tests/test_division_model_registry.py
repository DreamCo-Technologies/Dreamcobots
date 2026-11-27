import tempfile
import unittest
from pathlib import Path
from buddy.models.division_model_registry import load_division_model_registry,validate_division_model_registry,get_division_model_identity
from buddy.datasets.training_jobs import create_training_job

class FakeHub:
 def __init__(self,home,card): self.home=Path(home);self.card=card
 def get(self,dataset_id): return self.card if dataset_id==self.card["dataset_id"] else None

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
 def test_training_job_carries_isolated_model_identity_and_database_namespace(self):
  card={"dataset_id":"fixture.dataset","version":1,"content_sha256":"a"*64,
   "object_path":"objects/fixture.jsonl","split_manifest":{"train_sha256":"1"*64,
   "validation_sha256":"2"*64,"test_sha256":"3"*64},"training_approved":True,
   "rights_status":"VERIFIED","holdout":False,"data_plane":"licensed_training",
   "primary_masterbot_id":1,"collaborating_masterbot_ids":[]}
  with tempfile.TemporaryDirectory() as tmp:
   hub=FakeHub(Path(tmp)/"hub",card)
   job=create_training_job(hub,"fixture.dataset",1,"owner/approved-base-model","b"*40,
    compute_approval_id="compute-approval-1",model_license="Apache-2.0",
    model_license_url="https://example.org/license",model_license_status="VERIFIED",
    model_license_evidence="model-rights-review-1",output_dir=Path(tmp)/"jobs")
   self.assertEqual(job["division_model"]["model_name"],"dreamco/dreamfinance-mini")
   self.assertEqual(job["division_model"]["database_schema"],"dreamco_division_001")
   self.assertEqual(job["division_model"]["model_version"],"0.1.0")
   self.assertTrue(job["reproducibility"]["checkpoint_hashes_required"])
 def test_training_job_requires_compute_approval(self):
  card={"dataset_id":"fixture.dataset","version":1,"content_sha256":"a"*64,
   "object_path":"objects/fixture.jsonl","split_manifest":{"train_sha256":"1"*64,
   "validation_sha256":"2"*64,"test_sha256":"3"*64},"training_approved":True,
   "rights_status":"VERIFIED","holdout":False,"data_plane":"licensed_training",
   "primary_masterbot_id":1,"collaborating_masterbot_ids":[]}
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(Exception,"compute budget approval"):
    create_training_job(FakeHub(Path(tmp)/"hub",card),"fixture.dataset",1,
     "owner/base","b"*40,model_license="Apache-2.0",
     model_license_url="https://example.org/license",model_license_status="VERIFIED",
     model_license_evidence="review",output_dir=Path(tmp)/"jobs")

if __name__=="__main__": unittest.main()
