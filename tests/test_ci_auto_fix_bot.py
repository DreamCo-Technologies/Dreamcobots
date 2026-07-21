"""Tests for bots/ci_auto_fix_bot/ci_auto_fix_bot.py"""
import os
import sys
import tempfile

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.ci_auto_fix_bot.ci_auto_fix_bot import CIAutoFixBot, FixType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_bot(tmp_path=None) -> CIAutoFixBot:
    log_dir = str(tmp_path) if tmp_path else tempfile.mkdtemp()
    return CIAutoFixBot(log_dir=log_dir)


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestInstantiation:
    def test_instantiates(self):
        bot = CIAutoFixBot()
        assert bot is not None

    def test_default_log_dir(self):
        bot = CIAutoFixBot()
        assert bot._log_dir == "logs/ci-fixes"

    def test_custom_log_dir(self, tmp_path):
        bot = CIAutoFixBot(log_dir=str(tmp_path))
        assert bot._log_dir == str(tmp_path)

    def test_starts_with_empty_history(self):
        bot = CIAutoFixBot()
        assert bot.get_fix_history() == []


# ---------------------------------------------------------------------------
# analyze_logs
# ---------------------------------------------------------------------------

class TestAnalyzeLogs:
    def test_npm_error_detected(self):
        bot = CIAutoFixBot()
        log = "npm ERR! 404 tarball not found\nnpm ERR! code E404"
        assert bot.analyze_logs(log) == FixType.INSTALL_DEPS

    def test_npm_error_case_insensitive(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("NPM ERR! something") == FixType.INSTALL_DEPS

    def test_module_not_found(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("Module not found: Error: Can't resolve 'express'") == FixType.MISSING_MODULE

    def test_cannot_find_module(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("Cannot find module './config'") == FixType.MISSING_MODULE

    def test_python_module_not_found(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("ModuleNotFoundError: No module named 'stripe'") == FixType.MISSING_MODULE

    def test_import_error(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("ImportError: cannot import name 'foo'") == FixType.MISSING_MODULE

    def test_permission_denied(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("Permission denied: '/usr/bin/node'") == FixType.PERMISSIONS

    def test_eacces_error(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("EACCES: permission denied, access '/root'") == FixType.PERMISSIONS

    def test_exit_code_128(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("fatal: exit code 128") == FixType.PERMISSIONS

    def test_no_such_file(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("No such file or directory: 'dist/index.js'") == FixType.PATH

    def test_enoent(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("ENOENT: no such file or directory, open 'package.json'") == FixType.PATH

    def test_pathspec_error(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("error: pathspec 'main' did not match any file(s)") == FixType.PATH

    def test_pip_install_error(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("pip install failed for requirements.txt not found") == FixType.PIP_INSTALL

    def test_python_format_black_error(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("would reformat bots/my_bot.py\nblack --check python_bots/ failed") == FixType.PYTHON_FORMAT

    def test_python_format_black_check(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("Oh no! black --check found formatting issues") == FixType.PYTHON_FORMAT

    def test_java_format_gjf_error(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("google-java-format: 3 files would be reformatted") == FixType.JAVA_FORMAT

    def test_java_format_checkstyle_error(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("Checkstyle violation: line length > 100 in MyBot.java") == FixType.JAVA_FORMAT

    def test_js_format_prettier_check(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("prettier --check failed: Code style issues found") == FixType.JS_FORMAT

    def test_js_format_eslint_error(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("eslint error: 5 problems (3 errors, 2 warnings)") == FixType.JS_FORMAT

    def test_unknown_error(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("Something completely different went wrong") == FixType.UNKNOWN

    def test_empty_log(self):
        bot = CIAutoFixBot()
        assert bot.analyze_logs("") == FixType.UNKNOWN

    def test_npm_error_takes_priority_over_path(self):
        # npm ERR! appears before No such file — npm pattern wins
        bot = CIAutoFixBot()
        log = "npm ERR! 404\nNo such file or directory"
        assert bot.analyze_logs(log) == FixType.INSTALL_DEPS

    def test_multiline_log(self):
        bot = CIAutoFixBot()
        log = "\n".join([
            "Step 1 passed",
            "Step 2 passed",
            "npm ERR! 404 Not Found - GET https://registry.npmjs.org/...",
            "npm ERR! code E404",
        ])
        assert bot.analyze_logs(log) == FixType.INSTALL_DEPS


# ---------------------------------------------------------------------------
# detect_failure_type
# ---------------------------------------------------------------------------

class TestDetectFailureType:
    def test_returns_dict(self):
        bot = CIAutoFixBot()
        result = bot.detect_failure_type("npm ERR! something")
        assert isinstance(result, dict)

    def test_keys_present(self):
        bot = CIAutoFixBot()
        result = bot.detect_failure_type("npm ERR! something")
        assert "fix_type" in result
        assert "description" in result
        assert "requires_escalation" in result
        assert "commands" in result

    def test_install_deps_not_escalated(self):
        bot = CIAutoFixBot()
        result = bot.detect_failure_type("npm ERR! 404")
        assert result["requires_escalation"] is False

    def test_unknown_requires_escalation(self):
        bot = CIAutoFixBot()
        result = bot.detect_failure_type("totally unknown error")
        assert result["requires_escalation"] is True

    def test_commands_are_list(self):
        bot = CIAutoFixBot()
        result = bot.detect_failure_type("npm ERR!")
        assert isinstance(result["commands"], list)
        assert len(result["commands"]) > 0

    def test_unknown_commands_empty(self):
        bot = CIAutoFixBot()
        result = bot.detect_failure_type("unknown gibberish")
        assert result["commands"] == []


# ---------------------------------------------------------------------------
# get_fix_commands
# ---------------------------------------------------------------------------

class TestGetFixCommands:
    def test_install_deps_commands(self):
        bot = CIAutoFixBot()
        cmds = bot.get_fix_commands(FixType.INSTALL_DEPS)
        assert any("npm" in c for c in cmds)

    def test_missing_module_commands(self):
        bot = CIAutoFixBot()
        cmds = bot.get_fix_commands(FixType.MISSING_MODULE)
        assert any("npm install" in c for c in cmds)

    def test_permissions_commands(self):
        bot = CIAutoFixBot()
        cmds = bot.get_fix_commands(FixType.PERMISSIONS)
        assert any("safe.directory" in c for c in cmds)

    def test_path_commands(self):
        bot = CIAutoFixBot()
        cmds = bot.get_fix_commands(FixType.PATH)
        assert len(cmds) > 0

    def test_pip_install_commands(self):
        bot = CIAutoFixBot()
        cmds = bot.get_fix_commands(FixType.PIP_INSTALL)
        assert any("pip" in c for c in cmds)
        assert any("requirements" in c for c in cmds)

    def test_python_format_commands(self):
        bot = CIAutoFixBot()
        cmds = bot.get_fix_commands(FixType.PYTHON_FORMAT)
        assert any("black" in c for c in cmds)

    def test_java_format_commands(self):
        bot = CIAutoFixBot()
        cmds = bot.get_fix_commands(FixType.JAVA_FORMAT)
        assert any("google-java-format" in c for c in cmds)

    def test_js_format_commands(self):
        bot = CIAutoFixBot()
        cmds = bot.get_fix_commands(FixType.JS_FORMAT)
        assert any("prettier" in c for c in cmds)

    def test_unknown_returns_empty(self):
        bot = CIAutoFixBot()
        cmds = bot.get_fix_commands(FixType.UNKNOWN)
        assert cmds == []

    def test_returns_copy(self):
        bot = CIAutoFixBot()
        cmds1 = bot.get_fix_commands(FixType.INSTALL_DEPS)
        cmds2 = bot.get_fix_commands(FixType.INSTALL_DEPS)
        assert cmds1 == cmds2
        cmds1.clear()
        assert len(bot.get_fix_commands(FixType.INSTALL_DEPS)) > 0


# ---------------------------------------------------------------------------
# apply_fix
# ---------------------------------------------------------------------------

class TestApplyFix:
    def test_returns_dict(self):
        bot = CIAutoFixBot()
        result = bot.apply_fix(FixType.INSTALL_DEPS)
        assert isinstance(result, dict)

    def test_required_keys(self):
        bot = CIAutoFixBot()
        result = bot.apply_fix(FixType.INSTALL_DEPS)
        for key in ("fix_type", "description", "commands", "escalate", "applied_at"):
            assert key in result

    def test_not_escalated_for_known_fix(self):
        bot = CIAutoFixBot()
        result = bot.apply_fix(FixType.INSTALL_DEPS)
        assert result["escalate"] is False

    def test_escalated_for_unknown(self):
        bot = CIAutoFixBot()
        result = bot.apply_fix(FixType.UNKNOWN)
        assert result["escalate"] is True

    def test_applied_at_is_iso(self):
        bot = CIAutoFixBot()
        result = bot.apply_fix(FixType.INSTALL_DEPS)
        assert "T" in result["applied_at"]  # ISO 8601 format

    @pytest.mark.parametrize("fix_type", list(FixType))
    def test_all_fix_types_handled(self, fix_type):
        bot = CIAutoFixBot()
        result = bot.apply_fix(fix_type)
        assert result["fix_type"] == fix_type


# ---------------------------------------------------------------------------
# get_commit_commands
# ---------------------------------------------------------------------------

class TestGetCommitCommands:
    def test_returns_list(self):
        bot = CIAutoFixBot()
        cmds = bot.get_commit_commands(FixType.INSTALL_DEPS)
        assert isinstance(cmds, list)
        assert len(cmds) > 0

    def test_contains_git_config(self):
        bot = CIAutoFixBot()
        cmds = bot.get_commit_commands(FixType.INSTALL_DEPS)
        assert any("git config" in c for c in cmds)

    def test_contains_dreamco_bot_email(self):
        bot = CIAutoFixBot()
        cmds = bot.get_commit_commands(FixType.INSTALL_DEPS)
        assert any("bot@dreamco.ai" in c for c in cmds)

    def test_contains_git_push(self):
        bot = CIAutoFixBot()
        cmds = bot.get_commit_commands(FixType.INSTALL_DEPS)
        assert any("git push" in c for c in cmds)

    def test_commit_message_includes_fix_type(self):
        bot = CIAutoFixBot()
        cmds = bot.get_commit_commands(FixType.PERMISSIONS)
        commit_line = next(c for c in cmds if "commit -m" in c)
        assert "permissions" in commit_line


# ---------------------------------------------------------------------------
# get_retrigger_command
# ---------------------------------------------------------------------------

class TestGetRetriggerCommand:
    def test_returns_string(self):
        bot = CIAutoFixBot()
        cmd = bot.get_retrigger_command("My Workflow")
        assert isinstance(cmd, str)

    def test_includes_workflow_name(self):
        bot = CIAutoFixBot()
        cmd = bot.get_retrigger_command("CI/CD Workflow")
        assert "CI/CD Workflow" in cmd

    def test_uses_gh_cli(self):
        bot = CIAutoFixBot()
        cmd = bot.get_retrigger_command("CI")
        assert cmd.startswith("gh workflow run")


# ---------------------------------------------------------------------------
# log_fix
# ---------------------------------------------------------------------------

class TestLogFix:
    def test_returns_string(self, tmp_path):
        bot = make_bot(tmp_path)
        entry = bot.log_fix(FixType.INSTALL_DEPS, run_id="123", workflow_name="CI")
        assert isinstance(entry, str)

    def test_entry_contains_run_id(self, tmp_path):
        bot = make_bot(tmp_path)
        entry = bot.log_fix(FixType.INSTALL_DEPS, run_id="99999")
        assert "99999" in entry

    def test_entry_contains_fix_type(self, tmp_path):
        bot = make_bot(tmp_path)
        entry = bot.log_fix(FixType.PERMISSIONS, run_id="1")
        assert "permissions" in entry

    def test_entry_contains_workflow_name(self, tmp_path):
        bot = make_bot(tmp_path)
        entry = bot.log_fix(FixType.PATH, workflow_name="Auto Recovery CI Mechanism")
        assert "Auto Recovery CI Mechanism" in entry

    def test_log_file_created(self, tmp_path):
        bot = make_bot(tmp_path)
        bot.log_fix(FixType.INSTALL_DEPS)
        log_path = tmp_path / "fix-history.log"
        assert log_path.exists()

    def test_log_file_content(self, tmp_path):
        bot = make_bot(tmp_path)
        bot.log_fix(FixType.INSTALL_DEPS, run_id="555", workflow_name="CI/CD")
        log_path = tmp_path / "fix-history.log"
        content = log_path.read_text()
        assert "555" in content
        assert "CI/CD" in content

    def test_log_appends_multiple_entries(self, tmp_path):
        bot = make_bot(tmp_path)
        bot.log_fix(FixType.INSTALL_DEPS, run_id="1")
        bot.log_fix(FixType.PERMISSIONS, run_id="2")
        log_path = tmp_path / "fix-history.log"
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 2

    def test_fix_history_updated(self, tmp_path):
        bot = make_bot(tmp_path)
        bot.log_fix(FixType.PIP_INSTALL, run_id="10")
        history = bot.get_fix_history()
        assert len(history) == 1
        assert history[0]["fix_type"] == FixType.PIP_INSTALL
        assert history[0]["run_id"] == "10"


# ---------------------------------------------------------------------------
# get_fix_history
# ---------------------------------------------------------------------------

class TestGetFixHistory:
    def test_empty_initially(self):
        bot = CIAutoFixBot()
        assert bot.get_fix_history() == []

    def test_returns_copy(self, tmp_path):
        bot = make_bot(tmp_path)
        bot.log_fix(FixType.INSTALL_DEPS)
        h1 = bot.get_fix_history()
        h1.clear()
        assert len(bot.get_fix_history()) == 1


# ---------------------------------------------------------------------------
# escalate
# ---------------------------------------------------------------------------

class TestEscalate:
    def test_returns_dict(self):
        bot = CIAutoFixBot()
        result = bot.escalate("123", "CI/CD Workflow")
        assert isinstance(result, dict)

    def test_escalated_true(self):
        bot = CIAutoFixBot()
        result = bot.escalate("123", "CI/CD Workflow")
        assert result["escalated"] is True

    def test_contains_run_id(self):
        bot = CIAutoFixBot()
        result = bot.escalate("99999", "My Workflow")
        assert result["run_id"] == "99999"

    def test_contains_workflow_name(self):
        bot = CIAutoFixBot()
        result = bot.escalate("1", "My Workflow")
        assert result["workflow_name"] == "My Workflow"

    def test_message_mentions_manual_review(self):
        bot = CIAutoFixBot()
        result = bot.escalate("1", "CI")
        assert "manual review" in result["message"].lower()

    def test_html_url_stored(self):
        bot = CIAutoFixBot()
        result = bot.escalate("1", "CI", html_url="https://github.com/x/y/actions/runs/1")
        assert result["html_url"] == "https://github.com/x/y/actions/runs/1"

    def test_timestamp_present(self):
        bot = CIAutoFixBot()
        result = bot.escalate("1", "CI")
        assert "timestamp" in result and result["timestamp"]


# ---------------------------------------------------------------------------
# run (full pipeline)
# ---------------------------------------------------------------------------

class TestRun:
    def test_returns_dict(self, tmp_path):
        bot = make_bot(tmp_path)
        result = bot.run("npm ERR! 404", run_id="1", workflow_name="CI/CD")
        assert isinstance(result, dict)

    def test_known_fix_returns_commit_commands(self, tmp_path):
        bot = make_bot(tmp_path)
        result = bot.run("npm ERR! 404", run_id="1", workflow_name="CI/CD")
        assert "commit_commands" in result
        assert "retrigger_command" in result

    def test_known_fix_no_escalation(self, tmp_path):
        bot = make_bot(tmp_path)
        result = bot.run("npm ERR! 404", run_id="1", workflow_name="CI/CD")
        assert result["escalate"] is False

    def test_unknown_fix_escalates(self, tmp_path):
        bot = make_bot(tmp_path)
        result = bot.run("something totally unrecognized", run_id="2", workflow_name="CI/CD")
        assert result["escalate"] is True
        assert "escalation" in result
        assert result["escalation"]["escalated"] is True

    def test_unknown_no_commit_commands(self, tmp_path):
        bot = make_bot(tmp_path)
        result = bot.run("something totally unrecognized")
        assert "commit_commands" not in result

    def test_log_entry_written(self, tmp_path):
        bot = make_bot(tmp_path)
        bot.run("npm ERR! 404", run_id="777", workflow_name="CI")
        assert len(bot.get_fix_history()) == 1

    def test_fix_commands_present(self, tmp_path):
        bot = make_bot(tmp_path)
        result = bot.run("npm ERR! something", run_id="1", workflow_name="CI")
        assert isinstance(result["fix_commands"], list)
        assert len(result["fix_commands"]) > 0

    def test_permissions_fix_applied(self, tmp_path):
        bot = make_bot(tmp_path)
        result = bot.run("Permission denied: cannot open file", run_id="5", workflow_name="CI")
        assert result["fix_type"] == FixType.PERMISSIONS

    def test_pip_fix_applied(self, tmp_path):
        bot = make_bot(tmp_path)
        result = bot.run("pip install -r requirements.txt not found", run_id="6", workflow_name="CI")
        assert result["fix_type"] == FixType.PIP_INSTALL

    def test_path_fix_applied(self, tmp_path):
        bot = make_bot(tmp_path)
        result = bot.run("No such file or directory: dist/app.js", run_id="7", workflow_name="CI")
        assert result["fix_type"] == FixType.PATH

    def test_missing_module_fix_applied(self, tmp_path):
        bot = make_bot(tmp_path)
        result = bot.run("Module not found: Error: Can't resolve './utils'", run_id="8", workflow_name="CI")
        assert result["fix_type"] == FixType.MISSING_MODULE

    def test_retrigger_contains_workflow_name(self, tmp_path):
        bot = make_bot(tmp_path)
        result = bot.run("npm ERR! 404", run_id="1", workflow_name="Auto Recovery")
        assert "Auto Recovery" in result["retrigger_command"]

    @pytest.mark.parametrize("log,expected_fix", [
        ("npm ERR! 404", FixType.INSTALL_DEPS),
        ("Module not found: foo", FixType.MISSING_MODULE),
        ("Permission denied: /etc/hosts", FixType.PERMISSIONS),
        ("No such file or directory: build/", FixType.PATH),
        ("pip install -r requirements.txt", FixType.PIP_INSTALL),
        ("would reformat python_bots/my_bot.py", FixType.PYTHON_FORMAT),
        ("google-java-format: file needs formatting", FixType.JAVA_FORMAT),
        ("prettier --check: Code style issues found", FixType.JS_FORMAT),
        ("completely unknown error xyz", FixType.UNKNOWN),
    ])
    def test_all_fix_types(self, tmp_path, log, expected_fix):
        bot = make_bot(tmp_path)
        result = bot.run(log, run_id="99", workflow_name="CI")
        assert result["fix_type"] == expected_fix
