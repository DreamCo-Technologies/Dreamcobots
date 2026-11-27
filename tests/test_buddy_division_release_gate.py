import hashlib,json,tempfile,unittest
from pathlib import Path
from buddy.models.division_release_gate import validate_division_release,DivisionReleaseEvidenceError
COMMIT="a"*40
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(root,relative,payload):
 path=root/relative;path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(payload,sort_keys=True)+"\n",encoding="utf-8")
 return {"path":relative,"sha256":sha(path)}
def checkpoint(root):
 folder=root/"checkpoint";folder.mkdir()
 artifact=folder/"adapter.bin";artifact.write_bytes(b"verified model adapter bytes")
 files=[{"path":"adapter.bin","sha256":sha(artifact),"bytes":artifact.stat().st_size}]
 digest=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()
 return files,digest
def build_bundle(root):
 files,checkpoint_hash=checkpoint(root)
 dataset={"dataset_id":"dataset.finance.v1","version":1,"content_sha256":"1"*64,
  "training_approved":True,"rights_status":"VERIFIED","holdout":False,
  "primary_masterbot_id":1,"split_manifest":{"train_sha256":"2"*64,"validation_sha256":"3"*64,"test_sha256":"4"*64}}
 training={"execution_status":"COMPLETED","weights_trained":True,"production_promoted":False,
  "masterbot_id":1,"model_id":"dreamco.division.dreamfinance","dataset_id":dataset["dataset_id"],
  "dataset_sha256":dataset["content_sha256"],"split_manifest":dataset["split_manifest"],
  "base_model_revision":"b"*40,"tokenizer_revision":"b"*40,"checkpoint_sha256":checkpoint_hash,
  "tested_commit_sha":COMMIT,"checkpoint_files":files}
 docs={
  "postgres_probe":{"status":"CONNECTED_SCHEMAS_VERIFIED","expected_division_namespaces":65,"verified_division_namespaces":65,"missing_division_namespaces":[]},
  "dataset_catalog":{"status":"PERSISTED","masterbot_id":1,"schema":"dreamco_division_001"},
  "object_storage":{"status":"HEALTHY","encryption_at_rest":True,"versioning_enabled":True,"backup_restore_test":"PASS","retention_days":30},
  "provider_health":{"status":"HEALTHY","live_smoke_test":True,"provider_id":"openai","model_id":"gpt-5.4-mini","request_id":"req-123"},
  "dataset_card":dataset,"training_result":training,
  "benchmark_report":{"dataset_id":dataset["dataset_id"],"dataset_sha256":dataset["content_sha256"],
   "model_id":"dreamco.division.dreamfinance","checkpoint_sha256":checkpoint_hash,"tested_commit_sha":COMMIT,
   "domain_benchmark_status":"PASS","general_regression_status":"PASS","private_holdout_status":"PASS",
   "safety_status":"PASS","test_split_used_for_training":False,
   "performance_profile":{"latency_p95_ms":250,"tokens_per_second":35,"peak_memory_bytes":1000000,"cost_per_1k_tokens_usd":0.01}},
  "runtime_deployment":{"status":"HEALTHY","endpoint":"https://models.example.org/dreamfinance",
   "deployment_revision":"deploy-123","model_id":"dreamco.division.dreamfinance",
   "checkpoint_sha256":checkpoint_hash,"tested_commit_sha":COMMIT,"smoke_test":"PASS","rollback_target":"deploy-previous"}}
 refs={name:dump(root,f"evidence/{name}.json",payload) for name,payload in docs.items()}
 bundle={"schema":"dreamco.division_release_evidence.v1",
  "division":{"masterbot_id":1,"division_model_id":"DCM-001","model_id":"dreamco.division.dreamfinance","version":"0.1.0"},
  "tested_commit_sha":COMMIT,"checkpoint_root":"checkpoint","evidence":refs,
  "independent_review":{"reviewer_id":"reviewer-2","approval_id":"review-approval-9","approved":True}}
 path=root/"release-bundle.json";path.write_text(json.dumps(bundle,indent=2)+"\n")
 return path
class DivisionReleaseGateTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.bundle=build_bundle(self.root)
 def tearDown(self): self.temp.cleanup()
 def test_complete_evidence_is_eligible_for_independent_review(self):
  result=validate_division_release(self.bundle)
  self.assertEqual(result["status"],"READY_FOR_INDEPENDENT_REVIEW")
  self.assertEqual(result["evidence_refs_verified"],8)
  self.assertFalse(result["production_promotion_performed"])
 def test_missing_object_storage_blocks_release(self):
  bundle=json.loads(self.bundle.read_text());storage=self.root/"evidence/object_storage.json"
  payload=json.loads(storage.read_text());payload["backup_restore_test"]="NOT_RUN"
  storage.write_text(json.dumps(payload));bundle["evidence"]["object_storage"]["sha256"]=sha(storage)
  self.bundle.write_text(json.dumps(bundle))
  result=validate_division_release(self.bundle)
  self.assertEqual(result["status"],"BLOCKED")
  self.assertTrue(any("object storage" in x for x in result["blockers"]))
 def test_tampered_evidence_hash_blocks_release(self):
  dataset=self.root/"evidence/dataset_card.json";dataset.write_text(dataset.read_text()+" ")
  result=validate_division_release(self.bundle)
  self.assertEqual(result["status"],"BLOCKED")
  self.assertTrue(any("SHA-256 mismatch" in x for x in result["blockers"]))
 def test_wrong_division_identity_is_rejected(self):
  bundle=json.loads(self.bundle.read_text());bundle["division"]["masterbot_id"]=66
  self.bundle.write_text(json.dumps(bundle))
  with self.assertRaises(DivisionReleaseEvidenceError): validate_division_release(self.bundle)
if __name__=="__main__": unittest.main()
