"""
DreamCo Control Tower — Repo Manager
======================================
Manages GitHub repository monitoring for all bots in the Control Tower.

Responsibilities
----------------
- Track open/merged PRs, open issues, last commit, and workflow results.
- Provide heartbeat / sync checks for each repo.
- Flag repos that have conflicts or need manual intervention.
- Create Pull Requests via the GitHub API when ``GITHUB_TOKEN`` is set.

GitHub API calls are made through a thin ``GitHubClient`` abstraction so that
the rest of the system remains testable without live network access.
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


_DEFAULT_CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "repos.json")
_GITHUB_API = "https://api.github.com"


# ---------------------------------------------------------------------------
# Thin GitHub REST client
# ---------------------------------------------------------------------------

class GitHubClient:
    """Minimal GitHub REST v3 client.

    Parameters
    ----------
    token:
        Personal access token.  When ``None`` only unauthenticated calls
        are possible (rate-limited to 60 req/hour).
    """

    def __init__(self, token: Optional[str] = None) -> None:
        self._token = token or os.environ.get("GITHUB_TOKEN")

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "DreamCo-Control-Tower/1.0"}
        if self._token:
            headers["Authorization"] = f"token {self._token}"
        return headers

    def get(self, path: str) -> Any:
        """Perform a GET request and return parsed JSON, or None on error."""
        url = f"{_GITHUB_API}{path}"
        req = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
            return None

    def post(self, path: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Perform a POST request with a JSON body, return parsed JSON or None."""
        url = f"{_GITHUB_API}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={**self._headers(), "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
            return None


# ---------------------------------------------------------------------------
# Repo Manager
# ---------------------------------------------------------------------------

