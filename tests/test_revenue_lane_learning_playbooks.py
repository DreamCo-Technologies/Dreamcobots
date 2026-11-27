import unittest
from tools.validate_revenue_lane_learning_playbooks import validate


class RevenueLanePlaybookTests(unittest.TestCase):
    def setUp(self):
        self.source={"lanes":[{"id":"rfp","value":"procurement leads","monetization":["subscription"]}]}
        self.playbooks={"common_policy":{"source_rights_required":True,
            "production_actions_require_explicit_approval":True,"actual_revenue_requires_transaction_evidence":True},
            "lanes":[{"lane_id":"rfp","value":"procurement leads","monetization":["subscription"],
            "status":"playbook_defined_lesson_authoring_pending","learning_objective":"Teach procurement matching",
            "lane_specific_tasks":["Parse official notice","Check fit","Build matrix","Draft for review"],
            "shared_execution_sequence":[{"id":str(i)} for i in range(6)],
            "required_software_research":["commercial","open source"],"required_benchmark":["holdout"],
            "guardrails":["Use official sources"],"truth_rules":["Do not invent revenue"],
            "completion_evidence":["run id"]}]}

    def test_complete_blueprint_matches_source(self):
        self.assertEqual(validate(self.source,self.playbooks),[])

    def test_missing_lane_is_reported(self):
        self.playbooks["lanes"]=[]
        self.assertTrue(any("exactly match" in e for e in validate(self.source,self.playbooks)))

    def test_short_generic_lane_tasks_are_rejected(self):
        self.playbooks["lanes"][0]["lane_specific_tasks"]=["Do work"]
        self.assertTrue(any("four lane-specific" in e for e in validate(self.source,self.playbooks)))

    def test_completed_status_cannot_be_claimed_by_blueprint(self):
        self.playbooks["lanes"][0]["status"]="completed"
        self.assertTrue(any("must not imply" in e for e in validate(self.source,self.playbooks)))

    def test_revenue_must_require_transaction_evidence(self):
        self.playbooks["common_policy"]["actual_revenue_requires_transaction_evidence"]=False
        self.assertTrue(any("transaction_evidence" in e for e in validate(self.source,self.playbooks)))


if __name__=="__main__": unittest.main()
