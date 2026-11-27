import unittest
from scripts.validate_dreamco_resource_registry import validate
def sample(**updates):
 item={"id":"X","name":"source","category":"test","resource_type":"dataset","acquisition_status":"NOT_ACQUIRED","license_status":"UNVERIFIED","commercial_training_permission":"NOT_ESTABLISHED","quarantine_status":"BLOCKED_PENDING_REVIEW","source_provenance_required":True,"sha256_required":True}
 item.update(updates);return item
class ResourceRegistryTests(unittest.TestCase):
 def test_unknown_rights_are_validly_blocked(self):
  self.assertEqual(validate({"resource_count":1,"resources":[sample()]},expected_count=1),[])
 def test_training_approval_without_evidence_is_rejected(self):
  item=sample(acquisition_status="ACQUIRED",license_status="VERIFIED",commercial_training_permission="APPROVED",quarantine_status="APPROVED_FOR_TRAINING")
  self.assertTrue(validate({"resource_count":1,"resources":[item]},expected_count=1))
 def test_training_approval_requires_sha256_and_review(self):
  item=sample(acquisition_status="ACQUIRED",license_status="VERIFIED",commercial_training_permission="APPROVED",quarantine_status="APPROVED_FOR_TRAINING",license_evidence="contract",source_url="https://example.org/data",snapshot_sha256="a"*64,reviewed_by="reviewer")
  self.assertEqual(validate({"resource_count":1,"resources":[item]},expected_count=1),[])
 def test_rights_approval_alone_does_not_open_quarantine(self):
  item=sample(license_status="VERIFIED",license_evidence="license",commercial_training_permission="APPROVED")
  self.assertTrue(validate({"resource_count":1,"resources":[item]},expected_count=1))
 def test_registry_rejects_wrong_count(self):
  self.assertTrue(validate({"resource_count":0,"resources":[]}))
if __name__=="__main__": unittest.main()
