from __future__ import annotations
import json
import os
import tempfile
import unittest
from pathlib import Path
from buddy.datasets.hub import DatasetHub, DatasetPolicyError
from buddy.datasets.sources import discover, SourceAccessError
from buddy.datasets.unknown_router import route_problem
from buddy.datasets.training_jobs import create_training_job
from buddy.datasets.transformers_runner import validate_job, TrainingExecutionError, _split_hash

CARD = {"name":"DreamCo authored coding lessons","owner":"DreamCo Technologies","license":"DREAMCO_INTERNAL_OWNED","license_url":"https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/config/buddy-training-data-provenance-policy.json","license_url_status":"INTERNAL_POLICY_REFERENCE_NOT_A_PUBLIC_LICENSE","source":"dreamco_authored","source_id":"dreamco.authored.coding.lessons.v1","source_url":"https://github.com/DreamCo-Technologies/Dreamcobots","ai_training_allowed":True,"content_rights_verified":True,"owner_assignment_verified":True,"contributor_rights_verified":True,"owner_approval_id":"OWNER-APPROVAL-FIXTURE-001","privacy_review":"PASSED","data_plane":"dreamco_owned_training","rights_status":"VERIFIED","training_approved":True,"rights_evidence":"approved-authorship-register:fixture-001","primary_masterbot_id":41,"collaborating_masterbot_ids":[],"split_manifest":{"train_sha256":"a"*64,"validation_sha256":"b"*64,"test_sha256":"c"*64},"holdout":False}

