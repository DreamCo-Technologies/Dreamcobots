import unittest

from tools.run_buddy_study_evidence_session import (
    LESSON_PRIORITY,
    check_compatibility,
    extract_glossary,
    parse_division_profiles,
    score_active_recall,
    select_priority_lessons,
    validate_division_packet,
    validate_role_markers,
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

    def test_active_recall_scores_reference_answers(self):
        result = score_active_recall()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["score"], 100.0)
        self.assertFalse(result["independent_model_inference"])

    def test_glossary_only_emits_terms_found_in_approved_sources(self):
        glossary = extract_glossary({
            "internal-guide.md": "A tokenizer uses UTF-8 and normalization.",
            "synthetic.txt": "A merge updates the vocabulary.",
        })
        terms = {row["term"] for row in glossary}
        self.assertIn("tokenizer", terms)
        self.assertIn("UTF-8", terms)
        self.assertIn("merge", terms)
        self.assertNotIn("holdout", terms)

    def test_role_marker_contract_accepts_supported_roles(self):
        self.assertTrue(validate_role_markers(
            "<|system|>s<|user|>u<|assistant|>a<|tool|>t"
        ))

    def test_role_marker_contract_rejects_unknown_roles(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            validate_role_markers(
                "<|system|>s<|user|>u<|assistant|>a<|tool|>t<|root|>"
            )

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
