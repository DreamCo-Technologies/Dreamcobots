import hashlib, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validate_buddy_adapter_registry import main, validate

BASE = {"schema": "dreamco.buddy_student_adapter_registry.v1", "registry_version": "0.1.0",
        "truth": {"trained_weights_exist": False, "frontier_parity_proven": False}}

def entry(**kw):
    e = {"id": "buddy-student-code-s1", "version": "0.1.0", "base_model": {"repo": "x/y", "revision": "abc", "license": "apache-2.0"},
         "method": "lora_adapter", "teacher": "grok", "status": "planned", "trained_weights_exist": False,
         "artifacts": [], "model_card": None, "evidence": {}}
    e.update(kw); return e

class T(unittest.TestCase):
    def test_committed_registry_is_honest(self):
        self.assertEqual(main(), 0)
    def test_planned_entry_ok(self):
        self.assertEqual(validate({**BASE, "adapters": [entry()]}), [])
    def test_claim_without_artifacts_fails(self):
        self.assertTrue(validate({**BASE, "adapters": [entry(trained_weights_exist=True)]}))
    def test_trained_status_without_flag_fails(self):
        self.assertTrue(validate({**BASE, "adapters": [entry(status="trained")]}))
    def test_top_level_claim_without_proof_fails(self):
        r = {**BASE, "truth": {"trained_weights_exist": True, "frontier_parity_proven": False}, "adapters": []}
        self.assertTrue(validate(r))
    def test_real_artifact_passes_and_tamper_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "adapter_model.safetensors"; p.write_bytes(b"weights")
            art = {"path": p.name, "sha256": hashlib.sha256(b"weights").hexdigest(), "bytes": 7}
            e = entry(trained_weights_exist=True, status="trained", artifacts=[art], model_card="card.md", evidence={"eval_scorecard": "s.json"})
            self.assertEqual(validate({**BASE, "adapters": [e]}, Path(d)), [])
            p.write_bytes(b"tampere")
            self.assertTrue(validate({**BASE, "adapters": [e]}, Path(d)))
    def test_duplicate_version_fails(self):
        self.assertTrue(validate({**BASE, "adapters": [entry(), entry()]}))

if __name__ == "__main__":
    unittest.main()
