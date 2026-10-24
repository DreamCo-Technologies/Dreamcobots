"""Regression guard for the Actions workflow_run fanout incident.

This checks workflow definitions, not their execution or benchmark mastery.
The two summary jobs must not launch a fresh run for every completed job.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
SUMMARY_WORKFLOWS = ("actions-command-center.yml", "problem-registry.yml", "greenkeeper-root-cause.yml", "greenkeeper-orchestrator.yml")


def top_level_block(text: str, key: str) -> str:
    """Extract one top-level YAML mapping without a third-party YAML parser.

    This is intentionally a narrow guard for conventional workflow headers,
    not a general YAML parser. Missing or malformed headers fail closed.
    """
    lines = text.splitlines()
    marker = f"{key}:"
    starts = [index for index, line in enumerate(lines) if line.rstrip() == marker]
    if len(starts) != 1:
        raise ValueError(f"expected one top-level {marker} mapping")
    result = []
    for line in lines[starts[0] + 1 :]:
        if line and not line[0].isspace() and not line.lstrip().startswith("#"):
            break
        result.append(line)
    return "\n".join(result)


def event_declared(block: str, event: str) -> bool:
    return bool(re.search(rf"(?m)^\s+{re.escape(event)}\s*:", block))


class WorkflowFanoutGuardTests(unittest.TestCase):
    def test_header_parser_ignores_nested_job_steps(self):
        sample = "on:\n  schedule:\n    - cron: '0 * * * *'\npermissions:\n  contents: read\njobs:\n  demo:\n    steps:\n      - run: echo workflow_run:\n"
        block = top_level_block(sample, "on")
        self.assertTrue(event_declared(block, "schedule"))
        self.assertFalse(event_declared(block, "workflow_run"))

    def test_inline_workflow_run_cannot_bypass_guard(self):
        self.assertTrue(event_declared("  workflow_run: {types: [completed]}", "workflow_run"))
        self.assertTrue(event_declared("  workflow_run: # watch", "workflow_run"))

    def test_summary_workflows_do_not_fan_out_on_every_completed_run(self):
        for filename in SUMMARY_WORKFLOWS:
            with self.subTest(workflow=filename):
                content = (WORKFLOWS / filename).read_text(encoding="utf-8")
                triggers = top_level_block(content, "on")
                self.assertFalse(
                    event_declared(triggers, "workflow_run"),
                    f"{filename} must use bounded schedule/manual triggers, not workflow_run fanout",
                )
                self.assertTrue(event_declared(triggers, "schedule"))
                self.assertTrue(event_declared(triggers, "workflow_dispatch"))

    def test_summary_workflows_are_read_only(self):
        for filename in SUMMARY_WORKFLOWS:
            with self.subTest(workflow=filename):
                content = (WORKFLOWS / filename).read_text(encoding="utf-8")
                permissions = top_level_block(content, "permissions")
                self.assertRegex(permissions, r"(?m)^\s+contents:\s*read\s*$")
                self.assertNotRegex(permissions, r"(?m)^\s+contents:\s*write\s*$")

    def test_greenkeeper_uses_bounded_live_evidence_instead_of_event_fanout(self):
        for filename in ("greenkeeper-root-cause.yml", "greenkeeper-orchestrator.yml"):
            with self.subTest(workflow=filename):
                content = (WORKFLOWS / filename).read_text(encoding="utf-8")
                self.assertIn("tools/greenkeeper_observations.py", content)
                self.assertIn("--max-age-hours 6", content)
                self.assertIn("GH_TOKEN:", content)

    def test_registry_refreshes_evidence_before_classifying(self):
        content = (WORKFLOWS / "problem-registry.yml").read_text(encoding="utf-8")
        health = "python3 tools/audit_actions_health.py"
        registry = "python3 tools/problem_registry.py"
        self.assertIn(health, content)
        self.assertIn(registry, content)
        self.assertLess(content.index(health), content.index(registry))


if __name__ == "__main__":
    unittest.main()
