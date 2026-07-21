"""Tests for bots/revenue_validation/revenue_validation_bot.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.revenue_validation.revenue_validation_bot import (
    RevenueValidationBot,
    BotRevenueStatus,
    RevenueValidationReport,
    REQUIRED_FILES,
)


def _make_bot_dir(parent, name, files=None):
    """Helper: create a bot directory with optional files."""
    bot_dir = parent / name
    bot_dir.mkdir(parents=True, exist_ok=True)
    for f in (files or []):
        (bot_dir / f).write_text("{}")
    return bot_dir


# ---------------------------------------------------------------------------
# BotRevenueStatus
# ---------------------------------------------------------------------------


class TestBotRevenueStatus:
    def test_all_checks_true_is_ready(self):
        status = BotRevenueStatus(
            bot_name="my_bot",
            checks={"payments.js": True, "logger.js": True, "index.js": True},
        )
        assert status.is_ready is True

    def test_missing_one_check_not_ready(self):
        status = BotRevenueStatus(
            bot_name="my_bot",
            checks={"payments.js": False, "logger.js": True, "index.js": True},
        )
        assert status.is_ready is False

    def test_missing_files_lists_false_items(self):
        status = BotRevenueStatus(
            bot_name="my_bot",
            checks={"payments.js": False, "logger.js": True, "index.js": False},
        )
        assert "payments.js" in status.missing_files
        assert "index.js" in status.missing_files
        assert "logger.js" not in status.missing_files

    def test_to_dict_keys(self):
        status = BotRevenueStatus(
            bot_name="test_bot",
            checks={"payments.js": True, "logger.js": True, "index.js": True},
        )
        d = status.to_dict()
        assert "bot_name" in d
        assert "checks" in d
        assert "is_ready" in d
        assert "missing_files" in d

    def test_empty_checks_vacuously_ready(self):
        status = BotRevenueStatus(bot_name="empty_bot", checks={})
        assert status.is_ready is True  # all([]) == True (vacuously true)


# ---------------------------------------------------------------------------
# RevenueValidationBot — validate()
# ---------------------------------------------------------------------------


class TestRevenueValidationBotValidate:
    def test_no_bots_dir_returns_empty_report(self, tmp_path):
        validator = RevenueValidationBot(bots_dir=str(tmp_path / "bots"))
        report = validator.validate()
        assert report.total_bots == 0
        assert report.ready_bots == 0

    def test_fully_ready_bot_passes(self, tmp_path):
        bots_dir = tmp_path / "bots"
        _make_bot_dir(bots_dir, "good_bot", ["payments.js", "logger.js", "index.js"])
        validator = RevenueValidationBot(bots_dir=str(bots_dir))
        report = validator.validate()
        assert report.total_bots == 1
        assert report.ready_bots == 1
        assert report.blocked_bots == 0

    def test_bot_missing_payments_is_blocked(self, tmp_path):
        bots_dir = tmp_path / "bots"
        _make_bot_dir(bots_dir, "no_payment_bot", ["logger.js", "index.js"])
        validator = RevenueValidationBot(bots_dir=str(bots_dir))
        report = validator.validate()
        assert report.blocked_bots == 1

    def test_bot_missing_logger_is_blocked(self, tmp_path):
        bots_dir = tmp_path / "bots"
        _make_bot_dir(bots_dir, "no_logger_bot", ["payments.js", "index.js"])
        validator = RevenueValidationBot(bots_dir=str(bots_dir))
        report = validator.validate()
        assert report.blocked_bots == 1

    def test_bot_missing_index_is_blocked(self, tmp_path):
        bots_dir = tmp_path / "bots"
        _make_bot_dir(bots_dir, "no_index_bot", ["payments.js", "logger.js"])
        validator = RevenueValidationBot(bots_dir=str(bots_dir))
        report = validator.validate()
        assert report.blocked_bots == 1

    def test_multiple_bots_counted(self, tmp_path):
        bots_dir = tmp_path / "bots"
        _make_bot_dir(bots_dir, "bot_a", ["payments.js", "logger.js", "index.js"])
        _make_bot_dir(bots_dir, "bot_b", ["logger.js", "index.js"])
        _make_bot_dir(bots_dir, "bot_c", ["payments.js", "logger.js", "index.js"])
        validator = RevenueValidationBot(bots_dir=str(bots_dir))
        report = validator.validate()
        assert report.total_bots == 3
        assert report.ready_bots == 2
        assert report.blocked_bots == 1

    def test_strict_mode_fails_when_blocked(self, tmp_path):
        bots_dir = tmp_path / "bots"
        _make_bot_dir(bots_dir, "bad_bot", ["logger.js"])
        validator = RevenueValidationBot(bots_dir=str(bots_dir), strict=True)
        report = validator.validate()
        assert report.passed is False

    def test_non_strict_mode_passes_even_when_blocked(self, tmp_path):
        bots_dir = tmp_path / "bots"
        _make_bot_dir(bots_dir, "bad_bot", ["logger.js"])
        validator = RevenueValidationBot(bots_dir=str(bots_dir), strict=False)
        report = validator.validate()
        assert report.passed is True

    def test_filter_by_bot_name(self, tmp_path):
        bots_dir = tmp_path / "bots"
        _make_bot_dir(bots_dir, "bot_a", ["payments.js", "logger.js", "index.js"])
        _make_bot_dir(bots_dir, "bot_b", ["payments.js", "logger.js", "index.js"])
        validator = RevenueValidationBot(bots_dir=str(bots_dir))
        report = validator.validate(bot_names=["bot_a"])
        assert report.total_bots == 1
        assert report.results[0].bot_name == "bot_a"

    def test_non_directory_entries_skipped(self, tmp_path):
        bots_dir = tmp_path / "bots"
        bots_dir.mkdir()
        (bots_dir / "not_a_bot.txt").write_text("ignore me")
        validator = RevenueValidationBot(bots_dir=str(bots_dir))
        report = validator.validate()
        assert report.total_bots == 0


# ---------------------------------------------------------------------------
# validate_single_bot()
# ---------------------------------------------------------------------------


class TestValidateSingleBot:
    def test_single_bot_fully_ready(self, tmp_path):
        bots_dir = tmp_path / "bots"
        _make_bot_dir(bots_dir, "my_bot", ["payments.js", "logger.js", "index.js"])
        validator = RevenueValidationBot(bots_dir=str(bots_dir))
        status = validator.validate_single_bot("my_bot")
        assert status.is_ready is True

    def test_single_bot_missing_files(self, tmp_path):
        bots_dir = tmp_path / "bots"
        _make_bot_dir(bots_dir, "my_bot", ["logger.js"])
        validator = RevenueValidationBot(bots_dir=str(bots_dir))
        status = validator.validate_single_bot("my_bot")
        assert status.is_ready is False
        assert "payments.js" in status.missing_files
        assert "index.js" in status.missing_files

    def test_single_bot_absolute_path(self, tmp_path):
        bot_dir = tmp_path / "standalone_bot"
        bot_dir.mkdir()
        (bot_dir / "payments.js").write_text("{}")
        (bot_dir / "logger.js").write_text("{}")
        (bot_dir / "index.js").write_text("{}")
        validator = RevenueValidationBot(bots_dir=str(tmp_path))
        status = validator.validate_single_bot(str(bot_dir))
        assert status.is_ready is True


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


class TestRevenueReport:
    def test_report_is_string(self, tmp_path):
        validator = RevenueValidationBot(bots_dir=str(tmp_path / "bots"))
        report = validator.validate()
        assert isinstance(report.report_md, str)

    def test_report_has_header(self, tmp_path):
        validator = RevenueValidationBot(bots_dir=str(tmp_path / "bots"))
        report = validator.validate()
        assert "Revenue Validation Report" in report.report_md

    def test_report_lists_blocked_bots(self, tmp_path):
        bots_dir = tmp_path / "bots"
        _make_bot_dir(bots_dir, "broken_bot", [])
        validator = RevenueValidationBot(bots_dir=str(bots_dir))
        report = validator.validate()
        assert "broken_bot" in report.report_md

    def test_report_shows_all_clear_when_ready(self, tmp_path):
        bots_dir = tmp_path / "bots"
        _make_bot_dir(bots_dir, "good_bot", ["payments.js", "logger.js", "index.js"])
        validator = RevenueValidationBot(bots_dir=str(bots_dir))
        report = validator.validate()
        assert "ALL CLEAR" in report.report_md

    def test_to_dict_has_expected_keys(self, tmp_path):
        validator = RevenueValidationBot(bots_dir=str(tmp_path / "bots"))
        report = validator.validate()
        d = report.to_dict()
        assert "total_bots" in d
        assert "ready_bots" in d
        assert "blocked_bots" in d
        assert "passed" in d
        assert "results" in d
