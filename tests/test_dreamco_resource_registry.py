import unittest
from scripts.validate_dreamco_resource_registry import validate
class ResourceRegistryTests(unittest.TestCase):
 def test_unknown_rights_are_blocked(self):
  item={"id":"X","name":"source","category":"test","resource_type":"dataset","acquisition_status":"NOT_ACQUIRED","license_status":"UNVERIFIED","commercial_training_permission":"NOT_ESTABLISHED","quarantine_status":"BLOCKED_PENDING_REVIEW","source_provenance_required":True,"sha256_required":True}
  self.assertEqual(validate({"resource_count":1,"resources":[item]}),[])
 def test_training_approval_requires_evidence(self):
  item={"id":"X","name":"source","category":"test","resource_type":"dataset","acquisition_status":"ACQUIRED","license_status":"VERIFIED","commercial_training_permission":"APPROVED","quarantine_status":"APPROVED_FOR_TRAINING","source_provenance_required":True,"sha256_required":True}
  self.assertTrue(validate({"resource_count":1,"resources":[item]}))
 def test_registry_rejects_wrong_count(self):
  self.assertTrue(validate({"resource_count":0,"resources":[]}))
if __name__=="__main__": unittest.main()
