import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "change-impact-test-policy.json"
EXEMPTIONS = ROOT / "config" / "change-impact-test-exemptions.json"


class ChangeImpactTestPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads(POLICY.read_text(encoding="utf-8"))
        cls.exemptions = json.loads(EXEMPTIONS.read_text(encoding="utf-8"))

    def test_executable_extensions_cover_repo_languages(self):
        extensions = set(self.policy["executable_extensions"])
        for ext in {".py", ".ts", ".tsx", ".js", ".mjs", ".cjs"}:
            self.assertIn(ext, extensions)

    def test_high_risk_paths_cover_money_auth_security_and_data(self):
        words = set(self.policy["high_risk_path_keywords"])
        for word in {"stripe", "payment", "billing", "auth", "security", "secret", "privacy", "webhook", "migration", "database", "deploy", "permission", "tenant", "delete"}:
            self.assertIn(word, words)
        aliases = self.policy["high_risk_test_aliases"]
        self.assertIn("stripe", aliases)
        self.assertIn("auth", aliases)
        self.assertIn("database", aliases)

    def test_changed_executable_code_requires_relevant_evidence(self):
        blockers = " ".join(self.policy["release_blockers"]).lower()
        self.assertIn("no relevant verification evidence", blockers)
        self.assertIn("domain-relevant stronger evidence", blockers)
        self.assertIn("shared-core change lacks dependent-system regression evidence", blockers)

    def test_focused_mappings_reference_owned_sources_and_changed_test_paths(self):
        mappings = self.policy["focused_test_mappings"]
        self.assertGreaterEqual(len(mappings), 2)
        sources = []
        for mapping in mappings:
            self.assertTrue(mapping["sources"])
            self.assertTrue(mapping["tests"])
            self.assertTrue(all(test.startswith("tests/") for test in mapping["tests"]))
            sources.extend(mapping["sources"])
        self.assertEqual(len(sources), len(set(sources)))
        self.assertIn("client/src/components/ui/calendar.tsx", sources)
        self.assertIn("website/nav.js", sources)

    def test_focused_mappings_cover_non_matching_source_and_test_names(self):
        by_source = {
            source: set(mapping["tests"])
            for mapping in self.policy["focused_test_mappings"]
            for source in mapping["sources"]
        }
        self.assertIn("tests/test_decision_planning.py", by_source["buddy_os/intelligence/planner_arbitration.py"])
        self.assertIn("tests/test_decision_planning.py", by_source["buddy_os/intelligence/prediction_error.py"])
        self.assertIn("tests/buddy-expert-mode-page.test.mjs", by_source["server/routes.ts"])
        self.assertIn("tests/oauth-login-policy.test.mjs", by_source["website/sign-in.js"])
        self.assertIn("tests/test_repository_browser.py", by_source["tools/generate_command_center_data.py"])
        self.assertIn("tests/command-center-page.test.mjs", by_source["website/buddy-command-center.js"])
        for source in ("website/nav.js", "website/desk-chrome.js"):
            self.assertIn("tests/shared-repository-controls.test.mjs", by_source[source])

    def test_silent_test_bypasses_are_explicit_blockers(self):
        blockers = " ".join(self.policy["release_blockers"]).lower()
        self.assertIn("test file deleted", blockers)
        self.assertIn("test skip marker", blockers)
        anti = " ".join(self.policy["evidence_rules"]["anti_bypass"]).lower()
        self.assertIn("deleted", anti)
        self.assertIn("skip", anti)
        self.assertIn("unrelated", anti)
        self.assertGreaterEqual(len(self.policy["skip_markers"]), 6)

    def test_exemptions_are_explicit_and_temporary(self):
        required = set(self.policy["exemptions"]["required_fields"])
        self.assertEqual(required, {"path", "reason", "owner", "expires"})
        self.assertIn("temporary", self.policy["exemptions"]["rule"].lower())
        self.assertIn("cannot be used for critical", self.policy["exemptions"]["rule"].lower())
        self.assertIsInstance(self.exemptions["exemptions"], list)

    def test_policy_does_not_claim_bug_free_proof(self):
        self.assertIn("cannot prove absence of every defect", self.policy["truth_rule"].lower())

    def test_protected_html_changes_are_audited_and_require_changed_tests(self):
        import importlib.util
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        self.assertIn("website/divisions.html", self.policy["protected_source_paths"])
        self.assertIn("website/bots.html", self.policy["protected_source_paths"])
        module_path = ROOT / "tools" / "audit_change_test_coverage.py"
        spec = importlib.util.spec_from_file_location("dreamco_change_impact_auditor", module_path)
        auditor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auditor)
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "change-impact.json"
            argv = ["audit_change_test_coverage.py", "--base", "before", "--head", "after"]
            with patch.object(auditor, "OUT", out), patch("sys.argv", argv), patch.object(auditor, "added_skip_markers", return_value=[]):
                for page in ("website/divisions.html", "website/bots.html"):
                    with self.subTest(page=page):
                        with patch.object(auditor, "changed_name_status", return_value=[("M", page)]):
                            self.assertEqual(auditor.main(), 1)
                            report = json.loads(out.read_text())
                            self.assertEqual(report["changed_executable_file_count"], 1)
                            self.assertFalse(report["ok"])
                            self.assertIn(page, report["release_blockers"][0])
                        with patch.object(auditor, "changed_name_status", return_value=[
                            ("M", page),
                            ("M", "tests/specialist-prospectus-page.test.mjs"),
                        ]):
                            self.assertEqual(auditor.main(), 0)
                            report = json.loads(out.read_text())
                            self.assertTrue(report["ok"])
                            self.assertEqual(report["files"][0]["focused_tests"], ["tests/specialist-prospectus-page.test.mjs"])


if __name__ == "__main__":
    unittest.main()
