import unittest

from tools.run_buddy_study_evidence_session import (
    LESSON_PRIORITY,
    check_compatibility,
    extract_glossary,
    RECALL_ITEMS,
    parse_division_profiles,
    score_active_recall,
    select_priority_lessons,
    validate_division_packet,
    validate_role_markers,
    worked_bpe_pair_example,
)


class BuddyStudyEvidenceSessionTests(unittest.TestCase):
    def test_canonical_profile_parser_extracts_mission_and_focus_areas(self):
        source = '''
export const Profiles = {
  DreamAlpha: {
    purpose: "Coordinate safe workflows.",
    serves: ["operators"],
    outcome: "Reviewable work.",
    boundary: "No unapproved writes.",
    focusAreas: ["approvals", "observability"],
  },
  DreamBeta: {
    purpose: "Build reliable data systems.",
    serves: ["engineers"],
    outcome: "Validated datasets.",
    boundary: "No unknown-rights data.",
    focusAreas: ["data quality", "lineage"],
  },
};
'''
        profiles = parse_division_profiles(source, ["DreamAlpha", "DreamBeta"])
        self.assertEqual(profiles["DreamAlpha"]["purpose"], "Coordinate safe workflows.")
        self.assertEqual(profiles["DreamBeta"]["focusAreas"], ["data quality", "lineage"])

    def test_scheduler_selects_runnable_lessons_in_risk_first_order(self):
        curriculum = {
            "lessons": [
                {"id": lesson_id, "title": lesson_id, "outcome": "objective", "lab": "lab", "assessment": "test"}
                for lesson_id, _, _ in LESSON_PRIORITY
            ]
        }
        selected = select_priority_lessons(curriculum, 5)
        self.assertEqual(
            [row["lesson_id"] for row in selected],
            ["tok-06", "tok-01", "tok-04", "tok-11", "tok-12"],
        )
        self.assertEqual([row["priority_rank"] for row in selected], [1, 2, 3, 4, 5])

    def test_active_recall_is_blocked_without_learner_responses(self):
        result = score_active_recall()
        self.assertEqual(result["status"], "blocked_no_learner_responses")
        self.assertIsNone(result["score"])
        self.assertEqual(result["items_passed"], 0)
        self.assertTrue(all(item["learner_response"] is None for item in result["items"]))
        self.assertFalse(result["independent_model_inference"])

    def test_active_recall_scores_only_supplied_learner_responses(self):
        responses = [item["reference_answer"] for item in RECALL_ITEMS]
        result = score_active_recall(responses, "unit-test-learner")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["score"], 100.0)
        self.assertEqual(result["learner_id"], "unit-test-learner")
        self.assertEqual(result["response_mode"], "supplied_learner_response")
        self.assertFalse(result["independent_model_inference"])

    def test_active_recall_requires_nonempty_responses_and_learner_id(self):
        with self.assertRaisesRegex(ValueError, "exactly"):
            score_active_recall([], "unit-test-learner")
        with self.assertRaisesRegex(ValueError, "learner_id"):
            score_active_recall(["answer"] * len(RECALL_ITEMS), None)

    def test_active_recall_failed_answers_require_remediation(self):
        result = score_active_recall(["I do not know this yet."] * len(RECALL_ITEMS), "unit-test-learner")
        self.assertEqual(result["status"], "needs_remediation")
        self.assertEqual(result["score"], 0.0)

    def test_glossary_extracts_definitions_from_approved_sources_only(self):
        glossary = extract_glossary({
            "docs/internal-guide.md": (
                "- **Tokenizer:** A component that converts text into tokens.\n"
                "- **UTF-8:** Encodes Unicode text as bytes.\n"
                "- **Normalization:** A documented text transformation.\n"
                "BPE is mentioned here but has no authored definition.\n"
            ),
            "data/buddy-authorized-corpora/synthetic-ci-corpus.txt": (
                "A tokenizer uses UTF-8 and normalization.\n"
            ),
            "external/notes.md": "- **Unapproved:** This source must be ignored.\n",
        })
        by_term = {row["term"]: row for row in glossary}
        self.assertEqual(set(by_term), {"Tokenizer", "UTF-8", "Normalization"})
        self.assertEqual(by_term["Tokenizer"]["definition"], "A component that converts text into tokens.")
        self.assertEqual(by_term["Tokenizer"]["source_refs"], [{"path": "docs/internal-guide.md", "line": 1}])
        self.assertNotIn("BPE", by_term)
        self.assertNotIn("Unapproved", by_term)
        self.assertEqual(by_term["UTF-8"]["extraction_method"], "markdown_bold_definition_line")

    def test_role_marker_contract_accepts_supported_roles(self):
        self.assertTrue(validate_role_markers(
            "<|system|>s<|user|>u<|assistant|>a<|tool|>t"
        ))

    def test_role_marker_contract_rejects_unknown_roles(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            validate_role_markers(
                "<|system|>s<|user|>u<|assistant|>a<|tool|>t<|root|>"
            )

    def test_worked_bpe_example_uses_byte_pair_counts_and_checks_first_merge(self):
        result = worked_bpe_pair_example()
        self.assertTrue(result["passed"])
        self.assertEqual(result["selected_pair"], "ab")
        self.assertEqual(result["selected_frequency"], 4)
        self.assertEqual(result["first_trainer_merge"]["token_hex"], "6162")

    def test_tokenizer_checkpoint_mismatch_is_rejected(self):
        self.assertTrue(check_compatibility("a" * 64, "a" * 64))
        with self.assertRaisesRegex(ValueError, "mismatch"):
            check_compatibility("a" * 64, "b" * 64)

    def _valid_packet(self):
        return {
            "division_id": "dreamalpha",
            "division_name": "DreamAlpha",
            "focus_area": "approvals",
            "lesson_ids": ["tok-06"],
            "source_id": "synthetic-fixture",
            "source_sha256": "c" * 64,
            "rights_verified": True,
            "model_training_permission": True,
            "privacy_reviewed": True,
            "holdout": False,
            "sensitive": False,
            "commit_sha": "d" * 40,
            "input_hash": "c" * 64,
            "output_hash": "e" * 64,
            "test_results": {"passed": True},
            "specialist_assignment": "not_assigned_pending_owner_review",
            "owner_approval": None,
            "model_weight_training_executed": False,
        }

    def test_division_packet_requires_canonical_id_and_source_provenance(self):
        packet = self._valid_packet()
        self.assertTrue(validate_division_packet(packet, {"dreamalpha"}, "c" * 64))
        packet["division_id"] = "unknown"
        with self.assertRaisesRegex(ValueError, "unknown canonical"):
            validate_division_packet(packet, {"dreamalpha"}, "c" * 64)

    def test_division_packet_blocks_unapproved_specialist_assignment(self):
        packet = self._valid_packet()
        packet["specialist_assignment"] = "DreamAlpha_masterbot"
        with self.assertRaisesRegex(ValueError, "without owner approval"):
            validate_division_packet(packet, {"dreamalpha"}, "c" * 64)

    def test_division_packet_blocks_unknown_rights(self):
        packet = self._valid_packet()
        packet["rights_verified"] = False
        with self.assertRaisesRegex(PermissionError, "explicit source permission"):
            validate_division_packet(packet, {"dreamalpha"}, "c" * 64)

    def test_division_packet_blocks_model_weight_training(self):
        packet = self._valid_packet()
        packet["model_weight_training_executed"] = True
        with self.assertRaisesRegex(ValueError, "must not train"):
            validate_division_packet(packet, {"dreamalpha"}, "c" * 64)


if __name__ == "__main__":
    unittest.main()
