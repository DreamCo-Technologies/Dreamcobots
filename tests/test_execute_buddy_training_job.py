import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.execute_buddy_training_job import TrainingWorkerError,package_training_evidence,execute_approved_training_job

def file_manifest(root):
    rows=[]
    for path in sorted(x for x in root.rglob("*") if x.is_file()):
        rows.append({"path":path.relative_to(root).as_posix(),
            "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size})
    return rows

class TrainingEvidencePackagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.weights=self.root/"run"/"weights";self.checkpoints=self.root/"run"/"checkpoints";self.tokenizer=self.root/"run"/"tokenizer"
        for folder in (self.weights,self.checkpoints,self.tokenizer): folder.mkdir(parents=True)
        (self.weights/"adapter.bin").write_bytes(b"trained-weights")
        (self.checkpoints/"checkpoint-10.bin").write_bytes(b"optimizer-state")
        (self.tokenizer/"tokenizer.json").write_text('{"vocab":1}',encoding="utf-8")
        weight_files=file_manifest(self.weights)
        self.result={"schema":"dreamco.model_training_result.v3","job_id":"train-1",
            "execution_status":"COMPLETED","masterbot_id":1,"model_id":"dreamco/dreamfinance-mini",
            "model_version":"0.1.0","base_model_id":"teacher/base","base_model_revision":"a"*40,
            "tokenizer_revision":"a"*40,"tested_commit_sha":"b"*40,"compute_approval_id":"compute-1",
            "dataset_id":"finance.dataset","dataset_version":1,"dataset_sha256":"c"*64,
            "split_manifest":{"train_sha256":"d"*64,"validation_sha256":"e"*64,"test_sha256":"f"*64},
            "weights_trained":True,"production_promoted":False,"checkpoint_files":weight_files,
            "checkpoint_sha256":hashlib.sha256(json.dumps(weight_files,sort_keys=True).encode()).hexdigest(),
            "artifact_paths":{"weights":str(self.weights),"checkpoints":str(self.checkpoints),"tokenizer":str(self.tokenizer)},
            "artifact_hashes":{"checkpoints":file_manifest(self.checkpoints),"tokenizer":file_manifest(self.tokenizer)}}
    def tearDown(self): self.tmp.cleanup()

    def test_packages_all_model_artifacts_and_gate_compatible_training_result(self):
        evidence_root=self.root/"evidence"
        result=package_training_evidence(self.result,evidence_root)
        self.assertEqual(result["status"],"TRAINED_PENDING_BENCHMARK_AND_REVIEW")
        self.assertTrue(result["weights_trained"])
        self.assertFalse(result["production_promoted"])
        training=json.loads((evidence_root/"training-result.json").read_text())
        self.assertEqual(training["execution_status"],"COMPLETED")
        self.assertEqual(training["tested_commit_sha"],"b"*40)
        self.assertEqual(training["checkpoint_sha256"],result["checkpoint_sha256"])
        self.assertTrue((evidence_root/training["checkpoint_root"]/"adapter.bin").is_file())
        self.assertTrue((evidence_root/training["artifact_paths"]["checkpoints"]/"checkpoint-10.bin").is_file())
        self.assertTrue((evidence_root/training["artifact_paths"]["tokenizer"]/"tokenizer.json").is_file())
        fragment=json.loads((evidence_root/"training-evidence-fragment.json").read_text())
        self.assertEqual(fragment["division"]["division_model_id"],"DCM-001")
        self.assertEqual(fragment["evidence"]["training_result"]["sha256"],result["training_result_sha256"])

    def test_missing_tested_commit_or_checkpoint_hash_blocks_packaging(self):
        bad=dict(self.result);bad["tested_commit_sha"]=""
        with self.assertRaisesRegex(TrainingWorkerError,"tested commit"):
            package_training_evidence(bad,self.root/"evidence-a")
        bad=dict(self.result);bad["checkpoint_sha256"]="x"
        with self.assertRaisesRegex(TrainingWorkerError,"checkpoint manifest"):
            package_training_evidence(bad,self.root/"evidence-b")
        bad=dict(self.result);bad["checkpoint_sha256"]="0"*64
        with self.assertRaisesRegex(TrainingWorkerError,"does not match"):
            package_training_evidence(bad,self.root/"evidence-c")

    def test_changed_weight_file_is_rejected(self):
        (self.weights/"adapter.bin").write_bytes(b"tampered")
        with self.assertRaisesRegex(TrainingWorkerError,"hash or size mismatch"):
            package_training_evidence(self.result,self.root/"evidence")

    def test_execution_requires_explicit_enable_and_matching_approval(self):
        job_path=self.root/"job.json"
        job_path.write_text(json.dumps({"compute_approval_id":"compute-1"}))
        with patch.dict(os.environ,{},clear=True), patch("tools.execute_buddy_training_job.execute_job") as execute:
            with self.assertRaisesRegex(TrainingWorkerError,"ALLOW_TRAINING_EXECUTION"):
                execute_approved_training_job(job_path,"compute-1",self.root/"evidence")
            execute.assert_not_called()
        with patch.dict(os.environ,{"DREAMCO_ALLOW_TRAINING_EXECUTION":"1"},clear=True), patch("tools.execute_buddy_training_job.execute_job") as execute:
            with self.assertRaisesRegex(TrainingWorkerError,"does not match"):
                execute_approved_training_job(job_path,"wrong",self.root/"evidence")
            execute.assert_not_called()

if __name__=="__main__":
    unittest.main()
