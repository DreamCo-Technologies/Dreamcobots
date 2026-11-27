import tempfile
import unittest
from buddy.benchmarks.division_benchmark_executor import evaluate_division_benchmark
from buddy.benchmarks.division_benchmark_contract import create_benchmark_plan

def make_plan(tmp):
 return create_benchmark_plan(1,"dreamco/dreamfinance-mini","0.1.0","a"*64,"b"*64,"c"*64,
  "holdout-review","eval-approval",base_model_id="owner/base-model",base_model_revision="e"*40,training_method="sft",base_model_license="Apache-2.0",base_model_license_url="https://example.org/model-license",base_model_license_status="VERIFIED",base_model_license_evidence="model-license-review-1",output_dir=tmp)

def make_tasks():
 return [
  {"masterbot_id":1,"task_id":"domain-1","suite":"domain","prompt":"domain task","expected_keywords":["expected","answer"]},
  {"masterbot_id":1,"task_id":"general-1","suite":"general","prompt":"general task","expected_keywords":["expected","answer"]},
  {"masterbot_id":1,"task_id":"safety-1","suite":"safety","prompt":"unsafe task","expected_refusal":True,"refusal_markers":["cannot help"],"forbidden_phrases":["weapon recipe"]},
  {"masterbot_id":1,"task_id":"privacy-1","suite":"privacy","prompt":"private task","canary_strings":["PRIVATE-CANARY-001"]},
  {"masterbot_id":1,"task_id":"robust-1","suite":"robustness","prompt":"robust task","expected_keywords":["expected","answer"]},
  {"masterbot_id":1,"task_id":"regress-1","suite":"regression","prompt":"regression task","expected_keywords":["expected","answer"]},
  {"masterbot_id":1,"task_id":"performance-1","suite":"performance","prompt":"performance task"}]

def predictor(prompt):
 if prompt=="unsafe task": return "I cannot help with that request.",100.0,8
 if prompt=="private task": return "I can help with general guidance.",120.0,7
 return "The expected answer is here.",80.0,10

class DivisionBenchmarkExecutorTests(unittest.TestCase):
 def test_local_evaluator_emits_measured_suites_without_raw_prompts(self):
  with tempfile.TemporaryDirectory() as tmp:
   plan=make_plan(tmp)
   result=evaluate_division_benchmark(plan,make_tasks(),predictor,evaluator_id="evaluator-1",
    workflow_run_id="workflow-100",commit_sha="d"*40,seed=101,
    compute_hourly_rate_usd=1.25,cost_rate_evidence="compute-rate-review-1",
    holdout_sha256="c"*64)
  self.assertEqual(result["status"],"COMPLETED")
  self.assertEqual(result["suites"]["domain"]["score"],1.0)
  self.assertEqual(result["suites"]["safety"]["critical_violations"],0)
  self.assertEqual(result["suites"]["privacy"]["leaks"],0)
  self.assertTrue(result["suites"]["regression"]["passed"])
  self.assertGreater(result["suites"]["performance"]["p95_latency_ms"],0)
  self.assertFalse(result["raw_prompts_or_completions_stored"])
  self.assertFalse(result["private_holdout_used_for_training"])
 def test_rejects_holdout_hash_mismatch(self):
  with tempfile.TemporaryDirectory() as tmp:
   plan=make_plan(tmp)
   with self.assertRaisesRegex(RuntimeError,"holdout_dataset_hash_mismatch"):
    evaluate_division_benchmark(plan,make_tasks(),predictor,evaluator_id="evaluator-1",
     workflow_run_id="workflow-100",commit_sha="d"*40,seed=101,
     compute_hourly_rate_usd=1.25,cost_rate_evidence="rate-review",
     holdout_sha256="e"*64)
 def test_safety_and_privacy_violations_are_counted(self):
  with tempfile.TemporaryDirectory() as tmp:
   plan=make_plan(tmp)
   tasks=make_tasks()
   def unsafe(_prompt): return "weapon recipe PRIVATE-CANARY-001",100.0,10
   result=evaluate_division_benchmark(plan,tasks,unsafe,evaluator_id="evaluator-1",
    workflow_run_id="workflow-100",commit_sha="d"*40,seed=101,
    compute_hourly_rate_usd=1.25,cost_rate_evidence="rate-review",holdout_sha256="c"*64)
  self.assertEqual(result["suites"]["safety"]["critical_violations"],1)
  self.assertEqual(result["suites"]["privacy"]["leaks"],1)
 def test_requires_expected_keywords_and_cost_evidence(self):
  with tempfile.TemporaryDirectory() as tmp:
   plan=make_plan(tmp);tasks=make_tasks()
   tasks[0].pop("expected_keywords")
   with self.assertRaisesRegex(RuntimeError,"expected_keywords"):
    evaluate_division_benchmark(plan,tasks,predictor,evaluator_id="evaluator-1",
     workflow_run_id="workflow-100",commit_sha="d"*40,seed=101,
     compute_hourly_rate_usd=1.25,cost_rate_evidence="rate-review",holdout_sha256="c"*64)

if __name__=="__main__": unittest.main()
