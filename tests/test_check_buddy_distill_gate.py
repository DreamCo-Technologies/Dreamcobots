"""Tests for tools/check_buddy_distill_gate.py. Packets here are SYNTHETIC fixtures only."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import check_buddy_distill_gate as gate  # noqa: E402

H = "a" * 64


def synthetic_packet(**over):
    packet = {
        "schema": "dreamco.buddy_distill_evidence.v1",
        "synthetic_fixture": True,
        "adapter_id": "buddy-distill-synthetic-001",
        "teacher": {"model_id": "SYNTHETIC-teacher", "teacher_terms_check": {"permitted": True, "reviewed_by": "synthetic", "reviewed_at_utc": "2026-01-01T00:00:00Z", "terms_url": "https://example.invalid"}},
        "student": {"method": "lora_adapter", "base_model": "SYNTHETIC-base", "base_model_revision": "0123456789abcdef", "base_model_license_ok": True, "weight_format": "safetensors"},
        "baseline": {"holdout_score": 0.70, "holdout_fixture_sha256": H, "evaluated_at_utc": "2026-01-01T00:00:00Z"},
        "runs": [{"train_started_at_utc": f"2026-01-0{i + 2}T00:00:00Z", "holdout_score": 0.80, "regression": 0.01, "adapter_sha256": H, "sandbox_image_digest": "sha256:synthetic"} for i in range(3)],
        "safety_suite": {"passed": True, "suite_version": "synthetic"},
        "provenance": {"training_data_sha256": H, "sources_approved": True},
        "owner_approval": {"approved": True, "approved_by": "synthetic", "approved_at_utc": "2026-01-05T00:00:00Z"},
        "allowlist_eligible": True,
    }
    packet.update(over)
    return packet


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "config").mkdir()
        (self.tmp / "evidence/distill").mkdir(parents=True)
        shutil.copy(REPO / "config/buddy-distill-contract.json", self.tmp / "config/")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write_packet(self, packet, name="p.json"):
        (self.tmp / "evidence/distill" / name).write_text(json.dumps(packet))

    def set_contract(self, fn):
        path = self.tmp / "config/buddy-distill-contract.json"
        data = json.loads(path.read_text())
        fn(data)
        path.write_text(json.dumps(data))

    def test_real_repo_contract_passes_empty(self):
        code, lines = gate.run(REPO)
        self.assertEqual(code, 0, lines)

    def test_pass_when_no_packets_and_no_claims(self):
        self.assertEqual(gate.run(self.tmp)[0], 0)

    def test_fail_allowlist_claim_without_evidence(self):
        self.set_contract(lambda d: d["truth"].__setitem__("allowlisted_adapters", ["ghost-adapter"]))
        code, lines = gate.run(self.tmp)
        self.assertEqual(code, 1)
        self.assertTrue(any("ghost-adapter" in l for l in lines))

    def test_fail_train_before_baseline(self):
        p = synthetic_packet()
        p["runs"][0]["train_started_at_utc"] = "2025-12-31T00:00:00Z"
        self.write_packet(p)
        code, lines = gate.run(self.tmp)
        self.assertEqual(code, 1)
        self.assertTrue(any("eval-before-train" in l for l in lines))

    def test_fail_weight_file_in_tree(self):
        (self.tmp / "model.safetensors").write_bytes(b"x")
        code, lines = gate.run(self.tmp)
        self.assertEqual(code, 1)
        self.assertTrue(any("weight file" in l for l in lines))

    def test_fail_too_few_repetitions(self):
        p = synthetic_packet()
        p["runs"] = p["runs"][:2]
        self.write_packet(p)
        self.assertEqual(gate.run(self.tmp)[0], 1)

    def test_fail_teacher_terms_not_permitted(self):
        p = synthetic_packet()
        p["teacher"]["teacher_terms_check"]["permitted"] = False
        self.write_packet(p)
        self.assertEqual(gate.run(self.tmp)[0], 1)

    def test_fail_missing_owner_approval(self):
        p = synthetic_packet()
        p["owner_approval"]["approved"] = False
        self.write_packet(p)
        self.assertEqual(gate.run(self.tmp)[0], 1)

    def test_pass_complete_synthetic_packet_with_claim(self):
        self.write_packet(synthetic_packet())
        self.set_contract(lambda d: d["truth"].__setitem__("allowlisted_adapters", ["buddy-distill-synthetic-001"]))
        code, lines = gate.run(self.tmp)
        self.assertEqual(code, 0, lines)

    def test_fail_contract_allows_ci_training(self):
        self.set_contract(lambda d: d["ci_policy"].__setitem__("default_ci_trains", True))
        self.assertEqual(gate.run(self.tmp)[0], 1)


if __name__ == "__main__":
    unittest.main()
