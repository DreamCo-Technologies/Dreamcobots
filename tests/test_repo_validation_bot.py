"""Tests for bots/repo_validation_bot/repo_validation_bot.py"""

from __future__ import annotations

import os
import sys

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

from bots.repo_validation_bot.repo_validation_bot import (
    BotValidationResult,
    RepoValidationBot,
    ValidationReport,
    _check_app_export,
    _is_bot_dir,
    scan_repo,
    validate_bot,
)


# ---------------------------------------------------------------------------
# _is_bot_dir
# ---------------------------------------------------------------------------


class TestIsBotDir:
    def test_name_containing_bot(self):
        assert _is_bot_dir("/some/path/my_bot") is True

    def test_name_starting_with_bot(self):
        assert _is_bot_dir("/some/path/bot_manager") is True

    def test_name_not_containing_bot(self):
        assert _is_bot_dir("/some/path/utils") is False

    def test_case_insensitive(self):
        assert _is_bot_dir("/some/path/MyBOT") is True


# ---------------------------------------------------------------------------
# _check_app_export
# ---------------------------------------------------------------------------


class TestCheckAppExport:
    def test_correct_flask_app(self, tmp_path):
        f = tmp_path / "main.py"
        f.write_text("from flask import Flask\napp = Flask(__name__)\n")
        assert _check_app_export(str(f)) == []

    def test_correct_fastapi_app(self, tmp_path):
        f = tmp_path / "main.py"
        f.write_text("from fastapi import FastAPI\napp = FastAPI()\n")
        assert _check_app_export(str(f)) == []

    def test_wrong_variable_name_flask(self, tmp_path):
        f = tmp_path / "main.py"
        f.write_text("from flask import Flask\napplication = Flask(__name__)\n")
        issues = _check_app_export(str(f))
        assert len(issues) == 1
        assert "application" in issues[0]
        assert "app" in issues[0]

    def test_wrong_variable_name_fastapi(self, tmp_path):
        f = tmp_path / "main.py"
        f.write_text("from fastapi import FastAPI\nflask_app = FastAPI()\n")
        issues = _check_app_export(str(f))
        assert len(issues) == 1
        assert "flask_app" in issues[0]

    def test_no_framework_no_issues(self, tmp_path):
        f = tmp_path / "main.py"
        f.write_text("print('hello')\n")
        assert _check_app_export(str(f)) == []

    def test_invalid_syntax_returns_empty(self, tmp_path):
        f = tmp_path / "main.py"
        f.write_text("def broken(\n")
        assert _check_app_export(str(f)) == []

    def test_missing_file_returns_empty(self, tmp_path):
        path = str(tmp_path / "nonexistent.py")
        assert _check_app_export(path) == []

    def test_multiple_wrong_assignments(self, tmp_path):
        code = (
            "from flask import Flask\n"
            "from fastapi import FastAPI\n"
            "flask_instance = Flask(__name__)\n"
            "fast_instance = FastAPI()\n"
        )
        f = tmp_path / "main.py"
        f.write_text(code)
        issues = _check_app_export(str(f))
        # Both assignments are wrong
        assert len(issues) == 2


# ---------------------------------------------------------------------------
# validate_bot
# ---------------------------------------------------------------------------


class TestValidateBot:
    def test_valid_bot_passes(self, tmp_path):
        bot_dir = tmp_path / "my_bot"
        bot_dir.mkdir()
        (bot_dir / "main.py").write_text("print('running')\n")
        (bot_dir / "README.md").write_text("# My Bot\n")
        (bot_dir / "__init__.py").write_text("")
        result = validate_bot(str(bot_dir))
        assert result.passed is True
        assert result.issues == []

    def test_missing_main_file_fails(self, tmp_path):
        bot_dir = tmp_path / "my_bot"
        bot_dir.mkdir()
        (bot_dir / "README.md").write_text("# My Bot\n")
        result = validate_bot(str(bot_dir))
        assert result.passed is False
        assert any("main.py" in i or "index.js" in i or "bot.py" in i for i in result.issues)

    def test_missing_readme_fails(self, tmp_path):
        bot_dir = tmp_path / "my_bot"
        bot_dir.mkdir()
        (bot_dir / "main.py").write_text("print('running')\n")
        result = validate_bot(str(bot_dir))
        assert result.passed is False
        assert any("README.md" in i for i in result.issues)

    def test_wrong_app_name_fails(self, tmp_path):
        bot_dir = tmp_path / "my_bot"
        bot_dir.mkdir()
        (bot_dir / "main.py").write_text(
            "from flask import Flask\napplication = Flask(__name__)\n"
        )
        (bot_dir / "README.md").write_text("# Bot\n")
        (bot_dir / "__init__.py").write_text("")
        result = validate_bot(str(bot_dir))
        assert result.passed is False
        assert any("application" in i for i in result.issues)

    def test_correct_app_name_passes(self, tmp_path):
        bot_dir = tmp_path / "my_bot"
        bot_dir.mkdir()
        (bot_dir / "main.py").write_text(
            "from fastapi import FastAPI\napp = FastAPI()\n"
        )
        (bot_dir / "README.md").write_text("# Bot\n")
        (bot_dir / "__init__.py").write_text("")
        result = validate_bot(str(bot_dir))
        assert result.passed is True

    def test_missing_init_py_is_warning_not_error(self, tmp_path):
        bot_dir = tmp_path / "my_bot"
        bot_dir.mkdir()
        (bot_dir / "main.py").write_text("print('hi')\n")
        (bot_dir / "README.md").write_text("# Bot\n")
        result = validate_bot(str(bot_dir))
        # Should pass (no hard errors) but carry a warning
        assert result.passed is True
        assert any("__init__.py" in w for w in result.warnings)

    def test_index_js_satisfies_entry_point(self, tmp_path):
        bot_dir = tmp_path / "my_bot"
        bot_dir.mkdir()
        (bot_dir / "index.js").write_text("module.exports = {};\n")
        (bot_dir / "README.md").write_text("# Bot\n")
        result = validate_bot(str(bot_dir))
        assert result.passed is True

    def test_inaccessible_directory(self, tmp_path):
        result = validate_bot(str(tmp_path / "nonexistent_bot"))
        assert result.passed is False
        assert result.issues


