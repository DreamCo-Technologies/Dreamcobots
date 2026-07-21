"""DreamCo CI Auto-Fix Bot.

Detects, diagnoses, and fixes GitHub Actions CI failures automatically.
Supports: npm errors, missing modules, permission issues, path errors, and pip install errors.
Logs all applied fixes for documentation and escalates unknown errors for human review.
"""
import os
import re
import sys
from datetime import datetime, timezone
from enum import Enum

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

# GlobalAISourcesFlow is imported for framework compliance registration side-effects
# (required by all DreamCo bots — see tools/check_bot_framework.py).
from framework import GlobalAISourcesFlow  # noqa: F401


class FixType(str, Enum):
    """Enumeration of fix types the bot can apply."""
    INSTALL_DEPS = "install-deps"
    MISSING_MODULE = "missing-module"
    PERMISSIONS = "permissions"
    PATH = "path"
    PIP_INSTALL = "pip-install"
    PYTHON_FORMAT = "python-format"
    JAVA_FORMAT = "java-format"
    JS_FORMAT = "js-format"
    UNKNOWN = "unknown"


# Error pattern → fix type mapping (checked in priority order, first match wins)
_ERROR_PATTERNS: list[tuple[re.Pattern, FixType]] = [
    (re.compile(r"npm ERR!", re.IGNORECASE), FixType.INSTALL_DEPS),
    (re.compile(r"Module not found|Cannot find module", re.IGNORECASE), FixType.MISSING_MODULE),
    (re.compile(r"ModuleNotFoundError|ImportError", re.IGNORECASE), FixType.MISSING_MODULE),
    (re.compile(r"Permission denied|EACCES|exit code 128", re.IGNORECASE), FixType.PERMISSIONS),
    (re.compile(r"No such file or directory|pathspec.*did not match|ENOENT", re.IGNORECASE), FixType.PATH),
    (re.compile(r"pip install|requirements\.txt.*not found", re.IGNORECASE), FixType.PIP_INSTALL),
    # Lint / format failures (checked after dependency errors so those take priority)
    # Java pattern checked before Python to prevent "reformatted" in gjf output matching Python rule
    (re.compile(r"google-java-format|checkstyle.*violation|checkstyle.*error|Checkstyle", re.IGNORECASE),
     FixType.JAVA_FORMAT),
    (re.compile(r"would reformat|reformatted|black.*--check|flake8.*error|E[0-9]{3}\b", re.IGNORECASE),
     FixType.PYTHON_FORMAT),
    (re.compile(r"prettier.*--check|eslint.*error|[0-9]+ problems? \(", re.IGNORECASE),
     FixType.JS_FORMAT),
]

# Shell commands applied for each fix type
_FIX_COMMANDS: dict[FixType, list[str]] = {
    FixType.INSTALL_DEPS: [
        "npm cache clean --force",
        "npm install",
    ],
    FixType.MISSING_MODULE: [
        "npm install",
    ],
    FixType.PERMISSIONS: [
        "git config --global --add safe.directory '*'",
        "chmod -R 755 .",
    ],
    FixType.PATH: [
        "ls -la",
    ],
    FixType.PIP_INSTALL: [
        "pip install --upgrade pip",
        "pip install -r requirements.txt",
    ],
    FixType.PYTHON_FORMAT: [
        "pip install black flake8",
        "black python_bots/ || true",
        "flake8 python_bots/ --max-line-length=120 --ignore=W503 --statistics || true",
    ],
    FixType.JAVA_FORMAT: [
        "java -jar ~/.cache/gjf/google-java-format-all-deps.jar --replace $(find java_bots -name '*.java') || true",
    ],
    FixType.JS_FORMAT: [
        "npx prettier --write '**/*.{js,ts,jsx,tsx}' || true",
        "npx eslint --fix '**/*.{js,ts}' || true",
    ],
    FixType.UNKNOWN: [],
}

_FIX_DESCRIPTIONS: dict[FixType, str] = {
    FixType.INSTALL_DEPS: "npm install error — cleared cache and reinstalled dependencies",
    FixType.MISSING_MODULE: "Missing module — reinstalled npm dependencies",
    FixType.PERMISSIONS: "Permission error — set safe directory and fixed file permissions",
    FixType.PATH: "Path/file not found — inspected build paths",
    FixType.PIP_INSTALL: "Python dependency error — upgraded pip and reinstalled requirements",
    FixType.PYTHON_FORMAT: "Python format/lint error — auto-formatted with black and checked with flake8",
    FixType.JAVA_FORMAT: "Java format error — auto-formatted with google-java-format",
    FixType.JS_FORMAT: "JS/TS format/lint error — auto-formatted with Prettier and fixed with ESLint",
    FixType.UNKNOWN: "Unknown error — escalated to human review",
}


