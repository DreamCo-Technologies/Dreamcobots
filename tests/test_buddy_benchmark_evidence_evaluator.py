import unittest
from tools.evaluate_buddy_benchmark_packet import evaluate_packet
class BenchmarkEvidenceEvaluatorTests(unittest.TestCase):
 def setUp(self):
  self.definition={"schema":"dreamco.core_capability_benchmark_definitions.v1","benchmarks":[{"benchmark_id":"B-TEST","capability_id":"test","rubric":[{"dimension":"correctness","weight":60},{"dimension":"safety","weight":40}],"critical_gates":["No unsafe action"],"pass_threshold":80}]}
  self.packet={"schema":"dreamco.buddy_benchmark_evidence_packet.v1","benchmark_id":"B-TEST","model_id":"buddy-local","model_version":"0.1","training_fixture_sha256":"a"*64,"holdout_fixture_sha256":"b"*64,"scores":{"correctness":4,"safety":3},"critical_gates":{"No unsafe action":True},"evidence":{"run_id":"run-1","evaluated_at_utc":"2026-11-25T00:00:00Z","result_sha256":"c"*64,"source_commit":"abc123","evaluator_version":"1","reviewer_id":"reviewer-1"}}
 def test_weighted_score_and_candidate_pass(self):
  result=evaluate_packet(self.packet,self.definition); self.assertEqual(result["weighted_score"],85.0); self.assertTrue(result["candidate_pass"]); self.assertFalse(result["benchmark_execution_verified"]); self.assertEqual(result["independent_verification"],"pending"); self.assertFalse(result["mastery_claimed"])
 def test_critical_gate_failure_blocks_even_high_score(self):
  self.packet["critical_gates"]["No unsafe action"]=False; result=evaluate_packet(self.packet,self.definition); self.assertFalse(result["candidate_pass"]); self.assertIn("No unsafe action",result["failed_critical_gates"])
 def test_holdout_cannot_equal_training_fixture(self):
  self.packet["holdout_fixture_sha256"]=self.packet["training_fixture_sha256"]
  with self.assertRaisesRegex(ValueError,"distinct"): evaluate_packet(self.packet,self.definition)
 def test_missing_or_extra_rubric_dimensions_rejected(self):
  self.packet["scores"]["other"]=4
  with self.assertRaisesRegex(ValueError,"exactly the rubric"): evaluate_packet(self.packet,self.definition)
 def test_bad_evidence_hash_rejected(self):
  self.packet["evidence"]["result_sha256"]="not-a-hash"
  with self.assertRaisesRegex(ValueError,"SHA-256"): evaluate_packet(self.packet,self.definition)
 def test_unknown_benchmark_rejected(self):
  self.packet["benchmark_id"]="UNKNOWN"
  with self.assertRaisesRegex(ValueError,"unknown"): evaluate_packet(self.packet,self.definition)
if __name__=="__main__": unittest.main()
