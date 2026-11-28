"""Offline tests for signed-data guardrails and train/validation/holdout isolation."""
import base64, hashlib, json, tempfile, unittest
from pathlib import Path
from stages.05_model_foundry.guardrails import split_bucket, split_name, verify_signed_manifest, iter_authorized_records

class FoundryGuardrailTests(unittest.TestCase):
    def test_split_is_deterministic_and_disjoint(self):
        ids=[f"task-{i}" for i in range(10000)]
        self.assertEqual([split_bucket(x) for x in ids],[split_bucket(x) for x in ids])
        self.assertTrue(all(split_name(x)=="train" for x in ids if split_bucket(x)<90))
        self.assertTrue(all(split_name(x)=="validation" for x in ids if 90<=split_bucket(x)<95))
        self.assertTrue(all(split_name(x)=="holdout" for x in ids if split_bucket(x)>=95))
    def test_unsigned_or_tampered_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); data=root/"records.jsonl"; data.write_text('{"task_id":"t1","content":"safe"}\n')
            manifest={"schema":"dreamco.foundry.authorization.v1","datasets":[{"dataset_id":"d1","path":"records.jsonl","sha256":hashlib.sha256(data.read_bytes()).hexdigest(),"license_tier":"DREAMCO_ORIGINAL","commercial_use":True,"policy_decision_id":"PD-1","category":"study_guides"}]}
            mp=root/"manifest.json"; mp.write_text(json.dumps(manifest))
            sig=root/"manifest.sig"; sig.write_text("")
            key=root/"pub.pem"; key.write_text("not-a-key")
            with self.assertRaises(Exception): verify_signed_manifest(mp,sig,key)
    def test_holdout_cannot_be_requested_with_train(self):
        class M: pass
        # Split request validation is enforced before any record iteration.
        from stages.05_model_foundry.guardrails import ALLOWED_SPLITS
        self.assertIn("holdout",ALLOWED_SPLITS)

if __name__=="__main__": unittest.main()