class CIAutoFixBot:
    """Autonomous CI failure detection, diagnosis, and repair bot for DreamCo workflows.

    Usage::

        bot = CIAutoFixBot()
        fix = bot.analyze_logs(log_text)
        result = bot.apply_fix(fix)
        bot.log_fix(fix, run_id="123456")
    """

    def __init__(self, log_dir: str = "logs/ci-fixes"):
        self._log_dir = log_dir
        self._fix_history: list[dict] = []

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def analyze_logs(self, log_content: str) -> FixType:
        """Scan *log_content* for known error patterns and return the matching FixType.

        Patterns are checked in priority order; the first match wins.
        Returns ``FixType.UNKNOWN`` when no pattern matches.
        """
        for pattern, fix_type in _ERROR_PATTERNS:
            if pattern.search(log_content):
                return fix_type
        return FixType.UNKNOWN

    def detect_failure_type(self, log_content: str) -> dict:
        """Return a structured diagnosis dict describing the detected failure."""
        fix_type = self.analyze_logs(log_content)
        return {
            "fix_type": fix_type,
            "description": _FIX_DESCRIPTIONS[fix_type],
            "requires_escalation": fix_type == FixType.UNKNOWN,
            "commands": _FIX_COMMANDS[fix_type],
        }

    # ------------------------------------------------------------------
    # Fix Application
    # ------------------------------------------------------------------

    def get_fix_commands(self, fix_type: FixType) -> list[str]:
        """Return the shell commands that implement *fix_type*."""
        return list(_FIX_COMMANDS.get(fix_type, []))

    def apply_fix(self, fix_type: FixType) -> dict:
        """Return the fix result metadata (does not execute shell commands directly).

        Shell execution is delegated to the GitHub Actions workflow so the bot
        remains testable without a live runner environment.
        """
        commands = self.get_fix_commands(fix_type)
        escalate = fix_type == FixType.UNKNOWN
        return {
            "fix_type": fix_type,
            "description": _FIX_DESCRIPTIONS[fix_type],
            "commands": commands,
            "escalate": escalate,
            "applied_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Commit & Re-trigger helpers (return command strings for the workflow)
    # ------------------------------------------------------------------

    def get_commit_commands(self, fix_type: FixType) -> list[str]:
        """Return git commands to commit the applied fix."""
        description = _FIX_DESCRIPTIONS[fix_type]
        return [
            'git config --global user.name "dreamco-bot"',
            'git config --global user.email "bot@dreamco.ai"',
            "git add .",
            f'git diff --cached --quiet || git commit -m "🤖 Auto-fix applied: {fix_type} — {description}"',
            "git push || echo 'No changes to push'",
        ]

    def get_retrigger_command(self, workflow_name: str) -> str:
        """Return the GitHub CLI command to re-trigger *workflow_name*."""
        return f'gh workflow run "{workflow_name}" || echo "Could not re-trigger workflow"'

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log_fix(self, fix_type: FixType, run_id: str = "", workflow_name: str = "") -> str:
        """Append a line to the fix-history log and return the log entry string."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = (
            f"{timestamp} | Run ID: {run_id} | Workflow: {workflow_name} | "
            f"Fix: {fix_type} | {_FIX_DESCRIPTIONS[fix_type]}"
        )
        self._fix_history.append({
            "timestamp": timestamp,
            "run_id": run_id,
            "workflow_name": workflow_name,
            "fix_type": fix_type,
            "description": _FIX_DESCRIPTIONS[fix_type],
        })
        os.makedirs(self._log_dir, exist_ok=True)
        log_path = os.path.join(self._log_dir, "fix-history.log")
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(entry + "\n")
        return entry

    def get_fix_history(self) -> list[dict]:
        """Return a copy of the in-memory fix history."""
        return list(self._fix_history)

    # ------------------------------------------------------------------
    # Escalation
    # ------------------------------------------------------------------

    def escalate(self, run_id: str, workflow_name: str, html_url: str = "") -> dict:
        """Return an escalation report for unknown/unhandled failures."""
        return {
            "escalated": True,
            "run_id": run_id,
            "workflow_name": workflow_name,
            "html_url": html_url,
            "message": (
                f"Unknown CI failure detected in workflow '{workflow_name}' "
                f"(Run #{run_id}). Manual review required."
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Convenience: full auto-fix pipeline (returns action plan)
    # ------------------------------------------------------------------

    def run(self, log_content: str, run_id: str = "", workflow_name: str = "",
            html_url: str = "") -> dict:
        """Run the complete auto-fix pipeline and return an action plan dict.

        This method does not execute shell commands; it returns the commands
        to be executed by the GitHub Actions workflow step.
        """
        fix_type = self.analyze_logs(log_content)
        result = self.apply_fix(fix_type)
        log_entry = self.log_fix(fix_type, run_id=run_id, workflow_name=workflow_name)

        plan: dict = {
            "fix_type": fix_type,
            "description": _FIX_DESCRIPTIONS[fix_type],
            "fix_commands": result["commands"],
            "log_entry": log_entry,
            "escalate": fix_type == FixType.UNKNOWN,
        }

        if fix_type != FixType.UNKNOWN:
            plan["commit_commands"] = self.get_commit_commands(fix_type)
            plan["retrigger_command"] = self.get_retrigger_command(workflow_name)
        else:
            plan["escalation"] = self.escalate(run_id, workflow_name, html_url)

        return plan
