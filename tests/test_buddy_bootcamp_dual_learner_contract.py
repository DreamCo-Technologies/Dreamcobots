from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BuddyBootcampDualLearnerContractTests(unittest.TestCase):
    def test_bootcamp_supports_humans_and_ai_models_with_separate_evidence(self):
        registry = json.loads((ROOT / "config/buddy-course-track-registry.json").read_text(encoding="utf-8"))
        contract = registry["learner_contract"]

        self.assertEqual(contract["schema"], "dreamco.buddy_bootcamp_dual_learner.v1")
        self.assertEqual(set(contract["audiences"]), {"humans", "ai_models"})
        self.assertTrue(contract["shared_curriculum"])
        self.assertTrue(contract["separate_progress_records"])
        self.assertIn("assessment_result", contract["human"]["evidence_required"])
        self.assertIn("checkpoint_hash_when_weights_change", contract["ai_models"]["evidence_required"])
        self.assertIn("benchmark_and_holdout_results", contract["ai_models"]["evidence_required"])
        self.assertIn("prompts_and_retrieval_updates_are_not_weight_updates", contract["ai_models"]["guardrails"])
        self.assertIn("human_course_completion_is_not_model_training", contract["ai_models"]["guardrails"])

    def test_existing_tracks_remain_available_to_both_learner_types(self):
        registry = json.loads((ROOT / "config/buddy-course-track-registry.json").read_text(encoding="utf-8"))
        self.assertIn("tokenizer", {track["id"] for track in registry["tracks"]})
        self.assertTrue(all(track.get("delivery") for track in registry["tracks"]))


if __name__ == "__main__":
    unittest.main()
