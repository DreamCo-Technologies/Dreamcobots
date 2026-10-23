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

    def test_missing_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(AuditError, "production-evidence-ledger"):
                audit(Path(tmp))


if __name__ == "__main__":
    unittest.main()
