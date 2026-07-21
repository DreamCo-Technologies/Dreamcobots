"""
Tests for tools/auto_recovery.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Make tools/ importable from any working directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import auto_recovery  # noqa: E402


# ---------------------------------------------------------------------------
# check_python_version
# ---------------------------------------------------------------------------

class TestCheckPythonVersion:
    def test_passes_with_current_interpreter(self):
        result = auto_recovery.check_python_version()
        # The CI already runs on Python 3.8+, so this must always pass
        assert result["status"] == "ok"
        assert result["check"] == "python_version"
        assert result["fix_applied"] is False

    def test_fails_when_version_too_old(self):
        with patch.object(sys, "version_info", (2, 7, 18, "final", 0)):
            result = auto_recovery.check_python_version()
        assert result["status"] == "fail"
        assert result["manual_action"] is not None

    def test_detail_contains_version_numbers(self):
        result = auto_recovery.check_python_version()
        assert str(sys.version_info.major) in result["detail"]
        assert str(sys.version_info.minor) in result["detail"]


# ---------------------------------------------------------------------------
# check_dependencies
# ---------------------------------------------------------------------------

class TestCheckDependencies:
    def test_skip_when_requirements_missing(self, tmp_path):
        result = auto_recovery.check_dependencies(tmp_path / "no_such_file.txt")
        assert result["status"] == "skip"

    def test_ok_when_pip_check_passes(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("pytest\n")
        with patch.object(auto_recovery, "_run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = auto_recovery.check_dependencies(req)
        assert result["status"] == "ok"
        assert result["fix_applied"] is False

    def test_fix_applied_when_pip_check_fails_but_install_succeeds(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("pytest\n")
        responses = [
            MagicMock(returncode=1, stdout="some conflict", stderr=""),
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        with patch.object(auto_recovery, "_run", side_effect=responses):
            result = auto_recovery.check_dependencies(req)
        assert result["status"] == "ok"
        assert result["fix_applied"] is True

    def test_fail_when_both_pip_check_and_install_fail(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("pytest\n")
        responses = [
            MagicMock(returncode=1, stdout="conflict", stderr=""),
            MagicMock(returncode=1, stdout="", stderr="install error"),
        ]
        with patch.object(auto_recovery, "_run", side_effect=responses):
            result = auto_recovery.check_dependencies(req)
        assert result["status"] == "fail"
        assert result["fix_applied"] is False
        assert result["manual_action"] is not None


# ---------------------------------------------------------------------------
# check_framework_compliance
# ---------------------------------------------------------------------------

class TestCheckFrameworkCompliance:
    def test_skip_when_checker_missing(self, tmp_path):
        result = auto_recovery.check_framework_compliance(tmp_path)
        assert result["status"] == "skip"

    def test_ok_when_checker_returns_zero(self):
        with patch.object(auto_recovery, "_run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="All compliant", stderr="")
            result = auto_recovery.check_framework_compliance(REPO_ROOT)
        assert result["status"] == "ok"
        assert result["manual_action"] is None

    def test_fail_when_checker_returns_nonzero(self):
        with patch.object(auto_recovery, "_run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="violations found", stderr="")
            result = auto_recovery.check_framework_compliance(REPO_ROOT)
        assert result["status"] == "fail"
        assert result["manual_action"] is not None

    def test_real_checker_passes(self):
        """Integration test: the real repo must be fully compliant."""
        result = auto_recovery.check_framework_compliance(REPO_ROOT)
        assert result["status"] == "ok", result["detail"]


# ---------------------------------------------------------------------------
# check_uncommitted_changes
# ---------------------------------------------------------------------------

class TestCheckUncommittedChanges:
    def test_ok_when_working_tree_clean(self, tmp_path):
        with patch.object(auto_recovery, "_run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = auto_recovery.check_uncommitted_changes(tmp_path)
        assert result["status"] == "ok"

    def test_warn_when_changes_present(self, tmp_path):
        dirty_output = " M some_file.py\n?? untracked.txt\n"
        with patch.object(auto_recovery, "_run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=dirty_output, stderr="")
            result = auto_recovery.check_uncommitted_changes(tmp_path)
        assert result["status"] == "warn"
        assert "2" in result["detail"]

    def test_warn_truncates_long_file_list(self, tmp_path):
        # 10 changed files — list should be truncated with "..."
        lines = "\n".join(f" M file{i}.py" for i in range(10))
        with patch.object(auto_recovery, "_run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=lines, stderr="")
            result = auto_recovery.check_uncommitted_changes(tmp_path)
        assert "..." in result["detail"]


# ---------------------------------------------------------------------------
# write_log
# ---------------------------------------------------------------------------

class TestWriteLog:
    def test_creates_log_file(self, tmp_path):
        log = tmp_path / "recovery.log"
        results = [{"check": "python_version", "status": "ok", "detail": "ok", "fix_applied": False, "manual_action": None}]
        auto_recovery.write_log(results, log)
        assert log.exists()

    def test_log_is_valid_json_lines(self, tmp_path):
        log = tmp_path / "recovery.log"
        results = [{"check": "python_version", "status": "ok", "detail": "ok", "fix_applied": False, "manual_action": None}]
        auto_recovery.write_log(results, log)
        entry = json.loads(log.read_text().strip())
        assert "timestamp" in entry
        assert "results" in entry
        assert entry["results"][0]["check"] == "python_version"

    def test_appends_multiple_entries(self, tmp_path):
        log = tmp_path / "recovery.log"
        results = [{"check": "python_version", "status": "ok", "detail": "ok", "fix_applied": False, "manual_action": None}]
        auto_recovery.write_log(results, log)
        auto_recovery.write_log(results, log)
        lines = [l for l in log.read_text().splitlines() if l.strip()]
        assert len(lines) == 2

    def test_creates_parent_dirs(self, tmp_path):
        log = tmp_path / "subdir" / "deep" / "recovery.log"
        results = []
        auto_recovery.write_log(results, log)
        assert log.exists()


# ---------------------------------------------------------------------------
# send_webhook
# ---------------------------------------------------------------------------

class TestSendWebhook:
    def test_posts_to_webhook_url(self):
        results = [{"check": "python_version", "status": "ok", "detail": "ok", "fix_applied": False, "manual_action": None}]
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            # Should not raise
            auto_recovery.send_webhook("https://example.com/hook", results)

    def test_handles_webhook_error_gracefully(self):
        import urllib.error
        results = []
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("connection refused")):
            # Should print a warning but not raise
            auto_recovery.send_webhook("https://bad.example.com/hook", results)


# ---------------------------------------------------------------------------
# main() end-to-end
# ---------------------------------------------------------------------------

class TestMain:
    def test_returns_zero_when_all_checks_pass(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("")
        log = tmp_path / "recovery.log"

        # Patch _run so all subprocess calls succeed
        with patch.object(auto_recovery, "_run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            exit_code = auto_recovery.main([
                "--repo-root", str(REPO_ROOT),
                "--requirements", str(req),
                "--log-file", str(log),
            ])
        assert exit_code == 0
        assert log.exists()

    def test_returns_one_on_unresolvable_failure(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("some_package\n")
        log = tmp_path / "recovery.log"

        # pip check fails, pip install also fails; framework check and git status succeed
        responses = [
            MagicMock(returncode=1, stdout="conflict", stderr=""),   # pip check
            MagicMock(returncode=1, stdout="", stderr="error"),       # pip install
            MagicMock(returncode=0, stdout="All compliant", stderr=""),  # check_bot_framework
            MagicMock(returncode=0, stdout="", stderr=""),            # git status
        ]
        with patch.object(auto_recovery, "_run", side_effect=responses):
            exit_code = auto_recovery.main([
                "--repo-root", str(REPO_ROOT),
                "--requirements", str(req),
                "--log-file", str(log),
            ])
        assert exit_code == 1
