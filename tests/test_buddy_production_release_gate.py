import unittest
from buddy.certification.production_release_gate import evaluate_release,REQUIRED

class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.goals={"schema":"dreamco.all_bot_goals.v1",
                    "goals":[{"id":"g1"},{"id":"g2"}]}
    def test_missing_evidence_blocks_everything(self):
        r=evaluate_release(self.goals,{"goals":{}})
        self.assertEqual(r["blocked_goals"],2)
        self.assertFalse(r["fleet_production_ready"])
    def test_partial_evidence_not_fleet_ready(self):
        r=evaluate_release(self.goals,{"goals":{"g1":dict.fromkeys(REQUIRED,True)}})
        self.assertEqual(r["evidence_ready_goals"],1)
        self.assertFalse(r["fleet_production_ready"])
    def test_complete_evidence_required(self):
        checks=dict.fromkeys(REQUIRED,True)
        r=evaluate_release(self.goals,{"goals":{"g1":checks,"g2":checks}})
        self.assertTrue(r["fleet_production_ready"])
    def test_empty_inventory_not_ready(self):
        r=evaluate_release({"schema":"dreamco.all_bot_goals.v1","goals":[]},{"goals":{}})
        self.assertFalse(r["fleet_production_ready"])

if __name__=="__main__":
    unittest.main()