class RepoManager:
    """Monitor and manage GitHub repositories linked to the Control Tower.

    Parameters
    ----------
    config_path:
        Path to ``repos.json``.  Defaults to ``config/repos.json`` relative
        to this module.
    github_client:
        An optional pre-built :class:`GitHubClient` instance (useful for
        testing with a stub).
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        github_client: Optional[GitHubClient] = None,
    ) -> None:
        self._config_path = config_path or _DEFAULT_CONFIG
        self._client = github_client or GitHubClient()
        self._repos: Dict[str, Dict[str, Any]] = {}
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not os.path.exists(self._config_path):
            return
        try:
            with open(self._config_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, list):
                for entry in data:
                    name = entry.get("name")
                    if name:
                        self._repos[name] = entry
        except (json.JSONDecodeError, OSError):
            pass

    def save(self) -> None:
        """Persist the current repo registry to disk."""
        os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
        with open(self._config_path, "w", encoding="utf-8") as fh:
            json.dump(list(self._repos.values()), fh, indent=2)

    # ------------------------------------------------------------------
    # Registry CRUD
    # ------------------------------------------------------------------

    def add_repo(
        self,
        name: str,
        owner: str,
        branch: str = "main",
        url: str = "",
    ) -> Dict[str, Any]:
        """Register a repository for monitoring."""
        entry: Dict[str, Any] = {
            "name": name,
            "owner": owner,
            "branch": branch,
            "url": url or f"https://github.com/{owner}/{name}",
            "monitored": True,
            "lastCommit": None,
            "openPRs": 0,
            "openIssues": 0,
            "lastWorkflowResult": None,
            "conflictsDetected": False,
            "addedAt": datetime.now(timezone.utc).isoformat(),
        }
        self._repos[name] = entry
        return entry

    def remove_repo(self, name: str) -> bool:
        """Remove a repo from monitoring.  Returns True if it existed."""
        if name in self._repos:
            del self._repos[name]
            return True
        return False

    def get_repo(self, name: str) -> Optional[Dict[str, Any]]:
        """Return a single repo entry or None."""
        return self._repos.get(name)

    def list_repos(self) -> List[Dict[str, Any]]:
        """Return all monitored repositories."""
        return list(self._repos.values())

    # ------------------------------------------------------------------
    # GitHub sync
    # ------------------------------------------------------------------

    def sync_repo(self, name: str) -> Dict[str, Any]:
        """Fetch live data from GitHub for the given repo and update the local record.

        Returns
        -------
        dict
            The updated repo entry.  If the repo is unknown or the GitHub API
            call fails, returns ``{"error": "..."}`` without modifying state.
        """
        entry = self._repos.get(name)
        if entry is None:
            return {"error": f"Repo '{name}' not found in registry."}

        owner = entry.get("owner", "")
        if not owner:
            return {"error": "Repo entry is missing 'owner' field."}

        # Fetch basic repo info
        repo_data = self._client.get(f"/repos/{owner}/{name}")
        if repo_data and isinstance(repo_data, dict):
            entry["lastCommit"] = (
                repo_data.get("pushed_at") or repo_data.get("updated_at")
            )
            entry["openIssues"] = repo_data.get("open_issues_count", 0)

        # Fetch open PRs
        prs = self._client.get(f"/repos/{owner}/{name}/pulls?state=open&per_page=100")
        if isinstance(prs, list):
            entry["openPRs"] = len(prs)

        # Fetch latest workflow run result
        runs = self._client.get(f"/repos/{owner}/{name}/actions/runs?per_page=1")
        if isinstance(runs, dict):
            workflow_runs = runs.get("workflow_runs", [])
            if workflow_runs:
                latest = workflow_runs[0]
                entry["lastWorkflowResult"] = {
                    "status": latest.get("status"),
                    "conclusion": latest.get("conclusion"),
                    "name": latest.get("name"),
                    "updatedAt": latest.get("updated_at"),
                }

        entry["lastSynced"] = datetime.now(timezone.utc).isoformat()
        return entry

    def sync_all(self) -> Dict[str, Any]:
        """Sync all monitored repositories with GitHub."""
        results: Dict[str, Any] = {}
        for name in list(self._repos.keys()):
            if self._repos[name].get("monitored", True):
                results[name] = self.sync_repo(name)
        return results

    # ------------------------------------------------------------------
    # PR creation
    # ------------------------------------------------------------------

    def create_pr(
        self,
        repo_name: str,
        title: str,
        head: str,
        base: str = "main",
        body: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Open a Pull Request on GitHub.

        Parameters
        ----------
        repo_name:  Repository name (must be registered).
        title:      PR title.
        head:       Source branch (e.g. ``auto-update``).
        base:       Target branch (default: ``main``).
        body:       Optional PR description.

        Returns
        -------
        dict or None
            The GitHub API response (contains ``html_url`` on success), or
            ``None`` if the call failed.
        """
        entry = self._repos.get(repo_name)
        if entry is None:
            return None
        owner = entry.get("owner", "")
        if not owner:
            return None

        payload = {
            "title": title,
            "head": head,
            "base": base,
            "body": body or f"Automated PR created by DreamCo Control Tower on {datetime.now(timezone.utc).isoformat()}",
        }
        result = self._client.post(f"/repos/{owner}/{repo_name}/pulls", payload)
        if result and isinstance(result, dict):
            entry["lastPR"] = datetime.now(timezone.utc).isoformat()
            entry["lastPRUrl"] = result.get("html_url", "")
        return result

    # ------------------------------------------------------------------
    # Summaries
    # ------------------------------------------------------------------

    def get_summary(self) -> Dict[str, Any]:
        """Return a high-level snapshot of all monitored repos."""
        total_open_prs = sum(r.get("openPRs", 0) for r in self._repos.values())
        total_open_issues = sum(r.get("openIssues", 0) for r in self._repos.values())
        conflicts = [n for n, r in self._repos.items() if r.get("conflictsDetected")]
        return {
            "total_repos": len(self._repos),
            "total_open_prs": total_open_prs,
            "total_open_issues": total_open_issues,
            "conflicted_repos": conflicts,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
