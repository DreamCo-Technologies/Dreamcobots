import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class RunEverythingNowTests(unittest.TestCase):
    def test_writes_inflight_status_before_dependent_step(self) -> None:
        module = importlib.import_module("tools.run_everything_now")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "config").mkdir()
            (root / "config" / "run-everything-now.json").write_text(
                json.dumps({"truth_rule": "test truth rule"}) + "\n",
                encoding="utf-8",
            )
            (root / "tools").mkdir()
            (root / "tools" / "noop.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "tools" / "assert_snapshot.py").write_text(
                "import json\n"
                "from pathlib import Path\n"
                "status = json.loads(Path('config/generated/run-everything-now-latest.json').read_text())\n"
                "assert status['in_progress'] is True\n"
                "assert status['failed'] == 0\n"
                "assert status['completed_steps'] == 1\n"
                "assert status['pending_steps'] == 1\n"
                "assert status['results'][0]['name'] == 'first'\n"
                "print('snapshot ok')\n",
                encoding="utf-8",
            )
            steps = [
                ("first", [sys.executable, "tools/noop.py"]),
                ("second", [sys.executable, "tools/assert_snapshot.py"]),
            ]
            original = {
                "ROOT": module.ROOT,
                "CFG": module.CFG,
                "OUT": module.OUT,
                "REPORT": module.REPORT,
                "MAX_STEPS": module.MAX_STEPS,
            }
            try:
                module.ROOT = root
                module.CFG = {"truth_rule": "test truth rule"}
                module.OUT = root / "config" / "generated" / "run-everything-now-latest.json"
                module.REPORT = root / "reports" / "RUN_EVERYTHING_NOW.md"
                module.MAX_STEPS = steps
                with patch.object(sys, "argv", ["run_everything_now.py", "--mode", "maximum"]):
                    self.assertEqual(module.main(), 0)
                final = json.loads(module.OUT.read_text(encoding="utf-8"))
                self.assertFalse(final["in_progress"])
                self.assertEqual(final["completed_steps"], 2)
                self.assertEqual(final["pending_steps"], 0)
                self.assertEqual(final["failed"], 0)
                self.assertEqual(final["passed"], 2)
            finally:
                module.ROOT = original["ROOT"]
                module.CFG = original["CFG"]
                module.OUT = original["OUT"]
                module.REPORT = original["REPORT"]
                module.MAX_STEPS = original["MAX_STEPS"]


    def test_standard_mode_is_smaller_than_maximum(self) -> None:
        module = importlib.import_module("tools.run_everything_now")
        steps = [(f"step-{index}", [sys.executable, "-c", "pass"]) for index in range(42)]
        self.assertEqual(len(module.select_steps("quick", steps)), 26)
        self.assertEqual(len(module.select_steps("standard", steps)), 36)
        self.assertEqual(len(module.select_steps("maximum", steps)), 42)

    def test_known_release_gate_block_is_recorded_as_blocked_only_with_explicit_flag(self) -> None:
        module = importlib.import_module("tools.run_everything_now")
        result = module.classify_result(
            "full_certification",
            [sys.executable, "tools/build_full_system_certification.py"],
            1,
            json.dumps({"status": "blocked", "release_blockers": ["missing verification evidence"]}),
            "",
            allow_blocked=True,
        )
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["exit_code"], 1)
        self.assertEqual(result["blockers"], ["missing verification evidence"])

    def test_blocked_gate_remains_failure_without_explicit_flag(self) -> None:
        module = importlib.import_module("tools.run_everything_now")
        result = module.classify_result("full_certification", ["python"], 1, '{"status":"blocked"}', "")
        self.assertEqual(result["status"], "failed")

    def test_unrelated_failure_is_never_reclassified_as_blocked(self) -> None:
        module = importlib.import_module("tools.run_everything_now")
        result = module.classify_result("production_smoke", ["python"], 1, '{"status":"blocked"}', "", allow_blocked=True)
        self.assertEqual(result["status"], "failed")

    def test_snapshot_counts_blocked_separately_from_failed(self) -> None:
        module = importlib.import_module("tools.run_everything_now")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            original = {"OUT": module.OUT, "REPORT": module.REPORT, "CFG": module.CFG}
            try:
                module.OUT = root / "config" / "generated" / "run-everything-now-latest.json"
                module.REPORT = root / "reports" / "RUN_EVERYTHING_NOW.md"
                module.CFG = {"truth_rule": "blocked evidence is not a pass"}
                results = [
                    module.classify_result("full_certification", ["python"], 1, '{"status":"blocked","blockers":["missing evidence"]}', "", True),
                    module.classify_result("unified_bot_system", ["python"], 0, "ok", "", True),
                ]
                payload = module.write_snapshot("maximum", 2, results, False, True)
                self.assertEqual(payload["passed"], 1)
                self.assertEqual(payload["blocked"], 1)
                self.assertEqual(payload["failed"], 0)
                self.assertEqual(payload["execution_status"], "completed_with_blockers")
                report = module.REPORT.read_text(encoding="utf-8")
                self.assertIn("## Blocked release gates", report)
                self.assertIn("BLOCKED", report)
            finally:
                module.OUT = original["OUT"]
                module.REPORT = original["REPORT"]
                module.CFG = original["CFG"]

    def test_500_model_workflow_scopes_core_pytest_and_records_blocked_suites(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = (root / ".github" / "workflows" / "dreamco-unified-system.yml").read_text(encoding="utf-8")
        self.assertIn("python3 -m pytest -q tests --disable-warnings --maxfail=20", source)
        self.assertIn("career-pathways-test-status.json", source)
        self.assertIn("--allow-blocked", source)
        self.assertIn("tools/run_500_model_benchmarks.py", source)
        self.assertIn("no model inference", source.lower())

if __name__ == "__main__":
    unittest.main()
