import json
import unittest

from tools.audit_actions_health import MAX_MAJOR, OUT_JSON, PUBLIC_JSON, main


class ActionsHealthAuditTest(unittest.TestCase):
    def test_current_official_action_baseline_is_recognized(self) -> None:
        self.assertEqual(MAX_MAJOR["actions/checkout"], 7)
        self.assertEqual(MAX_MAJOR["actions/upload-pages-artifact"], 5)

    def test_all_workflows_pass_the_static_health_gate(self) -> None:
        result = main()
        report = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        blockers = [
            f"{item['workflow']}: {error}"
            for item in report["findings"]
            for error in item.get("errors", [])
        ]
        self.assertEqual(result, 0, "Static Actions blockers:\n" + "\n".join(blockers))
        self.assertEqual(report["critical_error_count"], 0)
        self.assertEqual(report["warning_count"], 0)
        self.assertEqual(report["schema"], "dreamco.actions_health.v2")
        self.assertEqual(report["summary"]["static_passing_workflows"], report["workflow_count"])
        self.assertEqual(report["summary"]["runtime_unknown_workflows"], report["workflow_count"])
        self.assertTrue(all(item["what_happens"] for item in report["findings"]))
        self.assertTrue(all(item["goal"] for item in report["findings"]))
        self.assertTrue(all(item["runtime_status"] == "unknown_until_run_evidence_loaded" for item in report["findings"]))
        public_report = json.loads(PUBLIC_JSON.read_text(encoding="utf-8"))
        self.assertEqual(public_report, report)
        self.assertEqual(len(report["findings"]), report["workflow_count"])
        self.assertTrue(all(len(item["upgrades"]) >= 3 for item in report["findings"]))
        self.assertTrue(all(item["github_url"].startswith("https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/") for item in report["findings"]))


    def test_problem_registry_workflow_requires_fresh_evidence_and_least_privilege(self) -> None:
        from tools.audit_actions_health import ROOT
        text = (ROOT / ".github/workflows/problem-registry.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", text)
        self.assertNotIn("contents: write", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("python3 tools/audit_actions_health.py", text)
        self.assertLess(text.index("python3 tools/audit_actions_health.py"),
                        text.index("python3 tools/problem_registry.py"))

    def test_problem_registry_rejects_missing_and_invalid_input_without_erasing_output(self) -> None:
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        from tools import problem_registry
        with TemporaryDirectory() as folder:
            root = Path(folder)
            actions = root / "actions.json"
            output = root / "registry.json"
            public = root / "public.json"
            report = root / "report.md"
            output.write_text('{"existing":"must-preserve"}', encoding="utf-8")
            with (patch.object(problem_registry, "ACTIONS", actions),
                  patch.object(problem_registry, "OUT", output),
                  patch.object(problem_registry, "PUBLIC", public),
                  patch.object(problem_registry, "REPORT", report)):
                for invalid in (None, "{", "{}", '{"schema":"dreamco.actions_health.v2","workflow_count":1,"findings":[]}'):
                    if invalid is None:
                        actions.unlink(missing_ok=True)
                    else:
                        actions.write_text(invalid, encoding="utf-8")
                    self.assertNotEqual(problem_registry.main(), 0)
                    self.assertEqual(json.loads(output.read_text()), {"existing": "must-preserve"})
                    self.assertFalse(public.exists())
                    self.assertFalse(report.exists())

    def test_problem_registry_processes_valid_current_scan(self) -> None:
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        from tools import problem_registry
        with TemporaryDirectory() as folder:
            root = Path(folder)
            actions = root / "actions.json"
            output = root / "registry.json"
            public = root / "public.json"
            report = root / "report.md"
            actions.write_text(json.dumps({
                "schema": "dreamco.actions_health.v2",
                "workflow_count": 1,
                "findings": [{"workflow": ".github/workflows/example.yml",
                              "errors": ["missing jobs section"], "warnings": []}],
            }), encoding="utf-8")
            with (patch.object(problem_registry, "ACTIONS", actions),
                  patch.object(problem_registry, "OUT", output),
                  patch.object(problem_registry, "PUBLIC", public),
                  patch.object(problem_registry, "REPORT", report)):
                self.assertEqual(problem_registry.main(), 0)
                data = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(data["summary"]["high"], 1)
                self.assertEqual(data["summary"]["observed"], 1)
                self.assertEqual(json.loads(public.read_text(encoding="utf-8")), data)
                self.assertTrue(report.exists())



if __name__ == "__main__":
    unittest.main()
