"""
DreamCo Control Tower — Auto-Upgrader
=======================================
Automated upgrade engine for DreamCo bots.

The :class:`AutoUpgrader` coordinates:

1. Pulling the latest code from the upstream branch.
2. Resolving merge conflicts automatically (``-X theirs`` strategy).
3. Running optional test suites.
4. Opening an auto-update Pull Request via :class:`~repo_manager.RepoManager`.

All git operations are executed through a *command runner* abstraction so the
class is fully testable without a real git installation.
"""

from __future__ import annotations

import subprocess
import sys
import os
import re
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

# Allow running from any working directory
sys.path.insert(0, os.path.dirname(__file__))
from bot_manager import BotManager, STATUS_UPDATING, STATUS_ACTIVE, STATUS_CONFLICT
from repo_manager import RepoManager

_PR_TITLE = "🤖 Auto-upgrade from DreamCo Control Tower"
_PR_BRANCH = "auto-update"

# Branch names may only contain alphanumerics, hyphens, underscores, slashes, and dots.
_SAFE_BRANCH_RE = re.compile(r"^[a-zA-Z0-9._/-]{1,255}$")


def _validate_branch(branch: str) -> str:
    """Return *branch* if it is safe, otherwise raise ``ValueError``."""
    if not _SAFE_BRANCH_RE.match(branch):
        raise ValueError(f"Unsafe branch name rejected: {branch!r}")
    return branch


def _validate_repo_path(repo_path: str, repo_root: str) -> str:
    """Return the resolved *repo_path* if it is under *repo_root*, else raise ``ValueError``."""
    resolved = os.path.realpath(repo_path)
    root_resolved = os.path.realpath(repo_root)
    if not resolved.startswith(root_resolved + os.sep) and resolved != root_resolved:
        raise ValueError(f"Repo path '{resolved}' is outside the repo root '{root_resolved}'.")
    return resolved


# ---------------------------------------------------------------------------
# Default command runner (wraps subprocess)
# ---------------------------------------------------------------------------

def _default_runner(cmd: List[str], cwd: Optional[str] = None) -> "subprocess.CompletedProcess[str]":
    """Run *cmd* in *cwd* and return the CompletedProcess result."""
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# AutoUpgrader
# ---------------------------------------------------------------------------

