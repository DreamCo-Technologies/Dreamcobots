"""Tests for the dynamic Markdown-to-implementation gap audit."""
import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_markdown_implementation_gaps import analyze_document, candidate_paths, render_report

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config/buddy/markdown-implementation-gap-policy.json").read_text(encoding="utf-8"))

class MarkdownImplementationGapTests(unittest.TestCase):
    def test_extracts_inline_and_markdown_link_paths(self):
        tick = chr(96)
        text = "See " + tick + "tools/run.py" + tick + " and [the test](tests/test_run.py)."
        self.assertEqual(candidate_paths(text), {"tools/run.py", "tests/test_run.py"})

    def test_ignores_empty_inline_code_and_empty_link_targets(self):
        tick = chr(96)
        self.assertEqual(candidate_paths("Empty " + tick + tick + " and [blank]()."), set())

    def test_detects_missing_implementation_references(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            tick = chr(96)
            row = analyze_document("docs/plan.md", "Buddy must implement this. See " + tick + "server/missing.ts" + tick + ".", POLICY, root)
            self.assertEqual(row["gap_status"], "broken_path_references")
            self.assertEqual(row["missing_paths"], ["server/missing.ts"])

    def test_distinguishes_code_paths_from_test_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "server").mkdir()
            (root / "tests").mkdir()
            (root / "server/app.ts").write_text("export const app = true")
            (root / "tests/app.test.ts").write_text("test('app', () => {})")
            tick = chr(96)
            text = "Build " + tick + "server/app.ts" + tick + " and verify " + tick + "tests/app.test.ts" + tick + "."
            row = analyze_document("docs/plan.md", text, POLICY, root)
            self.assertEqual(row["gap_status"], "implementation_and_test_paths_referenced_not_verified")
            self.assertFalse(row["execution_verified"])

    def test_flags_inventory_counts_for_review(self):
        row = analyze_document("README.md", "We have 1,051 bots across 45 divisions.", POLICY, ROOT)
        self.assertTrue(row["count_claim_review_required"])
        self.assertGreaterEqual(len(row["numeric_inventory_claims"]), 2)

    def test_generated_report_strips_trailing_whitespace(self):
        data = {
            "generated_at": "2026-11-24T00:00:00Z",
            "document_count": 1,
            "actionable_claim_lines": 1,
            "documents_with_missing_paths": 0,
            "documents_without_implementation_references": 1,
            "documents_without_test_references": 0,
            "documents_with_count_claims": 1,
            "numeric_inventory_claim_count": 1,
            "documents": [{
                "numeric_inventory_claims": [{"line": 1, "excerpt": "copied excerpt  "}],
                "path": "docs/example.md",
                "gap_status": "reference_only",
                "actionable_claim_lines": 1,
                "implementation_paths": [],
                "test_paths": [],
                "missing_paths": [],
                "next_action": "Review evidence."
            }],
            "truth_boundary": "Reference mapping only."
        }
        report = render_report(data)
        self.assertTrue(report.endswith("\n"))
        self.assertTrue(all(line == line.rstrip() for line in report.splitlines()))
        self.assertIn("- docs/example.md:1 — copied excerpt", report)

    def test_no_fixed_document_or_reference_ceiling(self):
        self.assertIsNone(POLICY["fixed_document_ceiling"])
        self.assertIsNone(POLICY["fixed_claim_ceiling"])
        self.assertIsNone(POLICY["fixed_reference_ceiling"])

if __name__ == "__main__":
    unittest.main()
