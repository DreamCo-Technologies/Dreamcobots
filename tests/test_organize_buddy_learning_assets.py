import unittest
from tools.organize_buddy_learning_assets import organize

class LearningOrganizationTests(unittest.TestCase):
    def guide(self, training=False, review="approved"):
        return {"schema":"dreamco.buddy_source_study_guide.v1",
          "source":{"source_type":"github","source_id":"demo/repo","url":"https://github.com/demo/repo","revision":"abc","license":"MIT"},
          "rights":{"study_permission":True,"summary_derivative_permission":True,"evaluation_permission":True,"training_permission":training,"evidence_ref":"rights:123"},
          "review":{"status":review,"reviewer":"human-reviewer","reviewed_at":"2026-11-24T12:00:00Z"},
          "summary":{"executive_overview":"overview " * 25,"detailed_explanation":"detailed explanation " * 30},
          "division_mapping":[{"division":"AI"}],
          "learning_objectives":["one","two","three"],"prerequisites":["python"],
          "sections":[{"heading":"intro","explanation":"section explanation " * 8,"source_locator":"README.md#intro"}],
          "key_concepts":[{"name":f"concept-{i}","explanation":"concept explanation"} for i in range(5)],
          "worked_examples":[{"name":"demo"}],
          "exercises":[{"name":f"exercise-{i}"} for i in range(3)],
          "knowledge_checks":[{"q":f"q-{i}"} for i in range(5)],
          "answer_key":[{"answer":f"a-{i}"} for i in range(5)],
          "references":[{"url":"https://github.com/demo/repo"}],
          "capstone":{"goal":"build a demo","acceptance_tests":["test passes"]}}
    def test_maps_summary_to_division_and_study_path(self):
        result=organize([self.guide()],["AI","Sales"])
        self.assertEqual(result["coverage"]["approved_guides_organized"],1)
        self.assertEqual(result["coverage"]["guides_rejected_or_pending"],0)
        p=result["packages"][0]
        self.assertEqual(p["division_ids"],["AI"])
        self.assertEqual(len(p["study_path"]["sequence"]),7)
        self.assertFalse(p["training"]["weight_training_eligible"])
        self.assertIn("core_concepts",p["summary"]["best_knowledge_extracted"])
        self.assertIn("detailed_sections",p["summary"]["best_knowledge_extracted"])
        self.assertIn("capstone",p["summary"]["best_knowledge_extracted"])
        self.assertEqual(p["study_path"]["sequence"][-1]["type"],"capstone")
        self.assertEqual(p["progress"]["mastery_status"],"not_assessed")
        self.assertEqual(result["division_curricula"][0]["available_learning_assets"],1)
    def test_only_approved_guides_are_organized(self):
        result=organize([self.guide(review="draft")],["AI"])
        self.assertEqual(result["packages"],[])
        self.assertEqual(result["coverage"]["guides_rejected_or_pending"],1)

    def test_incomplete_summary_is_rejected_with_reasons(self):
        guide=self.guide()
        guide["summary"]["detailed_explanation"]="too short"
        result=organize([guide],["AI"])
        self.assertEqual(result["packages"],[])
        self.assertTrue(any("detailed_explanation" in e for e in result["rejected_or_pending_guides"][0]["errors"]))
    def test_training_permission_is_separate(self):
        result=organize([self.guide(training=True)],["AI"])
        self.assertTrue(result["packages"][0]["training"]["weight_training_eligible"])
    def test_user_data_keeps_user_ownership_and_scope(self):
        data=[{"asset_id":"mine","consent_scope":["study"],"study_allowed":True,"training_allowed":False}]
        result=organize([],["AI"],data)
        self.assertEqual(result["user_data_registry"][0]["owner"],"user")
        self.assertFalse(result["user_data_registry"][0]["training_allowed"])
        self.assertIn("purpose-specific",result["user_data_registry"][0]["ownership_note"])
        self.assertEqual(result["coverage"]["user_data_assets_registered"],1)

if __name__=="__main__":unittest.main()
