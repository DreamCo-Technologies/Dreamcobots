import unittest
from tools.build_onet_task_curricula import build

class OnetCurriculaTests(unittest.TestCase):
    def test_builds_all_tasks_and_occupation_path(self):
        rows=[
          {"O*NET-SOC Code":"15-1252.00","Task ID":"1","Task":"Write code","Task Type":"Core","Date":"31.0"},
          {"O*NET-SOC Code":"15-1252.00","Task ID":"2","Task":"Test software","Task Type":"Supplemental","Date":"31.0"},
          {"O*NET-SOC Code":"41-2031.00","Task ID":"3","Task":"Assist customers","Task Type":"Core","Date":"31.0"}
        ]
        result=build(rows,"31.0")
        self.assertEqual(result["inventory"]["occupations"],2)
        self.assertEqual(result["inventory"]["task_statements"],3)
        dev=next(x for x in result["occupations"] if x["occupation_code"]=="15-1252.00")
        self.assertEqual(dev["task_count"],2)
        self.assertEqual(len(dev["task_playbooks"]),2)
        self.assertTrue(all(x["commercial_pathway"]["not_a_claim_of_qualification"] for x in dev["task_playbooks"]))
    def test_empty_or_incomplete_rows_do_not_create_fake_tasks(self):
        result=build([{"O*NET-SOC Code":"15-1252.00","Task ID":"","Task":"missing id"}],"31.0")
        self.assertEqual(result["inventory"]["task_statements"],0)
    def test_output_warns_not_certification(self):
        result=build([{"O*NET-SOC Code":"15-1252.00","Task ID":"1","Task":"Write code"}],"31.0")
        self.assertIn("not occupational certification",result["truth_boundary"])

if __name__=="__main__": unittest.main()
