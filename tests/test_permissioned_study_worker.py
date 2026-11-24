import tempfile
import unittest
from pathlib import Path

from buddy.learning.permissioned_study_worker import (
    StudyAuthorization, run_study_attempt,
)


class PermissionedStudyWorkerTests(unittest.TestCase):
    def test_public_metadata_only_study_cannot_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            auth = StudyAuthorization(
                "freeCodeCamp", "https://www.youtube.com/watch?v=abc",
                "public_metadata_only", frozenset({"open_official_page"}),
            )
            def study(ctx):
                self.assertFalse(ctx.media_download_allowed)
                self.assertFalse(ctx.transcript_ingestion_allowed)
                self.assertFalse(ctx.model_training_allowed)
                return {"lesson_status": "metadata_only"}
            result = run_study_attempt(auth, study, Path(tmp))
            self.assertTrue(result["temporary_workspace_erased"])
            self.assertFalse(any(Path(tmp).iterdir()))

    def test_unapproved_media_download_is_blocked_before_callback(self):
        with tempfile.TemporaryDirectory() as tmp:
            auth = StudyAuthorization(
                "source", "https://example.org/course", "pending",
                frozenset({"open_official_page", "download_media"}),
            )
            called = []
            with self.assertRaisesRegex(PermissionError, "explicit approved"):
                run_study_attempt(auth, lambda _ctx: called.append(True), Path(tmp))
            self.assertEqual(called, [])
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_approved_download_workspace_is_erased_after_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            auth = StudyAuthorization(
                "authorized source", "https://example.org/course", "approved",
                frozenset({"open_official_page", "download_media"}), "rights-ticket-123",
            )
            captured = []
            def study(ctx):
                self.assertTrue(ctx.media_download_allowed)
                (ctx.workspace / "temporary-video.bin").write_bytes(b"temporary")
                captured.append(ctx.workspace)
                return {"original_lesson_created": True}
            result = run_study_attempt(auth, study, Path(tmp))
            self.assertTrue(result["temporary_workspace_erased"])
            self.assertFalse(captured[0].exists())
            self.assertFalse(result["model_training_allowed"])

    def test_workspace_is_erased_when_callback_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            auth = StudyAuthorization("source", "https://example.org", "approved")
            captured = []
            def fail(ctx):
                (ctx.workspace / "partial.tmp").write_text("partial")
                captured.append(ctx.workspace)
                raise RuntimeError("study error")
            with self.assertRaisesRegex(RuntimeError, "study error"):
                run_study_attempt(auth, fail, Path(tmp))
            self.assertFalse(captured[0].exists())
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_workspace_is_erased_when_attempt_is_cancelled(self):
        class CancelStudy(BaseException):
            pass
        with tempfile.TemporaryDirectory() as tmp:
            auth = StudyAuthorization("source", "https://example.org", "approved")
            captured = []
            def cancel(ctx):
                (ctx.workspace / "partial.tmp").write_text("partial")
                captured.append(ctx.workspace)
                raise CancelStudy("cancelled")
            with self.assertRaises(CancelStudy):
                run_study_attempt(auth, cancel, Path(tmp))
            self.assertFalse(captured[0].exists())
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_transcript_permission_also_requires_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            auth = StudyAuthorization(
                "source", "https://example.org", "approved",
                frozenset({"ingest_transcript"}),
            )
            with self.assertRaisesRegex(PermissionError, "evidence reference"):
                run_study_attempt(auth, lambda _ctx: None, Path(tmp))


if __name__ == "__main__":
    unittest.main()
