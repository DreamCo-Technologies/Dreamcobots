"""
Tests for bots/sales_bot/ — SMSBot, FollowUpBot, ConversionTracker, and SalesBot.
"""

import sys
import os
import json
import tempfile

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.sales_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    list_tiers,
    get_upgrade_path,
    FEATURE_SMS_OUTREACH,
    FEATURE_FOLLOWUP_BOT,
    FEATURE_CONVERSION_TRACKING,
    FEATURE_VOICE_BOT,
    FEATURE_REVENUE_TRACKING,
)
from bots.sales_bot.sms_bot import (
    SMSBot,
    DEFAULT_SMS_TEMPLATE,
    IRRESISTIBLE_OFFER_TEMPLATE,
)
from bots.sales_bot.followup_bot import FollowUpBot
from bots.sales_bot.conversion_tracker import ConversionTracker, LeadStatus
from bots.sales_bot.sales_bot import (
    SalesBot,
    SalesBotError,
    SalesBotTierError,
)


# ---------------------------------------------------------------------------
# Framework compliance
# ---------------------------------------------------------------------------

class TestFrameworkCompliance:
    def test_sms_bot_has_framework_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "sales_bot", "sms_bot.py")
        with open(path) as f:
            text = f.read()
        assert any(m in text for m in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW"))

    def test_followup_bot_has_framework_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "sales_bot", "followup_bot.py")
        with open(path) as f:
            text = f.read()
        assert any(m in text for m in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW"))

    def test_conversion_tracker_has_framework_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "sales_bot", "conversion_tracker.py")
        with open(path) as f:
            text = f.read()
        assert any(m in text for m in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW"))

    def test_sales_bot_has_framework_marker(self):
        path = os.path.join(REPO_ROOT, "bots", "sales_bot", "sales_bot.py")
        with open(path) as f:
            text = f.read()
        assert any(m in text for m in ("GlobalAISourcesFlow", "GLOBAL AI SOURCES FLOW"))


# ---------------------------------------------------------------------------
# Tiers
# ---------------------------------------------------------------------------

class TestSalesBotTiers:
    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_free_tier_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 99.0

    def test_enterprise_tier_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 299.0

    def test_free_max_messages(self):
        assert get_tier_config(Tier.FREE).max_messages_per_day == 3

    def test_pro_max_messages(self):
        assert get_tier_config(Tier.PRO).max_messages_per_day == 20

    def test_enterprise_unlimited_messages(self):
        config = get_tier_config(Tier.ENTERPRISE)
        assert config.max_messages_per_day is None
        assert config.is_unlimited() is True

    def test_all_tiers_have_sms_outreach(self):
        for tier in Tier:
            assert get_tier_config(tier).has_feature(FEATURE_SMS_OUTREACH)

    def test_free_lacks_followup(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_FOLLOWUP_BOT)

    def test_pro_has_followup(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_FOLLOWUP_BOT)

    def test_enterprise_has_voice(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_VOICE_BOT)

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None


# ---------------------------------------------------------------------------
# SMS Bot
# ---------------------------------------------------------------------------

class TestSMSBot:
    def test_build_message_uses_name(self):
        bot = SMSBot()
        lead = {"name": "John's Roofing", "phone": "+15550000001"}
        msg = bot.build_message(lead)
        assert "John's Roofing" in msg

    def test_default_template_present(self):
        assert "{name}" in DEFAULT_SMS_TEMPLATE

    def test_irresistible_offer_template(self):
        assert "5 people" in IRRESISTIBLE_OFFER_TEMPLATE
        assert "{name}" in IRRESISTIBLE_OFFER_TEMPLATE

    def test_send_sms_returns_record(self):
        bot = SMSBot()
        lead = {"name": "Alice", "phone": "+15550000001"}
        record = bot.send_sms(lead)
        assert record["status"] == "sent"
        assert record["lead_name"] == "Alice"

    def test_send_batch_capped_at_max(self):
        bot = SMSBot(max_per_cycle=3)
        leads = [{"name": f"Lead {i}", "phone": f"+1555{i:07d}"} for i in range(10)]
        results = bot.send_batch(leads)
        assert len(results) == 3

    def test_send_batch_fewer_than_max(self):
        bot = SMSBot(max_per_cycle=10)
        leads = [{"name": "A"}, {"name": "B"}]
        results = bot.send_batch(leads)
        assert len(results) == 2

    def test_get_messages_sent(self):
        bot = SMSBot()
        bot.send_sms({"name": "A", "phone": "+1"})
        bot.send_sms({"name": "B", "phone": "+2"})
        assert bot.get_send_count() == 2

    def test_run_returns_status(self):
        bot = SMSBot()
        result = bot.run()
        assert "SMS Bot" in result

    def test_custom_template(self):
        bot = SMSBot(template="Hello {name}!")
        lead = {"name": "Bob"}
        msg = bot.build_message(lead)
        assert msg == "Hello Bob!"

    def test_missing_name_uses_default(self):
        bot = SMSBot()
        lead = {"phone": "+15550000001"}
        msg = bot.build_message(lead)
        assert "there" in msg


# ---------------------------------------------------------------------------
# Follow-Up Bot
# ---------------------------------------------------------------------------

class TestFollowUpBot:
    def _make_leads_file(self, leads: list) -> str:
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        json.dump(leads, f)
        f.close()
        return f.name

    def test_run_with_no_file(self):
        bot = FollowUpBot(leads_path="/nonexistent/leads.json")
        result = bot.run()
        assert "No leads" in result

    def test_run_sends_followups(self):
        leads = [
            {"name": "Alice", "phone": "+1"},
            {"name": "Bob", "phone": "+2"},
            {"name": "Carol", "phone": "+3"},
        ]
        path = self._make_leads_file(leads)
        bot = FollowUpBot(leads_path=path, max_followups=3)
        result = bot.run()
        assert "3" in result
        assert bot.get_followup_count() == 3

    def test_run_capped_at_max_followups(self):
        leads = [{"name": f"Lead {i}", "phone": f"+{i}"} for i in range(10)]
        path = self._make_leads_file(leads)
        bot = FollowUpBot(leads_path=path, max_followups=2)
        bot.run()
        assert bot.get_followup_count() == 2

    def test_followup_message_includes_name(self):
        bot = FollowUpBot()
        lead = {"name": "Mike"}
        msg = bot.build_followup_message(lead)
        assert "Mike" in msg

    def test_send_followup_record(self):
        bot = FollowUpBot()
        lead = {"name": "Alice", "phone": "+1"}
        record = bot.send_followup(lead)
        assert record["status"] == "followup_sent"
        assert record["lead_name"] == "Alice"

    def test_get_followup_log(self):
        bot = FollowUpBot()
        bot.send_followup({"name": "A", "phone": "+1"})
        bot.send_followup({"name": "B", "phone": "+2"})
        log = bot.get_followup_log()
        assert len(log) == 2


# ---------------------------------------------------------------------------
# Conversion Tracker
# ---------------------------------------------------------------------------

class TestConversionTracker:
    def test_add_lead(self):
        tracker = ConversionTracker()
        lead = tracker.add_lead("lead001", "Alice", "+1")
        assert lead["lead_id"] == "lead001"
        assert lead["status"] == LeadStatus.NEW.value

    def test_update_status_interested(self):
        tracker = ConversionTracker()
        tracker.add_lead("l1", "Bob")
        updated = tracker.update_status("l1", LeadStatus.INTERESTED)
        assert updated["status"] == LeadStatus.INTERESTED.value

    def test_update_status_closed_adds_revenue(self):
        tracker = ConversionTracker(revenue_per_deal=50.0)
        tracker.add_lead("l1", "Alice")
        tracker.update_status("l1", LeadStatus.CLOSED)
        metrics = tracker.get_metrics()
        assert metrics["revenue_usd"] == 50.0
        assert metrics["deals_closed"] == 1

    def test_update_nonexistent_lead(self):
        tracker = ConversionTracker()
        result = tracker.update_status("nonexistent", LeadStatus.CLOSED)
        assert result is None

    def test_record_message_sent(self):
        tracker = ConversionTracker()
        tracker.record_message_sent()
        tracker.record_message_sent()
        metrics = tracker.get_metrics()
        assert metrics["messages_sent"] == 2

    def test_get_metrics_all_statuses(self):
        tracker = ConversionTracker(revenue_per_deal=100.0)
        tracker.add_lead("l1", "A")
        tracker.add_lead("l2", "B")
        tracker.add_lead("l3", "C")
        tracker.update_status("l1", LeadStatus.INTERESTED)
        tracker.update_status("l2", LeadStatus.CLOSED)
        tracker.update_status("l3", LeadStatus.NO_RESPONSE)
        metrics = tracker.get_metrics()
        assert metrics["leads_collected"] == 3
        assert metrics["interested"] == 1
        assert metrics["deals_closed"] == 1
        assert metrics["no_response"] == 1
        assert metrics["revenue_usd"] == 100.0

    def test_conversion_rate_calculated(self):
        tracker = ConversionTracker(revenue_per_deal=50.0)
        tracker.add_lead("l1", "A")
        tracker.add_lead("l2", "B")
        tracker.add_lead("l3", "C")
        tracker.add_lead("l4", "D")
        tracker.update_status("l1", LeadStatus.CLOSED)
        tracker.update_status("l2", LeadStatus.CLOSED)
        metrics = tracker.get_metrics()
        assert metrics["conversion_rate_pct"] == 50.0

    def test_get_leads_by_status(self):
        tracker = ConversionTracker()
        tracker.add_lead("l1", "A")
        tracker.add_lead("l2", "B")
        tracker.update_status("l1", LeadStatus.INTERESTED)
        interested = tracker.get_leads_by_status(LeadStatus.INTERESTED)
        assert len(interested) == 1
        assert interested[0]["lead_id"] == "l1"

    def test_get_conversion_log(self):
        tracker = ConversionTracker()
        tracker.add_lead("l1", "A")
        tracker.update_status("l1", LeadStatus.INTERESTED)
        tracker.update_status("l1", LeadStatus.CLOSED)
        log = tracker.get_conversion_log()
        assert len(log) == 2

    def test_multiple_closed_deals_revenue(self):
        tracker = ConversionTracker(revenue_per_deal=300.0)
        for i in range(3):
            tracker.add_lead(f"l{i}", f"Lead {i}")
            tracker.update_status(f"l{i}", LeadStatus.CLOSED)
        metrics = tracker.get_metrics()
        assert metrics["revenue_usd"] == 900.0
        assert metrics["deals_closed"] == 3


# ---------------------------------------------------------------------------
# Sales Bot
# ---------------------------------------------------------------------------

class TestSalesBot:
    def test_run_daily_cycle_free_tier(self):
        bot = SalesBot(tier=Tier.FREE, niche="roofing")
        leads = [{"name": f"Lead {i}", "phone": f"+1555{i}"} for i in range(5)]
        result = bot.run_daily_cycle(leads)
        assert result["leads_processed"] == 5
        assert result["messages_sent"] > 0

    def test_run_daily_cycle_no_leads(self):
        bot = SalesBot(tier=Tier.FREE)
        result = bot.run_daily_cycle([])
        assert result["leads_processed"] == 0
        assert result["messages_sent"] == 0

    def test_messages_capped_at_cycle_limit(self):
        bot = SalesBot(tier=Tier.FREE, messages_per_cycle=3)
        leads = [{"name": f"L{i}", "phone": f"+{i}"} for i in range(10)]
        result = bot.run_daily_cycle(leads)
        assert result["messages_sent"] == 3

    def test_close_deal(self):
        bot = SalesBot(tier=Tier.PRO)
        leads = [{"id": "l1", "name": "Alice", "phone": "+1"}]
        bot.run_daily_cycle(leads)
        result = bot.close_deal("l1")
        assert result["status"] == "closed"
        assert result["total_revenue_usd"] == 50.0

    def test_close_nonexistent_deal(self):
        bot = SalesBot(tier=Tier.FREE)
        result = bot.close_deal("nonexistent")
        assert "error" in result

    def test_mark_interested(self):
        bot = SalesBot(tier=Tier.FREE)
        bot.run_daily_cycle([{"id": "l1", "name": "Bob", "phone": "+1"}])
        result = bot.mark_interested("l1")
        assert result["status"] == "interested"

    def test_mark_no_response(self):
        bot = SalesBot(tier=Tier.FREE)
        bot.run_daily_cycle([{"id": "l1", "name": "Carol", "phone": "+1"}])
        result = bot.mark_no_response("l1")
        assert result["status"] == "no_response"

    def test_get_revenue(self):
        bot = SalesBot(tier=Tier.PRO)
        bot.run_daily_cycle([{"id": "l1", "name": "Alice", "phone": "+1"}])
        bot.close_deal("l1")
        assert bot.get_revenue() == 50.0

    def test_get_conversion_metrics(self):
        bot = SalesBot(tier=Tier.PRO)
        bot.run_daily_cycle([{"id": "l1", "name": "A"}, {"id": "l2", "name": "B"}])
        metrics = bot.get_conversion_metrics()
        assert "leads_collected" in metrics
        assert "messages_sent" in metrics
        assert "deals_closed" in metrics

    def test_get_offer_message(self):
        bot = SalesBot(tier=Tier.FREE, niche="roofing")
        msg = bot.get_offer_message("Mike's Roofing")
        assert "Mike's Roofing" in msg
        assert "5 people" in msg

    def test_pro_followup_enabled(self):
        bot = SalesBot(tier=Tier.PRO, niche="real_estate")
        result = bot.run_daily_cycle([])
        assert "Skipped" not in result["followup_result"]

    def test_free_followup_skipped(self):
        bot = SalesBot(tier=Tier.FREE)
        result = bot.run_daily_cycle([])
        assert "Skipped" in result["followup_result"]

    def test_run_returns_string(self):
        bot = SalesBot(tier=Tier.FREE, niche="roofing")
        result = bot.run()
        assert isinstance(result, str)
        assert "Sales Bot" in result

    def test_process_payload(self):
        bot = SalesBot(tier=Tier.FREE)
        result = bot.process({"leads": [{"name": "Alice", "phone": "+1"}]})
        assert result["leads_processed"] == 1

    def test_run_log_tracks_cycles(self):
        bot = SalesBot(tier=Tier.FREE)
        bot.run_daily_cycle([{"name": "A"}])
        bot.run_daily_cycle([{"name": "B"}])
        log = bot.get_run_log()
        assert len(log) == 2

    def test_niche_stored(self):
        bot = SalesBot(tier=Tier.FREE, niche="med_spa")
        result = bot.run_daily_cycle([])
        assert result["niche"] == "med_spa"
