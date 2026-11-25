import unittest
from tools.organize_buddy_learning_assets import organize

class LearningOrganizationTests(unittest.TestCase):
    def guide(self, training=False, review="approved"):
        return {"source":{"source_type":"github","source_id":"demo/repo","revision":"abc","license":"MIT"},
          "rights":{"study_permission":True,"summary_derivative_permission":True,"evaluation_permission":True,"training_permission":training,"evidence_ref":"rights:123"},
          "review":{"status":review},"summary":{"executive_overview":"overview","detailed_explanation":"details"},
          "division_mapping":[{"division":"AI"}],"learning_objectives":["one"],"prerequisites":["python"],
          "sections":[{"heading":"intro"}],"key_concepts":[{"name":"RAG","explanation":"retrieval"}],
          "worked_examples":[{"name":"demo"}],"exercises":[{"name":"build"}],"knowledge_checks":[{"q":"q"}],
          "capstone":{"acceptance_tests":["test passes"]}}
    def test_maps_summary_to_division_and_study_path(self):
        result=organize([self.guide()],["AI","Sales"])
        self.assertEqual(result["coverage"]["approved_guides_organized"],1)
        p=result["packages"][0]
        self.assertEqual(p["division_ids"],["AI"])
        self.assertEqual(len(p["study_path"]["sequence"]),7)
        self.assertFalse(p["training"]["weight_training_eligible"])
        self.assertEqual(result["division_curricula"][0]["available_learning_assets"],1)
    def test_only_approved_guides_are_organized(self):
        result=organize([self.guide(review="draft")],["AI"])
        self.assertEqual(result["packages"],[])
    def test_training_permission_is_separate(self):
        result=organize([self.guide(training=True)],["AI"])
        self.assertTrue(result["packages"][0]["training"]["weight_training_eligible"])
    def test_user_data_keeps_user_ownership_and_scope(self):
        data=[{"asset_id":"mine","consent_scope":["study"],"study_allowed":True,"training_allowed":False}]
        result=organize([],["AI"],data)
        self.assertEqual(result["user_data_registry"][0]["owner"],"user")
        self.assertFalse(result["user_data_registry"][0]["training_allowed"])

if __name__=="__main__":unittest.main()
