import unittest
from buddy.certification.task_distillation import distill
from buddy.certification.tool_execution_bench import execute

class TaskDistillationTests(unittest.TestCase):
    def test_rights_and_dedup(self):
        row={"rights":"owned","permission_to_derive":True,"domain":"coding",
             "task_description":"Fix parser","success_criteria":"All tests pass"}
        x=distill([row,row,{**row,"rights":"unknown"}])
        self.assertEqual(x["count"],1)
        self.assertFalse(x["tasks"][0]["holdout_answer_in_training"])
    def test_no_permission(self):
        self.assertEqual(distill([{"rights":"licensed","domain":"research",
           "task_description":"Study","success_criteria":"Accurate"}])["count"],0)
    def test_real_stateful_sandbox(self):
        x=execute(["read_inventory","read_reserved","calculate_available","publish"])
        self.assertEqual(x["state"]["available"],5)
        self.assertTrue(x["state"]["published"])
        self.assertTrue(x["sandbox_executed"])
    def test_publish_requires_calculation(self):
        x=execute(["publish"])
        self.assertFalse(x["state"]["published"])
        self.assertEqual(x["receipts"][0]["status"],"blocked")
    def test_unknown_action_rejected(self):
        with self.assertRaises(ValueError):
            execute(["external_payment"])

if __name__=="__main__":
    unittest.main()
