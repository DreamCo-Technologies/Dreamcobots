from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BuddyMasteryLedgerTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_mastery_requires_evidence_and_revalidation(self):
        text = self.read("buddy_os/benchmarks/mastery_ledger.yaml")
        for item in (
            "requires_repeated_acceptance: true",
            "requires_evidence: true",
            "single_pass_is_not_mastery: true",
            "stale_mastery_must_be_revalidated: true",
            "regression_reopens_investigation: true",
        ):
            self.assertIn(item, text)

    def test_repository_baseline_matches_current_evidence(self):
        text = self.read("buddy_os/benchmarks/mastery_ledger.yaml")
        self.assertIn("live_benchmark_programs_with_live_evidence: 0", text)
        self.assertIn("tracked_benchmark_surfaces: 40", text)
        self.assertIn("bots_certified: 1051", text)
        self.assertIn("capability_contracts_certified: 8408", text)

    def test_gap_planner_requires_machine_actionable_output(self):
        text = self.read("buddy_os/benchmarks/mastery_gap_planner.yaml")
        for item in (
            "read_mastery_ledger",
            "identify_missing_evidence",
            "rank_by_expected_improvement_per_cost",
            "generate_action",
            "execute_in_sandbox",
            "update_ledger",
        ):
            self.assertIn(item, text)
        self.assertIn("never_close_gap_without_evidence: true", text)

    def test_dashboard_distinguishes_verification_levels(self):
        text = self.read("buddy_os/benchmarks/mastery_dashboard_contract.yaml")
        for label in (
            "repository_verified",
            "sandbox_verified",
            "live_provider_verified",
            "production_verified",
            "not_verified",
        ):
            self.assertIn(label, text)


if __name__ == "__main__":
    unittest.main()
