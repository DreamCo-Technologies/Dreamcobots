import unittest
from buddy.datasets.license_policy import assess_training_candidate,normalize_license
from buddy.datasets.discovery_fleet import _query_for
class DatasetLicensePolicyTests(unittest.TestCase):
 def candidate(self):
  return {"source":"huggingface","id":"org/dataset","url":"https://huggingface.co/datasets/org/dataset",
   "license":"cc-by-4.0","ai_training_allowed":True,"content_rights_verified":True,"privacy_review":"PASSED"}
 def test_allowlisted_license_is_only_a_candidate_not_approval(self):
  result=assess_training_candidate(self.candidate())
  self.assertIn("CANDIDATE",result["status"])
  self.assertFalse(result["training_approved"])
 def test_public_listing_or_license_alone_does_not_allow_training(self):
  item=self.candidate();item.pop("ai_training_allowed")
  self.assertEqual(assess_training_candidate(item)["status"],"BLOCKED_NO_EXPLICIT_AI_TRAINING_PERMISSION")
 def test_unknown_or_restrictive_license_is_blocked(self):
  item=self.candidate();item["license"]="CC-BY-NC-4.0"
  self.assertEqual(assess_training_candidate(item)["status"],"BLOCKED_LICENSE_REQUIRES_MANUAL_TERMS_REVIEW")
  item["license"]="unknown"
  self.assertEqual(assess_training_candidate(item)["status"],"BLOCKED_UNKNOWN_LICENSE")
 def test_unverified_privacy_and_rights_are_blocked(self):
  item=self.candidate();item["privacy_review"]="PENDING"
  self.assertEqual(assess_training_candidate(item)["status"],"BLOCKED_PRIVACY_REVIEW")
  item["privacy_review"]="PASSED";item["content_rights_verified"]=False
  self.assertEqual(assess_training_candidate(item)["status"],"BLOCKED_CONTENT_RIGHTS_UNVERIFIED")
 def test_aliases_normalize(self):
  self.assertEqual(normalize_license("Apache 2.0"),"Apache-2.0")
 def test_all_masterbots_have_query_fallback(self):
  self.assertTrue(_query_for("DreamFinance"))
  self.assertTrue(_query_for("DreamUnknownDivision"))
if __name__=="__main__":unittest.main()
