import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "trusted-code-delivery-program.json"


class TrustedCodeDeliveryPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.program = json.loads(PROGRAM.read_text(encoding="utf-8"))

    def test_quality_stack_is_deep(self):
        layers = set(self.program["quality_layers"])
        required = {
            "syntax_and_parse_validation", "type_checking", "static_analysis", "unit_tests",
            "integration_tests", "contract_and_schema_tests", "negative_and_error_path_tests",
            "boundary_and_edge_case_tests", "regression_tests", "security_and_secret_handling_tests",
            "dependency_and_supply_chain_review", "privacy_and_permission_tests", "end_to_end_tests",
            "build_and_packaging_tests", "deployment_smoke_tests", "rollback_or_safe_revert_test",
            "observability_and_failure_visibility", "post_release_regression_monitoring"
        }
        self.assertTrue(required.issubset(layers))
        self.assertGreaterEqual(len(layers), 24)

    def test_generated_code_must_ship_with_evidence(self):
        rules = " ".join(self.program["generated_code_rules"]).lower()
        for phrase in [
            "generate tests with code", "do not call generated code verified merely because it compiles",
            "do not silently catch or hide", "do not weaken thresholds", "regression fixture",
            "unverified code must be labeled"
        ]:
            self.assertIn(phrase, rules)

    def test_high_risk_code_gets_stronger_tests(self):
        high = set(self.program["risk_classes"]["high"])
        critical = set(self.program["risk_classes"]["critical"])
        for item in {"authentication", "authorization", "payments", "user data", "database migrations", "security", "external side effects"}:
            self.assertIn(item, high)
        for item in {"secret handling", "financial movement", "destructive production actions", "tenant isolation", "data deletion"}:
            self.assertIn(item, critical)

    def test_release_blockers_include_known_bad_conditions(self):
        blockers = " ".join(self.program["release_blockers"]).lower()
        for phrase in [
            "syntax/type/build failure", "failing required test", "security defect", "secret exposure",
            "data-loss", "failed deployment health check", "missing rollback", "hidden/skipped failure"
        ]:
            self.assertIn(phrase, blockers)

    def test_policy_never_makes_impossible_bug_free_guarantee(self):
        truth = self.program["truth_rule"].lower()
        self.assertIn("no finite test suite can prove", truth)
        self.assertIn("block known-bad", truth)
        self.assertIn("repair regressions quickly", truth)


if __name__ == "__main__":
    unittest.main()
