"""Synthetic fixtures only: tests do not assert model capability or training."""
import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_buddy_teacher_coverage import AuditError, SOURCES, audit


def fixture(root: Path):
    inputs = {
        "production": {"summary": {"real_divisions": 2, "production_ready_divisions": 0},
                       "divisions": [{"name": "DreamCodeLab", "production_ready": False},
                                     {"name": "DreamData", "production_ready": False}]},
        "masterbots": {"canonical_count": 2, "divisions": [{"name": "DreamCodeLab"}, {"name": "AnotherTaxonomy"}]},
        "tasks": {"tasks": ["coding", "sql"], "runs": 0},
        "suites": {"suites": [{"id": "coding_suite"}, {"id": "sql_suite"}]},
        "models": {"models": [{"id": "docs-only", "task_types": ["coding"]}]},
        "students": {"adapters": [], "truth": {"trained_weights_exist": False}},
        "distill": {"status": "contract_draft_no_runs"},
    }
    for key, path in SOURCES.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(inputs[key]), encoding="utf-8")


class TeacherCoverageTests(unittest.TestCase):
    def test_truthful_inventory_and_declared_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            report = audit(root)
            self.assertEqual(report["summary"]["actual_divisions"], 2)
            self.assertEqual(report["summary"]["masterbot_only_names"], ["AnotherTaxonomy"])
            self.assertEqual(report["summary"]["independent_holdout_receipts_in_this_audit"], 0)
            self.assertEqual(report["summary"]["representative_fixture_suggestions"], 2)
            self.assertEqual(report["task_routes"][0]["declared_candidate_model_ids"], ["docs-only"])
            self.assertEqual(report["task_routes"][0]["independently_verified_model_ids"], [])
            self.assertTrue(all(x["independent_holdout_receipt"] is None for x in report["division_coverage"]))

    def test_duplicate_division_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["divisions"].append(data["divisions"][0])
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "duplicate name"):
                audit(root)

    def test_summary_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"]["real_divisions"] = 3
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "count disagrees"):
                audit(root)

    def test_alias_proposals_do_not_count_as_verified_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["models"]
            data = json.loads(p.read_text())
            data["models"] = [{"id": "code-only", "task_types": ["code"]}]
            p.write_text(json.dumps(data))
            report = audit(root)
            coding = next(row for row in report["task_routes"] if row["task"] == "coding")
            self.assertEqual(coding["declared_candidate_model_ids"], [])
            self.assertEqual(coding["suggested_alias_model_ids_unverified"], ["code-only"])
            self.assertEqual(coding["independently_verified_model_ids"], [])
            self.assertIn("coding", report["summary"]["benchmark_tasks_without_exact_catalog_type"])
            self.assertIn("code", report["summary"]["catalog_model_task_types_not_in_benchmark_registry"])

    def test_missing_dedicated_suite_is_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["suites"]
            p.write_text(json.dumps({"suites": [{"id": "code_generation"}]}))
            report = audit(root)
            coding = next(row for row in report["task_routes"] if row["task"] == "coding")
            sql = next(row for row in report["task_routes"] if row["task"] == "sql")
            self.assertEqual(coding["candidate_suite_ids_design_only"], ["code_generation"])
            self.assertFalse(coding["needs_dedicated_suite_design"])
            self.assertTrue(sql["needs_dedicated_suite_design"])
            self.assertIn("sql", report["summary"]["benchmark_tasks_without_candidate_suite_design"])

    def test_inconsistent_weight_claim_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["students"]
            p.write_text(json.dumps({"adapters": [], "truth": {"trained_weights_exist": True}}))
            with self.assertRaisesRegex(AuditError, "without any registered student adapter"):
                audit(root)

    def test_invalid_benchmark_run_count_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["tasks"]
            p.write_text(json.dumps({"tasks": ["coding"], "runs": -1}))
            with self.assertRaisesRegex(AuditError, "nonnegative integer"):
                audit(root)

    def test_missing_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(AuditError, "production-evidence-ledger"):
                audit(Path(tmp))


    def test_string_readiness_is_not_truth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["divisions"][0]["production_ready"] = "false"
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "production_ready must be a boolean"):
                audit(root)

    def test_boolean_benchmark_run_count_is_not_an_integer_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["tasks"]
            data = json.loads(p.read_text())
            data["runs"] = True
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "nonnegative integer"):
                audit(root)

    def test_ledger_zero_weight_artifacts_rejects_distill_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"]["trained_weight_artifacts"] = 0
            p.write_text(json.dumps(data))
            p = root / SOURCES["distill"]
            p.write_text(json.dumps({
                "status": "research_only",
                "truth": {"trained_weights_exist": True, "distill_runs_exist": False},
            }))
            with self.assertRaisesRegex(AuditError, "reports zero artifacts"):
                audit(root)

    def test_division_subtotal_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["production"]
            data = json.loads(p.read_text())
            data["summary"].update({"canonical_divisions": 2, "supplemental_divisions": 1})
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AuditError, "subtotals disagree"):
                audit(root)

    def test_non_boolean_distill_claim_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            p = root / SOURCES["distill"]
            p.write_text(json.dumps({
                "status": "contract_draft_no_runs",
                "truth": {"distill_runs_exist": "false"},
            }))
            with self.assertRaisesRegex(AuditError, "distill_runs_exist must be a boolean"):
                audit(root)


if __name__ == "__main__":
    unittest.main()
