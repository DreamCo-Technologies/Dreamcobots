import unittest
from tools.buddy_division_coverage import build

def fixture():
    return (
        {"canonical_count":2,"divisions":[{"id":1,"name":"DreamScience"},{"id":2,"name":"DreamFinance"}]},
        {"tasks":["reasoning","sql"]},
        {"examples":[{"division":"DreamScience","task_family":"reasoning"}]},
        {"goals":[{"status":"PARTIAL"},{"status":"BLOCKED"}]},
    )

class DivisionCoverageTests(unittest.TestCase):
    def test_requirements_not_misrepresented_as_measurements(self):
        result=build(*fixture())
        self.assertEqual(result["counts"]["required_division_task_pairs"],4)
        self.assertEqual(result["counts"]["measured_pairs_in_this_report"],0)
        self.assertFalse(result["production_ready"])
        self.assertEqual(result["counts"]["divisions_without_model_route_example"],1)
    def test_goal_statuses(self):
        self.assertEqual(build(*fixture())["counts"]["goal_statuses"],{"BLOCKED":1,"PARTIAL":1})
    def test_duplicate_division_rejected(self):
        data=list(fixture());data[0]["divisions"][1]["id"]=1
        with self.assertRaises(ValueError):build(*data)
    def test_count_mismatch_rejected(self):
        data=list(fixture());data[0]["canonical_count"]=65
        with self.assertRaises(ValueError):build(*data)
    def test_duplicate_task_rejected(self):
        data=list(fixture());data[1]["tasks"]=["sql","sql"]
        with self.assertRaises(ValueError):build(*data)
    def test_deterministic(self):
        self.assertEqual(build(*fixture()),build(*fixture()))

if __name__=="__main__":unittest.main()
