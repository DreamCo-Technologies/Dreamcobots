"""Tests for Full Empire Mode modules:
  - bots/lead_gen_bot/maps_scraper.py  (MapsScraperBot)
  - bots/sales_bot/closer_bot.py       (CloserBot)
  - bots/real_estate_bot/deal_finder.py (DealFinderBot)
  - dashboard/app.py                   (Flask dashboard)
  - bots/ai_learning_system/learning_loop.py (LearningLoop)
"""

import json
import os
import sys
import tempfile

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.lead_gen_bot.tiers import Tier as LeadTier
from bots.lead_gen_bot.maps_scraper import MapsScraperBot, MapsScraperBotTierError, Bot as LeadBot
from bots.sales_bot.tiers import Tier as SalesTier
from bots.sales_bot.closer_bot import CloserBot, CloserBotTierError, Bot as SalesBot
from bots.real_estate_bot.deal_finder import DealFinderBot, DealFinderTierError, Bot as DealBot
from bots.ai_learning_system.learning_loop import LearningLoop

# ---------------------------------------------------------------------------
# MapsScraperBot
# ---------------------------------------------------------------------------

class TestMapsScraperBotInstantiation:
    def test_default_tier_is_free(self):
        bot = MapsScraperBot()
        assert bot.tier == LeadTier.FREE

    def test_pro_tier(self):
        bot = MapsScraperBot(tier=LeadTier.PRO)
        assert bot.tier == LeadTier.PRO

    def test_enterprise_tier(self):
        bot = MapsScraperBot(tier=LeadTier.ENTERPRISE)
        assert bot.tier == LeadTier.ENTERPRISE

    def test_name(self):
        bot = MapsScraperBot()
        assert bot.name == "Maps Scraper Bot"

    def test_bot_alias(self):
        bot = LeadBot()
        assert isinstance(bot, MapsScraperBot)


class TestMapsScraperBotLeads:
    def test_returns_list(self):
        bot = MapsScraperBot()
        leads = bot.get_mock_realistic_leads()
        assert isinstance(leads, list)

    def test_free_tier_max_5(self):
        bot = MapsScraperBot(tier=LeadTier.FREE)
        leads = bot.get_mock_realistic_leads()
        assert len(leads) <= 5

    def test_pro_tier_max_50(self):
        bot = MapsScraperBot(tier=LeadTier.PRO)
        leads = bot.get_mock_realistic_leads()
        assert len(leads) <= 50

    def test_enterprise_gets_all(self):
        bot = MapsScraperBot(tier=LeadTier.ENTERPRISE)
        leads = bot.get_mock_realistic_leads()
        assert len(leads) == len(MapsScraperBot.MOCK_LEADS)

    def test_lead_has_required_keys(self):
        bot = MapsScraperBot()
        leads = bot.get_mock_realistic_leads()
        for lead in leads:
            assert "name" in lead
            assert "phone" in lead
            assert "city" in lead


