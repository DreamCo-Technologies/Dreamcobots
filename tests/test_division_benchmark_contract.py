import tempfile
import unittest
from buddy.benchmarks.division_benchmark_contract import create_benchmark_plan,validate_benchmark_evidence,assemble_benchmark_evidence

def make_plan(tmp):
 return create_benchmark_plan(1,"dreamco/dreamfinance-mini","0.1.0","a"*64,"b"*64,"c"*64,
  "holdout-review-001","evaluation-approval-001",tmp)

def make_evidence(plan):
 runs=[]
 for i,seed in enumerate((101,202,303),1):
  runs.append({"run_id":f"run-{i}","workflow_run_id":str(9000+i),"commit_sha":"d"*40,
   "evaluator_id":f"independent-evaluator-{i}","seed":seed,
   "evaluation_dataset_sha256":plan["holdout_dataset_sha256"],
   "weights_sha256":plan["weights_sha256"],"private_holdout_used_for_training":False,
   "suites":{"domain":{"score":0.94},"general":{"score":0.86},
    "safety":{"critical_violations":0},"privacy":{"leaks":0},
    "robustness":{"score":0.89},"regression":{"passed":True},
    "performance":{"p95_latency_ms":1200.0,"cost_usd_per_1k_tokens":0.04}}})
 return {"schema":"dreamco.division_benchmark_evidence.v1","plan_id":plan["plan_id"],
  "masterbot_id":plan["masterbot_id"],"model_name":plan["model_name"],
  "model_version":plan["model_version"],"weights_sha256":plan["weights_sha256"],
  "holdout_dataset_sha256":plan["holdout_dataset_sha256"],
  "holdout_rights_evidence":"holdout-review-001","private_holdout_used_for_training":False,"runs":runs}

class DivisionBenchmarkContractTests(unittest.TestCase):
 def test_plan_requires_distinct_training_and_private_holdout(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(ValueError,"distinct"):
    create_benchmark_plan(1,"dreamco/dreamfinance-mini","0.1.0","a"*64,"b"*64,"b"*64,
     "rights","approval",tmp)
 def test_plan_requires_valid_canonical_division(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(ValueError,"canonical"):
    create_benchmark_plan(66,"dreamco/unknown-mini","0.1.0","a"*64,"b"*64,"c"*64,
     "rights","approval",tmp)
 def test_three_independent_runs_pass_only_to_review(self):
  with tempfile.TemporaryDirectory() as tmp:
   plan=make_plan(tmp);result=validate_benchmark_evidence(plan,make_evidence(plan))
  self.assertTrue(result["passed"])
  self.assertEqual(result["status"],"BENCHMARKED_READY_FOR_INDEPENDENT_REVIEW")
  self.assertFalse(result["certified"])
  self.assertFalse(result["production_deployed"])
  self.assertFalse(result["promotion_allowed"])
 def test_assembler_builds_evidence_from_persisted_run_records(self):
  with tempfile.TemporaryDirectory() as tmp:
   plan=make_plan(tmp);raw=make_evidence(plan)
   run_records=[]
   for run in raw["runs"]:
    run_records.append({"schema":"dreamco.division_benchmark_run.v1","plan_id":plan["plan_id"],**run})
   evidence=assemble_benchmark_evidence(plan,run_records)
   result=validate_benchmark_evidence(plan,evidence)
  self.assertTrue(result["passed"])
  self.assertEqual(evidence["holdout_rights_evidence"],"holdout-review-001")
 def test_duplicate_run_ids_and_seeds_are_blocked(self):
  with tempfile.TemporaryDirectory() as tmp:
   plan=make_plan(tmp);evidence=make_evidence(plan)
   evidence["runs"][1]["run_id"]=evidence["runs"][0]["run_id"]
   evidence["runs"][2]["seed"]=evidence["runs"][0]["seed"]
   result=validate_benchmark_evidence(plan,evidence)
  self.assertFalse(result["passed"])
  self.assertIn("run_ids_missing_or_duplicated",result["issues"])
  self.assertIn("benchmark_seeds_must_be_independent",result["issues"])
 def test_holdout_contamination_and_safety_failures_are_blocked(self):
  with tempfile.TemporaryDirectory() as tmp:
   plan=make_plan(tmp);evidence=make_evidence(plan)
   evidence["runs"][0]["private_holdout_used_for_training"]=True
   evidence["runs"][1]["suites"]["safety"]["critical_violations"]=1
   result=validate_benchmark_evidence(plan,evidence)
  self.assertFalse(result["passed"])
  self.assertIn("run_1_holdout_contamination",result["issues"])
  self.assertIn("run_2_failed_one_or_more_acceptance_thresholds",result["issues"])
 def test_plan_identity_and_weight_hash_must_match(self):
  with tempfile.TemporaryDirectory() as tmp:
   plan=make_plan(tmp);evidence=make_evidence(plan);evidence["weights_sha256"]="e"*64
   result=validate_benchmark_evidence(plan,evidence)
  self.assertFalse(result["passed"])
  self.assertIn("weights_sha256_does_not_match_plan",result["issues"])

if __name__=="__main__": unittest.main()
