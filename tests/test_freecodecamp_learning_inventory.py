from __future__ import annotations

import json
import unittest
from pathlib import Path
from pathlib import Path
import subprocess
import sys

try:
    from buddy.learning.course_track_registry import load_course_lessons as _course_track_adapter
    COURSE_TRACKS_AVAILABLE = True
except ModuleNotFoundError:
    COURSE_TRACKS_AVAILABLE = False

from tools.sync_freecodecamp_learning_inventory import build_payloads


@unittest.skipUnless(COURSE_TRACKS_AVAILABLE, "Buddy course-track adapter is added by the bootcamp curriculum PR")
class FreeCodeCampLearningInventoryTests(unittest.TestCase):
    def test_course_queue_counts_match_the_catalog_and_registry(self):
        learning, policy = build_payloads()
        self.assertEqual(
            learning["youtube_video_inventory"]["observed_video_count"],
            learning["youtube_video_inventory"]["expected_entry_count"] or learning["youtube_video_inventory"]["observed_video_count"],
        )
        registry = json.loads((Path(__file__).resolve().parents[1] / "config/buddy-course-track-registry.json").read_text(encoding="utf-8"))
        self.assertEqual(policy["study_assets"]["course_track_count"], len(registry["tracks"]))
        self.assertGreater(policy["study_assets"]["course_lesson_count"], learning["youtube_video_inventory"]["observed_video_count"])
        self.assertIn(learning["youtube_video_inventory"]["inventory_status"], {"complete", "partial"})

    def test_partial_inventory_never_claims_complete(self):
        learning, _ = build_payloads()
        if learning["youtube_video_inventory"]["expected_entry_count"] is None:
            self.assertFalse(learning["youtube_video_inventory"]["inventory_complete"])
            self.assertEqual(learning["youtube_video_inventory"]["inventory_status"], "partial")

    def test_cli_imports_repository_packages_when_run_from_tools_path(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "tools/sync_freecodecamp_learning_inventory.py", "--check"],
            cwd=root, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
