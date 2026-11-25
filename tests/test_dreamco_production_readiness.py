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


 def test_markdown_candidates_are_not_blockers_until_confirmed(self):
  from tools.dreamco_production_readiness import classify_requirement, missing_requirement_evidence
  self.assertEqual(classify_requirement({}),"UNTRIAGED_CANDIDATE")
  self.assertEqual(missing_requirement_evidence({}),[])
  confirmed={"confirmed_requirement":True}
  self.assertEqual(classify_requirement(confirmed),"CONFIRMED_REQUIREMENT")
  self.assertEqual(set(missing_requirement_evidence(confirmed)),{"implementation","tests","runtime_routes","benchmark_evidence"})

 def test_candidate_triage_is_grouped_by_source(self):
  from tools.dreamco_production_readiness import build_candidate_triage
  rows=[{"id":"DCO-A","source":"docs/a.md"},{"id":"DCO-B","source":"docs/a.md"},{"id":"DCO-C","source":"docs/b.md"}]
  result=build_candidate_triage(rows)
  self.assertEqual([(item["source"],item["candidate_count"]) for item in result],[("docs/a.md",2),("docs/b.md",1)])
  self.assertLessEqual(len(result[0]["sample_requirement_ids"]),5)

 def test_production_gates_require_existing_same_sha_artifacts_and_successful_checks(self):
  from tools.dreamco_production_readiness import build_production_gate_records
  policy={"production_gates":["tests_pass"]}
  current_sha="a"*40
  records,findings=build_production_gate_records(policy,{},current_sha,"DreamCo-Technologies/Dreamcobots","test-token")
  self.assertEqual(records[0]["status"],"BLOCKED")
  self.assertEqual(len(findings),1)
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)
   artifact=root/"tests/test_example.py"
   artifact.parent.mkdir(parents=True)
   artifact.write_text("test",encoding="utf-8")
   evidence={"production_gates":{"tests_pass":{"status":"VERIFIED","evidence":[
    {"path":"tests/test_example.py","sha":current_sha,"check_id":"12345"}
   ]}}}
   verifier=lambda repository,check_id,sha,token: repository=="DreamCo-Technologies/Dreamcobots" and check_id=="12345" and sha==current_sha and token=="test-token"
   records,findings=build_production_gate_records(
    policy,evidence,current_sha,"DreamCo-Technologies/Dreamcobots","test-token",root=root,verify_check=verifier
   )
   self.assertEqual(records[0]["status"],"VERIFIED")
   self.assertEqual(findings,[])
   stale={"production_gates":{"tests_pass":{"status":"VERIFIED","evidence":[
    {"path":"tests/test_example.py","sha":"b"*40,"check_id":"12345"}
   ]}}}
   records,findings=build_production_gate_records(
    policy,stale,current_sha,"DreamCo-Technologies/Dreamcobots","test-token",root=root,verify_check=verifier
   )
   self.assertEqual(records[0]["status"],"BLOCKED")
   self.assertTrue(any("SHA" in item for item in records[0]["verification_errors"]))
   failed=lambda *args: False
   records,findings=build_production_gate_records(
    policy,evidence,current_sha,"DreamCo-Technologies/Dreamcobots","test-token",root=root,verify_check=failed
   )
   self.assertEqual(records[0]["status"],"BLOCKED")
   self.assertTrue(any("successfully" in item for item in records[0]["verification_errors"]))

 def test_requirement_source_filter_excludes_notes_and_generated_catalogs(self):
  from tools.dreamco_production_readiness import ROOT, is_requirement_source
  self.assertFalse(is_requirement_source(ROOT/".agents/memory/MEMORY.md"))
  self.assertFalse(is_requirement_source(ROOT/"docs/BUDDY_ADDITIONAL_TAXONOMY_SYSTEMS.md"))
  self.assertTrue(is_requirement_source(ROOT/"docs/BUDDY_TOLKIEN_STUDY_TRACK.md"))

if __name__=="__main__": unittest.main()