# ---------------------------------------------------------------------------
# scan_repo
# ---------------------------------------------------------------------------


class TestScanRepo:
    def test_empty_repo_returns_empty_report(self, tmp_path):
        root = tmp_path / "repo"
        root.mkdir()
        report = scan_repo(str(root))
        assert report.total == 0
        assert report.all_passed is True

    def test_single_valid_bot(self, tmp_path):
        root = tmp_path / "repo"
        root.mkdir()
        bot_dir = root / "my_bot"
        bot_dir.mkdir()
        (bot_dir / "main.py").write_text("print('hi')\n")
        (bot_dir / "README.md").write_text("# Bot\n")
        (bot_dir / "__init__.py").write_text("")
        report = scan_repo(str(root))
        assert report.total == 1
        assert report.passed == 1
        assert report.failed == 0

    def test_single_invalid_bot(self, tmp_path):
        root = tmp_path / "repo"
        root.mkdir()
        bot_dir = root / "my_bot"
        bot_dir.mkdir()
        # Missing README.md
        (bot_dir / "main.py").write_text("print('hi')\n")
        report = scan_repo(str(root))
        assert report.total == 1
        assert report.failed == 1
        assert report.all_passed is False

    def test_mixed_bots(self, tmp_path):
        root = tmp_path / "repo"
        root.mkdir()
        good = root / "good_bot"
        good.mkdir()
        (good / "main.py").write_text("print('good')\n")
        (good / "README.md").write_text("# Good\n")
        (good / "__init__.py").write_text("")

        bad = root / "bad_bot"
        bad.mkdir()
        # missing README.md intentionally — only main.py is present
        (bad / "main.py").write_text("print('bad')\n")

        report = scan_repo(str(root))
        assert report.total == 2
        assert report.passed == 1
        assert report.failed == 1

    def test_non_bot_dirs_ignored(self, tmp_path):
        root = tmp_path / "repo"
        root.mkdir()
        non_bot = root / "utils"
        non_bot.mkdir()
        (non_bot / "helpers.py").write_text("")
        report = scan_repo(str(root))
        assert report.total == 0


# ---------------------------------------------------------------------------
# ValidationReport helpers
# ---------------------------------------------------------------------------


class TestValidationReport:
    def test_all_passed_true_when_no_failures(self):
        r = ValidationReport(total=3, passed=3, failed=0)
        assert r.all_passed is True

    def test_all_passed_false_when_failures(self):
        r = ValidationReport(total=3, passed=2, failed=1)
        assert r.all_passed is False

    def test_to_dict_contains_required_keys(self):
        r = ValidationReport(total=1, passed=1, failed=0)
        d = r.to_dict()
        assert "total" in d
        assert "passed" in d
        assert "failed" in d
        assert "all_passed" in d
        assert "results" in d

    def test_to_text_contains_summary(self):
        r = ValidationReport(total=2, passed=2, failed=0)
        text = r.to_text()
        assert "ALL BOTS VALID" in text

    def test_to_text_contains_failure_message(self):
        r = ValidationReport(
            total=1,
            passed=0,
            failed=1,
            results=[
                BotValidationResult(
                    bot_name="bad_bot",
                    bot_path="/tmp/bad_bot",
                    passed=False,
                    issues=["Missing README.md"],
                )
            ],
        )
        text = r.to_text()
        assert "FAILED" in text
        assert "bad_bot" in text


# ---------------------------------------------------------------------------
# RepoValidationBot class
# ---------------------------------------------------------------------------


class TestRepoValidationBot:
    def test_run_returns_report(self, tmp_path):
        root = tmp_path / "repo"
        root.mkdir()
        bot = RepoValidationBot(repo_root=str(root))
        report = bot.run()
        assert isinstance(report, ValidationReport)

    def test_run_detects_valid_bot(self, tmp_path):
        root = tmp_path / "repo"
        root.mkdir()
        bot_dir = root / "my_bot"
        bot_dir.mkdir()
        (bot_dir / "main.py").write_text("print('hi')\n")
        (bot_dir / "README.md").write_text("# Bot\n")
        (bot_dir / "__init__.py").write_text("")
        bot = RepoValidationBot(repo_root=str(root))
        report = bot.run()
        assert report.total == 1
        assert report.passed == 1
