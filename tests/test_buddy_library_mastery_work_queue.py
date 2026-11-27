import unittest
from tools.validate_buddy_library_mastery_work_queue import validate
class LibraryMasteryWorkQueueTests(unittest.TestCase):
 def setUp(self):
  self.seeds={"candidates":[{"id":"seed-a"},{"id":"seed-b"}]}
  self.ecosystems={"ecosystems":[{"id":"python"}]}
  self.coverage={"ecosystems":[{"id":"python"}]}
  candidate=lambda cid:{"candidate_id":cid,"required_work":["resolve_canonical_package_identity","assign_exact_ecosystem_and_official_registry","pin_current_version_and_release_date","verify_official_documentation_and_source_repository","review_license_security_advisories_and_maintenance","inventory_public_api_with_versioned_provenance","write_original_use_cases_and_three_practice_exercises","build_safe_local_sandbox_without_untrusted_execution","define_task_benchmark_and_private_holdout","human_review_and_approve_for_internal_study"],"package_identity_status":"unverified_candidate","license_status":"unknown_pending_review","mastery_status":"not_assessed","rights":{"download":"pending","execution":"prohibited_until_review","training":"pending"}}
  self.queue={"schema":"dreamco.buddy_library_mastery_work_queue.v1","worldwide_completeness_claimed":False,"counts":{"seed_candidates":2},"ecosystem_work_items":[{"ecosystem_id":"python","status":"ecosystem_discovery_review_required"}],"candidate_work_items":[candidate("seed-a"),candidate("seed-b")]}
 def test_exact_candidate_and_ecosystem_coverage(self): self.assertEqual(validate(self.seeds,self.ecosystems,self.coverage,self.queue),[])
 def test_missing_candidate_detected(self):
  self.queue["candidate_work_items"].pop(); self.assertTrue(any("candidate coverage mismatch" in e for e in validate(self.seeds,self.ecosystems,self.coverage,self.queue)))
 def test_rights_promotion_rejected(self):
  self.queue["candidate_work_items"][0]["rights"]["execution"]="approved"; self.assertTrue(any("rights boundary weakened" in e for e in validate(self.seeds,self.ecosystems,self.coverage,self.queue)))
 def test_mastery_claim_rejected(self):
  self.queue["candidate_work_items"][0]["mastery_status"]="mastered"; self.assertTrue(any("cannot claim mastery" in e for e in validate(self.seeds,self.ecosystems,self.coverage,self.queue)))
 def test_worldwide_completeness_claim_rejected(self):
  self.queue["worldwide_completeness_claimed"]=True; self.assertTrue(any("worldwide completeness" in e for e in validate(self.seeds,self.ecosystems,self.coverage,self.queue)))
if __name__=="__main__": unittest.main()
