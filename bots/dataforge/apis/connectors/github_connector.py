"""GitHub REST API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class GitHubConnector:
    """GitHubConnector for DataForge AI."""

    BASE_URL = "https://api.github.com"

    def __init__(self):
        """Initialize connector, reading token from environment."""
        self.token = os.environ.get("GITHUB_TOKEN", "")
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def search_repositories(self, query: str, per_page: int = 10) -> dict:
        """Search GitHub repositories.

        Args:
            query: Search query string.
            per_page: Results per page (default 10).

        Returns:
            API response dict or error dict.
        """
        import requests
        params = {"q": query, "per_page": per_page}
        try:
            response = requests.get(f"{self.BASE_URL}/search/repositories", params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            logger.info("GitHub repository search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("GitHub search_repositories error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_repo(self, owner: str, repo: str) -> dict:
        """Get details for a specific GitHub repository.

        Args:
            owner: Repository owner (user or org).
            repo: Repository name.

        Returns:
            API response dict or error dict.
        """
        import requests
        try:
            response = requests.get(f"{self.BASE_URL}/repos/{owner}/{repo}", headers=self.headers, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("GitHub get_repo error: %s", e)
            return {"status": "error", "message": str(e)}
