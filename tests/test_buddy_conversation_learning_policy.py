import unittest
from tools.buddy_conversation_learning_policy import evaluate_candidate
POLICY = {"cross_user_learning": {"minimum_cohort_size": 20}}
class BuddyConversationLearningPolicyTests(unittest.TestCase):
    def test_personal_memory_requires_opt_in_and_user_scope(self):
        c={"scope":"personal_memory","content_form":"structured_preference","personal_memory_opt_in":True,"user_id":"user-1","retention_days":90}
        self.assertEqual(evaluate_candidate(c,POLICY)["decision"],"ALLOW_CANDIDATE")
    def test_sensitive_personal_memory_requires_separate_opt_in(self):
        c={"scope":"personal_memory","content_form":"structured_preference","personal_memory_opt_in":True,"user_id":"u1","retention_days":30,"contains_sensitive_data":True}
        self.assertIn("sensitive_memory_opt_in_required",evaluate_candidate(c,POLICY)["reasons"])
        c["sensitive_memory_opt_in"]=True
        self.assertEqual(evaluate_candidate(c,POLICY)["decision"],"ALLOW_CANDIDATE")
    def test_raw_transcript_is_never_accepted(self):
        c={"scope":"personal_memory","content_form":"raw_transcript","raw_transcript":True,"personal_memory_opt_in":True,"user_id":"u1","retention_days":30}
        r=evaluate_candidate(c,POLICY); self.assertEqual(r["decision"],"DENY"); self.assertIn("raw_transcript_prohibited",r["reasons"])
    def test_cross_user_requires_separate_opt_ins_and_minimum_cohort(self):
        c={"scope":"cross_user_shared","content_form":"aggregate_pattern","product_improvement_opt_in":True,"cross_user_sharing_opt_in":True,"deidentified":True,"cohort_size":20}
        self.assertEqual(evaluate_candidate(c,POLICY)["decision"],"ALLOW_CANDIDATE")
        c["cohort_size"]=3; self.assertIn("minimum_cohort_not_met",evaluate_candidate(c,POLICY)["reasons"])
    def test_shared_records_reject_identifiers_and_sensitive_data(self):
        c={"scope":"cross_user_shared","content_form":"aggregate_pattern","product_improvement_opt_in":True,"cross_user_sharing_opt_in":True,"deidentified":True,"cohort_size":30,"user_id":"u1","contains_sensitive_data":True}
        r=evaluate_candidate(c,POLICY); self.assertEqual(r["decision"],"DENY"); self.assertIn("direct_identifiers_prohibited_in_shared_record",r["reasons"])
    def test_foundation_model_training_has_separate_evidence_gates(self):
        c={"scope":"foundation_model_training","content_form":"verified_procedure","foundation_model_training_opt_in":True,"rights_evidence":True,"deidentified":True,"privacy_review_passed":True,"human_review_passed":True,"dataset_card_present":True,"withdrawal_path_present":True}
        self.assertEqual(evaluate_candidate(c,POLICY)["decision"],"ALLOW_CANDIDATE"); c["foundation_model_training_opt_in"]=False; self.assertEqual(evaluate_candidate(c,POLICY)["decision"],"DENY")
if __name__ == "__main__": unittest.main()
