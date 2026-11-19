import json, tempfile, unittest, io
from pathlib import Path
from unittest.mock import patch
from tools.dreamco_production_readiness import fetch_pull_requests
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

 def test_pr_inventory_fails_closed_without_token(self):
  result=fetch_pull_requests("DreamCo-Technologies/Dreamcobots",None)
  self.assertEqual(result["status"],"BLOCKED_NO_TOKEN")
  self.assertEqual(result["pull_requests"],[])
 def test_pr_inventory_fetches_and_normalizes_api_results(self):
  payload=[{"number":7,"title":"Example","state":"open","draft":True,"head":{"ref":"topic","sha":"abc"},"base":{"ref":"main"},"updated_at":"2026-11-19T00:00:00Z","merged_at":None,"html_url":"https://github.com/example"}]
  with patch("tools.dreamco_production_readiness.urllib.request.urlopen",return_value=io.BytesIO(json.dumps(payload).encode())) as fetch:
   result=fetch_pull_requests("DreamCo-Technologies/Dreamcobots","test-token")
  self.assertEqual(result["status"],"COMPLETE")
  self.assertEqual(result["pull_requests"][0]["number"],7)
  self.assertEqual(result["pull_requests"][0]["head_sha"],"abc")
  fetch.assert_called_once()

if __name__=="__main__": unittest.main()
