import unittest
from buddy.certification.fleet_study_queue import make_queue

def goal():
    return {"schema":"dreamco.all_bot_goals.v1","goals":[
        {"id":"g1","bot_id":"Code/a","division":"Code","goal":"Fix tests",
         "declared_learning_plan":["Official docs"],"tools_needed":["sandbox"]}]}

class FleetQueueTests(unittest.TestCase):
    def test_unverified_champion_not_assumed(self):
        report=make_queue(goal(),{"schema":"dreamco.task_champions.v1",
          "champions":[{"goal_id":"g1","champion_model":"model-x","selection_basis":"unverified"}]})
        self.assertIsNone(report["tasks"][0]["champion_model"])
        self.assertEqual(report["tasks"][0]["next_action"],"design_independent_executable_benchmark")
    def test_verified_mapping(self):
        report=make_queue(goal(),{"schema":"dreamco.task_champions.v1",
          "champions":[{"goal_id":"g1","champion_model":"model-y",
           "selection_basis":"independently_verified_comparable_trials","buddy_gap":0.15}]})
        self.assertEqual(report["tasks"][0]["next_action"],"study_and_retest_specific_failure")
        self.assertEqual(report["tasks"][0]["champion_model"],"model-y")
        self.assertFalse(report["tasks"][0]["training_started"])
    def test_pagination(self):
        g=goal()
        g["goals"].append({**g["goals"][0],"id":"g2","bot_id":"Code/b"})
        empty={"schema":"dreamco.task_champions.v1","champions":[]}
        first=make_queue(g,empty,max_items=1,offset=0)
        second=make_queue(g,empty,max_items=1,offset=1)
        self.assertNotEqual(first["tasks"][0]["goal_id"],second["tasks"][0]["goal_id"])
        self.assertEqual(first["remaining"],1)
        self.assertEqual(second["remaining"],0)
    def test_budget(self):
        with self.assertRaises(ValueError):
            make_queue(goal(),{"schema":"dreamco.task_champions.v1"},max_items=0)

if __name__=="__main__":
    unittest.main()
