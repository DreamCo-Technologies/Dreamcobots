import hashlib
import tempfile
import unittest
from pathlib import Path
from buddy.models.evidence_gate import verify_division_evidence, EvidenceGateError

DOMAINS = ["infrastructure", "dataset", "training", "benchmark", "runtime"]

class EvidenceGateTests(unittest.TestCase):
    def make_manifest(self, root):
        records = []
        for domain in DOMAINS:
            path = Path(root) / (domain + ".json")
            path.write_text('{"status":"PASS"}')
            records.append({"domain":domain,"status":"PASS","masterbot_id":7,
                "evidence_id":"ev-"+domain,"observed_at":"2026-11-24T00:00:00Z",
                "artifact_path":path.name,"artifact_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                "source_ref":"workflow-run-123"})
        return {"schema":"dreamco.division_evidence_manifest.v1","masterbot_id":7,"evidence":records}

    def test_all_domains_require_hash_verified_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = verify_division_evidence(self.make_manifest(tmp), tmp)
            self.assertEqual(result["status"],"READY_FOR_INDEPENDENT_REVIEW")
            self.assertFalse(result["production_promotion"])
            self.assertEqual(len(result["verified_domains"]),5)

    def test_missing_domain_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self.make_manifest(tmp)
            manifest["evidence"] = manifest["evidence"][:-1]
            result = verify_division_evidence(manifest,tmp)
            self.assertEqual(result["status"],"BLOCKED")
            self.assertIn("runtime",result["missing_domains"])

    def test_hash_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self.make_manifest(tmp)
            manifest["evidence"][0]["artifact_sha256"] = "0"*64
            result = verify_division_evidence(manifest,tmp)
            self.assertEqual(result["status"],"BLOCKED")
            self.assertIn("artifact_hash_mismatch",[x["reason"] for x in result["failures"]])

    def test_cross_division_evidence_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self.make_manifest(tmp)
            manifest["evidence"][0]["masterbot_id"] = 8
            result = verify_division_evidence(manifest,tmp)
            self.assertEqual(result["status"],"BLOCKED")

    def test_bad_schema_rejected(self):
        with self.assertRaises(EvidenceGateError):
            verify_division_evidence({"schema":"wrong","masterbot_id":1,"evidence":[]}, ".")

if __name__ == "__main__": unittest.main()
