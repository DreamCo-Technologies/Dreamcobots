import unittest

from buddy.builder.strategy_runner import run


class StrategyRunnerTest(unittest.TestCase):
    def test_run_records_a_receipt_and_no_score(self) -> None:
        with self.assertRaises(PermissionError):
            run("ReAct", False)
        report = run("ReAct", True)
        self.assertIsNone(report["score"])
        self.assertFalse(report["model_called"])


if __name__ == "__main__":
    unittest.main()
