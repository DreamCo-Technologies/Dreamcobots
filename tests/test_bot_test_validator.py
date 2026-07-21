"""
Tests for tools/bot_test_validator.py
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Make tools/ importable from any working directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from bot_test_validator import (  # noqa: E402
    BotTestValidator,
    TestResult,
    ValidationReport,
    _suggest_fixes,
    IGNORED_TESTS,
)


# ---------------------------------------------------------------------------
# _suggest_fixes
# ---------------------------------------------------------------------------


class TestSuggestFixes:
    def test_module_not_found_suggests_pip(self):
        suggestions = _suggest_fixes("ModuleNotFoundError: No module named 'stripe'")
        assert any("pip install" in s for s in suggestions)

    def test_import_error_suggests_pip(self):
        suggestions = _suggest_fixes("ImportError: cannot import name 'Foo'")
        assert any("pip install" in s for s in suggestions)

    def test_no_module_named_suggests_path_check(self):
        suggestions = _suggest_fixes("No module named 'dreamco.core'")
        assert any("requirements.txt" in s for s in suggestions)

    def test_assertion_error_suggestion(self):
        suggestions = _suggest_fixes("AssertionError: assert 1 == 2")
        assert any("assertion" in s.lower() for s in suggestions)

    def test_attribute_error_suggestion(self):
        suggestions = _suggest_fixes("AttributeError: 'NoneType' object has no attribute 'run'")
        assert any("attribute" in s.lower() or "class" in s.lower() for s in suggestions)

    def test_type_error_suggestion(self):
        suggestions = _suggest_fixes("TypeError: foo() takes 1 positional argument but 2 were given")
        assert any("argument" in s.lower() or "type" in s.lower() for s in suggestions)

    def test_file_not_found_suggestion(self):
        suggestions = _suggest_fixes("FileNotFoundError: [Errno 2] No such file or directory: 'config.json'")
        assert any("file" in s.lower() for s in suggestions)

    def test_connection_error_suggestion(self):
        suggestions = _suggest_fixes("ConnectionError: failed to establish a new connection")
        assert any("mock" in s.lower() for s in suggestions)

    def test_unknown_error_returns_generic_advice(self):
        suggestions = _suggest_fixes("some completely unknown error XYZ")
        assert len(suggestions) >= 1
        assert any("pytest" in s.lower() or "review" in s.lower() for s in suggestions)

    def test_returns_list(self):
        assert isinstance(_suggest_fixes("anything"), list)


# ---------------------------------------------------------------------------
# TestResult
# ---------------------------------------------------------------------------


class TestTestResult:
    def test_passed_result(self):
        r = TestResult("test_foo.py", passed=True, exit_code=0, stdout="1 passed", stderr="", duration=0.5)
        assert r.passed is True
        assert r.exit_code == 0

    def test_failed_result(self):
        r = TestResult("test_bar.py", passed=False, exit_code=1, stdout="FAILED", stderr="", duration=0.8)
        assert r.passed is False

    def test_to_dict_contains_required_keys(self):
        r = TestResult("test_foo.py", True, 0, "ok", "", 1.23)
        d = r.to_dict()
        for key in ("test_file", "passed", "exit_code", "stdout", "stderr",
                    "duration_seconds", "retry_count", "timestamp"):
            assert key in d

    def test_to_dict_truncates_long_stdout(self):
        long_output = "x" * 5000
        r = TestResult("t.py", True, 0, long_output, "", 1.0)
        assert len(r.to_dict()["stdout"]) <= 2000

    def test_to_dict_truncates_long_stderr(self):
        long_err = "e" * 3000
        r = TestResult("t.py", False, 1, "", long_err, 1.0)
        assert len(r.to_dict()["stderr"]) <= 1000

    def test_retry_count_stored(self):
        r = TestResult("t.py", True, 0, "", "", 1.0, retry_count=2)
        assert r.to_dict()["retry_count"] == 2


# ---------------------------------------------------------------------------
# ValidationReport
# ---------------------------------------------------------------------------


class TestValidationReport:
    def _make_report(self, pass_count: int = 0, fail_count: int = 0) -> ValidationReport:
        results = (
            [TestResult(f"test_p{i}.py", True, 0, "", "", 0.1) for i in range(pass_count)]
            + [TestResult(f"test_f{i}.py", False, 1, "FAILED", "", 0.2) for i in range(fail_count)]
        )
        return ValidationReport(results)

    def test_all_passed_when_empty(self):
        report = ValidationReport([])
        assert report.all_passed is True
        assert report.total == 0

    def test_passed_count(self):
        report = self._make_report(pass_count=3, fail_count=1)
        assert report.passed_count == 3

    def test_failed_count(self):
        report = self._make_report(pass_count=2, fail_count=2)
        assert report.failed_count == 2

    def test_all_passed_true_when_no_failures(self):
        report = self._make_report(pass_count=5)
        assert report.all_passed is True

    def test_all_passed_false_when_failures(self):
        report = self._make_report(pass_count=3, fail_count=1)
        assert report.all_passed is False

    def test_failed_results_only_failures(self):
        report = self._make_report(pass_count=2, fail_count=2)
        assert all(not r.passed for r in report.failed_results())
        assert len(report.failed_results()) == 2

    def test_to_dict_contains_required_keys(self):
        report = self._make_report(pass_count=1)
        d = report.to_dict()
        for key in ("timestamp", "total", "passed", "failed", "all_passed", "results"):
            assert key in d

    def test_to_dict_results_list(self):
        report = self._make_report(pass_count=2, fail_count=1)
        assert len(report.to_dict()["results"]) == 3

    def test_to_markdown_contains_header(self):
        report = self._make_report(pass_count=2)
        md = report.to_markdown()
        assert "Bot Test Validation Report" in md

    def test_to_markdown_contains_pass_status(self):
        report = self._make_report(pass_count=2)
        md = report.to_markdown()
        assert "ALL PASSED" in md

    def test_to_markdown_contains_fail_status(self):
        report = self._make_report(fail_count=1)
        md = report.to_markdown()
        assert "FAILED" in md

    def test_to_markdown_contains_failure_details(self):
        report = self._make_report(fail_count=1)
        md = report.to_markdown()
        assert "Failure Details" in md

    def test_to_markdown_skips_failure_section_when_all_pass(self):
        report = self._make_report(pass_count=3)
        md = report.to_markdown()
        assert "Failure Details" not in md


# ---------------------------------------------------------------------------
# BotTestValidator — discover_tests
# ---------------------------------------------------------------------------


class TestDiscoverTests:
    def test_discovers_test_files(self, tmp_path):
        (tmp_path / "test_foo.py").write_text("# foo")
        (tmp_path / "test_bar.py").write_text("# bar")
        (tmp_path / "helper.py").write_text("# helper")
        v = BotTestValidator(tests_dir=str(tmp_path))
        found = v.discover_tests()
        names = [f.name for f in found]
        assert "test_foo.py" in names
        assert "test_bar.py" in names
        assert "helper.py" not in names

    def test_ignores_excluded_tests(self, tmp_path):
        for name in IGNORED_TESTS:
            (tmp_path / name).write_text("# ignored")
        (tmp_path / "test_valid.py").write_text("# valid")
        v = BotTestValidator(tests_dir=str(tmp_path))
        found = v.discover_tests()
        names = [f.name for f in found]
        for name in IGNORED_TESTS:
            assert name not in names
        assert "test_valid.py" in names

    def test_bot_pattern_filters_results(self, tmp_path):
        (tmp_path / "test_mining_bot.py").write_text("# mining")
        (tmp_path / "test_sales_bot.py").write_text("# sales")
        (tmp_path / "test_other.py").write_text("# other")
        v = BotTestValidator(tests_dir=str(tmp_path), bot_pattern="mining_bot")
        found = v.discover_tests()
        assert len(found) == 1
        assert found[0].name == "test_mining_bot.py"

    def test_empty_dir_returns_empty_list(self, tmp_path):
        v = BotTestValidator(tests_dir=str(tmp_path))
        assert v.discover_tests() == []

    def test_nonexistent_dir_returns_empty_list(self, tmp_path):
        v = BotTestValidator(tests_dir=str(tmp_path / "no_such_dir"))
        assert v.discover_tests() == []

    def test_results_are_sorted(self, tmp_path):
        for name in ("test_z.py", "test_a.py", "test_m.py"):
            (tmp_path / name).write_text("")
        v = BotTestValidator(tests_dir=str(tmp_path))
        found = [f.name for f in v.discover_tests()]
        assert found == sorted(found)


# ---------------------------------------------------------------------------
# BotTestValidator — run_test_file
# ---------------------------------------------------------------------------


class TestRunTestFile:
    def test_passing_test_returns_passed_true(self, tmp_path):
        test_file = tmp_path / "test_simple.py"
        test_file.write_text("def test_ok():\n    assert 1 == 1\n")
        v = BotTestValidator(max_retries=0)
        result = v.run_test_file(test_file)
        assert result.passed is True
        assert result.exit_code == 0

    def test_failing_test_returns_passed_false(self, tmp_path):
        test_file = tmp_path / "test_bad.py"
        test_file.write_text("def test_fail():\n    assert 1 == 2\n")
        v = BotTestValidator(max_retries=0)
        result = v.run_test_file(test_file)
        assert result.passed is False
        assert result.exit_code != 0

    def test_retry_count_recorded_on_failure(self, tmp_path):
        test_file = tmp_path / "test_retry.py"
        test_file.write_text("def test_fail():\n    assert False\n")
        v = BotTestValidator(max_retries=1)
        result = v.run_test_file(test_file)
        assert result.retry_count >= 1

    def test_timeout_recorded_as_failure(self, tmp_path):
        test_file = tmp_path / "test_to.py"
        test_file.write_text("def test_hang():\n    pass\n")
        v = BotTestValidator(max_retries=0)
        with patch("subprocess.run", side_effect=__import__("subprocess").TimeoutExpired(cmd="pytest", timeout=1)):
            result = v.run_test_file(test_file)
        assert result.passed is False
        assert "timed out" in result.stderr.lower()

    def test_duration_is_positive(self, tmp_path):
        test_file = tmp_path / "test_dur.py"
        test_file.write_text("def test_ok():\n    assert True\n")
        v = BotTestValidator(max_retries=0)
        result = v.run_test_file(test_file)
        assert result.duration > 0


# ---------------------------------------------------------------------------
# BotTestValidator — run_all
# ---------------------------------------------------------------------------


class TestRunAll:
    def test_empty_tests_dir_returns_empty_report(self, tmp_path):
        v = BotTestValidator(tests_dir=str(tmp_path))
        report = v.run_all()
        assert report.total == 0
        assert report.all_passed is True

    def test_all_pass_report(self, tmp_path):
        for i in range(3):
            (tmp_path / f"test_bot{i}.py").write_text("def test_ok():\n    assert True\n")
        v = BotTestValidator(tests_dir=str(tmp_path), max_retries=0)
        report = v.run_all()
        assert report.total == 3
        assert report.all_passed is True

    def test_failure_captured_in_report(self, tmp_path):
        (tmp_path / "test_good.py").write_text("def test_ok():\n    assert True\n")
        (tmp_path / "test_bad.py").write_text("def test_fail():\n    assert False\n")
        v = BotTestValidator(tests_dir=str(tmp_path), max_retries=0)
        report = v.run_all()
        assert report.failed_count == 1
        assert report.passed_count == 1
        assert not report.all_passed

    def test_fail_fast_stops_on_first_failure(self, tmp_path):
        for i in range(5):
            (tmp_path / f"test_bot{i}.py").write_text(
                "def test_fail():\n    assert False\n"
            )
        v = BotTestValidator(tests_dir=str(tmp_path), max_retries=0, fail_fast=True)
        report = v.run_all()
        # With fail_fast only 1 test should have been attempted
        assert report.total == 1

    def test_log_file_written(self, tmp_path):
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_ok.py").write_text("def test_ok():\n    assert True\n")
        log = tmp_path / "out.log"
        v = BotTestValidator(
            tests_dir=str(tmp_path / "tests"),
            log_file=str(log),
            max_retries=0,
        )
        v.run_all()
        assert log.exists()
        data = json.loads(log.read_text().strip())
        assert "results" in data

    def test_log_file_is_valid_json(self, tmp_path):
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_x.py").write_text("def test_x():\n    pass\n")
        log = tmp_path / "v.log"
        v = BotTestValidator(
            tests_dir=str(tmp_path / "tests"),
            log_file=str(log),
            max_retries=0,
        )
        v.run_all()
        parsed = json.loads(log.read_text().strip())
        assert isinstance(parsed, dict)
        assert "timestamp" in parsed


# ---------------------------------------------------------------------------
# main() CLI
# ---------------------------------------------------------------------------


class TestMain:
    def test_returns_zero_when_all_pass(self, tmp_path):
        from bot_test_validator import main

        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_ok.py").write_text("def test_ok():\n    assert True\n")
        log = tmp_path / "run.log"

        exit_code = main([
            "--tests-dir", str(tests),
            "--log-file", str(log),
            "--max-retries", "0",
        ])
        assert exit_code == 0

    def test_returns_one_when_failures(self, tmp_path):
        from bot_test_validator import main

        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_fail.py").write_text("def test_fail():\n    assert False\n")
        log = tmp_path / "run.log"

        exit_code = main([
            "--tests-dir", str(tests),
            "--log-file", str(log),
            "--max-retries", "0",
        ])
        assert exit_code == 1

    def test_bot_pattern_flag(self, tmp_path):
        from bot_test_validator import main

        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_mining_bot.py").write_text("def test_ok():\n    assert True\n")
        (tests / "test_sales_bot.py").write_text("def test_fail():\n    assert False\n")
        log = tmp_path / "run.log"

        # Only running mining_bot should pass
        exit_code = main([
            "--tests-dir", str(tests),
            "--log-file", str(log),
            "--max-retries", "0",
            "--bot", "mining_bot",
        ])
        assert exit_code == 0

    def test_report_file_written(self, tmp_path):
        from bot_test_validator import main

        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_ok.py").write_text("def test_ok():\n    assert True\n")
        report = tmp_path / "report.md"
        log = tmp_path / "run.log"

        main([
            "--tests-dir", str(tests),
            "--log-file", str(log),
            "--report", str(report),
            "--max-retries", "0",
        ])
        assert report.exists()
        assert "Bot Test Validation Report" in report.read_text()
