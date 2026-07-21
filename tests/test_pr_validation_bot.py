"""Tests for bots/pr_validation_bot/pr_validation_bot.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from unittest.mock import patch, MagicMock
from bots.pr_validation_bot.pr_validation_bot import (
    PRValidationBot,
    ValidationResult,
    RevenueCheck,
    FileStatus,
    CRITICAL_FILES,
)


# ---------------------------------------------------------------------------
# FileStatus and classification tests
# ---------------------------------------------------------------------------


class TestFileStatusClassification:
    def setup_method(self):
        self.bot = PRValidationBot(repo_root=REPO_ROOT)

    def test_deleted_file_goes_to_deleted_list(self):
        files = [FileStatus(path="index.js", status="D")]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 1
        assert deleted[0].path == "index.js"
        assert len(skipped) == 0

    def test_modified_file_goes_to_skipped(self):
        files = [FileStatus(path="index.js", status="M")]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 0
        assert "index.js" in skipped

    def test_renamed_file_goes_to_skipped(self):
        files = [FileStatus(path="README.md", status="R")]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 0
        assert "README.md" in skipped

    def test_added_file_not_in_either_list(self):
        files = [FileStatus(path="new_bot.py", status="A")]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 0
        assert len(skipped) == 0

    def test_mixed_statuses_correctly_classified(self):
        files = [
            FileStatus(path="index.js", status="D"),
            FileStatus(path="package.json", status="M"),
            FileStatus(path="README.md", status="R"),
            FileStatus(path="new_file.py", status="A"),
        ]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 1
        assert deleted[0].path == "index.js"
        assert "package.json" in skipped
        assert "README.md" in skipped
        assert "new_file.py" not in skipped

    def test_multiple_deleted_files(self):
        files = [
            FileStatus(path="index.js", status="D"),
            FileStatus(path="package.json", status="D"),
        ]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 2
        assert len(skipped) == 0

    def test_modified_critical_file_not_restored(self):
        """Modified critical files must NOT be auto-restored."""
        files = [FileStatus(path="framework/__init__.py", status="M")]
        deleted, skipped = self.bot._classify_files(files)
        assert len(deleted) == 0
        assert "framework/__init__.py" in skipped


# ---------------------------------------------------------------------------
# Revenue check tests
# ---------------------------------------------------------------------------


class TestRevenueCheck:
    def test_fully_ready_bot(self, tmp_path):
        bot_dir = tmp_path / "my_bot"
        bot_dir.mkdir()
        (bot_dir / "payments.js").write_text("{}")
        (bot_dir / "logger.js").write_text("{}")
        (bot_dir / "index.js").write_text("{}")
        rc = RevenueCheck(
            bot_path="my_bot",
            has_payment=True,
            has_logger=True,
            has_offer=True,
        )
        assert rc.is_ready is True

    def test_missing_payment_not_ready(self):
        rc = RevenueCheck(
            bot_path="bot_x", has_payment=False, has_logger=True, has_offer=True
        )
        assert rc.is_ready is False

    def test_missing_logger_not_ready(self):
        rc = RevenueCheck(
            bot_path="bot_y", has_payment=True, has_logger=False, has_offer=True
        )
        assert rc.is_ready is False

    def test_missing_offer_not_ready(self):
        rc = RevenueCheck(
            bot_path="bot_z", has_payment=True, has_logger=True, has_offer=False
        )
        assert rc.is_ready is False

    def test_to_dict_contains_expected_keys(self):
        rc = RevenueCheck(
            bot_path="bot_a", has_payment=True, has_logger=True, has_offer=True
        )
        d = rc.to_dict()
        assert "bot_path" in d
        assert "has_payment" in d
        assert "has_logger" in d
        assert "has_offer" in d
        assert "is_ready" in d


# ---------------------------------------------------------------------------
# Critical file existence check
# ---------------------------------------------------------------------------


class TestCriticalFilesExist:
    def test_missing_critical_file_returns_false(self, tmp_path):
        bot = PRValidationBot(repo_root=str(tmp_path))
        assert bot._check_critical_files_exist() is False

    def test_all_critical_files_present(self, tmp_path):
        for f in CRITICAL_FILES:
            full = tmp_path / f
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text("")
        bot = PRValidationBot(repo_root=str(tmp_path))
        assert bot._check_critical_files_exist() is True


# ---------------------------------------------------------------------------
# Revenue bot validation
# ---------------------------------------------------------------------------


class TestValidateRevenueBots:
    def test_no_bots_dir_returns_empty(self, tmp_path):
        bot = PRValidationBot(repo_root=str(tmp_path))
        checks = bot._validate_revenue_bots()
        assert checks == []

    def test_bot_with_all_files_is_ready(self, tmp_path):
        bots_dir = tmp_path / "bots"
        my_bot = bots_dir / "my_bot"
        my_bot.mkdir(parents=True)
        (my_bot / "payments.js").write_text("{}")
        (my_bot / "logger.js").write_text("{}")
        (my_bot / "index.js").write_text("{}")
        bot = PRValidationBot(repo_root=str(tmp_path))
        checks = bot._validate_revenue_bots()
        assert len(checks) == 1
        assert checks[0].is_ready is True

    def test_bot_missing_payments_not_ready(self, tmp_path):
        bots_dir = tmp_path / "bots"
        my_bot = bots_dir / "my_bot"
        my_bot.mkdir(parents=True)
        (my_bot / "logger.js").write_text("{}")
        (my_bot / "index.js").write_text("{}")
        bot = PRValidationBot(repo_root=str(tmp_path))
        checks = bot._validate_revenue_bots()
        assert not checks[0].has_payment
        assert checks[0].is_ready is False

    def test_multiple_bots_scanned(self, tmp_path):
        bots_dir = tmp_path / "bots"
        for name in ["bot_a", "bot_b", "bot_c"]:
            (bots_dir / name).mkdir(parents=True)
        bot = PRValidationBot(repo_root=str(tmp_path))
        checks = bot._validate_revenue_bots()
        assert len(checks) == 3


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


class TestBuildReport:
    def test_report_contains_passed_status(self):
        bot = PRValidationBot()
        result = ValidationResult(passed=True, critical_files_ok=True)
        result.report_md = bot._build_report(result)
        assert "PASSED" in result.report_md

    def test_report_contains_failed_status(self):
        bot = PRValidationBot()
        result = ValidationResult(passed=False, critical_files_ok=False)
        result.report_md = bot._build_report(result)
        assert "FAILED" in result.report_md

    def test_report_lists_restored_files(self):
        bot = PRValidationBot()
        result = ValidationResult(
            passed=True,
            critical_files_ok=True,
            restored_files=["index.js"],
        )
        result.report_md = bot._build_report(result)
        assert "index.js" in result.report_md
        assert "Auto-Restored" in result.report_md

    def test_report_lists_skipped_files(self):
        bot = PRValidationBot()
        result = ValidationResult(
            passed=True,
            critical_files_ok=True,
            skipped_files=["package.json"],
        )
        result.report_md = bot._build_report(result)
        assert "package.json" in result.report_md
        assert "Skipped" in result.report_md

    def test_report_has_revenue_table(self):
        bot = PRValidationBot()
        result = ValidationResult(
            passed=True,
            critical_files_ok=True,
            revenue_checks=[
                RevenueCheck("my_bot", has_payment=True, has_logger=True, has_offer=True)
            ],
        )
        result.report_md = bot._build_report(result)
        assert "Revenue Readiness" in result.report_md
        assert "my_bot" in result.report_md

    def test_report_is_string(self):
        bot = PRValidationBot()
        result = ValidationResult(passed=True, critical_files_ok=True)
        md = bot._build_report(result)
        assert isinstance(md, str)

    def test_report_contains_pr_validation_header(self):
        bot = PRValidationBot()
        result = ValidationResult(passed=True, critical_files_ok=True)
        md = bot._build_report(result)
        assert "PR Validation Report" in md


# ---------------------------------------------------------------------------
# ValidationResult dataclass
# ---------------------------------------------------------------------------


class TestValidationResult:
    def test_default_values(self):
        r = ValidationResult(passed=True, critical_files_ok=True)
        assert r.restored_files == []
        assert r.skipped_files == []
        assert r.revenue_checks == []
        assert r.errors == []
        assert r.report_md == ""

    def test_passed_false_when_errors(self):
        r = ValidationResult(
            passed=False,
            critical_files_ok=True,
            errors=["something wrong"],
        )
        assert not r.passed
