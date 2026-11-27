import unittest
from tools.validate_buddy_benchmark_program_guides import validate
class BenchmarkProgramGuideTests(unittest.TestCase):
 def setUp(self):
  self.index={"schema":"dreamco.benchmark_index_source.v1","programs":[{"id":"repo","generator":"tools/build.py","check_command":"pytest"}]}
  self.guides={"schema":"dreamco.buddy_benchmark_program_guides.v1","program_count":1,"programs":[{
   "benchmark_id":"repo","title":"Repository evidence","scope":"contracts","generator":"tools/build.py","check_command":"pytest","cadence":"per change","benchmark_purpose":"Assess repository.",
   "methodology":["step"],"evaluation_metrics":["pass rate"],"thresholds":{"status":"source_defined_or_pending","values":None},
   "baseline_and_comparator":"baseline","workload_and_environment":"isolated","reproducibility":{"required":True},
   "holdout_and_contamination_controls":{"required":True},"safety_and_permissions":{"default":"read_only"},
   "evidence_artifacts":["manifest"],"remediation":"fix and retest","limitations":["not executed"],"review":{"status":"pending"},
   "execution_status":"not_executed_by_guide_generation","guide_status":"original_program_guide_draft_needs_human_review"
  }]}
 def test_exact_program_coverage(self): self.assertEqual(validate(self.index,self.guides),[])
 def test_missing_program_is_detected(self):
  self.guides["programs"]=[]; self.assertTrue(any("coverage mismatch" in e for e in validate(self.index,self.guides)))
 def test_command_drift_is_detected(self):
  self.guides["programs"][0]["check_command"]="wrong"; self.assertTrue(any("command or generator mismatch" in e for e in validate(self.index,self.guides)))
 def test_unverified_guide_cannot_claim_execution(self):
  self.guides["programs"][0]["execution_status"]="passed"; self.assertTrue(any("cannot claim execution" in e for e in validate(self.index,self.guides)))
 def test_thresholds_must_not_be_invented(self):
  self.guides["programs"][0]["thresholds"]["values"]={"score":90}; self.assertTrue(any("must not invent" in e for e in validate(self.index,self.guides)))
if __name__=="__main__": unittest.main()
