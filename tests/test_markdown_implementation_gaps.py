"""Tests for the dynamic Markdown-to-implementation gap audit."""
import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_markdown_implementation_gaps import analyze_document, candidate_paths

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config/buddy/markdown-implementation-gap-policy.json").read_text(encoding="utf-8"))

class MarkdownImplementationGapTests(unittest.TestCase):
    def test_extracts_inline_and_markdown_link_paths(self):
        text = "See \`tools/run.py\` and [the test](tests/test_run.py)."
        self.assertEqual(candidate_paths(text), {"tools/run.py", "tests/test_run.py"})

    def test_detects_missing_implementation_references(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            row = analyze_document("docs/plan.md", "Buddy must implement this. See \`server/missing.ts\`.", POLICY, root)
            self.assertEqual(row["gap_status"], "broken_path_references")
            self.assertEqual(row["missing_paths"], ["server/missing.ts"])

    def test_distinguishes_code_paths_from_test_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "server").mkdir()
            (root / "tests").mkdir()
            (root / "server/app.ts").write_text("export const app = true")
            (root / "tests/app.test.ts").write_text("test('app', () => {})")
            row = analyze_document("docs/plan.md", "Build \`server/app.ts\` and verify \`tests/app.test.ts\`.", POLICY, root)
            self.assertEqual(row["gap_status"], "implementation_and_test_paths_referenced_not_verified")
            self.assertFalse(row["execution_verified"])

    def test_flags_inventory_counts_for_review(self):
        row = analyze_document("README.md", "We have 1,051 bots across 45 divisions.", POLICY, ROOT)
        self.assertTrue(row["count_claim_review_required"])
        self.assertGreaterEqual(len(row["numeric_inventory_claims"]), 2)

    def test_no_fixed_document_or_reference_ceiling(self):
        self.assertIsNone(POLICY["fixed_document_ceiling"])
        self.assertIsNone(POLICY["fixed_claim_ceiling"])
        self.assertIsNone(POLICY["fixed_reference_ceiling"])

if __name__ == "__main__":
    unittest.main()
