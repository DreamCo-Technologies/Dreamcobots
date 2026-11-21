import unittest
from buddy.certification.training_planner import propose

class TrainingPlannerTests(unittest.TestCase):
    def setUp(self):
        self.plan={"schema":"dreamco.unified_build_training_plan.v1","training_loop":{"methods":["tool_improvement","retrieval","prompt_or_policy"]}}
        self.daily={"schema":"dreamco.daily_capability_lab.v1","results":[{"id":"x","kind":"tool","gaps":["No baseline"],"duplicate_of":None}]}
    def test_proposes_without_training(self):
        x=propose(self.plan,self.daily)
        self.assertEqual(x["total"],1)
        self.assertFalse(x["tasks"][0]["training_started"])
        self.assertFalse(x["automatic_execution"])
    def test_skips_exact_duplicate(self):
        self.daily["results"][0]["duplicate_of"]="original"
        self.assertEqual(propose(self.plan,self.daily)["total"],0)
    def test_rejects_wrong_schema(self):
        with self.assertRaises(ValueError):
            propose({},self.daily)
if __name__=="__main__":
    unittest.main()
