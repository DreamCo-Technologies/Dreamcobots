"""Tests for the dynamic Markdown-to-implementation gap audit."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.audit_markdown_implementation_gaps import analyze_document, candidate_external_paths, candidate_paths, candidate_path_templates, render_report, tracked_markdown

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


    def test_path_templates_and_machine_local_paths_are_not_broken_repo_references(self):
        text = (
            "See `data/evidence/<asset_id>/<run>.json`, "
            "`benchmarks/america_gov/{sandbox.py,test_sandbox.py,catalog.json}`, "
            "and `/home/box/roadmap/_crons.json`."
        )
        templates = candidate_path_templates(text)
        external = candidate_external_paths(text)
        self.assertIn("data/evidence/<asset_id>/<run>.json", templates)
        self.assertIn("benchmarks/america_gov/{sandbox.py,test_sandbox.py,catalog.json}", templates)
        self.assertEqual(external, {"/home/box/roadmap/_crons.json"})
        self.assertEqual(candidate_paths(text), set())
        with tempfile.TemporaryDirectory() as temp:
            row = analyze_document("docs/template.md", text, POLICY, Path(temp))
            self.assertEqual(row["missing_paths"], [])
            self.assertEqual(set(row["path_templates"]), templates)
            self.assertEqual(set(row["external_paths"]), external)


    def test_dot_prefixed_github_workflow_paths_remain_repository_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workflow = root / ".github/workflows/pages.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("name: Pages", encoding="utf-8")
            text = "See `.github/workflows/pages.yml` for the publishing workflow."
            self.assertEqual(candidate_paths(text), {".github/workflows/pages.yml"})
            row = analyze_document("docs/pages.md", text, POLICY, root)
            self.assertEqual(row["referenced_paths"], [".github/workflows/pages.yml"])
            self.assertEqual(row["missing_paths"], [])

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

    def test_tracked_markdown_includes_md_and_mdx_and_respects_exclusions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "config/buddy").mkdir(parents=True)
            (root / "config/buddy/markdown-implementation-gap-policy.json").write_text(
                json.dumps({
                    "excluded_path_segments": ["node_modules"],
                    "excluded_paths": ["docs/excluded.md"],
                }),
                encoding="utf-8",
            )
            for relative in ("README.md", "docs/page.mdx", "docs/excluded.md", "docs/notes.txt", "node_modules/ignored.mdx"):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            found = {path.relative_to(root).as_posix() for path in tracked_markdown(root)}
            self.assertEqual(found, {"README.md", "docs/page.mdx"})

    def test_no_fixed_document_or_reference_ceiling(self):
        self.assertIsNone(POLICY["fixed_document_ceiling"])
        self.assertIsNone(POLICY["fixed_claim_ceiling"])
        self.assertIsNone(POLICY["fixed_reference_ceiling"])

if __name__ == "__main__":
    unittest.main()
