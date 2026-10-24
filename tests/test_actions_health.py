import json
import unittest

from tools.audit_actions_health import MAX_MAJOR, OUT_JSON, PUBLIC_JSON, main


class ActionsHealthAuditTest(unittest.TestCase):
    def test_static_audit_detects_missing_local_unittest_modules(self) -> None:
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from tools.audit_actions_health import missing_unittest_modules

        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "buddy" / "builder").mkdir(parents=True)
            (root / "buddy" / "builder" / "__init__.py").write_text("")
            (root / "tests").mkdir()
            (root / "tests" / "test_valid.py").write_text("")

            # A parent package must not mask an absent test module.
            self.assertEqual(
                missing_unittest_modules(
                    "run: python3 -m unittest buddy.builder.evidence_gate_test", root
                ),
                ["buddy.builder.evidence_gate_test"],
            )
            # Check every explicit target, not only the first one.
            self.assertEqual(
                missing_unittest_modules(
                    "run: python3 -m unittest tests.test_valid tests.test_missing", root
                ),
                ["tests.test_missing"],
            )
            # Class and method selectors resolve through their actual module.
            self.assertEqual(
                missing_unittest_modules(
                    "run: python3 -m unittest tests.test_valid.Case.test_method", root
                ),
                [],
            )
            # Dynamic discovery and external dependencies are not local paths.
            self.assertEqual(
                missing_unittest_modules(
                    "run: python3 -m unittest discover -s tests -p 'test_*.py'", root
                ),
                [],
            )
            self.assertEqual(
                missing_unittest_modules("run: python3 -m unittest external.module", root),
                [],
            )

    def test_conflicted_review_branch_still_receives_actions_health_checks(self) -> None:
        from tools.audit_actions_health import ROOT

        workflow = (ROOT / ".github/workflows/actions-health.yml").read_text(
            encoding="utf-8"
        )
        push_block = workflow.split("  push:", 1)[1].split("  pull_request:", 1)[0]
        self.assertIn("codex/consolidated-dreamco-completion", push_block)
        self.assertIn("tools/audit_actions_health.py", push_block)
        self.assertIn("tests/test_actions_health.py", push_block)
        self.assertIn("  pull_request:", workflow)

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
        self.assertIn("cmp config/generated/problem-registry.json website/data/problem-registry.json", text)
        self.assertLess(text.index("python3 tools/auto_repair_policy.py"), text.index("cmp config/generated/problem-registry.json website/data/problem-registry.json"))
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



    def test_live_audit_fetches_all_workflow_pages(self) -> None:
        from unittest.mock import patch
        from tools import audit_actions_live

        first = [{"id": i} for i in range(1, 101)]
        second = [{"id": i} for i in range(101, 114)]

        def fake_api(path):
            return {"total_count": 113, "workflows": second if "page=2" in path else first}

        with patch.object(audit_actions_live, "api", side_effect=fake_api) as mocked:
            rows = audit_actions_live.fetch_workflow_inventory("org/repo")
        self.assertEqual(len(rows), 113)
        self.assertEqual(mocked.call_count, 2)

    def test_live_audit_rejects_truncated_or_duplicate_pages(self) -> None:
        from unittest.mock import patch
        from tools import audit_actions_live

        first = [{"id": i} for i in range(1, 101)]
        cases = [
            [{"total_count": 113, "workflows": first},
             {"total_count": 113, "workflows": []}],
            [{"total_count": 101, "workflows": first},
             {"total_count": 101, "workflows": [{"id": 100}]}],
        ]
        for pages in cases:
            with self.subTest(last_page=pages[-1]), patch.object(
                audit_actions_live, "api", side_effect=pages
            ):
                with self.assertRaises(RuntimeError):
                    audit_actions_live.fetch_workflow_inventory("org/repo")

    def test_live_audit_rejects_unbounded_or_malformed_inventory(self) -> None:
        from unittest.mock import patch
        from tools import audit_actions_live

        with patch.object(audit_actions_live, "api", return_value={
            "workflows": [{"id": 1}]
        }):
            with self.assertRaises(RuntimeError):
                audit_actions_live.fetch_workflow_inventory("org/repo")
        with patch.object(audit_actions_live, "api", return_value={
            "total_count": 2, "workflows": [{"id": 1}]
        }) as mocked:
            with self.assertRaises(RuntimeError):
                audit_actions_live.fetch_workflow_inventory("org/repo", page_limit=1)
            self.assertEqual(mocked.call_count, 1)




    def test_live_sample_full_recent_page_is_not_30_day_proof(self) -> None:
        from datetime import datetime, timedelta, timezone
        from tools.audit_actions_live import recent_run_sample

        cutoff = datetime(2026, 9, 24, tzinfo=timezone.utc)
        runs = [
            {"created_at": (cutoff + timedelta(days=1, seconds=10 - i)).isoformat(),
             "conclusion": "success"}
            for i in range(10)
        ]
        recent, complete = recent_run_sample(runs, cutoff)
        self.assertEqual(len(recent), 10)
        self.assertFalse(complete, "Ten recent runs cannot prove the whole 30-day window")

    def test_live_sample_coverage_complete_when_history_ends_or_crosses_cutoff(self) -> None:
        from datetime import datetime, timedelta, timezone
        from tools.audit_actions_live import recent_run_sample

        cutoff = datetime(2026, 9, 24, tzinfo=timezone.utc)
        newest = {"created_at": (cutoff + timedelta(days=1)).isoformat(), "conclusion": "failure"}
        old = {"created_at": (cutoff - timedelta(days=1)).isoformat(), "conclusion": "failure"}
        recent, complete = recent_run_sample([newest, old], cutoff)
        self.assertEqual(recent, [newest])
        self.assertTrue(complete)
        recent, complete = recent_run_sample([newest] * 9 + [old], cutoff)
        self.assertEqual(len(recent), 9)
        self.assertTrue(complete)
        self.assertEqual(recent_run_sample([], cutoff), ([], True))

    def test_live_sample_rejects_malformed_unordered_or_oversized_evidence(self) -> None:
        from datetime import datetime, timedelta, timezone
        from tools.audit_actions_live import recent_run_sample

        cutoff = datetime(2026, 9, 24, tzinfo=timezone.utc)
        new = {"created_at": (cutoff + timedelta(days=2)).isoformat()}
        old = {"created_at": (cutoff + timedelta(days=1)).isoformat()}
        cases = [
            None, {}, [None], [{}], [{"created_at": "bad-date"}],
            [{"created_at": "2026-10-01T00:00:00"}],
            [old, new], [new] * 11,
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(RuntimeError):
                recent_run_sample(case, cutoff)


if __name__ == "__main__":
    unittest.main()