class TestMapsScraperBotRun:
    def test_run_returns_string(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        bot = MapsScraperBot()
        result = bot.run()
        assert isinstance(result, str)

    def test_run_contains_collected(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        bot = MapsScraperBot()
        result = bot.run()
        assert "Collected" in result

    def test_run_creates_leads_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        bot = MapsScraperBot()
        bot.run()
        assert (tmp_path / "data" / "leads.json").exists()

    def test_run_leads_file_is_valid_jsonl(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        bot = MapsScraperBot()
        bot.run()
        with open(tmp_path / "data" / "leads.json") as f:
            for line in f:
                if line.strip():
                    json.loads(line)  # should not raise


class TestMapsScraperBotDescribeTier:
    def test_describe_contains_tier_name(self):
        bot = MapsScraperBot()
        desc = bot.describe_tier()
        assert "Maps Scraper Bot" in desc

    def test_describe_contains_price(self):
        bot = MapsScraperBot()
        desc = bot.describe_tier()
        assert "$" in desc


# ---------------------------------------------------------------------------
# CloserBot
# ---------------------------------------------------------------------------

class TestCloserBotInstantiation:
    def test_default_tier_is_free(self):
        bot = CloserBot()
        assert bot.tier == SalesTier.FREE

    def test_pro_tier(self):
        bot = CloserBot(tier=SalesTier.PRO)
        assert bot.tier == SalesTier.PRO

    def test_name(self):
        bot = CloserBot()
        assert bot.name == "Closer Bot"

    def test_bot_alias(self):
        bot = SalesBot()
        assert isinstance(bot, CloserBot)


class TestCloserBotNoLeads:
    def test_run_returns_no_leads_message(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        bot = CloserBot()
        result = bot.run()
        assert result == "No leads available"


class TestCloserBotWithLeads:
    def _write_leads(self, path, leads):
        os.makedirs(path / "data", exist_ok=True)
        with open(path / "data" / "leads.json", "w") as f:
            for lead in leads:
                f.write(json.dumps(lead) + "\n")

    def test_run_returns_string(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        self._write_leads(tmp_path, [{"name": "Acme", "phone": "555-0000", "city": "Chicago"}])
        bot = CloserBot()
        result = bot.run()
        assert isinstance(result, str)

    def test_run_contains_attempted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        self._write_leads(tmp_path, [{"name": "Acme", "phone": "555-0000", "city": "Chicago"}])
        bot = CloserBot()
        result = bot.run()
        assert "Attempted" in result

    def test_free_tier_max_5_pitches(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        leads = [{"name": f"Biz{i}", "phone": "555-0000", "city": "City"} for i in range(10)]
        self._write_leads(tmp_path, leads)
        bot = CloserBot(tier=SalesTier.FREE)
        result = bot.run()
        assert "5" in result

    def test_generate_pitch_contains_name(self):
        bot = CloserBot()
        pitch = bot.generate_pitch({"name": "Cool Biz", "phone": "555-0000"})
        assert "Cool Biz" in pitch

    def test_generate_pitch_returns_string(self):
        bot = CloserBot()
        pitch = bot.generate_pitch({"name": "Any Biz"})
        assert isinstance(pitch, str)


class TestCloserBotDescribeTier:
    def test_describe_contains_closer(self):
        bot = CloserBot()
        desc = bot.describe_tier()
        assert "Closer Bot" in desc


# ---------------------------------------------------------------------------
# DealFinderBot
# ---------------------------------------------------------------------------

class TestDealFinderBotInstantiation:
    def test_default_tier_is_free(self):
        bot = DealFinderBot()
        assert bot.tier == LeadTier.FREE

    def test_pro_tier(self):
        from bots.real_estate_bot.tiers import get_bot_tier_info
        bot = DealFinderBot(tier=LeadTier.PRO)
        assert bot.tier == LeadTier.PRO

    def test_name(self):
        bot = DealFinderBot()
        assert bot.name == "Real Estate Deal Finder"

    def test_bot_alias(self):
        bot = DealBot()
        assert isinstance(bot, DealFinderBot)


class TestDealFinderBotFindDeals:
    def test_returns_list(self):
        bot = DealFinderBot()
        deals = bot.find_deals()
        assert isinstance(deals, list)

    def test_free_tier_max_3(self):
        bot = DealFinderBot(tier=LeadTier.FREE)
        # Run multiple times to account for randomness
        for _ in range(10):
            deals = bot.find_deals()
            assert len(deals) <= 3

    def test_deal_has_price(self):
        bot = DealFinderBot()
        deals = bot.find_deals()
        for deal in deals:
            assert "price" in deal

    def test_deal_has_estimated_value(self):
        bot = DealFinderBot()
        deals = bot.find_deals()
        for deal in deals:
            assert "estimated_value" in deal

    def test_deal_estimated_value_exceeds_price(self):
        bot = DealFinderBot()
        for _ in range(5):
            deals = bot.find_deals()
            for deal in deals:
                assert deal["estimated_value"] > deal["price"]

    def test_deal_has_equity_spread(self):
        bot = DealFinderBot()
        deals = bot.find_deals()
        for deal in deals:
            assert "equity_spread" in deal

    def test_deal_has_roi_pct(self):
        bot = DealFinderBot()
        deals = bot.find_deals()
        for deal in deals:
            assert "roi_pct" in deal


class TestDealFinderBotRun:
    def test_run_returns_string(self):
        bot = DealFinderBot()
        result = bot.run()
        assert isinstance(result, str)

    def test_run_contains_found(self):
        bot = DealFinderBot()
        result = bot.run()
        assert "Found" in result


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class TestDashboardApp:
    def test_home_returns_200(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from dashboard.app import create_app
        flask_app = create_app(leads_path=str(tmp_path / "data" / "leads.json"))
        client = flask_app.test_client()
        response = client.get("/")
        assert response.status_code == 200

    def test_home_contains_dashboard_title(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from dashboard.app import create_app
        flask_app = create_app(leads_path=str(tmp_path / "data" / "leads.json"))
        client = flask_app.test_client()
        response = client.get("/")
        assert b"DreamCo Empire Dashboard" in response.data

    def test_home_shows_zero_leads_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from dashboard.app import create_app
        flask_app = create_app(leads_path=str(tmp_path / "data" / "leads.json"))
        client = flask_app.test_client()
        response = client.get("/")
        assert b"Leads: 0" in response.data

    def test_home_counts_leads_correctly(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        leads_file = tmp_path / "data" / "leads.json"
        leads_file.parent.mkdir(parents=True)
        with open(leads_file, "w") as f:
            for i in range(3):
                f.write(json.dumps({"name": f"Biz{i}"}) + "\n")
        from dashboard.app import create_app
        flask_app = create_app(leads_path=str(leads_file))
        client = flask_app.test_client()
        response = client.get("/")
        assert b"Leads: 3" in response.data

    def test_api_leads_endpoint(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from dashboard.app import create_app
        flask_app = create_app(leads_path=str(tmp_path / "data" / "leads.json"))
        client = flask_app.test_client()
        response = client.get("/api/leads")
        assert response.status_code == 200
        data = response.get_json()
        assert "leads" in data
        assert "est_revenue" in data


# ---------------------------------------------------------------------------
# LearningLoop
# ---------------------------------------------------------------------------

class TestLearningLoopInstantiation:
    def test_default_threshold(self):
        loop = LearningLoop()
        assert loop.underperform_threshold == 30

    def test_custom_threshold(self):
        loop = LearningLoop(underperform_threshold=50)
        assert loop.underperform_threshold == 50

    def test_no_generator_by_default(self):
        loop = LearningLoop()
        assert loop.generator is None


class TestLearningLoopPerformanceTracking:
    def test_track_and_retrieve(self):
        loop = LearningLoop()
        loop.track_performance("bot_a", 75.0)
        assert loop.get_performance_log()["bot_a"] == 75.0

    def test_multiple_bots(self):
        loop = LearningLoop()
        loop.track_performance("bot_a", 80.0)
        loop.track_performance("bot_b", 20.0)
        log = loop.get_performance_log()
        assert "bot_a" in log
        assert "bot_b" in log

    def test_get_underperformers_returns_low_scorers(self):
        loop = LearningLoop(underperform_threshold=30)
        loop.track_performance("good_bot", 90.0)
        loop.track_performance("bad_bot", 10.0)
        under = loop.get_underperformers()
        assert "bad_bot" in under
        assert "good_bot" not in under

    def test_no_underperformers_when_all_high(self):
        loop = LearningLoop(underperform_threshold=30)
        loop.track_performance("bot_a", 80.0)
        assert loop.get_underperformers() == []

    def test_log_is_copy(self):
        loop = LearningLoop()
        loop.track_performance("bot_a", 50.0)
        log = loop.get_performance_log()
        log["bot_a"] = 99.0
        assert loop.get_performance_log()["bot_a"] == 50.0


class TestLearningLoopTrackRevenue:
    def test_no_file_returns_zero(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        loop = LearningLoop()
        assert loop.track_revenue() == 0.0

    def test_counts_leads(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "data").mkdir()
        with open(tmp_path / "data" / "leads.json", "w") as f:
            for i in range(5):
                f.write(json.dumps({"name": f"Biz{i}"}) + "\n")
        loop = LearningLoop()
        assert loop.track_revenue() == 50.0


class TestLearningLoopOptimize:
    class _FakeGenerator:
        def __init__(self):
            self.created = []

        def create_bot(self, name):
            self.created.append(name)

    def test_low_revenue_creates_lead_booster(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)  # no leads.json → revenue = 0
        gen = self._FakeGenerator()
        loop = LearningLoop(generator=gen)
        loop.optimize()
        assert "lead_booster_bot" in gen.created

    def test_high_revenue_creates_sales_scaler(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "data").mkdir()
        with open(tmp_path / "data" / "leads.json", "w") as f:
            for i in range(60):  # 60 * $10 = $600 > 500
                f.write(json.dumps({"name": f"Biz{i}"}) + "\n")
        gen = self._FakeGenerator()
        loop = LearningLoop(generator=gen)
        loop.optimize()
        assert "sales_scaler_bot" in gen.created

    def test_underperformer_creates_optimized_bot(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        gen = self._FakeGenerator()
        loop = LearningLoop(generator=gen)
        loop.track_performance("old_bot", 5.0)
        loop.optimize()
        assert "old_bot_optimized" in gen.created

    def test_optimize_no_generator_does_not_raise(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        loop = LearningLoop(generator=None)
        loop.optimize()  # should not raise
