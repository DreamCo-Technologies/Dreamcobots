from __future__ import annotations

import json
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

    def test_postcss_does_not_load_tailwind_as_a_legacy_plugin(self) -> None:
        postcss = (ROOT / "postcss.config.js").read_text(encoding="utf-8")
        self.assertIn("autoprefixer", postcss)
        self.assertNotIn("tailwindcss: {}", postcss)

    def test_vite_uses_official_tailwind_plugin(self) -> None:
        vite = (ROOT / "vite.config.ts").read_text(encoding="utf-8")
        self.assertIn('@tailwindcss/vite', vite)
        self.assertIn('tailwindcss()', vite)

    def test_first_four_mastery_plan_is_machine_readable(self) -> None:
        path = ROOT / "benchmarks/tasks/first_four_mastery.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual([item["source_id"] for item in data["sources"]], ["SRC-001", "SRC-002", "SRC-003", "SRC-004"])
        self.assertTrue(data["parallel"])
        self.assertTrue(data["mastery_gate"]["transfer_test"])
        self.assertTrue(data["mastery_gate"]["regression_test"])


if __name__ == "__main__":
    unittest.main()
