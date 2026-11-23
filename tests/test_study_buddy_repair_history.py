import unittest
from unittest.mock import patch

from tools.study_buddy_repair_history import build_index, classify_paths


class HistoricalRepairStudyTests(unittest.TestCase):
    def test_classifies_multiple_areas(self):
        self.assertEqual(
            classify_paths(["tools/repair.py", "tests/test_repair.py", ".github/workflows/ci.yml"]),
            ["python", "workflow"],
        )

    def test_history_is_never_marked_verified_or_training_ready(self):
        git_outputs = iter([
            "a" * 40 + "\x1ffix: repair generated index\n",
            "tools/build_index.py\ntests/test_build_index.py\n",
        ])
        with patch("tools.study_buddy_repair_history.run_git", side_effect=lambda *a, **k: next(git_outputs)):
            result = build_index(10)
        self.assertEqual(result["record_count"], 1)
        record = result["records"][0]
        self.assertFalse(record["verified_fix"])
        self.assertFalse(record["training_eligible"])
        self.assertEqual(record["learning_state"], "HISTORICAL_CANDIDATE_REQUIRES_VERIFICATION")
        self.assertEqual(record["test_paths"], ["tests/test_build_index.py"])

    def test_no_patch_or_log_content_is_exported(self):
        git_outputs = iter(["b" * 40 + "\x1fsecurity repair\n", "src/auth.py\n"])
        with patch("tools.study_buddy_repair_history.run_git", side_effect=lambda *a, **k: next(git_outputs)):
            result = build_index(1)
        self.assertNotIn("patch", result["records"][0])
        self.assertNotIn("logs", result["records"][0])


if __name__ == "__main__":
    unittest.main()
