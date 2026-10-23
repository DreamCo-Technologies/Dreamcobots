"""Regression contracts for high-frequency GitHub Actions workflow fanout.

The command-center and problem-registry reports are hourly snapshots.
They must not subscribe to every upstream workflow completion because
large upstream fanout causes cancelled runs and unnecessary queued jobs.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def triggers(path: str) -> str:
    content = (ROOT / path).read_text(encoding="utf-8")
    return content.split("\npermissions:", 1)[0]


class WorkflowFanoutBudgetTests(unittest.TestCase):
    def test_actions_command_center_remains_hourly_and_manual(self):
        block = triggers(".github/workflows/actions-command-center.yml")
        self.assertRegex(block, r"(?m)^  workflow_dispatch:\s*$")
        self.assertRegex(block, r"(?m)^  schedule:\s*$")
        self.assertRegex(block, r'(?m)^    - cron: ["\']11 \* \* \* \*["\']$')
        self.assertNotRegex(block, r"(?m)^  workflow_run:\s*$")
        self.assertRegex(block, r"(?m)^  push:\s*$")
        self.assertRegex(block, r"(?m)^    branches: \[main\]$")

    def test_problem_registry_remains_hourly_and_manual(self):
        block = triggers(".github/workflows/problem-registry.yml")
        self.assertRegex(block, r"(?m)^  workflow_dispatch:\s*$")
        self.assertRegex(block, r"(?m)^  schedule:\s*$")
        self.assertRegex(block, r'(?m)^    - cron: ["\']17 \* \* \* \*["\']$')
        self.assertNotRegex(block, r"(?m)^  workflow_run:\s*$")


if __name__ == "__main__":
    unittest.main()
