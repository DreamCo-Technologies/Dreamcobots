from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.innovation import InnovationEngine, InnovationRequest, InnovationWeights


class BuddyInnovationEngineTests(unittest.TestCase):
    def test_generates_and_ranks_six_distinct_designs(self):
        result = InnovationEngine().run(
            InnovationRequest(
                objective="Build a replayable science simulation with clear learning evidence.",
                audience="middle school students",
                tags=("education", "simulation"),
            )
        )
        self.assertEqual(len(result.candidates), 6)
        self.assertEqual(len({item.candidate_id for item in result.candidates}), 6)
        self.assertGreaterEqual(result.candidates[0].weighted_score, result.candidates[-1].weighted_score)
        self.assertEqual(result.winner.candidate_id, result.candidates[0].candidate_id)

    def test_run_records_durable_checkpoints_and_rollback_digest(self):
        result = InnovationEngine().run(
            InnovationRequest(
                objective="Create a local-first family learning experience with captions.",
                audience="parents and children",
                mode="trusted",
                tags=("education", "privacy", "accessibility"),
            )
        )
        self.assertEqual(result.execution["status"], "succeeded")
        self.assertEqual(len(result.execution["checkpoints"]), 3)
        self.assertTrue(result.rollback_checkpoint["digest"].startswith("sha256:"))

    def test_mode_weights_are_normalized(self):
        for mode in ("balanced", "bold", "trusted", "lean"):
            self.assertAlmostEqual(sum(InnovationWeights.for_mode(mode).normalized().values()), 1.0)

    def test_design_scores_are_not_treated_as_production_evidence(self):
        result = InnovationEngine().run(
            InnovationRequest(
                objective="Build a useful client task manager with reversible automation.",
                audience="small business owners",
            )
        )
        self.assertTrue(result.release_gate["design_score_is_not_production_evidence"])
        self.assertEqual(result.release_gate["status"], "observed_evidence_required")

    def test_release_stays_blocked_until_every_observed_check_passes(self):
        engine = InnovationEngine()
        blocked = engine.evaluate_release({"functional_tests": True})
        self.assertEqual(blocked.status, "blocked")
        self.assertIn("human_acceptance", blocked.missing_checks)
        passed = engine.evaluate_release({name: True for name in engine.REQUIRED_OBSERVED_CHECKS})
        self.assertEqual(passed.status, "production_candidate_owner_approval_required")
        self.assertEqual(passed.missing_checks, [])

    def test_invalid_or_unknown_mode_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown innovation mode"):
            InnovationEngine().run(
                InnovationRequest(
                    objective="Build a complete reversible workflow for a client.",
                    audience="client",
                    mode="unbounded",
                )
            )

    def test_constraints_change_ranking_instead_of_being_metadata_only(self):
        result = InnovationEngine().run(
            InnovationRequest(
                objective="Build a resilient task system with a strict device budget.",
                audience="people using personal laptops",
                mode="lean",
                constraints=("local_first", "strict_cost_ceiling"),
            )
        )
        self.assertEqual(result.winner.lens, "local_first_mesh")

    def test_rollback_snapshot_does_not_mutate_with_winner(self):
        result = InnovationEngine().run(
            InnovationRequest(
                objective="Build a reversible client workflow with transparent decisions.",
                audience="small business teams",
            )
        )
        snapshot_architecture = list(result.rollback_checkpoint["snapshot"]["architecture"])
        result.winner.architecture.append("unverified change")
        self.assertEqual(result.rollback_checkpoint["snapshot"]["architecture"], snapshot_architecture)


if __name__ == "__main__":
    unittest.main()
