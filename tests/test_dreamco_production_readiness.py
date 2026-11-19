import json, tempfile, unittest
from pathlib import Path
class ProductionReadinessContractTests(unittest.TestCase):
 def test_policy_requires_fail_closed_gates(self):
  p=json.loads((Path(__file__).resolve().parents[1]/"governance/dreamco-always-on-policy.json").read_text())
  self.assertIn("tests_pass",p["production_gates"])
  self.assertIn("production_isolation_verified",p["production_gates"])
  self.assertFalse(p["repair"]["auto_apply"])
  self.assertFalse(p["repair"]["auto_merge"])
 def test_traceability_has_runtime_and_benchmark(self):
  p=json.loads((Path(__file__).resolve().parents[1]/"governance/dreamco-always-on-policy.json").read_text())
  self.assertIn("runtime_route",p["traceability"])
  self.assertIn("benchmark_evidence",p["traceability"])
if __name__=="__main__": unittest.main()