class AutoUpgrader:
    """Orchestrates automated upgrades for all registered bots.

    Parameters
    ----------
    bot_manager:
        :class:`BotManager` instance used to look up bot metadata and update
        statuses.
    repo_manager:
        :class:`RepoManager` instance used to open PRs.
    repo_root:
        Filesystem path to the root of the cloned repository.  Bot
        ``repoPath`` values are resolved relative to this.
    run_tests:
        When *True* (default), attempt ``npm test`` / ``pytest`` in the bot
        directory before opening a PR.
    runner:
        Callable with the same signature as :func:`_default_runner`.  Override
        in tests to avoid real subprocess calls.
    """

    def __init__(
        self,
        bot_manager: BotManager,
        repo_manager: RepoManager,
        repo_root: str = "",
        run_tests: bool = True,
        runner: Optional[Callable] = None,
    ) -> None:
        self._bm = bot_manager
        self._rm = repo_manager
        self._repo_root = repo_root or os.getcwd()
        self._run_tests = run_tests
        self._runner = runner or _default_runner
        self._upgrade_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def upgrade_bot(self, name: str, branch: str = "main") -> Dict[str, Any]:
        """Run the full upgrade pipeline for a single bot.

        Steps
        -----
        1. Pull (rebase) from *branch*.
        2. On conflict, auto-resolve with ``-X theirs``.
        3. Optionally run tests.
        4. Open an auto-update PR.
        5. Update the bot registry.

        Returns
        -------
        dict
            ``{"bot": name, "status": "ok"|"conflict_resolved"|"error", ...}``
        """
        bot = self._bm.get_bot(name)
        if bot is None:
            return {"bot": name, "status": "error", "detail": "Bot not found in registry."}

        self._bm.set_status(name, STATUS_UPDATING)
        repo_path = os.path.join(self._repo_root, bot.get("repoPath", ""))
        result: Dict[str, Any] = {
            "bot": name,
            "repoPath": repo_path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Validate inputs before touching the filesystem
        try:
            repo_path = _validate_repo_path(repo_path, self._repo_root)
            branch = _validate_branch(branch)
        except ValueError as exc:
            self._bm.set_status(name, STATUS_ACTIVE)
            result["status"] = "error"
            result["detail"] = str(exc)
            self._upgrade_log.append(result)
            return result

        # 1. Pull
        pull_result = self._pull(repo_path, branch)
        result["pull"] = pull_result

        if pull_result["success"]:
            result["status"] = "ok"
        else:
            # 2. Auto-resolve conflicts
            merge_result = self._merge_theirs(repo_path, branch)
            result["merge"] = merge_result
            if merge_result["success"]:
                result["status"] = "conflict_resolved"
                self._bm.mark_conflict(name, False)
            else:
                result["status"] = "error"
                self._bm.mark_conflict(name, True)
                self._upgrade_log.append(result)
                return result

        # 3. Optional tests
        if self._run_tests:
            test_result = self._run_test_suite(repo_path)
            result["tests"] = test_result

        # 4. Open PR
        repo_name = bot.get("repoName", "")
        if repo_name:
            pr = self._rm.create_pr(
                repo_name,
                title=_PR_TITLE,
                head=_PR_BRANCH,
                body=f"Auto-upgrade for bot `{name}` triggered by DreamCo Control Tower.",
            )
            result["pr"] = pr.get("html_url") if (pr and isinstance(pr, dict)) else None
            if pr:
                self._bm.record_pr(name, pr.get("html_url", ""))

        # 5. Update registry
        self._bm.record_update(name)
        self._bm.set_status(name, STATUS_ACTIVE)
        self._upgrade_log.append(result)
        return result

    def upgrade_all(self, branch: str = "main") -> Dict[str, Any]:
        """Run :meth:`upgrade_bot` for every bot in the registry.

        Returns
        -------
        dict
            Keys are bot names, values are the per-bot result dicts.
        """
        results: Dict[str, Any] = {}
        for bot in self._bm.list_bots():
            name = bot.get("name", "")
            if name:
                results[name] = self.upgrade_bot(name, branch)
        return results

    def get_upgrade_log(self) -> List[Dict[str, Any]]:
        """Return the history of upgrade attempts in this session."""
        return list(self._upgrade_log)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _pull(self, repo_path: str, branch: str) -> Dict[str, Any]:
        """Attempt ``git pull --rebase origin <branch>``."""
        completed = self._runner(
            ["git", "-C", repo_path, "pull", "--rebase", "origin", branch],
        )
        return {
            "cmd": f"git -C {repo_path} pull --rebase origin {branch}",
            "success": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }

    def _merge_theirs(self, repo_path: str, branch: str) -> Dict[str, Any]:
        """Attempt ``git merge -X theirs origin/<branch>`` to auto-resolve."""
        completed = self._runner(
            ["git", "-C", repo_path, "merge", "-X", "theirs", f"origin/{branch}"],
        )
        return {
            "cmd": f"git -C {repo_path} merge -X theirs origin/{branch}",
            "success": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }

    def _run_test_suite(self, repo_path: str) -> Dict[str, Any]:
        """Try to run tests in *repo_path* (pytest preferred, then npm test)."""
        # Try pytest first
        pytest_run = self._runner(["python", "-m", "pytest", "--tb=no", "-q"], cwd=repo_path)
        if pytest_run.returncode == 0:
            return {"runner": "pytest", "success": True, "output": pytest_run.stdout.strip()}
        if pytest_run.returncode != 2:  # 2 = no tests collected (acceptable)
            return {"runner": "pytest", "success": False, "output": pytest_run.stderr.strip()}

        # Fall back to npm test
        npm_run = self._runner(["npm", "test", "--if-present"], cwd=repo_path)
        return {
            "runner": "npm",
            "success": npm_run.returncode == 0,
            "output": npm_run.stdout.strip() or npm_run.stderr.strip(),
        }
