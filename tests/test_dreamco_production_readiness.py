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


 def test_generator_writes_valid_json_and_markdown_with_fail_closed_status(self):
  from tools import dreamco_production_readiness as module
  with tempfile.TemporaryDirectory() as temp:
   output=Path(temp)
   with patch.object(module,"OUT",output), patch.object(module,"tracked",return_value=[]), \
        patch.object(module,"EVIDENCE",Path(temp)/"missing-evidence.json"), \
        patch.object(module,"fetch_pull_requests",return_value={"status":"BLOCKED_NO_TOKEN","pull_requests":[],"pages_fetched":0}), \
        patch("sys.stdout",new=io.StringIO()):
    self.assertEqual(module.main(),0)
   report=json.loads((output/"production-readiness-master-list.json").read_text())
   routes=json.loads((output/"resource-routing-inventory.json").read_text())
   markdown=(output/"production-readiness-master-list.md").read_text()
   self.assertEqual(report["summary"]["production_readiness"],"BLOCKED")
   self.assertEqual(report["summary"]["pull_request_inventory_status"],"BLOCKED_NO_TOKEN")
   self.assertIn("## Limitations",markdown)
   self.assertTrue(routes["routes"])

if __name__=="__main__": unittest.main()
