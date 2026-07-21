"""
DreamCo Control Tower — Python Integration Module
===================================================

Provides Python-native wrappers for the DreamCo Control Tower's core
capabilities so that the existing Python bot ecosystem can participate in:

  - Heartbeat reporting (push live status to the Control Tower backend)
  - Auto-upgrade triggers (call the backend API to schedule upgrades)
  - GitHub repository status queries
  - Centralized bot registry synchronisation

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_DEFAULT_TOWER_URL = os.environ.get("CONTROL_TOWER_URL", "http://localhost:3001")
_GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
_GITHUB_API = "https://api.github.com"


# ---------------------------------------------------------------------------
# HTTP helper (no external dependencies required)
# ---------------------------------------------------------------------------

def _http_get(url: str, token: str = "") -> dict[str, Any]:
    """Perform a simple GET request and return the parsed JSON body."""
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "DreamCo-ControlTower/1.0")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return {"error": str(exc), "status_code": exc.code}
    except Exception as exc:
        return {"error": str(exc)}


def _http_post(url: str, data: dict[str, Any], token: str = "") -> dict[str, Any]:
    """Perform a simple POST request with JSON body and return the parsed response."""
    payload = json.dumps(data).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "DreamCo-ControlTower/1.0")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode() if exc.fp else ""
        return {"error": str(exc), "status_code": exc.code, "body": body}
    except Exception as exc:
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Heartbeat
# ---------------------------------------------------------------------------

class HeartbeatClient:
    """Send heartbeat pings from a Python bot to the Control Tower backend."""

    def __init__(self, tower_url: str = _DEFAULT_TOWER_URL) -> None:
        self._url = tower_url.rstrip("/")

    def ping(self, bot_name: str, status: str = "active", metadata: Optional[dict] = None) -> dict[str, Any]:
        """
        Send a heartbeat ping for *bot_name*.

        Parameters
        ----------
        bot_name : str
            Registered name of the bot (must match an entry in bots.json).
        status : str
            Current operational status: ``"active"``, ``"updating"``, or ``"offline"``.
        metadata : dict, optional
            Additional key-value pairs to include in the ping payload.
        """
        payload = {
            "bot": bot_name,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(metadata or {}),
        }
        result = _http_post(f"{self._url}/api/heartbeat/ping", payload)
        return result

    def tower_alive(self) -> bool:
        """Return ``True`` if the Control Tower backend responds to its heartbeat endpoint."""
        resp = _http_get(f"{self._url}/api/heartbeat")
        return resp.get("status") == "ok"


# ---------------------------------------------------------------------------
# GitHub Repository Manager
# ---------------------------------------------------------------------------

class GitHubRepoManager:
    """
    Python interface to GitHub repository operations used by the Control Tower.

    Uses the GitHub REST API directly (no third-party library required).
    """

    def __init__(self, token: str = _GITHUB_TOKEN) -> None:
        self._token = token

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_open_prs(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Return open pull requests for *owner/repo*."""
        data = _http_get(
            f"{_GITHUB_API}/repos/{owner}/{repo}/pulls?state=open&per_page=20",
            token=self._token,
        )
        if isinstance(data, list):
            return [
                {
                    "number": pr.get("number"),
                    "title": pr.get("title"),
                    "author": pr.get("user", {}).get("login"),
                    "branch": pr.get("head", {}).get("ref"),
                    "created_at": pr.get("created_at"),
                    "url": pr.get("html_url"),
                }
                for pr in data
            ]
        return []

    def get_open_issues(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Return open issues (excluding PRs) for *owner/repo*."""
        data = _http_get(
            f"{_GITHUB_API}/repos/{owner}/{repo}/issues?state=open&per_page=20",
            token=self._token,
        )
        if isinstance(data, list):
            return [
                {
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "labels": [lb.get("name") for lb in issue.get("labels", [])],
                    "url": issue.get("html_url"),
                }
                for issue in data
                if "pull_request" not in issue
            ]
        return []

    def get_latest_commit(self, owner: str, repo: str, branch: str = "main") -> Optional[dict[str, Any]]:
        """Return the most recent commit on *branch* for *owner/repo*."""
        data = _http_get(
            f"{_GITHUB_API}/repos/{owner}/{repo}/commits?sha={branch}&per_page=1",
            token=self._token,
        )
        if isinstance(data, list) and data:
            c = data[0]
            return {
                "sha": c.get("sha", "")[:7],
                "message": c.get("commit", {}).get("message", "").split("\n")[0],
                "author": c.get("commit", {}).get("author", {}).get("name"),
                "date": c.get("commit", {}).get("author", {}).get("date"),
                "url": c.get("html_url"),
            }
        return None

    def get_workflow_runs(self, owner: str, repo: str, per_page: int = 5) -> list[dict[str, Any]]:
        """Return the most recent workflow runs for *owner/repo*."""
        data = _http_get(
            f"{_GITHUB_API}/repos/{owner}/{repo}/actions/runs?per_page={per_page}",
            token=self._token,
        )
        runs = data.get("workflow_runs", []) if isinstance(data, dict) else []
        return [
            {
                "id": r.get("id"),
                "name": r.get("name"),
                "status": r.get("status"),
                "conclusion": r.get("conclusion"),
                "branch": r.get("head_branch"),
                "created_at": r.get("created_at"),
                "url": r.get("html_url"),
            }
            for r in runs
        ]

    def get_repo_status(self, owner: str, repo: str) -> dict[str, Any]:
        """Return a full status snapshot for *owner/repo*."""
        open_prs = self.get_open_prs(owner, repo)
        open_issues = self.get_open_issues(owner, repo)
        latest_commit = self.get_latest_commit(owner, repo)
        workflow_runs = self.get_workflow_runs(owner, repo)
        latest_run = workflow_runs[0] if workflow_runs else None

        return {
            "owner": owner,
            "repo": repo,
            "open_prs": open_prs,
            "open_issues": open_issues,
            "latest_commit": latest_commit,
            "workflow_runs": workflow_runs,
            "summary": {
                "open_pr_count": len(open_prs),
                "open_issue_count": len(open_issues),
                "last_workflow_status": (latest_run or {}).get("conclusion", "unknown"),
                "has_conflicts": any(
                    "conflict" in (pr.get("title") or "").lower() for pr in open_prs
                ),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def super_dashboard_snapshot(self, owner: str, repo: str) -> dict[str, Any]:
        """Return compact workflow and repository metrics for the Super Dashboard."""
        status = self.get_repo_status(owner, repo)
        summary = status.get("summary", {})
        workflow_runs = status.get("workflow_runs", [])
        latest_run = workflow_runs[0] if workflow_runs else {}
        return {
            "open_pr_count": int(summary.get("open_pr_count", 0)),
            "open_issue_count": int(summary.get("open_issue_count", 0)),
            "last_workflow_status": summary.get("last_workflow_status", "unknown"),
            "latest_workflow_name": latest_run.get("name", "n/a"),
            "latest_workflow_conclusion": latest_run.get("conclusion", "unknown"),
        }

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str = "main",
        body: str = "",
    ) -> dict[str, Any]:
        """Open a pull request in *owner/repo*."""
        return _http_post(
            f"{_GITHUB_API}/repos/{owner}/{repo}/pulls",
            {"title": title, "head": head, "base": base, "body": body},
            token=self._token,
        )

    def re_run_workflow(self, owner: str, repo: str, run_id: int) -> dict[str, Any]:
        """Re-trigger a previously failed workflow run."""
        return _http_post(
            f"{_GITHUB_API}/repos/{owner}/{repo}/actions/runs/{run_id}/rerun",
            {},
            token=self._token,
        )


# ---------------------------------------------------------------------------
# Bot Registry Sync
# ---------------------------------------------------------------------------

class BotRegistrySync:
    """
    Synchronise the Python bot ecosystem with the Control Tower's bot registry
    (config/bots.json).
    """

    def __init__(self, registry_path: Optional[str] = None) -> None:
        if registry_path is None:
            # Default: look two levels up for the config directory.
            default = Path(__file__).parent.parent.parent / "dreamco-control-tower" / "config" / "bots.json"
            registry_path = str(default)
        self._path = Path(registry_path)

    def load(self) -> list[dict[str, Any]]:
        """Load the current bot registry from disk."""
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save(self, bots: list[dict[str, Any]]) -> None:
        """Persist the bot registry to disk."""
        self._path.write_text(json.dumps(bots, indent=2), encoding="utf-8")

    def register(
        self,
        name: str,
        repo_name: str,
        owner: str,
        repo_path: str = "",
        tier: str = "pro",
    ) -> dict[str, Any]:
        """
        Add a new bot to the registry (or update an existing entry).

        Returns the updated entry.
        """
        bots = self.load()
        existing = next((b for b in bots if b["name"] == name), None)
        entry: dict[str, Any] = {
            "name": name,
            "repoName": repo_name,
            "repoPath": repo_path,
            "branch": "main",
            "owner": owner,
            "status": "active",
            "tier": tier,
            "heartbeatUrl": None,
            "lastHeartbeat": None,
            "lastPR": None,
            "openIssues": 0,
        }
        if existing is not None:
            existing.update(entry)
        else:
            bots.append(entry)
        self.save(bots)
        return entry

    def update_heartbeat(self, name: str, status: str = "active") -> Optional[dict[str, Any]]:
        """Update the ``lastHeartbeat`` field for the named bot."""
        bots = self.load()
        bot = next((b for b in bots if b["name"] == name), None)
        if bot is None:
            return None
        bot["lastHeartbeat"] = datetime.now(timezone.utc).isoformat()
        bot["status"] = status
        self.save(bots)
        return bot

    def get(self, name: str) -> Optional[dict[str, Any]]:
        """Retrieve a single bot entry by name."""
        return next((b for b in self.load() if b["name"] == name), None)

    def list_all(self) -> list[dict[str, Any]]:
        """Return all registered bots."""
        return self.load()
