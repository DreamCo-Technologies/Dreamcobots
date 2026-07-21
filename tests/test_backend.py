"""Tests for FastAPI backend endpoints."""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestFiverrEndpoints:
    def test_generate_gig_success(self):
        payload = {
            "title": "Python SEO Guide",
            "keywords": ["python", "seo"],
            "word_count": 200,
        }
        response = client.post("/fiverr/generate-gig", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Python SEO Guide"
        assert "content" in data
        assert data["revenue"] == 25.0

    def test_generate_gig_content_not_empty(self):
        payload = {"title": "Content Test", "keywords": ["content"], "word_count": 100}
        response = client.post("/fiverr/generate-gig", json=payload)
        assert response.status_code == 200
        assert len(response.json()["content"]) > 0

    def test_run_batch_returns_completed_count(self):
        payload = [
            {"title": "Gig A", "keywords": ["a"], "word_count": 100},
            {"title": "Gig B", "keywords": ["b"], "word_count": 100},
        ]
        response = client.post("/fiverr/run-batch", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] == 2
        assert data["revenue"] > 0


class TestLeadEndpoints:
    SAMPLE_HTML = """
    <html><body>
      <div class="lead">
        name: "Test User"
        test.user@example.com
        company: TestCo
        https://test.example.com
      </div>
    </body></html>
    """

    def test_scrape_leads_returns_list(self):
        response = client.post("/leads/scrape", json={"html": self.SAMPLE_HTML})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_scrape_leads_extracts_email(self):
        response = client.post("/leads/scrape", json={"html": self.SAMPLE_HTML})
        assert response.status_code == 200
        leads = response.json()
        emails = [l["email"] for l in leads]
        assert any("test.user@example.com" in e for e in emails)

    def test_run_outreach_returns_metrics(self):
        response = client.post("/leads/run-outreach", json={"html": self.SAMPLE_HTML})
        assert response.status_code == 200
        data = response.json()
        assert "leads_found" in data
        assert "emails_sent" in data
        assert "revenue" in data

    def test_export_csv_returns_dict_with_csv_key(self):
        response = client.get("/leads/export-csv")
        assert response.status_code == 200
        assert "csv" in response.json()


class TestRevenueEndpoint:
    def test_revenue_endpoint_structure(self):
        response = client.get("/revenue")
        assert response.status_code == 200
        data = response.json()
        assert "total_usd" in data
        assert "entries" in data
        assert isinstance(data["total_usd"], float)
