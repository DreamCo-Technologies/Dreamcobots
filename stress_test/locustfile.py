"""Locust load test definitions for DreamCo backend endpoints."""

from __future__ import annotations

from locust import HttpUser, between, task


class BaseDreamCoUser(HttpUser):
    wait_time = between(1, 3)

    def _headers(self, tier: str) -> dict[str, str]:
        return {"x-api-key": f"{tier}-key", "x-api-tier": tier}

    @task(2)
    def health_check(self) -> None:
        with self.client.get("/health", headers=self._headers("free"), catch_response=True) as response:
            if response.status_code != 200:
                response.failure("health failed")

    @task(1)
    def gig_generation(self) -> None:
        payload = {"title": "AI SEO Gig", "keywords": ["seo", "content"], "word_count": 250}
        with self.client.post("/fiverr/generate-gig", json=payload, headers=self._headers("pro"), catch_response=True) as response:
            if response.status_code != 200:
                response.failure("gig generation failed")

    @task(1)
    def lead_scraping(self) -> None:
        payload = {"html": "<html><body><a href='mailto:test@example.com'>Test</a></body></html>"}
        with self.client.post("/leads/scrape", json=payload, headers=self._headers("enterprise"), catch_response=True) as response:
            if response.status_code != 200:
                response.failure("lead scrape failed")

    @task(1)
    def revenue_query(self) -> None:
        with self.client.get("/revenue", headers=self._headers("pro"), catch_response=True) as response:
            if response.status_code != 200:
                response.failure("revenue query failed")


class FreeUserLoad(BaseDreamCoUser):
    weight = 3


class ProUserLoad(BaseDreamCoUser):
    weight = 2
    wait_time = between(0.5, 2)


class EnterpriseUserLoad(BaseDreamCoUser):
    weight = 1
    wait_time = between(0.2, 1.2)