class DatasetHubRuntimeTests(unittest.TestCase):
    def test_versioned_persistent_card_and_content_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); sample=root/"sample.jsonl"
            sample.write_text('{"instruction":"Explain a Python function","output":"A reusable block of code."}\n{"instruction":"Explain SQL joins","output":"Combine related rows."}\n',encoding="utf-8")
            hub=DatasetHub(root/"hub")
            one=hub.register(CARD,sample)
            two=hub.register({**CARD,"dataset_id":one["dataset_id"]},sample)
            self.assertEqual(one["version"],1); self.assertEqual(two["version"],2)
            self.assertEqual(one["content_sha256"],two["content_sha256"])
            self.assertEqual(hub.get(one["dataset_id"],1)["version"],1)
            self.assertEqual(hub.stats()["dataset_versions"],2)

    def test_discovery_metadata_does_not_authorize_ingestion(self):
        with tempfile.TemporaryDirectory() as temp:
            sample=Path(temp)/"x.jsonl"; sample.write_text('{"x":1}\n')
            hub=DatasetHub(Path(temp)/"hub")
            with self.assertRaises(DatasetPolicyError):
                hub.register({**CARD,"training_approved":False},sample)

    def test_internal_license_requires_owner_and_contributor_rights(self):
        with tempfile.TemporaryDirectory() as temp:
            sample=Path(temp)/"x.jsonl"
            sample.write_text('{"instruction":"Explain a function","output":"A reusable code block."}\\n',encoding="utf-8")
            hub=DatasetHub(Path(temp)/"hub")
            with self.assertRaisesRegex(DatasetPolicyError,"INTERNAL_OWNERSHIP_OR_CONTRIBUTOR_RIGHTS"):
                hub.register({**CARD,"owner_assignment_verified":False},sample)

    def test_internal_license_cannot_be_reused_for_third_party_source(self):
        with tempfile.TemporaryDirectory() as temp:
            sample=Path(temp)/"x.jsonl"
            sample.write_text('{"instruction":"Explain a function","output":"A reusable code block."}\\n',encoding="utf-8")
            hub=DatasetHub(Path(temp)/"hub")
            with self.assertRaisesRegex(DatasetPolicyError,"INTERNAL_OWNERSHIP_OR_CONTRIBUTOR_RIGHTS"):
                hub.register({**CARD,"source":"huggingface"},sample)

    def test_unknown_license_and_holdout_are_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            hub=DatasetHub(temp)
            with self.assertRaises(DatasetPolicyError):
                hub.register({**CARD,"rights_status":"UNKNOWN"})
            with self.assertRaises(DatasetPolicyError):
                hub.register({**CARD,"data_plane":"evaluation_only_holdout","holdout":True,"training_approved":True})

    def test_quality_flags_pii(self):
        with tempfile.TemporaryDirectory() as temp:
            sample=Path(temp)/"x.jsonl"; sample.write_text('{"email":"person@example.com"}\n')
            with self.assertRaises(DatasetPolicyError):
                DatasetHub(Path(temp)/"hub").register(CARD,sample)

    def test_network_is_off_by_default(self):
        old=os.environ.pop("DREAMCO_ALLOW_SOURCE_NETWORK",None)
        try:
            result = discover("transformer")
            self.assertEqual(result["results"], [])
            self.assertEqual(result["model_results"], [])
            self.assertTrue(result["source_errors"])
        finally:
            if old is not None: os.environ["DREAMCO_ALLOW_SOURCE_NETWORK"]=old

    def test_training_job_requires_compute_approval_and_never_executes(self):
        with tempfile.TemporaryDirectory() as temp:
            sample=Path(temp)/"x.jsonl"; sample.write_text('{"instruction":"Do a task","output":"Complete it safely."}\n')
            hub=DatasetHub(Path(temp)/"hub"); card=hub.register(CARD,sample)
            with self.assertRaises(DatasetPolicyError):
                create_training_job(hub,card["dataset_id"],41,"buddy-student","0123456789abcdef0123456789abcdef01234567")
            job=create_training_job(hub,card["dataset_id"],41,"buddy-student","0123456789abcdef0123456789abcdef01234567","budget-approval-fixture","apache-2.0","https://example.com/license","VERIFIED","model-license-review-001",output_dir=Path(temp)/"jobs")
            self.assertEqual(job["execution_status"],"NOT_EXECUTED")
            self.assertFalse(job["weights_updated"])
            with self.assertRaises(TrainingExecutionError):
                validate_job(json.loads(Path(job["manifest_path"]).read_text()),"wrong-approval")

    def test_training_manifest_validates_exact_content_and_split_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            rows = [
                {"split":"train","masterbot_id":41,"text":"Teach a simple Python loop."},
                {"split":"validation","masterbot_id":41,"text":"Explain a SQL query."},
                {"split":"test","masterbot_id":41,"text":"Describe a safe deployment."},
            ]
            sample = Path(temp) / "splits.jsonl"
            sample.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            split_manifest = {f"{name}_sha256": _split_hash(rows, name) for name in ("train","validation","test")}
            hub = DatasetHub(Path(temp) / "hub")
            card = hub.register({**CARD,"split_manifest":split_manifest},sample)
            job = create_training_job(hub,card["dataset_id"],41,"buddy-student",
                "0123456789abcdef0123456789abcdef01234567","budget-approval-fixture",
                "apache-2.0","https://example.com/license","VERIFIED","model-license-review-001",
                output_dir=Path(temp)/"jobs")
            manifest = json.loads(Path(job["manifest_path"]).read_text())
            object_path, checked_rows = validate_job(manifest,"budget-approval-fixture")
            self.assertEqual(object_path.name,Path(card["object_path"]).name)
            self.assertEqual(len(checked_rows),3)

    def test_problem_routes_to_specialist_candidates_without_claiming_mastery(self):
        with tempfile.TemporaryDirectory() as temp:
            result=route_problem("Build a SQL database analytics pipeline",DatasetHub(temp))
            self.assertTrue(result["masterbot_candidates"])
            self.assertFalse(result["claims"]["problem_solved"])
            self.assertFalse(result["claims"]["weights_trained"])
            self.assertTrue(result["research_task_id"].startswith("research-"))
            self.assertEqual(DatasetHub(Path(temp)).stats()["pending_research_tasks"],1)

if __name__=="__main__":
    unittest.main()
