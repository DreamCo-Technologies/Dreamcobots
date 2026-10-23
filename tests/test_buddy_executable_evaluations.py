import unittest
from unittest.mock import patch
from buddy.certification.executable_evaluations import evaluate, compare
from buddy.certification.model_benchmarks import CallableAdapter

class ExecutableTests(unittest.TestCase):
    def test_research(self):
        a=CallableAdapter("fixture",lambda p:"25")
        result=evaluate({"id":"r","domain":"research","kind":"research",
                         "prompt":"question","expected":"25"},a)
        self.assertTrue(result["passed"])
        self.assertFalse(result["independent_verified"])
    def test_real_stateful_tools(self):
        a=CallableAdapter("fixture",lambda p:'["read_inventory","read_reserved","calculate_available","publish"]')
        result=evaluate({"id":"t","domain":"multi_step_tools","kind":"multi_step_tools",
                         "prompt":"question","inventory":8,"reserved":3},a)
        self.assertTrue(result["passed"])
        self.assertTrue(result["receipt"]["sandbox_executed"])
    def test_code_requires_sandbox(self):
        a=CallableAdapter("fixture",lambda p:"def square(n): return n*n")
        with patch("buddy.certification.executable_evaluations.run_python_tests",
                   return_value={"passed":False,"sandbox_executed":False}):
            result=evaluate({"id":"c","domain":"coding","kind":"coding_python",
                             "prompt":"question","hidden_tests":"hidden"},a)
        self.assertFalse(result["passed"])
    def test_cannot_claim_certification(self):
        a=CallableAdapter("fixture",lambda p:"25")
        result=compare([{"id":"r","domain":"research","kind":"research",
                         "prompt":"question","expected":"25"}],[a])
        self.assertFalse(result["champions_certified"])

if __name__=="__main__":
    unittest.main()
