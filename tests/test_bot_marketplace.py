"""Tests for bots/bot_marketplace — at least 45 test cases."""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from bots.bot_marketplace.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_BROWSE,
    FEATURE_BUY_BOTS,
    FEATURE_SELL_BOTS,
    FEATURE_MONETIZE,
    FEATURE_UPSELL,
    FEATURE_ANALYTICS,
    FEATURE_FORTUNE500_INTEGRATION,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
)
from bots.bot_marketplace.marketplace_catalog import MarketplaceCatalog, BOT_CATEGORIES
from bots.bot_marketplace.monetization_engine import MonetizationEngine, UPSELL_TYPES
from bots.bot_marketplace.integration_hub import IntegrationHub, INTEGRATION_PARTNERS
from bots.bot_marketplace.bot_marketplace import (
    BotMarketplace,
    BotMarketplaceError,
    BotMarketplaceTierError,
)


# ===========================================================================
# Helpers
# ===========================================================================

def _active_listing(catalog: MarketplaceCatalog, **kwargs) -> dict:
    """Create and immediately approve a listing."""
    defaults = dict(
        seller_id="seller1",
        bot_name="TestBot",
        category="PRODUCTIVITY",
        description="A test bot",
        price_usd=19.99,
    )
    defaults.update(kwargs)
    listing = catalog.list_bot(**defaults)
    catalog.approve_listing(listing["listing_id"])
    return catalog.get_listing(listing["listing_id"])


