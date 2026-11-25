import unittest
from tools.build_buddy_source_study_queue import build_queue, validate_guide

class SourceStudyQueueTests(unittest.TestCase):
    def setUp(self):
        self.row={"source_type":"huggingface_dataset","source_id":"org/demo","url":"https://huggingface.co/datasets/org/demo"}
        self.snapshot={"generated_at":"2026-11-24T00:00:00Z","resources":[self.row]}
    def test_unknown_rights_are_blocked(self):
        result=build_queue(self.snapshot,{"resources":[]})
        self.assertEqual(result["counts"]["rights_pending"],1)
        self.assertEqual(result["queue"][0]["status"],"rights_pending")
    def test_all_separate_permissions_and_evidence_required(self):
        grant={**self.row,"study_permission":True,"summary_derivative_permission":True,"evaluation_permission":True,"training_permission":False,"evidence_ref":"license-review-42"}
        result=build_queue(self.snapshot,{"resources":[grant]})
        self.assertEqual(result["counts"]["guide_authoring_eligible"],1)
        self.assertFalse(result["queue"][0]["training_permission"])
    def test_training_permission_does_not_replace_study_permissions(self):
        grant={**self.row,"training_permission":True,"evidence_ref":"review"}
        result=build_queue(self.snapshot,{"resources":[grant]})
        self.assertEqual(result["queue"][0]["status"],"rights_pending")
    def test_queue_is_not_mastery(self):
        result=build_queue(self.snapshot,{"resources":[]})
        self.assertIn("not a completed summary",result["truth_boundary"])
    def test_guide_validation_rejects_unapproved_source(self):
        errors=validate_guide({},{"source_type":"github_repository","source_id":"a/b","url":"https://github.com/a/b","status":"rights_pending"})
        self.assertIn("source is not rights-cleared for guide authoring",errors)

if __name__=="__main__": unittest.main()
