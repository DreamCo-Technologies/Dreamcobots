import json,tempfile,unittest
from pathlib import Path
from buddy.datasets.hub import DatasetHub,DatasetPolicyError
from buddy.datasets.private_holdout_jobs import create_private_holdout_job
from buddy.datasets.private_holdout_runner import PrivateHoldoutBenchmarkError,score_prediction,validate_private_holdout_job

def holdout_card():
 return {"dataset_id":"finance.private.holdout","name":"Finance private eval","owner":"DreamCo",
 "license":"CC-BY-4.0","license_url":"https://example.org/license","source_url":"https://example.org/source",
 "source":"dreamco","source_id":"finance-eval-001","data_plane":"evaluation_only_holdout",
 "holdout":True,"training_approved":False,"evaluation_approved":True,"rights_status":"VERIFIED",
 "rights_evidence":"review-eval-1","privacy_review":"PASSED","primary_masterbot_id":1,"max_duplicate_rate":0.01}

def candidate(model,role):
 return {"model_id":model,"revision":"a"*40,"license":"Apache-2.0",
 "license_url":"https://example.org/model-license","license_status":"VERIFIED",
 "license_evidence":"model-review-1","role":role}

class PrivateHoldoutTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.hub=DatasetHub(self.root/"hub")
  self.source=self.root/"holdout.jsonl"
  rows=[{"masterbot_id":1,"split":"test","task_id":"finance-001","prompt":"Compute 2 + 2","expected":"4","metric":"exact_match"},
        {"masterbot_id":1,"split":"test","task_id":"finance-002","prompt":"Name currency of Japan","expected":"yen","metric":"token_f1"}]
  self.source.write_text("".join(json.dumps(x)+"\n" for x in rows),encoding="utf-8")
  self.card=self.hub.register_evaluation_holdout(holdout_card(),self.source)
  self.candidates=[candidate("base/model","baseline"),candidate("dreamco/finance-adapter","trained_candidate")]
 def tearDown(self): self.tmp.cleanup()
 def test_holdout_is_stored_as_not_training_approved(self):
  card=self.hub.get(self.card["dataset_id"])
  self.assertTrue(card["holdout"]);self.assertFalse(card["training_approved"])
  self.assertEqual(card["data_plane"],"evaluation_only_holdout")
  self.assertIn("test_sha256",card["split_manifest"])
 def test_job_requires_holdout_and_pins_hashes(self):
  job=create_private_holdout_job(self.hub,self.card["dataset_id"],1,self.candidates,"compute-1",self.root/"jobs")
  obj,rows=validate_private_holdout_job(json.loads(Path(job["manifest_path"]).read_text()),"compute-1")
  self.assertEqual(len(rows),2);self.assertTrue(obj.is_file())
  self.assertFalse(job["training_started"])
 def test_wrong_approval_is_rejected(self):
  job=create_private_holdout_job(self.hub,self.card["dataset_id"],1,self.candidates,"compute-1",self.root/"jobs")
  payload=json.loads(Path(job["manifest_path"]).read_text())
  with self.assertRaisesRegex(PrivateHoldoutBenchmarkError,"approval"):
   validate_private_holdout_job(payload,"wrong")
 def test_holdout_cannot_be_registered_as_training_data(self):
  bad=holdout_card();bad["training_approved"]=True
  with self.assertRaises(DatasetPolicyError): self.hub.register_evaluation_holdout(bad,self.source)
 def test_owner_mismatch_and_data_tampering_are_rejected(self):
  job=create_private_holdout_job(self.hub,self.card["dataset_id"],1,self.candidates,"compute-1",self.root/"jobs")
  payload=json.loads(Path(job["manifest_path"]).read_text());payload["masterbot_id"]=2
  with self.assertRaisesRegex(PrivateHoldoutBenchmarkError,"owner_mismatch"):
   validate_private_holdout_job(payload,"compute-1")
  payload=json.loads(Path(job["manifest_path"]).read_text())
  obj=self.hub.home/payload["dataset_object_path"];obj.write_text("{}\n")
  with self.assertRaisesRegex(PrivateHoldoutBenchmarkError,"hash_mismatch"):
   validate_private_holdout_job(payload,"compute-1")
 def test_metric_helpers(self):
  self.assertEqual(score_prediction("4","4")["exact_match"],1.0)
  self.assertEqual(score_prediction("yen","yen")["token_f1"],1.0)
  self.assertEqual(score_prediction("dollars","yen")["token_f1"],0.0)

if __name__=="__main__":unittest.main()
