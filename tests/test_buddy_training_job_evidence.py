import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from buddy.datasets.training_jobs import create_training_job
from buddy.datasets.transformers_runner import TrainingExecutionError,validate_job

class FakeHub:
    def __init__(self,home,card):
        self.home=Path(home);self.card=card
    def get(self,dataset_id,version=None):
        if dataset_id==self.card["dataset_id"] and (version is None or version==self.card["version"]):
            return self.card
        return None

def make_rows():
    return [
      {"masterbot_id":1,"split":"train","text":"training example one"},
      {"masterbot_id":1,"split":"validation","text":"validation example two"},
      {"masterbot_id":1,"split":"test","text":"held out example three"}
    ]

def split_hash(rows,split):
    canonical="".join(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n" for row in rows if row["split"]==split)
    return hashlib.sha256(canonical.encode()).hexdigest()

class TrainingJobEvidenceTests(unittest.TestCase):
    def test_training_job_pins_shared_tokenizer_and_tested_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            card={"dataset_id":"finance.dataset","version":1,"training_approved":True,
              "rights_status":"VERIFIED","holdout":False,"content_sha256":"a"*64,
              "object_path":"objects/dataset.jsonl","split_manifest":{
                "train_sha256":"b"*64,"validation_sha256":"c"*64,"test_sha256":"d"*64},
              "primary_masterbot_id":1,"collaborating_masterbot_ids":[]}
            hub=FakeHub(temp,card)
            job=create_training_job(hub,"finance.dataset",1,"base/model","a"*40,
              compute_approval_id="compute-1",model_license="Apache-2.0",
              model_license_url="https://example.org/license",model_license_status="VERIFIED",
              model_license_evidence="review-1",tested_commit_sha="b"*40,output_dir=Path(temp)/"jobs")
            self.assertEqual(job["tokenizer_revision"],"a"*40)
            self.assertEqual(job["tested_commit_sha"],"b"*40)
            self.assertEqual(job["division_model"]["database_schema"],"dreamco_division_001")

    def test_validate_job_requires_immutable_commit_and_tokenizer(self):
        with tempfile.TemporaryDirectory() as temp:
            hub=Path(temp);objects=hub/"objects";objects.mkdir()
            rows=make_rows();source=objects/"dataset.jsonl"
            source.write_text("".join(json.dumps(row)+"\n" for row in rows),encoding="utf-8")
            content_sha=hashlib.sha256(source.read_bytes()).hexdigest()
            split_manifest={f"{name}_sha256":split_hash(rows,name) for name in ("train","validation","test")}
            card={"dataset_id":"finance.dataset","version":1,"training_approved":True,
              "rights_status":"VERIFIED","holdout":False,"content_sha256":content_sha,
              "object_path":"objects/dataset.jsonl","split_manifest":split_manifest,
              "primary_masterbot_id":1,"collaborating_masterbot_ids":[]}
            job={"schema":"dreamco.model_training_job.v1","job_id":"train-1111111111111111","execution_status":"NOT_EXECUTED",
              "compute_approval_id":"compute-1","base_model_revision":"a"*40,
              "tokenizer_revision":"b"*40,"tested_commit_sha":"c"*40,
              "model_license":"Apache-2.0","model_license_url":"https://example.org/license",
              "model_license_status":"VERIFIED","model_license_evidence":"review-1",
              "training_method":"sft","dataset_hub_path":str(hub),"dataset_id":"finance.dataset",
              "dataset_version":1,"dataset_object_path":"objects/dataset.jsonl","dataset_sha256":content_sha,
              "dataset_card_sha256":hashlib.sha256(json.dumps(card,sort_keys=True).encode()).hexdigest(),
              "split_manifest":split_manifest,"masterbot_id":1,"model_id":"base/model",
              "division_model":{"model_name":"dreamco/dreamfinance-mini","model_version":"0.1.0",
                "division_slug":"dreamfinance","artifact_root":"artifacts/division-models/dreamfinance",
                "database_schema":"dreamco_division_001"}}
            with patch("buddy.datasets.transformers_runner.DatasetHub") as hub_cls:
                hub_cls.return_value.get.return_value=card
                obj,lane=validate_job(job,"compute-1")
            self.assertEqual(obj,source)
            self.assertEqual(len(lane),3)
            bad=dict(job);bad["tested_commit_sha"]=""
            with patch("buddy.datasets.transformers_runner.DatasetHub") as hub_cls, patch.dict("os.environ", {"GITHUB_SHA": ""}):
                hub_cls.return_value.get.return_value=card
                with self.assertRaisesRegex(TrainingExecutionError,"tested commit SHA"):
                    validate_job(bad,"compute-1")
            bad=dict(job);bad["tokenizer_revision"]="not-a-revision"
            with patch("buddy.datasets.transformers_runner.DatasetHub") as hub_cls:
                hub_cls.return_value.get.return_value=card
                with self.assertRaisesRegex(TrainingExecutionError,"Tokenizer revision"):
                    validate_job(bad,"compute-1")

if __name__=="__main__":
    unittest.main()
