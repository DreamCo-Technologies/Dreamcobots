import json
import tempfile
import unittest
from pathlib import Path

from tools.run_institute_fleet_benchmarks import build_fleet_plan, run_fleet


class CompetitiveFleetOrchestratorTests(unittest.TestCase):
    def test_plan_uses_all_65_canonical_masterbots_without_relabeling_them(self):
        registry = Path("config/masterbot-65-registry.json")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = build_fleet_plan(registry, root / "candidates", root / "fixtures", root / "adapters")
            self.assertEqual(len(plan), 65)
            self.assertEqual(plan[0]["division_id"], "DreamFinance")
            self.assertEqual(len({item["masterbot_id"] for item in plan}), 65)

    def test_missing_artifacts_are_blocked_not_scored_as_zero_or_passed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.json"
            bots = [{"id": i, "name": f"DreamDivision{i}"} for i in range(1, 66)]
            registry.write_text(json.dumps({"canonical_count": 65, "divisions": bots}), encoding="utf-8")
            baseline = root / "baselines.json"
            baseline.write_text(json.dumps({"schema": "dreamco.competitive_baseline_registry.v1", "baselines": []}), encoding="utf-8")
            report = run_fleet(registry, root / "candidates", root / "fixtures", root / "adapters",
                               baseline, root / "report.json", max_candidates=3)
            self.assertEqual(report["candidates_requested"], 3)
            self.assertEqual(report["candidates_evaluated"], 0)
            self.assertEqual(report["candidates_blocked"], 3)
            self.assertEqual(report["fleet_status"], "BLOCKED")
            self.assertTrue(all(item["status"] == "BLOCKED" for item in report["results"]))
            self.assertTrue((root / "report.json").is_file())


if __name__ == "__main__":
    unittest.main()
