from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from benchmarks.buddy_benchmark_runner import run

ROOT = Path(__file__).resolve().parents[1]


class BuddyEpicFoundationTest(unittest.TestCase):
    def test_universal_benchmark_runner_is_free_first_and_deterministic(self) -> None:
        task_file = ROOT / "benchmarks" / "tasks" / "universal_1000_smoke.json"
        report = run(task_file)
        self.assertEqual(report["benchmark_id"], 1000)
        self.assertTrue(report["free_first"])
        self.assertEqual(report["cost_usd"], 0.0)
        self.assertIsInstance(report["results"], list)

    def test_client_entry_uses_tailwind_v4_stylesheet(self) -> None:
        main = (ROOT / "client/src/main.tsx").read_text(encoding="utf-8")
        self.assertIn('"./index-v4.css"', main)
        css = (ROOT / "client/src/index-v4.css").read_text(encoding="utf-8")
        self.assertIn('@import "tailwindcss";', css)
        self.assertIn('@config "../../tailwind.config.ts";', css)

    def test_postcss_and_vite_use_tailwind_v4_path(self) -> None:
        postcss = (ROOT / "postcss.config.js").read_text(encoding="utf-8")
        vite = (ROOT / "vite.config.ts").read_text(encoding="utf-8")
        self.assertIn("autoprefixer", postcss)
        self.assertNotIn("tailwindcss: {}", postcss)
        self.assertIn('@tailwindcss/vite', vite)
        self.assertIn('tailwindcss()', vite)

    def test_actions_health_auditor_is_runnable(self) -> None:
        proc = subprocess.run(
            [sys.executable, "tools/audit_actions_health.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        report = json.loads((ROOT / "config/generated/actions-health-report.json").read_text())
        self.assertEqual(report["critical_error_count"], 0)
        self.assertEqual(report["warning_count"], 0)

    def test_optional_runner_skips_missing_lane_without_failure(self) -> None:
        proc = subprocess.run(
            [sys.executable, "tools/run_optional_script.py", "tools/definitely_missing_buddy_lane.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("skipped by policy", proc.stdout)

    def test_first_four_mastery_plan_is_machine_readable(self) -> None:
        path = ROOT / "benchmarks/tasks/first_four_mastery.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            [item["source_id"] for item in data["sources"]],
            ["SRC-001", "SRC-002", "SRC-003", "SRC-004"],
        )
        self.assertTrue(data["parallel"])
        self.assertTrue(data["mastery_gate"]["transfer_test"])
        self.assertTrue(data["mastery_gate"]["regression_test"])


if __name__ == "__main__":
    unittest.main()
