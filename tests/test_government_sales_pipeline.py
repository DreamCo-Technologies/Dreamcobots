import unittest
from datetime import date
from tools.build_government_sales_pipeline import build

class SalesPipelineTests(unittest.TestCase):
    def test_every_onet_task_gets_a_sales_playbook(self):
        tasks={"occupations":[{"occupation_code":"15-1252.00","occupation_title":"Software Developers",
          "tasks":[{"task_id":"1","task":"Write code"},{"task_id":"2","task":"Test software"}]}]}
        result=build(tasks,{"opportunities":[]},date(2026,11,24))
        self.assertEqual(result["counts"]["onet_task_playbooks"],2)
        self.assertTrue(all(x["human_approval_required"] for x in result["task_playbooks"]))
    def test_only_fully_verified_opportunity_is_ready_for_bid_review(self):
        tasks={"occupations":[]}
        good={"opportunity_id":"A","title":"IT support","agency":"City","due_date":"2026-12-01","url":"https://example.gov/a",
          "active":True,"eligibility_verified":True,"capability_match_verified":True,"compliance_review_passed":True}
        bad={"opportunity_id":"B","title":"Unknown","due_date":"2026-11-01","active":True}
        result=build(tasks,{"opportunities":[good,bad]},date(2026,11,24))
        self.assertEqual(result["government_opportunities"][0]["status"],"bid_review_ready")
        self.assertEqual(result["government_opportunities"][1]["status"],"expired_or_inactive")
    def test_invalid_due_date_never_qualifies_for_bid_review(self):
        result=build({"occupations":[]},{"opportunities":[{"opportunity_id":"C","active":True,
          "eligibility_verified":True,"capability_match_verified":True,"compliance_review_passed":True}]},date(2026,11,24))
        opportunity=result["government_opportunities"][0]
        self.assertEqual(opportunity["status"],"human_review_required")
        self.assertIn("due_date_valid",opportunity["missing_checks"])
        self.assertEqual(opportunity["readiness_checks"],6)

    def test_no_automatic_outreach_or_bid(self):
        result=build({"occupations":[]},{"opportunities":[]},date(2026,11,24))
        self.assertTrue(result["policy"]["no_auto_outreach"])
        self.assertTrue(result["policy"]["no_auto_bid_submission"])

if __name__=="__main__": unittest.main()