# ===========================================================================
# Tier tests
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_free_price_zero(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_free_max_listings(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_listings == 1

    def test_pro_max_listings(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_listings == 10

    def test_enterprise_unlimited_listings(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_listings is None
        assert cfg.is_unlimited_listings()

    def test_free_max_purchases(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_purchases == 3

    def test_enterprise_unlimited_purchases(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_purchases is None

    def test_platform_fee_descends_with_tier(self):
        free_fee = get_tier_config(Tier.FREE).platform_fee_pct
        pro_fee = get_tier_config(Tier.PRO).platform_fee_pct
        ent_fee = get_tier_config(Tier.ENTERPRISE).platform_fee_pct
        assert free_fee > pro_fee > ent_fee

    def test_enterprise_platform_fee_10_pct(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.platform_fee_pct == 0.10

    def test_pro_platform_fee_15_pct(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.platform_fee_pct == 0.15

    def test_upgrade_from_free_is_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_from_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_enterprise_has_fortune500_feature(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_FORTUNE500_INTEGRATION)

    def test_free_lacks_analytics(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_ANALYTICS)

    def test_pro_has_analytics(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_ANALYTICS)


# ===========================================================================
# MarketplaceCatalog tests
# ===========================================================================

class TestMarketplaceCatalog:
    def setup_method(self):
        self.catalog = MarketplaceCatalog()

    def test_list_bot_returns_pending(self):
        listing = self.catalog.list_bot(
            seller_id="s1", bot_name="Bot A", category="ANALYTICS",
            description="desc", price_usd=10.0,
        )
        assert listing["status"] == "PENDING_REVIEW"

    def test_approve_listing_sets_active(self):
        listing = self.catalog.list_bot(
            seller_id="s1", bot_name="Bot B", category="FINANCE",
            description="desc", price_usd=5.0,
        )
        approved = self.catalog.approve_listing(listing["listing_id"])
        assert approved["status"] == "ACTIVE"

    def test_get_listing_returns_dict(self):
        listing = self.catalog.list_bot(
            seller_id="s1", bot_name="Bot C", category="CRM",
            description="desc", price_usd=0.0,
        )
        fetched = self.catalog.get_listing(listing["listing_id"])
        assert fetched["listing_id"] == listing["listing_id"]

    def test_get_listing_missing_raises(self):
        with pytest.raises(KeyError):
            self.catalog.get_listing("nonexistent-id")

    def test_search_only_returns_active(self):
        self.catalog.list_bot("s1", "PendingBot", "HR", "desc", 5.0)
        results = self.catalog.search_listings()
        assert all(r["status"] == "ACTIVE" for r in results)

    def test_search_by_query(self):
        _active_listing(self.catalog, bot_name="SuperSearch Bot", description="searches everything")
        _active_listing(self.catalog, bot_name="OtherBot", description="does other stuff")
        results = self.catalog.search_listings(query="supersearch")
        assert len(results) == 1
        assert results[0]["bot_name"] == "SuperSearch Bot"

    def test_search_by_category(self):
        _active_listing(self.catalog, category="GAMING")
        _active_listing(self.catalog, category="FINANCE")
        results = self.catalog.search_listings(category="GAMING")
        assert all(r["category"] == "GAMING" for r in results)

    def test_search_by_max_price(self):
        _active_listing(self.catalog, price_usd=10.0)
        _active_listing(self.catalog, price_usd=100.0)
        results = self.catalog.search_listings(max_price=50.0)
        assert all(r["price_usd"] <= 50.0 for r in results)

    def test_get_featured_bots_highest_rated(self):
        l1 = _active_listing(self.catalog, bot_name="HighRated")
        l2 = _active_listing(self.catalog, bot_name="LowRated")
        self.catalog.rate_bot(l1["listing_id"], "u1", 5)
        self.catalog.rate_bot(l2["listing_id"], "u2", 2)
        featured = self.catalog.get_featured_bots(1)
        assert featured[0]["listing_id"] == l1["listing_id"]

    def test_get_popular_bots(self):
        l1 = _active_listing(self.catalog, bot_name="PopularBot")
        l2 = _active_listing(self.catalog, bot_name="UnknownBot")
        l1["purchase_count"] = 50
        l2["purchase_count"] = 1
        popular = self.catalog.get_popular_bots(1)
        assert popular[0]["listing_id"] == l1["listing_id"]

    def test_get_new_arrivals_ordering(self):
        l1 = _active_listing(self.catalog, bot_name="FirstBot")
        l2 = _active_listing(self.catalog, bot_name="SecondBot")
        arrivals = self.catalog.get_new_arrivals(2)
        # most recent first — l2 was created after l1
        assert arrivals[0]["listing_id"] == l2["listing_id"]

    def test_rate_bot_valid(self):
        listing = _active_listing(self.catalog)
        entry = self.catalog.rate_bot(listing["listing_id"], "u1", 4, "Great bot!")
        assert entry["rating"] == 4
        assert entry["review"] == "Great bot!"

    def test_rate_bot_invalid_rating_raises(self):
        listing = _active_listing(self.catalog)
        with pytest.raises(ValueError):
            self.catalog.rate_bot(listing["listing_id"], "u1", 6)

    def test_get_bot_stats_no_ratings(self):
        listing = _active_listing(self.catalog)
        stats = self.catalog.get_bot_stats(listing["listing_id"])
        assert stats["avg_rating"] == 0.0
        assert stats["review_count"] == 0

    def test_get_bot_stats_with_ratings(self):
        listing = _active_listing(self.catalog)
        lid = listing["listing_id"]
        self.catalog.rate_bot(lid, "u1", 4)
        self.catalog.rate_bot(lid, "u2", 2)
        stats = self.catalog.get_bot_stats(lid)
        assert stats["avg_rating"] == 3.0
        assert stats["review_count"] == 2

    def test_invalid_category_raises(self):
        with pytest.raises(ValueError):
            self.catalog.list_bot("s1", "Bot", "INVALID_CAT", "desc", 10.0)

    def test_negative_price_raises(self):
        with pytest.raises(ValueError):
            self.catalog.list_bot("s1", "Bot", "FINANCE", "desc", -5.0)

    def test_all_categories_available(self):
        assert "PRODUCTIVITY" in BOT_CATEGORIES
        assert "HEALTHCARE" in BOT_CATEGORIES
        assert len(BOT_CATEGORIES) == 15


# ===========================================================================
# MonetizationEngine tests
# ===========================================================================

class TestMonetizationEngine:
    def setup_method(self):
        self.catalog = MarketplaceCatalog()
        self.engine = MonetizationEngine(catalog=self.catalog)

    def _listed_bot(self, price: float = 100.0) -> dict:
        return _active_listing(self.catalog, seller_id="seller1", price_usd=price)

    def test_purchase_bot_returns_transaction(self):
        listing = self._listed_bot()
        txn = self.engine.purchase_bot(listing["listing_id"], "buyer1")
        assert "transaction_id" in txn
        assert txn["buyer_id"] == "buyer1"

    def test_purchase_bot_platform_fee_15pct(self):
        listing = self._listed_bot(100.0)
        txn = self.engine.purchase_bot(listing["listing_id"], "buyer1", platform_fee_pct=0.15)
        assert txn["platform_fee"] == 15.0
        assert txn["seller_earnings"] == 85.0

    def test_purchase_bot_platform_fee_10pct(self):
        listing = self._listed_bot(200.0)
        txn = self.engine.purchase_bot(listing["listing_id"], "buyer1", platform_fee_pct=0.10)
        assert txn["platform_fee"] == 20.0
        assert txn["seller_earnings"] == 180.0

    def test_purchase_increments_purchase_count(self):
        listing = self._listed_bot()
        lid = listing["listing_id"]
        self.engine.purchase_bot(lid, "buyer1")
        self.engine.purchase_bot(lid, "buyer2")
        stats = self.catalog.get_bot_stats(lid)
        assert stats["purchase_count"] == 2

    def test_create_upsell(self):
        listing = self._listed_bot()
        upsell = self.engine.create_upsell(
            listing["listing_id"], "PREMIUM_SKILL", "Extra Skill", "Adds power", 9.99
        )
        assert "upsell_id" in upsell
        assert upsell["upsell_type"] == "PREMIUM_SKILL"

    def test_get_upsells_empty(self):
        listing = self._listed_bot()
        assert self.engine.get_upsells(listing["listing_id"]) == []

    def test_get_upsells_returns_all(self):
        listing = self._listed_bot()
        lid = listing["listing_id"]
        self.engine.create_upsell(lid, "PREMIUM_SKILL", "Skill 1", "d", 5.0)
        self.engine.create_upsell(lid, "PRO_TEMPLATE", "Tmpl", "d", 3.0)
        upsells = self.engine.get_upsells(lid)
        assert len(upsells) == 2

    def test_purchase_upsell(self):
        listing = self._listed_bot()
        upsell = self.engine.create_upsell(
            listing["listing_id"], "ADVANCED_API", "API Pack", "desc", 49.0
        )
        txn = self.engine.purchase_upsell(upsell["upsell_id"], "buyer1", platform_fee_pct=0.15)
        assert txn["gross_amount"] == 49.0
        assert txn["platform_fee"] == pytest.approx(7.35, rel=1e-2)

    def test_invalid_upsell_type_raises(self):
        listing = self._listed_bot()
        with pytest.raises(ValueError):
            self.engine.create_upsell(listing["listing_id"], "INVALID", "n", "d", 5.0)

    def test_seller_dashboard_totals(self):
        listing = self._listed_bot(100.0)
        lid = listing["listing_id"]
        self.engine.purchase_bot(lid, "b1", platform_fee_pct=0.15)
        self.engine.purchase_bot(lid, "b2", platform_fee_pct=0.15)
        dash = self.engine.get_seller_dashboard("seller1")
        assert dash["total_sales"] == 2
        assert dash["total_revenue"] == pytest.approx(200.0)
        assert dash["platform_fees_paid"] == pytest.approx(30.0)
        assert dash["net_earnings"] == pytest.approx(170.0)

    def test_seller_dashboard_top_bots(self):
        l1 = self._listed_bot(50.0)
        l2 = _active_listing(self.catalog, seller_id="seller1", price_usd=200.0)
        self.engine.purchase_bot(l1["listing_id"], "b1", 0.15)
        self.engine.purchase_bot(l2["listing_id"], "b2", 0.15)
        dash = self.engine.get_seller_dashboard("seller1")
        assert len(dash["top_bots"]) == 2

    def test_revenue_projection(self):
        listing = self._listed_bot(100.0)
        self.engine.purchase_bot(listing["listing_id"], "b1", 0.15)
        proj = self.engine.get_revenue_projection("seller1", months=6)
        assert proj["projection_months"] == 6
        assert proj["projected_net_earnings"] >= 0


# ===========================================================================
# IntegrationHub tests
# ===========================================================================

class TestIntegrationHub:
    def setup_method(self):
        self.hub = IntegrationHub()

    def test_register_integration(self):
        integ = self.hub.register_integration("listing1", "SALESFORCE")
        assert integ["partner"] == "SALESFORCE"
        assert integ["status"] == "REGISTERED"

    def test_register_invalid_partner_raises(self):
        with pytest.raises(ValueError):
            self.hub.register_integration("listing1", "INVALID_PARTNER")

    def test_get_integration(self):
        integ = self.hub.register_integration("listing1", "SAP")
        fetched = self.hub.get_integration(integ["integration_id"])
        assert fetched["integration_id"] == integ["integration_id"]

    def test_get_missing_integration_raises(self):
        with pytest.raises(KeyError):
            self.hub.get_integration("does-not-exist")

    def test_list_integrations_all(self):
        self.hub.register_integration("l1", "SLACK")
        self.hub.register_integration("l2", "JIRA")
        result = self.hub.list_integrations()
        assert len(result) == 2

    def test_list_integrations_filtered(self):
        self.hub.register_integration("l1", "SLACK")
        self.hub.register_integration("l2", "JIRA")
        result = self.hub.list_integrations(listing_id="l1")
        assert len(result) == 1
        assert result[0]["listing_id"] == "l1"

    def test_test_integration_connected(self):
        integ = self.hub.register_integration("l1", "ZENDESK")
        result = self.hub.test_integration(integ["integration_id"])
        assert result["status"] == "CONNECTED"
        assert "latency_ms" in result

    def test_generate_webhook(self):
        integ = self.hub.register_integration("l1", "HUBSPOT")
        webhook = self.hub.generate_integration_webhook(integ["integration_id"])
        assert "webhook_url" in webhook
        assert "secret_token" in webhook
        assert isinstance(webhook["events"], list)
        assert len(webhook["events"]) > 0

    def test_all_partners_registered(self):
        assert "SALESFORCE" in INTEGRATION_PARTNERS
        assert "TABLEAU" in INTEGRATION_PARTNERS
        assert len(INTEGRATION_PARTNERS) == 12


# ===========================================================================
# BotMarketplace tier-enforcement tests
# ===========================================================================

class TestBotMarketplaceTierEnforcement:
    def test_free_can_browse(self):
        mp = BotMarketplace(tier=Tier.FREE)
        assert isinstance(mp.browse(), list)

    def test_free_can_list_one_bot(self):
        mp = BotMarketplace(tier=Tier.FREE, user_id="seller_free")
        listing = mp.list_bot("MyBot", "PRODUCTIVITY", "A bot", 5.0)
        assert listing["status"] == "PENDING_REVIEW"

    def test_free_cannot_list_second_bot(self):
        mp = BotMarketplace(tier=Tier.FREE, user_id="seller_free")
        mp.list_bot("Bot1", "PRODUCTIVITY", "d", 5.0)
        with pytest.raises(BotMarketplaceTierError):
            mp.list_bot("Bot2", "FINANCE", "d", 10.0)

    def test_free_cannot_get_seller_dashboard(self):
        mp = BotMarketplace(tier=Tier.FREE)
        with pytest.raises(BotMarketplaceTierError):
            mp.get_seller_dashboard()

    def test_free_cannot_create_upsell(self):
        mp = BotMarketplace(tier=Tier.FREE)
        with pytest.raises(BotMarketplaceTierError):
            mp.create_upsell("lid", "PREMIUM_SKILL", "n", "d", 5.0)

    def test_free_cannot_register_integration(self):
        mp = BotMarketplace(tier=Tier.FREE)
        with pytest.raises(BotMarketplaceTierError):
            mp.register_integration("lid", "SALESFORCE")

    def test_free_max_3_purchases(self):
        mp = BotMarketplace(tier=Tier.FREE, user_id="buyer_free")
        catalog = mp.catalog
        # Create 4 listings as a different user
        lids = []
        for i in range(4):
            listing = catalog.list_bot("s0", f"Bot{i}", "PRODUCTIVITY", "d", 1.0)
            catalog.approve_listing(listing["listing_id"])
            lids.append(listing["listing_id"])
        mp.buy_bot(lids[0])
        mp.buy_bot(lids[1])
        mp.buy_bot(lids[2])
        with pytest.raises(BotMarketplaceTierError):
            mp.buy_bot(lids[3])

    def test_pro_can_sell(self):
        mp = BotMarketplace(tier=Tier.PRO, user_id="seller_pro")
        listing = mp.list_bot("ProBot", "ANALYTICS", "d", 49.0)
        assert "listing_id" in listing

    def test_pro_can_get_dashboard(self):
        mp = BotMarketplace(tier=Tier.PRO, user_id="seller_pro")
        dash = mp.get_seller_dashboard()
        assert dash["seller_id"] == "seller_pro"

    def test_pro_can_create_upsell(self):
        mp = BotMarketplace(tier=Tier.PRO, user_id="seller_pro")
        listing = mp.list_bot("ProBot", "ANALYTICS", "d", 49.0)
        upsell = mp.create_upsell(
            listing["listing_id"], "PREMIUM_SKILL", "Skill", "d", 9.99
        )
        assert "upsell_id" in upsell

    def test_pro_cannot_register_fortune500_integration(self):
        mp = BotMarketplace(tier=Tier.PRO)
        with pytest.raises(BotMarketplaceTierError):
            mp.register_integration("lid", "SALESFORCE")

    def test_enterprise_can_register_integration(self):
        mp = BotMarketplace(tier=Tier.ENTERPRISE, user_id="ent_seller")
        listing = mp.list_bot("EntBot", "SECURITY", "d", 199.0)
        catalog_listing = mp.catalog.approve_listing(listing["listing_id"])
        integ = mp.register_integration(listing["listing_id"], "ORACLE")
        assert integ["partner"] == "ORACLE"

    def test_enterprise_platform_fee_lower_than_pro(self):
        ent = get_tier_config(Tier.ENTERPRISE)
        pro = get_tier_config(Tier.PRO)
        assert ent.platform_fee_pct < pro.platform_fee_pct

    def test_enterprise_unlimited_listings(self):
        mp = BotMarketplace(tier=Tier.ENTERPRISE, user_id="ent_seller")
        for i in range(15):
            mp.list_bot(f"Bot{i}", "PRODUCTIVITY", "d", float(i))
        assert mp._user_listing_count == 15

    def test_get_tier_info_structure(self):
        mp = BotMarketplace(tier=Tier.PRO)
        info = mp.get_tier_info()
        assert "tier" in info
        assert "platform_fee_pct" in info

    def test_get_upgrade_info_free_to_pro(self):
        mp = BotMarketplace(tier=Tier.FREE)
        upgrade = mp.get_upgrade_info()
        assert upgrade is not None
        assert upgrade["tier"] == "pro"

    def test_get_upgrade_info_enterprise_none(self):
        mp = BotMarketplace(tier=Tier.ENTERPRISE)
        assert mp.get_upgrade_info() is None

    def test_chat_browse_response(self):
        mp = BotMarketplace(tier=Tier.FREE)
        response = mp.chat("browse marketplace")
        assert "listing" in response.lower() or "found" in response.lower()

    def test_chat_tier_info(self):
        mp = BotMarketplace(tier=Tier.PRO)
        response = mp.chat("what tier am I on?")
        assert "Pro" in response or "pro" in response

    def test_chat_upgrade_suggestion(self):
        mp = BotMarketplace(tier=Tier.FREE)
        response = mp.chat("upgrade my plan")
        assert "Pro" in response or "upgrade" in response.lower()

    def test_chat_generic_message(self):
        mp = BotMarketplace(tier=Tier.FREE)
        response = mp.chat("hello there")
        assert isinstance(response, str)
        assert len(response) > 0
