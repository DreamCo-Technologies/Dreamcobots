import unittest
from buddy.certification.fleet_study_pages import paginate

class FleetPagesTests(unittest.TestCase):
    def test_all_goals_once(self):
        goals={"schema":"dreamco.all_bot_goals.v1","goals":[
            {"id":str(i),"bot_id":"b","division":"D","goal":"g"}
            for i in range(7)]}
        champions={"schema":"dreamco.task_champions.v1","champions":[]}
        manifest,pages=paginate(goals,champions,page_size=3)
        self.assertEqual(manifest["pages"],3)
        self.assertEqual(manifest["queued_goals"],7)
        self.assertEqual([len(p["tasks"]) for p in pages],[3,3,1])
        self.assertTrue(manifest["all_pages_review_only"])
    def test_duplicate_rejected(self):
        goals={"schema":"dreamco.all_bot_goals.v1","goals":[
            {"id":"duplicate","bot_id":"b","division":"D","goal":"g"}]*2}
        with self.assertRaises(ValueError):
            paginate(goals,{"schema":"dreamco.task_champions.v1","champions":[]})

if __name__=="__main__":
    unittest.main()
