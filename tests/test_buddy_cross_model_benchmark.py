from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from buddy.datasets.hub import DatasetHub,DatasetPolicyError
from buddy.datasets.benchmark_jobs import create_benchmark_job
from buddy.datasets.benchmark_runner import validate_benchmark_job,BenchmarkExecutionError
from buddy.datasets.transformers_runner import _split_hash

class CrossModelBenchmarkTests(unittest.TestCase):
 def test_job_requires_verified_baseline_and_alternatives(self):
  with tempfile.TemporaryDirectory() as temp:
   rows=[{"split":"train","masterbot_id":41,"text":"train"},{"split":"validation","masterbot_id":41,"text":"validate"},{"split":"test","masterbot_id":41,"text":"heldout"}]
   sample=Path(temp)/"data.jsonl";sample.write_text("".join(json.dumps(x)+"\n" for x in rows))
   card={"name":"bench","owner":"DreamCo","license":"internal","license_url":"https://example.com/license","source_url":"https://github.com/DreamCo-Technologies/Dreamcobots","data_plane":"dreamco_owned_training","rights_status":"VERIFIED","training_approved":True,"rights_evidence":"review-1","primary_masterbot_id":41,"collaborating_masterbot_ids":[],"split_manifest":{f"{s}_sha256":_split_hash(rows,s) for s in ("train","validation","test")}}
   hub=DatasetHub(Path(temp)/"hub");registered=hub.register(card,sample)
   models=[{"model_id":"org/base","revision":"1"*40,"license":"apache-2.0","license_url":"https://example.com/license","license_status":"VERIFIED","license_evidence":"review-base","role":"baseline"},
    {"model_id":"org/alt","revision":"2"*40,"license":"mit","license_url":"https://example.com/license","license_status":"VERIFIED","license_evidence":"review-alt","role":"open_weight_alternative"}]
   job=create_benchmark_job(hub,registered["dataset_id"],41,models,"compute-review-1",Path(temp)/"jobs")
   manifest=json.loads(Path(job["manifest_path"]).read_text())
   obj,holdout=validate_benchmark_job(manifest,"compute-review-1")
   self.assertEqual(len(holdout),1);self.assertTrue(obj.is_file())
 def test_unverified_model_license_is_blocked(self):
  with tempfile.TemporaryDirectory() as temp:
   rows=[{"split":"train","masterbot_id":41,"text":"train"},{"split":"validation","masterbot_id":41,"text":"validate"},{"split":"test","masterbot_id":41,"text":"heldout"}]
   sample=Path(temp)/"data.jsonl";sample.write_text("".join(json.dumps(x)+"\n" for x in rows))
   card={"name":"bench","owner":"DreamCo","license":"internal","license_url":"https://example.com/license","source_url":"https://github.com/DreamCo-Technologies/Dreamcobots","data_plane":"dreamco_owned_training","rights_status":"VERIFIED","training_approved":True,"rights_evidence":"review-1","primary_masterbot_id":41,"collaborating_masterbot_ids":[],"split_manifest":{f"{s}_sha256":_split_hash(rows,s) for s in ("train","validation","test")}}
   hub=DatasetHub(Path(temp)/"hub");registered=hub.register(card,sample)
   models=[{"model_id":"org/base","revision":"1"*40,"license":"apache-2.0","license_url":"https://example.com/license","license_status":"UNKNOWN","license_evidence":"missing","role":"baseline"},{"model_id":"org/alt","revision":"2"*40,"license":"mit","license_url":"https://example.com/license","license_status":"VERIFIED","license_evidence":"review-alt","role":"open_weight_alternative"}]
   with self.assertRaises(DatasetPolicyError):
    create_benchmark_job(hub,registered["dataset_id"],41,models,"compute-review-1",Path(temp)/"jobs")
 def test_wrong_compute_approval_is_rejected(self):
  with tempfile.TemporaryDirectory() as temp:
   with self.assertRaises(BenchmarkExecutionError):
    validate_benchmark_job({"schema":"dreamco.cross_model_benchmark_job.v1","execution_status":"NOT_EXECUTED","compute_approval_id":"correct"},"wrong")
if __name__=="__main__":unittest.main()
