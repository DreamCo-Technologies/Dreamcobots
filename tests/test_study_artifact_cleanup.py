import tempfile
import unittest
from pathlib import Path

from buddy.learning.study_artifact_cleanup import (
    cleanup_study_downloads,
    create_study_workspace,
    study_download_workspace,
)


class StudyArtifactCleanupTests(unittest.TestCase):
    def test_workspace_is_erased_after_successful_study(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            captured = None
            with study_download_workspace(base) as workspace:
                captured = workspace
                (workspace / "lesson.tmp").write_bytes(b"temporary media")
                (workspace / "nested").mkdir()
                (workspace / "nested" / "segment.tmp").write_bytes(b"segment")
            self.assertFalse(captured.exists())

    def test_workspace_is_erased_when_study_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            captured = None
            with self.assertRaisesRegex(RuntimeError, "study failed"):
                with study_download_workspace(base) as workspace:
                    captured = workspace
                    (workspace / "lesson.tmp").write_text("temporary")
                    raise RuntimeError("study failed")
            self.assertFalse(captured.exists())

    def test_cleanup_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            workspace = create_study_workspace(base)
            self.assertTrue(cleanup_study_downloads(workspace, base))
            self.assertFalse(cleanup_study_downloads(workspace, base))

    def test_refuses_paths_outside_managed_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "managed"
            base.mkdir()
            outside = Path(tmp) / "important"
            outside.mkdir()
            (outside / "keep.txt").write_text("keep")
            with self.assertRaisesRegex(ValueError, "outside"):
                cleanup_study_downloads(outside, base)
            self.assertTrue((outside / "keep.txt").exists())


if __name__ == "__main__":
    unittest.main()
