import unittest
from buddy.registrar.registrar import issue_transcript, load_catalog, verify_transcript_seal


class DreamCoInstituteRegistrarTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_catalog()
        self.college = self.catalog["colleges"][0]
        self.evidence = {
            course["code"]: {
                "score_pct": 94,
                "assessment_evidence_id": f"assessment-{course['code']}",
                "practicum_passed": True,
                "independent_holdout_passed": True,
            }
            for course in self.college["courses"]
        }

    def test_catalog_has_five_colleges_and_55_unique_domain_assignments(self):
        self.assertEqual(len(self.catalog["colleges"]), 5)
        assignments = self.catalog["division_crosswalk"]["academic_assignments"]
        self.assertEqual(len(assignments), 55)
        self.assertEqual(len({row["domain_id"] for row in assignments}), 55)

    def test_credits_require_assessment_practicum_and_holdout(self):
        missing = dict(self.evidence)
        missing[self.college["courses"][0]["code"]] = {
            "score_pct": 99,
            "assessment_evidence_id": "assessment-1",
            "practicum_passed": True,
            "independent_holdout_passed": False,
        }
        transcript = issue_transcript("candidate-1", self.college["id"], missing, catalog=self.catalog)
        self.assertEqual(transcript["academic_record"][0]["credits_earned"], 0)
        self.assertFalse(transcript["summary"]["graduated"])

    def test_gpa_counts_attempted_credits_even_when_credit_is_not_awarded(self):
        mixed = dict(self.evidence)
        first_code = self.college["courses"][0]["code"]
        mixed[first_code] = {
            "score_pct": 50,
            "assessment_evidence_id": "assessment-fail",
            "practicum_passed": True,
            "independent_holdout_passed": True,
        }
        transcript = issue_transcript("candidate-1", self.college["id"], mixed, catalog=self.catalog)
        self.assertEqual(transcript["academic_record"][0]["credits_earned"], 0)
        self.assertLess(transcript["summary"]["cumulative_gpa"], 4.0)
        self.assertEqual(transcript["summary"]["credits_attempted"], transcript["summary"]["credits_required"])

    def test_degree_requires_thesis_defense_and_registrar_review(self):
        without_thesis = issue_transcript("candidate-1", self.college["id"], self.evidence, catalog=self.catalog)
        self.assertFalse(without_thesis["summary"]["graduated"])
        thesis = {"thesis_record_id": "thesis-1", "oral_defense_passed": True, "independent_review_id": "review-1"}
        with_thesis = issue_transcript("candidate-1", self.college["id"], self.evidence, thesis, "registrar-1", self.catalog)
        self.assertTrue(with_thesis["summary"]["graduated"])
        self.assertEqual(with_thesis["summary"]["credits_earned"], with_thesis["summary"]["credits_required"])

    def test_seal_detects_transcript_tampering_and_is_not_signature(self):
        transcript = issue_transcript("candidate-1", self.college["id"], self.evidence, catalog=self.catalog)
        self.assertTrue(verify_transcript_seal(transcript))
        transcript["summary"]["cumulative_gpa"] = 4.0
        self.assertFalse(verify_transcript_seal(transcript))
        self.assertEqual(transcript["seal_type"], "integrity_checksum_not_digital_signature")

    def test_bad_scores_and_unknown_colleges_are_rejected(self):
        bad = dict(self.evidence)
        bad[self.college["courses"][0]["code"]] = {"score_pct": 101}
        with self.assertRaises(ValueError):
            issue_transcript("candidate-1", self.college["id"], bad, catalog=self.catalog)
        with self.assertRaises(ValueError):
            issue_transcript("candidate-1", "unknown", {}, catalog=self.catalog)

    def test_unresolved_operational_ownership_is_not_changed_by_academic_assignment(self):
        unresolved = [row for row in self.catalog["division_crosswalk"]["academic_assignments"] if row["domain_id"] == "dreamaffiliate"]
        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0]["operational_masterbot_ownership"], "unchanged_from_canonical_crosswalk")
        self.assertEqual(unresolved[0]["academic_assignment_status"], "proposed_academic_home")


if __name__ == "__main__":
    unittest.main()
