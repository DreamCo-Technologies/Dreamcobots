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


if __name__ == "__main__":
    unittest.main()
