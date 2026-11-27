import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from tools.daily_bot_study_scan import main, scan


class DailyBotStudyScanTest(unittest.TestCase):
    def test_scan_covers_bots_without_claiming_production_mastery(self) -> None:
        report = scan()
        self.assertGreaterEqual(report["bot_count"], 1100)
        self.assertGreater(report["original_bot_studies"], 100)
        self.assertFalse(report["production_mastered"])
        self.assertTrue(report["speed"])

    def test_check_reports_backlog_without_misclassifying_it_as_scan_failure(self) -> None:
        report = {
            "ready": False,
            "missing_files": [],
            "bot_count": 1120,
            "sandbox_studied": 0,
            "open_tasks": 3303,
            "original_bot_studies": 200,
            "elapsed_seconds": 0.1,
        }
        with patch("tools.daily_bot_study_scan.scan", return_value=report), patch(
            "tools.daily_bot_study_scan.write_report"
        ), redirect_stdout(StringIO()):
            self.assertEqual(main(["--check"]), 0)

    def test_check_fails_when_required_files_are_missing(self) -> None:
        report = {
            "ready": False,
            "missing_files": ["buddy/learning/required.py"],
            "bot_count": 1120,
            "sandbox_studied": 0,
            "open_tasks": 3303,
            "original_bot_studies": 200,
            "elapsed_seconds": 0.1,
        }
        with patch("tools.daily_bot_study_scan.scan", return_value=report), patch(
            "tools.daily_bot_study_scan.write_report"
        ), redirect_stdout(StringIO()):
            self.assertEqual(main(["--check"]), 1)


if __name__ == "__main__":
    unittest.main()
