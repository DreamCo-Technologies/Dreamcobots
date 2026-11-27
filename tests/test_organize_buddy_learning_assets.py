import unittest
from tools.organize_buddy_learning_assets import organize

class LearningOrganizationTests(unittest.TestCase):
    def guide(self, training=False, review="approved"):
        return {"schema":"dreamco.buddy_source_study_guide.v1",
          "source":{"source_type":"github","source_id":"demo/repo","url":"https://github.com/demo/repo","revision":"abc","license":"MIT"},
          "rights":{"study_permission":True,"summary_derivative_permission":True,"evaluation_permission":True,"training_permission":training,"evidence_ref":"rights:123"},
          "review":{"status":review,"reviewer":"human-reviewer","reviewed_at":"2026-11-24T12:00:00Z"},
          "authorship":{"authoring_entity":"ChatGPT GPT-6","authoring_model":"GPT-6","model_version":"GPT-6","commissioned_for":"user","human_contribution":"User directed scope, ownership intent and division mapping.","owner_designation":"User-designated owner of original DreamCo-authored expression.","owner_confirmation_status":"pending"},
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
        self.assertEqual(p["ownership"]["artifact_owner"],"user_designated_owner")
        self.assertEqual(len(p["study_path"]["sequence"]),10)
        self.assertFalse(p["training"]["weight_training_eligible"])
        self.assertIn("core_concepts",p["summary"]["best_knowledge_extracted"])
        self.assertIn("detailed_sections",p["summary"]["best_knowledge_extracted"])
        self.assertIn("capstone",p["summary"]["best_knowledge_extracted"])
        self.assertEqual(p["study_path"]["sequence"][-1]["type"],"teach_back_and_transfer")
        self.assertEqual(p["progress"]["mastery_status"],"not_assessed")
        self.assertEqual(result["division_curricula"][0]["available_learning_assets"],1)
    def test_structured_division_registry_rows_are_normalized(self):
        result=organize([self.guide()],[{"id":"ai","name":"AI"},{"division":"Sales"}])
        self.assertEqual(result["coverage"]["divisions"],2)
        self.assertEqual(result["coverage"]["approved_guides_organized"],1)
        self.assertEqual(result["packages"][0]["division_ids"],["AI"])

    def test_invalid_or_duplicate_division_registry_rows_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"non-empty name or division"):
            organize([], [{"id":"missing-name"}])
        with self.assertRaisesRegex(ValueError,"duplicate division names"):
            organize([], ["AI", {"name":"AI"}])

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
    def test_occupational_guide_requires_software_agent_and_commercial_depth(self):
        guide=self.guide()
        guide["source"]["source_type"]="onet_task"
        guide["workflow"]=[{"step":i,"inputs":"in","actions":"do","outputs":"out","verification":"check"} for i in range(5)]
        guide["software_and_tools"]=[{"category":"CRM","capabilities":"manage leads","examples":"tool A","alternatives":"open source","verification_date":"2026-11-24","license_or_pricing_review":"checked"} for _ in range(3)]
        guide["agent_capabilities"]=["research","CRM","reporting"]
        guide["commercial_pathway"]={"buyer_research":[],"offer_scope":{},"pricing_model":{},"sales_workflow":[],"eligibility_and_credentials":[]}
        result=organize([guide],["AI"])
        self.assertEqual(result["coverage"]["approved_guides_organized"],1)
        extracted=result["packages"][0]["summary"]["best_knowledge_extracted"]
        self.assertEqual(len(extracted["software_and_tools"]),3)
        self.assertEqual(len(extracted["agent_capabilities"]),3)

    def test_missing_ownership_record_blocks_guide(self):
        guide=self.guide()
        del guide["authorship"]
        result=organize([guide],["AI"])
        self.assertEqual(result["packages"],[])
        self.assertTrue(any("authorship" in e for e in result["rejected_or_pending_guides"][0]["errors"]))

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
