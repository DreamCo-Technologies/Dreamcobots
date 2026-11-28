"""Offline tests for signed-data guardrails and train/validation/holdout isolation."""
import importlib.util
from pathlib import Path
import tempfile, unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("foundry_guardrails",ROOT/"stages/05_model_foundry/guardrails.py")
GUARD=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(GUARD)

class FoundryGuardrailTests(unittest.TestCase):
    def test_split_is_deterministic_and_disjoint(self):
        ids=[f"task-{i}" for i in range(10000)]
        self.assertEqual([GUARD.split_bucket(x) for x in ids],[GUARD.split_bucket(x) for x in ids])
        self.assertTrue(all(GUARD.split_name(x)=="train" for x in ids if GUARD.split_bucket(x)<90))
        self.assertTrue(all(GUARD.split_name(x)=="validation" for x in ids if 90<=GUARD.split_bucket(x)<95))
        self.assertTrue(all(GUARD.split_name(x)=="holdout" for x in ids if GUARD.split_bucket(x)>=95))
    def test_unsigned_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); mp=root/"manifest.json"; mp.write_text('{"schema":"dreamco.foundry.authorization.v1","datasets":[]}')
            sig=root/"manifest.sig"; sig.write_text("")
            key=root/"pub.pem"; key.write_text("not-a-key")
            with self.assertRaises(Exception): GUARD.verify_signed_manifest(mp,sig,key)
    def test_holdout_cannot_be_mixed_with_train(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"records.jsonl"; p.write_text("")
            manifest={"datasets":[{"_resolved_path":str(p),"category":"study_guides"}]}
            with self.assertRaises(PermissionError):
                list(GUARD.iter_authorized_records(manifest,splits={"train","holdout"}))

if __name__=="__main__": unittest.main()
