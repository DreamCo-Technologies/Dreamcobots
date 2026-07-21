"""Tests for bots/government_contract_bot/sam_api.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.government_contract_bot.sam_api import SAMGovAPI


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestInstantiation:
    def test_mock_when_no_api_key(self):
        api = SAMGovAPI()
        assert api.is_mock is True

    def test_mock_forced(self):
        api = SAMGovAPI(mock=True)
        assert api.is_mock is True


# ---------------------------------------------------------------------------
# search_contracts (mock mode)
# ---------------------------------------------------------------------------

class TestSearchContracts:
    def setup_method(self):
        self.api = SAMGovAPI(mock=True)

    def test_returns_dict(self):
        result = self.api.search_contracts()
        assert isinstance(result, dict)

    def test_required_keys_present(self):
        result = self.api.search_contracts(keyword="IT")
        for key in ("opportunities", "total", "keyword", "timestamp"):
            assert key in result

    def test_keyword_reflected(self):
        result = self.api.search_contracts(keyword="cybersecurity")
        assert result["keyword"] == "cybersecurity"

    def test_default_keyword(self):
        result = self.api.search_contracts()
        assert result["keyword"] == "IT"

    def test_opportunities_is_list(self):
        result = self.api.search_contracts()
        assert isinstance(result["opportunities"], list)

    def test_limit_respected(self):
        result = self.api.search_contracts(limit=2)
        assert len(result["opportunities"]) <= 2

    def test_opportunity_has_notice_id(self):
        result = self.api.search_contracts()
        for opp in result["opportunities"]:
            assert "noticeId" in opp

    def test_opportunity_has_title(self):
        result = self.api.search_contracts(keyword="Cloud")
        for opp in result["opportunities"]:
            assert "title" in opp
            assert "Cloud" in opp["title"]

    def test_opportunity_estimated_value_positive(self):
        result = self.api.search_contracts()
        for opp in result["opportunities"]:
            assert opp.get("estimatedValue", 0) > 0
