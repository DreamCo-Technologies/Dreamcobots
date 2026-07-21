"""
DreamCo Control Tower — GitHub Integration

Provides GitHub API wrappers for the Control Tower:
  - Repository status (PRs, commits, workflow runs)
  - Automated pull requests
  - Git pull/merge operations with conflict resolution
  - Workflow trigger support

# GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import subprocess
import sys
import os
from datetime import datetime, timezone
from typing import Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from framework import GlobalAISourcesFlow  # noqa: F401


class GitHubIntegration:
    """GitHub API and git operations wrapper for the DreamCo Control Tower."""

    def __init__(self, token: Optional[str] = None, owner: str = "ireanjordan24") -> None:
        # Distinguish between None (not provided → fall back to env) and "" (explicitly
        # empty → treat as "no token" to allow safe testing without a live credential).
        self._token = token if token is not None else os.environ.get("GITHUB_TOKEN", "")
        self._owner = owner
        self._event_log: list[dict] = []

    # ------------------------------------------------------------------
    # Repository status
    # ------------------------------------------------------------------

    def get_repo_status(self, repo_name: str) -> dict:
        """Return a summary of repository status including open PRs and last commit.

        When a real GitHub token is provided the result will attempt to call
        the GitHub REST API.  When no token is available (or network is
        unavailable) a degraded offline response is returned instead so the
        dashboard always has a valid structure to render.
        """
        try:
            import urllib.request
            import json as _json

            headers = {"Accept": "application/vnd.github+json"}
            if self._token:
                headers["Authorization"] = f"Bearer {self._token}"

            def _gh_get(path: str) -> Any:
                url = f"https://api.github.com{path}"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    return _json.loads(resp.read())

            pr_data = _gh_get(f"/repos/{self._owner}/{repo_name}/pulls?state=open&per_page=10")
            commit_data = _gh_get(f"/repos/{self._owner}/{repo_name}/commits?per_page=1")
            runs_data = _gh_get(f"/repos/{self._owner}/{repo_name}/actions/runs?per_page=1")

            last_commit = commit_data[0] if commit_data else {}
            last_run = runs_data.get("workflow_runs", [{}])[0]

            status = {
                "repo": repo_name,
                "owner": self._owner,
                "open_prs": len(pr_data),
                "last_commit_sha": last_commit.get("sha", "")[:7],
                "last_commit_message": (
                    last_commit.get("commit", {}).get("message", "")[:80]
                ),
                "last_commit_at": (
                    last_commit.get("commit", {}).get("committer", {}).get("date", "")
                ),
                "last_workflow_status": last_run.get("conclusion", "unknown"),
                "last_workflow_name": last_run.get("name", ""),
                "online": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            status = {
                "repo": repo_name,
                "owner": self._owner,
                "open_prs": 0,
                "last_commit_sha": "",
                "last_commit_message": "",
                "last_commit_at": "",
                "last_workflow_status": "unknown",
                "last_workflow_name": "",
                "online": False,
                "error": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        self._event_log.append({"action": "get_repo_status", "repo": repo_name, **status})
        return status

    # ------------------------------------------------------------------
    # Pull / merge operations
    # ------------------------------------------------------------------

    def pull_latest(self, repo_path: str, branch: str = "main") -> dict:
        """Run ``git pull --rebase origin <branch>`` in *repo_path*.

        Returns a result dict with keys ``success``, ``output``, and
        optionally ``error``.
        """
        try:
            out = subprocess.check_output(
                ["git", "-C", repo_path, "pull", "--rebase", "origin", branch],
                stderr=subprocess.STDOUT,
                text=True,
            )
            result = {"success": True, "output": out.strip(), "repo_path": repo_path}
        except subprocess.CalledProcessError as exc:
            result = {
                "success": False,
                "output": exc.output.strip() if exc.output else "",
                "error": str(exc),
                "repo_path": repo_path,
            }
        self._event_log.append({"action": "pull_latest", **result})
        return result

    def auto_merge(self, repo_path: str, strategy: str = "theirs") -> dict:
        """Attempt to resolve conflicts using *strategy* (``theirs`` or ``ours``)."""
        try:
            out = subprocess.check_output(
                ["git", "-C", repo_path, "merge", f"-X{strategy}", "origin/main"],
                stderr=subprocess.STDOUT,
                text=True,
            )
            result = {"success": True, "output": out.strip(), "strategy": strategy}
        except subprocess.CalledProcessError as exc:
            result = {
                "success": False,
                "output": exc.output.strip() if exc.output else "",
                "error": str(exc),
                "strategy": strategy,
            }
        self._event_log.append({"action": "auto_merge", "repo_path": repo_path, **result})
        return result

    # ------------------------------------------------------------------
    # Pull requests
    # ------------------------------------------------------------------

    def create_pull_request(
        self,
        repo_name: str,
        head: str,
        title: str,
        body: str = "🤖 Auto-generated by DreamCo Control Tower",
        base: str = "main",
    ) -> dict:
        """Create a pull request via the GitHub API.

        Returns the PR URL on success or an error dict on failure.
        """
        try:
            import urllib.request
            import json as _json

            if not self._token:
                return {"success": False, "error": "GITHUB_TOKEN not configured"}

            payload = _json.dumps({
                "title": title,
                "body": body,
                "head": head,
                "base": base,
            }).encode()

            req = urllib.request.Request(
                f"https://api.github.com/repos/{self._owner}/{repo_name}/pulls",
                data=payload,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = _json.loads(resp.read())
            result = {
                "success": True,
                "pr_number": data.get("number"),
                "pr_url": data.get("html_url"),
                "title": title,
            }
        except Exception as exc:
            result = {"success": False, "error": str(exc), "title": title}

        self._event_log.append({"action": "create_pull_request", "repo": repo_name, **result})
        return result

    # ------------------------------------------------------------------
    # Event log
    # ------------------------------------------------------------------

    def get_event_log(self, limit: int = 50) -> list[dict]:
        """Return the most recent *limit* logged events."""
        return list(self._event_log[-limit:])

    def clear_event_log(self) -> None:
        """Clear all logged events."""
        self._event_log.clear()


__all__ = ["GitHubIntegration"]
