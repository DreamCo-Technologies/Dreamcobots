import json,tempfile,unittest
from pathlib import Path
from tools.build_division_owner_review_queue import (
 OwnerReviewQueueError,build_owner_review_queue,validate_owner_review_queue)

class DivisionOwnerReviewQueueTests(unittest.TestCase):
 def test_current_source_preserves_all_unresolved_owner_decisions(self):
  root=Path(__file__).resolve().parents[1]
  queue=build_owner_review_queue(root/"config/generated/division-resource-readiness-map.json")
  validate_owner_review_queue(queue)
  self.assertEqual(queue["counts"]["pending_masterbot_mappings"],20)
  self.assertEqual(queue["counts"]["unassigned_domain_profiles"],10)
  self.assertTrue(all(x["no_mapping_inferred"] for x in queue["masterbot_domain_decisions"]))
 def test_builds_pending_queue_without_guessing(self):
  source={"owner_review":{"masterbot_domain_decisions":[
   {"masterbot_id":1,"masterbot_name":"Alpha","primary_domain_id":None,
    "candidate_domain_ids":[],"resource_bundle_id":"division-resource-001",
    "decision":"PENDING_OWNER_REVIEW","owner_approval":None,"evidence":[]}],
   "unassigned_domain_profiles":[{"domain_id":"alpha-domain","domain_name":"Alpha Domain",
    "candidate_masterbot_ids":[],"standalone_resource_bundle_id":"domain-resource-alpha",
    "decision":"PENDING_OWNER_REVIEW","owner_approval":None,"evidence":[]}]}}
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"map.json";path.write_text(json.dumps(source))
   queue=build_owner_review_queue(path)
  validate_owner_review_queue(queue)
  self.assertIsNone(queue["masterbot_domain_decisions"][0]["proposed_primary_domain_id"])
  self.assertEqual(queue["unassigned_domain_profiles"][0]["candidate_masterbot_ids"],[])
 def test_rejects_owner_approval_in_pending_queue(self):
  queue={"schema":"dreamco.division_owner_review_queue.v1",
   "counts":{"pending_masterbot_mappings":1,"unassigned_domain_profiles":0},
   "masterbot_domain_decisions":[{"decision":"PENDING_OWNER_REVIEW","no_mapping_inferred":True,
    "owner_approval":{"approval_id":"fake"}}],"unassigned_domain_profiles":[]}
  with self.assertRaisesRegex(OwnerReviewQueueError,"separate_signed_decision"):
   validate_owner_review_queue(queue)
 def test_rejects_inferred_mapping(self):
  queue={"schema":"dreamco.division_owner_review_queue.v1",
   "counts":{"pending_masterbot_mappings":1,"unassigned_domain_profiles":0},
   "masterbot_domain_decisions":[{"decision":"APPROVED","no_mapping_inferred":False}],
   "unassigned_domain_profiles":[]}
  with self.assertRaisesRegex(OwnerReviewQueueError,"inferred_assignment"):
   validate_owner_review_queue(queue)

if __name__=="__main__": unittest.main()
