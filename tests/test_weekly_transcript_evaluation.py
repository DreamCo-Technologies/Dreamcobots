import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from tools.build_weekly_transcript_evaluation import build_report, validate_manifest


POLICY = {"requirement": "Each approved transcript is evaluated weekly."}


class WeeklyTranscriptEvaluationTests(unittest.TestCase):
    def test_missing_manifest_is_blocked_not_passed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_report(POLICY, root / "missing.json", root / "ledger.json", date(2026, 11, 24))
        self.assertEqual(report["status"], "blocked")
        self.assertIsNone(report["coverage"])
        self.assertEqual(report["blocked_reasons"], ["approved_transcript_manifest_missing"])
        self.assertEqual(report["synthetic_evaluations_created"], 0)

    def test_every_approved_transcript_is_due_without_weekly_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({
                "schema": "dreamco.authorized_transcript_manifest.v1",
                "transcripts": [{
                    "transcript_id": "lesson-001",
                    "transcript_sha256": "a" * 64,
                    "source_url": "https://example.org/lesson",
                    "rights_evidence_ref": "rights-001",
                    "division_ids": [1, 2],
                    "rights_status": "approved",
                    "evaluation_allowed": True
                }]
            }))
            report = build_report(POLICY, manifest, root / "ledger.json", date(2026, 11, 24))
        self.assertEqual(report["due_count"], 1)
        self.assertEqual(report["due_transcripts"][0]["status"], "due_not_evaluated")
        self.assertEqual(report["status"], "blocked")

    def test_matching_weekly_real_result_satisfies_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            ledger = root / "ledger.json"
            manifest.write_text(json.dumps({
                "schema": "dreamco.authorized_transcript_manifest.v1",
                "transcripts": [{
                    "transcript_id": "lesson-001", "transcript_sha256": "b" * 64,
                    "source_url": "https://example.org/lesson", "rights_evidence_ref": "rights-001",
                    "division_ids": [1], "rights_status": "approved", "evaluation_allowed": True
                }]
            }))
            ledger.write_text(json.dumps({
                "schema": "dreamco.buddy_transcript_evaluation_ledger.v1",
                "evaluations": [{
                    "transcript_id": "lesson-001", "transcript_sha256": "b" * 64,
                    "iso_week": "2026-W48", "result": "failed",
                    "buddy_model_id": "buddy-test", "buddy_model_version": "0.1",
                    "evaluation_suite_version": "1", "rights_evidence_ref": "rights-001", "run_id": "123"
                }]
            }))
            report = build_report(POLICY, manifest, ledger, date(2026, 11, 24))
        self.assertEqual(report["due_count"], 0)
        self.assertEqual(report["evaluated_count"], 1)
        self.assertEqual(report["status"], "blocked")  # no real inference adapter is registered

    def test_rejects_transcript_without_rights_approval(self):
        with self.assertRaises(ValueError):
            validate_manifest({"schema": "dreamco.authorized_transcript_manifest.v1", "transcripts": [{
                "transcript_id": "x", "transcript_sha256": "c" * 64, "source_url": "https://example.org/x",
                "rights_evidence_ref": "rights-x", "division_ids": [1],
                "rights_status": "pending", "evaluation_allowed": False
            }]})


if __name__ == "__main__":
    unittest.main()
