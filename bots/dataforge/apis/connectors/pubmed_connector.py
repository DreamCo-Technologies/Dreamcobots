"""PubMed Entrez API connector for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os

logger = logging.getLogger(__name__)


class PubMedConnector:
    """PubMedConnector for DataForge AI."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self):
        """Initialize connector with optional email for API requests."""
        self.email = os.environ.get("PUBMED_EMAIL", "dataforge@example.com")

    def search(self, query: str, retmax: int = 10) -> dict:
        """Search PubMed articles.

        Args:
            query: Search query string.
            retmax: Maximum number of results (default 10).

        Returns:
            API response dict with article IDs or error dict.
        """
        import requests
        params = {"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json", "email": self.email}
        try:
            response = requests.get(f"{self.BASE_URL}/esearch.fcgi", params=params, timeout=30)
            response.raise_for_status()
            logger.info("PubMed search completed for: %s", query)
            return {"status": "success", "data": response.json()}
        except requests.RequestException as e:
            logger.error("PubMed search error: %s", e)
            return {"status": "error", "message": str(e)}

    def fetch_article(self, pmid: str) -> dict:
        """Fetch a PubMed article by PMID.

        Args:
            pmid: PubMed article identifier.

        Returns:
            API response dict with article data or error dict.
        """
        import requests
        params = {"db": "pubmed", "id": pmid, "retmode": "json", "email": self.email}
        try:
            response = requests.get(f"{self.BASE_URL}/efetch.fcgi", params=params, timeout=30)
            response.raise_for_status()
            return {"status": "success", "data": response.text}
        except requests.RequestException as e:
            logger.error("PubMed fetch_article error: %s", e)
            return {"status": "error", "message": str(e)}
