"""
Tests for bots/wealth_system_bot/wealth_system_bot.py

Covers:
  1.  Tiers
  2.  Global Registry
  3.  Localization
  4.  Member Management
  5.  KYC / AML Compliance
  6.  Governance
  7.  Asset Allocation
  8.  Dividend Engine
  9.  DreamCoin
  10. Bot Tasks
  11. Referral System
  12. Analytics
  13. Chat and process interface
  14. Tier restrictions
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.wealth_system_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_WEALTH_HUBS,
    FEATURE_TREASURY_MANAGEMENT,
    FEATURE_GOVERNANCE_VOTING,
    FEATURE_DIVIDEND_ENGINE,
    FEATURE_ASSET_ALLOCATION,
    FEATURE_DREAMCOIN,
    FEATURE_KYC_COMPLIANCE,
    FEATURE_AML_COMPLIANCE,
    FEATURE_GLOBAL_REGISTRY,
    FEATURE_MULTI_LANGUAGE,
    FEATURE_MULTI_CURRENCY,
    FEATURE_INCOME_BOTS,
    FEATURE_ASSET_BOTS,
    FEATURE_TRADING_BOTS,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
    FEATURE_STRIPE_BILLING,
    FEATURE_REFERRAL_SYSTEM,
    FEATURE_MARKETPLACE,
)
from bots.wealth_system_bot.wealth_system_bot import (
    WealthSystemBot,
    WealthSystemBotError,
    WealthSystemBotTierError,
    WealthSystemBotNotFoundError,
    AssetTier,
    PayoutSchedule,
    BotType,
    ComplianceStatus,
    HubStatus,
    Language,
    Region,
    WealthHub,
    Member,
    GovernanceProposal,
    DividendRecord,
    AssetAllocation,
    ComplianceRecord,
    BotTask,
    RegionConfig,
    REGION_CONFIG_CATALOGUE,
    LANGUAGE_LABELS,
)


# ===========================================================================
# Helpers
# ===========================================================================

def _make_bot(tier: Tier = Tier.FREE) -> WealthSystemBot:
    return WealthSystemBot(tier=tier)


def _make_hub(bot: WealthSystemBot, owner_id: str = "owner_1", name: str = "Test Hub"):
    return bot.register_hub(
        owner_id=owner_id,
        name=name,
        city="Austin",
        state="TX",
        country="USA",
        region=Region.NORTH_AMERICA,
        language=Language.EN,
        currency="USD",
    )


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_free_price_zero(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_hub_limit(self):
        assert get_tier_config(Tier.FREE).max_hubs == 3

    def test_pro_unlimited_hubs(self):
        assert get_tier_config(Tier.PRO).max_hubs is None
        assert get_tier_config(Tier.PRO).is_unlimited_hubs() is True

    def test_enterprise_unlimited_hubs(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_hubs() is True

    def test_free_member_limit(self):
        assert get_tier_config(Tier.FREE).max_members_per_hub == 10

    def test_pro_member_limit(self):
        assert get_tier_config(Tier.PRO).max_members_per_hub == 100

    def test_enterprise_no_member_limit(self):
        assert get_tier_config(Tier.ENTERPRISE).max_members_per_hub is None

    def test_free_has_wealth_hubs(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_WEALTH_HUBS)

    def test_free_has_treasury_management(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_TREASURY_MANAGEMENT)

    def test_free_lacks_governance(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_GOVERNANCE_VOTING)

    def test_free_lacks_dividend_engine(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_DIVIDEND_ENGINE)

    def test_free_lacks_kyc(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_KYC_COMPLIANCE)

    def test_free_lacks_trading_bots(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_TRADING_BOTS)

    def test_pro_has_governance(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_GOVERNANCE_VOTING)

    def test_pro_has_dividend_engine(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_DIVIDEND_ENGINE)

    def test_pro_has_kyc(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_KYC_COMPLIANCE)

    def test_pro_has_aml(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_AML_COMPLIANCE)

    def test_pro_has_income_bots(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_INCOME_BOTS)

    def test_pro_has_asset_bots(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_ASSET_BOTS)

    def test_pro_lacks_trading_bots(self):
        assert not get_tier_config(Tier.PRO).has_feature(FEATURE_TRADING_BOTS)

    def test_pro_lacks_analytics(self):
        assert not get_tier_config(Tier.PRO).has_feature(FEATURE_ANALYTICS)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feat in [
            FEATURE_WEALTH_HUBS, FEATURE_TREASURY_MANAGEMENT, FEATURE_GOVERNANCE_VOTING,
            FEATURE_DIVIDEND_ENGINE, FEATURE_ASSET_ALLOCATION, FEATURE_DREAMCOIN,
            FEATURE_KYC_COMPLIANCE, FEATURE_AML_COMPLIANCE, FEATURE_GLOBAL_REGISTRY,
            FEATURE_MULTI_LANGUAGE, FEATURE_MULTI_CURRENCY, FEATURE_INCOME_BOTS,
            FEATURE_ASSET_BOTS, FEATURE_TRADING_BOTS, FEATURE_ANALYTICS,
            FEATURE_WHITE_LABEL, FEATURE_STRIPE_BILLING, FEATURE_REFERRAL_SYSTEM,
            FEATURE_MARKETPLACE,
        ]:
            assert cfg.has_feature(feat), f"Enterprise missing: {feat}"

    def test_upgrade_free_to_pro(self):
        assert get_upgrade_path(Tier.FREE).tier == Tier.PRO

    def test_upgrade_pro_to_enterprise(self):
        assert get_upgrade_path(Tier.PRO).tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_tier_config_is_dataclass(self):
        cfg = get_tier_config(Tier.PRO)
        assert isinstance(cfg, TierConfig)

    def test_list_tiers_order(self):
        tiers = list_tiers()
        assert tiers[0].tier == Tier.FREE
        assert tiers[1].tier == Tier.PRO
        assert tiers[2].tier == Tier.ENTERPRISE


# ===========================================================================
# 2. Global Registry
# ===========================================================================

class TestGlobalRegistry:
    def setup_method(self):
        self.bot = _make_bot(Tier.FREE)

    def test_register_hub_returns_wealth_hub(self):
        hub = _make_hub(self.bot)
        assert isinstance(hub, WealthHub)

    def test_register_hub_has_id(self):
        hub = _make_hub(self.bot)
        assert hub.hub_id.startswith("hub_")

    def test_register_hub_name(self):
        hub = _make_hub(self.bot, name="My Hub")
        assert hub.name == "My Hub"

    def test_register_hub_city_country(self):
        hub = _make_hub(self.bot)
        assert hub.city == "Austin"
        assert hub.country == "USA"

    def test_register_hub_region(self):
        hub = _make_hub(self.bot)
        assert hub.region == Region.NORTH_AMERICA

    def test_register_hub_status_active(self):
        hub = _make_hub(self.bot)
        assert hub.status == HubStatus.ACTIVE

    def test_register_hub_initial_treasury(self):
        hub = _make_hub(self.bot)
        assert hub.treasury_balance == 0.0

    def test_register_hub_language(self):
        hub = self.bot.register_hub(
            owner_id="u1", name="French Hub", city="Paris",
            state="IDF", country="France", region=Region.EUROPE,
            language=Language.FR, currency="EUR",
        )
        assert hub.language == Language.FR
        assert hub.currency == "EUR"

    def test_free_tier_max_3_hubs(self):
        for i in range(3):
            _make_hub(self.bot, name=f"Hub {i}")
        with pytest.raises(WealthSystemBotTierError):
            _make_hub(self.bot, name="Hub 4")

    def test_pro_tier_unlimited_hubs(self):
        bot = _make_bot(Tier.PRO)
        for i in range(5):
            _make_hub(bot, name=f"Hub {i}")
        assert len(bot.list_hubs()) == 5

    def test_get_hub_returns_hub(self):
        hub = _make_hub(self.bot)
        fetched = self.bot.get_hub(hub.hub_id)
        assert fetched.hub_id == hub.hub_id

    def test_get_hub_not_found(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.get_hub("nonexistent_hub")

    def test_list_hubs_all(self):
        _make_hub(self.bot, name="Hub A")
        _make_hub(self.bot, name="Hub B")
        assert len(self.bot.list_hubs()) == 2

    def test_list_hubs_filter_by_region(self):
        _make_hub(self.bot, name="NA Hub")
        # Each bot instance has its own hub store; EU hub on separate bot not visible here
        assert len(self.bot.list_hubs(region=Region.NORTH_AMERICA)) == 1
        assert len(self.bot.list_hubs(region=Region.EUROPE)) == 0

    def test_list_hubs_filter_by_region_multi(self):
        bot = _make_bot(Tier.PRO)
        bot.register_hub(
            owner_id="u1", name="NA Hub", city="NYC",
            state="NY", country="USA", region=Region.NORTH_AMERICA,
        )
        bot.register_hub(
            owner_id="u2", name="EU Hub", city="Berlin",
            state="BE", country="Germany", region=Region.EUROPE,
        )
        assert len(bot.list_hubs(region=Region.NORTH_AMERICA)) == 1
        assert len(bot.list_hubs(region=Region.EUROPE)) == 1

    def test_list_hubs_filter_by_country(self):
        _make_hub(self.bot, name="US Hub")
        hubs = self.bot.list_hubs(country="USA")
        assert len(hubs) == 1

    def test_list_hubs_filter_by_city(self):
        _make_hub(self.bot, name="Austin Hub")
        hubs = self.bot.list_hubs(city="Austin")
        assert len(hubs) == 1
        hubs_none = self.bot.list_hubs(city="Dallas")
        assert len(hubs_none) == 0

    def test_list_hubs_city_case_insensitive(self):
        _make_hub(self.bot)
        assert len(self.bot.list_hubs(city="austin")) == 1

    def test_get_region_config_returns_region_config(self):
        rc = self.bot.get_region_config(Region.NORTH_AMERICA)
        assert isinstance(rc, RegionConfig)

    def test_get_region_config_currency(self):
        rc = self.bot.get_region_config(Region.EUROPE)
        assert rc.default_currency == "EUR"

    def test_get_region_config_all_regions(self):
        for region in Region:
            rc = self.bot.get_region_config(region)
            assert rc.region == region

    def test_list_supported_regions(self):
        regions = self.bot.list_supported_regions()
        assert len(regions) == len(list(Region))
        assert Region.AFRICA in regions

    def test_region_config_has_kyc_requirements(self):
        rc = self.bot.get_region_config(Region.NORTH_AMERICA)
        assert len(rc.kyc_requirements) > 0

    def test_region_config_has_compliance_agencies(self):
        rc = self.bot.get_region_config(Region.EUROPE)
        assert len(rc.compliance_agencies) > 0

    def test_region_config_aml_threshold(self):
        rc = self.bot.get_region_config(Region.NORTH_AMERICA)
        assert rc.aml_threshold_usd > 0


# ===========================================================================
# 3. Localization
# ===========================================================================

class TestLocalization:
    def setup_method(self):
        self.bot = _make_bot(Tier.FREE)
        self.hub = _make_hub(self.bot)

    def test_get_language_label_english(self):
        assert self.bot.get_language_label(Language.EN) == "English"

    def test_get_language_label_spanish(self):
        assert self.bot.get_language_label(Language.ES) == "Spanish"

    def test_get_language_label_all(self):
        for lang in Language:
            label = self.bot.get_language_label(lang)
            assert isinstance(label, str) and len(label) > 0

    def test_language_labels_dict_complete(self):
        for lang in Language:
            assert lang in LANGUAGE_LABELS

    def test_translate_hub_summary_returns_dict(self):
        result = self.bot.translate_hub_summary(self.hub.hub_id, Language.EN)
        assert isinstance(result, dict)

    def test_translate_hub_summary_hub_id(self):
        result = self.bot.translate_hub_summary(self.hub.hub_id, Language.EN)
        assert result["hub_id"] == self.hub.hub_id

    def test_translate_hub_summary_english_greeting(self):
        result = self.bot.translate_hub_summary(self.hub.hub_id, Language.EN)
        assert "Welcome" in result["greeting"]

    def test_translate_hub_summary_spanish_greeting(self):
        result = self.bot.translate_hub_summary(self.hub.hub_id, Language.ES)
        assert "Bienvenido" in result["greeting"]

    def test_translate_hub_summary_french_greeting(self):
        result = self.bot.translate_hub_summary(self.hub.hub_id, Language.FR)
        assert "Bienvenue" in result["greeting"]

    def test_translate_hub_summary_language_field(self):
        result = self.bot.translate_hub_summary(self.hub.hub_id, Language.ZH)
        assert result["language"] == Language.ZH.value

    def test_translate_hub_summary_has_treasury(self):
        result = self.bot.translate_hub_summary(self.hub.hub_id, Language.EN)
        assert "treasury_balance" in result

    def test_translate_hub_summary_not_found(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.translate_hub_summary("bad_hub", Language.EN)


# ===========================================================================
# 4. Member Management
# ===========================================================================

class TestMemberManagement:
    def setup_method(self):
        self.bot = _make_bot(Tier.FREE)
        self.hub = _make_hub(self.bot)

    def test_add_member_returns_member(self):
        member = self.bot.add_member(self.hub.hub_id, "user_1")
        assert isinstance(member, Member)

    def test_add_member_has_id(self):
        member = self.bot.add_member(self.hub.hub_id, "user_1")
        assert member.member_id.startswith("mbr_")

    def test_add_member_links_to_hub(self):
        member = self.bot.add_member(self.hub.hub_id, "user_1")
        assert member.hub_id == self.hub.hub_id

    def test_add_member_zero_contribution(self):
        member = self.bot.add_member(self.hub.hub_id, "user_1")
        assert member.contribution_total == 0.0

    def test_add_member_appears_in_hub(self):
        member = self.bot.add_member(self.hub.hub_id, "user_1")
        assert member.member_id in self.bot.get_hub(self.hub.hub_id).members

    def test_get_member_returns_member(self):
        m = self.bot.add_member(self.hub.hub_id, "user_1")
        fetched = self.bot.get_member(m.member_id)
        assert fetched.member_id == m.member_id

    def test_get_member_not_found(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.get_member("nonexistent_member")

    def test_get_hub_members_returns_list(self):
        self.bot.add_member(self.hub.hub_id, "user_1")
        self.bot.add_member(self.hub.hub_id, "user_2")
        members = self.bot.get_hub_members(self.hub.hub_id)
        assert len(members) == 2

    def test_contribute_updates_treasury(self):
        m = self.bot.add_member(self.hub.hub_id, "user_1")
        self.bot.contribute(m.member_id, 1000.0)
        assert self.bot.get_hub(self.hub.hub_id).treasury_balance == 1000.0

    def test_contribute_updates_member_total(self):
        m = self.bot.add_member(self.hub.hub_id, "user_1")
        self.bot.contribute(m.member_id, 500.0)
        assert self.bot.get_member(m.member_id).contribution_total == 500.0

    def test_contribute_recalculates_ownership_single(self):
        m = self.bot.add_member(self.hub.hub_id, "user_1")
        self.bot.contribute(m.member_id, 1000.0)
        assert self.bot.get_member(m.member_id).ownership_pct == pytest.approx(100.0)

    def test_contribute_recalculates_ownership_two_members(self):
        m1 = self.bot.add_member(self.hub.hub_id, "user_1")
        m2 = self.bot.add_member(self.hub.hub_id, "user_2")
        self.bot.contribute(m1.member_id, 3000.0)
        self.bot.contribute(m2.member_id, 1000.0)
        assert self.bot.get_member(m1.member_id).ownership_pct == pytest.approx(75.0)
        assert self.bot.get_member(m2.member_id).ownership_pct == pytest.approx(25.0)

    def test_ownership_sums_to_100(self):
        m1 = self.bot.add_member(self.hub.hub_id, "user_1")
        m2 = self.bot.add_member(self.hub.hub_id, "user_2")
        m3 = self.bot.add_member(self.hub.hub_id, "user_3")
        self.bot.contribute(m1.member_id, 1000.0)
        self.bot.contribute(m2.member_id, 2000.0)
        self.bot.contribute(m3.member_id, 3000.0)
        total = sum(
            self.bot.get_member(mid).ownership_pct for mid in [m1.member_id, m2.member_id, m3.member_id]
        )
        assert total == pytest.approx(100.0)

    def test_free_tier_member_capacity(self):
        for i in range(10):
            self.bot.add_member(self.hub.hub_id, f"user_{i}")
        with pytest.raises(WealthSystemBotTierError):
            self.bot.add_member(self.hub.hub_id, "user_overflow")

    def test_pro_tier_member_capacity_100(self):
        bot = _make_bot(Tier.PRO)
        hub = _make_hub(bot)
        for i in range(100):
            bot.add_member(hub.hub_id, f"user_{i}")
        with pytest.raises(WealthSystemBotTierError):
            bot.add_member(hub.hub_id, "user_overflow")

    def test_enterprise_no_member_limit(self):
        bot = _make_bot(Tier.ENTERPRISE)
        hub = _make_hub(bot)
        for i in range(120):
            bot.add_member(hub.hub_id, f"user_{i}")
        assert len(bot.get_hub_members(hub.hub_id)) == 120


# ===========================================================================
# 5. KYC / AML Compliance
# ===========================================================================

class TestKYCAMLCompliance:
    def setup_method(self):
        self.bot = _make_bot(Tier.PRO)
        self.hub = _make_hub(self.bot)

    def test_submit_kyc_returns_compliance_record(self):
        record = self.bot.submit_kyc("user_1", self.hub.hub_id, ["passport", "address"])
        assert isinstance(record, ComplianceRecord)

    def test_submit_kyc_pending_status(self):
        record = self.bot.submit_kyc("user_1", self.hub.hub_id, ["passport"])
        assert record.status == ComplianceStatus.PENDING

    def test_submit_kyc_has_id(self):
        record = self.bot.submit_kyc("user_1", self.hub.hub_id, ["passport"])
        assert record.record_id.startswith("kyc_")

    def test_submit_kyc_compliance_type(self):
        record = self.bot.submit_kyc("user_1", self.hub.hub_id, ["passport"])
        assert record.compliance_type == "kyc"

    def test_approve_kyc(self):
        record = self.bot.submit_kyc("user_1", self.hub.hub_id, ["passport"])
        approved = self.bot.approve_kyc(record.record_id)
        assert approved.status == ComplianceStatus.APPROVED

    def test_reject_kyc(self):
        record = self.bot.submit_kyc("user_1", self.hub.hub_id, ["passport"])
        rejected = self.bot.reject_kyc(record.record_id, "Documents expired")
        assert rejected.status == ComplianceStatus.REJECTED
        assert "expired" in rejected.notes

    def test_reject_kyc_not_found(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.reject_kyc("nonexistent_id", "reason")

    def test_approve_kyc_not_found(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.approve_kyc("nonexistent_id")

    def test_submit_aml_check_below_threshold_auto_approved(self):
        record = self.bot.submit_aml_check("user_1", self.hub.hub_id, 500.0)
        assert record.status == ComplianceStatus.APPROVED

    def test_submit_aml_check_above_threshold_pending(self):
        # North America threshold is $10,000
        record = self.bot.submit_aml_check("user_1", self.hub.hub_id, 15000.0)
        assert record.status == ComplianceStatus.PENDING

    def test_submit_aml_check_compliance_type(self):
        record = self.bot.submit_aml_check("user_1", self.hub.hub_id, 100.0)
        assert record.compliance_type == "aml"

    def test_submit_aml_has_id(self):
        record = self.bot.submit_aml_check("user_1", self.hub.hub_id, 100.0)
        assert record.record_id.startswith("aml_")

    def test_get_compliance_records(self):
        self.bot.submit_kyc("user_1", self.hub.hub_id, ["id"])
        self.bot.submit_aml_check("user_1", self.hub.hub_id, 500.0)
        records = self.bot.get_compliance_records(self.hub.hub_id)
        assert len(records) == 2

    def test_get_compliance_records_empty(self):
        assert self.bot.get_compliance_records(self.hub.hub_id) == []

    def test_kyc_requires_pro_tier(self):
        free_bot = _make_bot(Tier.FREE)
        hub = _make_hub(free_bot)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.submit_kyc("user_1", hub.hub_id, ["passport"])

    def test_aml_requires_pro_tier(self):
        free_bot = _make_bot(Tier.FREE)
        hub = _make_hub(free_bot)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.submit_aml_check("user_1", hub.hub_id, 500.0)

    def test_aml_different_region_threshold(self):
        bot = _make_bot(Tier.PRO)
        # Africa threshold is $3,000
        hub = bot.register_hub(
            owner_id="o1", name="Africa Hub", city="Lagos",
            state="Lagos", country="Nigeria", region=Region.AFRICA,
        )
        record = bot.submit_aml_check("u1", hub.hub_id, 4000.0)
        assert record.status == ComplianceStatus.PENDING


# ===========================================================================
# 6. Governance
# ===========================================================================

class TestGovernance:
    def setup_method(self):
        self.bot = _make_bot(Tier.PRO)
        self.hub = _make_hub(self.bot)

    def test_create_proposal_returns_proposal(self):
        p = self.bot.create_proposal(self.hub.hub_id, "prop_1", "Title", "Desc")
        assert isinstance(p, GovernanceProposal)

    def test_create_proposal_has_id(self):
        p = self.bot.create_proposal(self.hub.hub_id, "prop_1", "Title", "Desc")
        assert p.proposal_id.startswith("prop_")

    def test_create_proposal_open_status(self):
        p = self.bot.create_proposal(self.hub.hub_id, "prop_1", "Title", "Desc")
        assert p.status == "open"

    def test_create_proposal_zero_votes(self):
        p = self.bot.create_proposal(self.hub.hub_id, "prop_1", "Title", "Desc")
        assert p.votes_for == 0
        assert p.votes_against == 0

    def test_vote_for_increments(self):
        p = self.bot.create_proposal(self.hub.hub_id, "prop_1", "Title", "Desc")
        updated = self.bot.vote_on_proposal(p.proposal_id, "voter_1", True)
        assert updated.votes_for == 1

    def test_vote_against_increments(self):
        p = self.bot.create_proposal(self.hub.hub_id, "prop_1", "Title", "Desc")
        updated = self.bot.vote_on_proposal(p.proposal_id, "voter_1", False)
        assert updated.votes_against == 1

    def test_vote_on_proposal_not_found(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.vote_on_proposal("bad_id", "voter", True)

    def test_finalize_proposal_approved(self):
        p = self.bot.create_proposal(self.hub.hub_id, "prop_1", "Title", "Desc")
        self.bot.vote_on_proposal(p.proposal_id, "v1", True)
        self.bot.vote_on_proposal(p.proposal_id, "v2", True)
        self.bot.vote_on_proposal(p.proposal_id, "v3", False)
        result = self.bot.finalize_proposal(p.proposal_id)
        assert result.status == "approved"

    def test_finalize_proposal_rejected(self):
        p = self.bot.create_proposal(self.hub.hub_id, "prop_1", "Title", "Desc")
        self.bot.vote_on_proposal(p.proposal_id, "v1", False)
        self.bot.vote_on_proposal(p.proposal_id, "v2", False)
        result = self.bot.finalize_proposal(p.proposal_id)
        assert result.status == "rejected"

    def test_finalize_proposal_tie_rejected(self):
        p = self.bot.create_proposal(self.hub.hub_id, "prop_1", "Title", "Desc")
        self.bot.vote_on_proposal(p.proposal_id, "v1", True)
        self.bot.vote_on_proposal(p.proposal_id, "v2", False)
        result = self.bot.finalize_proposal(p.proposal_id)
        assert result.status == "rejected"

    def test_finalize_proposal_not_found(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.finalize_proposal("bad_id")

    def test_list_proposals(self):
        self.bot.create_proposal(self.hub.hub_id, "p1", "Title 1", "Desc 1")
        self.bot.create_proposal(self.hub.hub_id, "p2", "Title 2", "Desc 2")
        proposals = self.bot.list_proposals(self.hub.hub_id)
        assert len(proposals) == 2

    def test_list_proposals_empty(self):
        assert self.bot.list_proposals(self.hub.hub_id) == []

    def test_governance_requires_pro_tier(self):
        free_bot = _make_bot(Tier.FREE)
        hub = _make_hub(free_bot)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.create_proposal(hub.hub_id, "p1", "Title", "Desc")


# ===========================================================================
# 7. Asset Allocation
# ===========================================================================

class TestAssetAllocation:
    def setup_method(self):
        self.bot = _make_bot(Tier.PRO)
        self.hub = _make_hub(self.bot)

    def test_set_asset_allocation_returns_allocation(self):
        alloc = self.bot.set_asset_allocation(
            self.hub.hub_id, 40, 40, 20, {"BTC": 0.2, "ETH": 0.2}
        )
        assert isinstance(alloc, AssetAllocation)

    def test_set_asset_allocation_stores_values(self):
        alloc = self.bot.set_asset_allocation(self.hub.hub_id, 40, 40, 20, {})
        assert alloc.stability_pct == 40
        assert alloc.growth_pct == 40
        assert alloc.high_growth_pct == 20

    def test_set_asset_allocation_invalid_sum_raises(self):
        with pytest.raises(ValueError):
            self.bot.set_asset_allocation(self.hub.hub_id, 50, 40, 20, {})

    def test_set_asset_allocation_zero_sum_raises(self):
        with pytest.raises(ValueError):
            self.bot.set_asset_allocation(self.hub.hub_id, 0, 0, 0, {})

    def test_get_asset_allocation_returns_allocation(self):
        self.bot.set_asset_allocation(self.hub.hub_id, 40, 40, 20, {})
        alloc = self.bot.get_asset_allocation(self.hub.hub_id)
        assert alloc.hub_id == self.hub.hub_id

    def test_get_asset_allocation_not_set(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.get_asset_allocation(self.hub.hub_id)

    def test_rebalance_portfolio_updates_timestamp(self):
        self.bot.set_asset_allocation(self.hub.hub_id, 40, 40, 20, {})
        alloc = self.bot.get_asset_allocation(self.hub.hub_id)
        first_ts = alloc.last_rebalanced
        rebalanced = self.bot.rebalance_portfolio(self.hub.hub_id)
        # last_rebalanced is refreshed on each call; the new timestamp is a valid ISO string
        assert isinstance(rebalanced.last_rebalanced, str)
        assert rebalanced.last_rebalanced >= first_ts

    def test_rebalance_portfolio_not_set(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.rebalance_portfolio(self.hub.hub_id)

    def test_asset_allocation_requires_pro_tier(self):
        free_bot = _make_bot(Tier.FREE)
        hub = _make_hub(free_bot)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.set_asset_allocation(hub.hub_id, 40, 40, 20, {})

    def test_asset_allocation_stores_assets_dict(self):
        assets = {"REAL_ESTATE": 0.5, "STOCKS": 0.3, "BONDS": 0.2}
        alloc = self.bot.set_asset_allocation(self.hub.hub_id, 40, 40, 20, assets)
        assert alloc.assets == assets


# ===========================================================================
# 8. Dividend Engine
# ===========================================================================

class TestDividendEngine:
    def setup_method(self):
        self.bot = _make_bot(Tier.PRO)
        self.hub = _make_hub(self.bot)
        m1 = self.bot.add_member(self.hub.hub_id, "user_1")
        m2 = self.bot.add_member(self.hub.hub_id, "user_2")
        self.bot.contribute(m1.member_id, 3000.0)
        self.bot.contribute(m2.member_id, 1000.0)
        self.m1 = m1
        self.m2 = m2

    def test_distribute_dividends_returns_record(self):
        record = self.bot.distribute_dividends(
            self.hub.hub_id, 1000.0, PayoutSchedule.MONTHLY
        )
        assert isinstance(record, DividendRecord)

    def test_distribute_dividends_has_id(self):
        record = self.bot.distribute_dividends(
            self.hub.hub_id, 1000.0, PayoutSchedule.MONTHLY
        )
        assert record.dividend_id.startswith("div_")

    def test_distribute_dividends_amount(self):
        record = self.bot.distribute_dividends(
            self.hub.hub_id, 1000.0, PayoutSchedule.MONTHLY
        )
        assert record.amount == 1000.0

    def test_distribute_dividends_proportional(self):
        record = self.bot.distribute_dividends(
            self.hub.hub_id, 1000.0, PayoutSchedule.MONTHLY
        )
        assert record.member_payouts[self.m1.member_id] == pytest.approx(750.0)
        assert record.member_payouts[self.m2.member_id] == pytest.approx(250.0)

    def test_distribute_dividends_with_reinvest(self):
        record = self.bot.distribute_dividends(
            self.hub.hub_id, 1000.0, PayoutSchedule.COMPOUND, reinvest_pct=20.0
        )
        # Only 80% distributed
        assert record.amount == pytest.approx(800.0)

    def test_distribute_dividends_reinvest_adds_to_treasury(self):
        initial = self.bot.get_hub(self.hub.hub_id).treasury_balance
        self.bot.distribute_dividends(
            self.hub.hub_id, 1000.0, PayoutSchedule.COMPOUND, reinvest_pct=10.0
        )
        new_balance = self.bot.get_hub(self.hub.hub_id).treasury_balance
        assert new_balance == pytest.approx(initial + 100.0)

    def test_get_dividend_history_returns_list(self):
        self.bot.distribute_dividends(self.hub.hub_id, 500.0, PayoutSchedule.WEEKLY)
        self.bot.distribute_dividends(self.hub.hub_id, 200.0, PayoutSchedule.MONTHLY)
        history = self.bot.get_dividend_history(self.hub.hub_id)
        assert len(history) == 2

    def test_get_dividend_history_empty(self):
        assert self.bot.get_dividend_history(self.hub.hub_id) == []

    def test_dividend_requires_pro_tier(self):
        free_bot = _make_bot(Tier.FREE)
        hub = _make_hub(free_bot)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.distribute_dividends(hub.hub_id, 100.0, PayoutSchedule.MONTHLY)

    def test_distribute_payout_schedule_stored(self):
        record = self.bot.distribute_dividends(
            self.hub.hub_id, 100.0, PayoutSchedule.WEEKLY
        )
        assert record.payout_schedule == PayoutSchedule.WEEKLY


# ===========================================================================
# 9. DreamCoin
# ===========================================================================

class TestDreamCoin:
    def setup_method(self):
        self.bot = _make_bot(Tier.PRO)
        self.hub = _make_hub(self.bot)
        self.member = self.bot.add_member(self.hub.hub_id, "user_1")

    def test_stake_dreamcoin_returns_member(self):
        m = self.bot.stake_dreamcoin(self.member.member_id, 100.0)
        assert isinstance(m, Member)

    def test_stake_dreamcoin_adds_balance(self):
        self.bot.stake_dreamcoin(self.member.member_id, 100.0)
        assert self.bot.get_dreamcoin_balance(self.member.member_id) == 100.0

    def test_stake_dreamcoin_accumulates(self):
        self.bot.stake_dreamcoin(self.member.member_id, 50.0)
        self.bot.stake_dreamcoin(self.member.member_id, 75.0)
        assert self.bot.get_dreamcoin_balance(self.member.member_id) == 125.0

    def test_get_dreamcoin_balance_initial_zero(self):
        assert self.bot.get_dreamcoin_balance(self.member.member_id) == 0.0

    def test_dreamcoin_requires_pro_tier(self):
        free_bot = _make_bot(Tier.FREE)
        hub = _make_hub(free_bot)
        m = free_bot.add_member(hub.hub_id, "user_1")
        with pytest.raises(WealthSystemBotTierError):
            free_bot.stake_dreamcoin(m.member_id, 100.0)

    def test_get_dreamcoin_balance_member_not_found(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.get_dreamcoin_balance("bad_member_id")


# ===========================================================================
# 10. Bot Tasks
# ===========================================================================

class TestBotTasks:
    def setup_method(self):
        self.bot = _make_bot(Tier.PRO)
        self.hub = _make_hub(self.bot)

    def test_run_income_bot_returns_task(self):
        task = self.bot.run_income_bot(self.hub.hub_id, "Content income")
        assert isinstance(task, BotTask)

    def test_run_income_bot_type(self):
        task = self.bot.run_income_bot(self.hub.hub_id, "Content income")
        assert task.bot_type == BotType.INCOME

    def test_run_income_bot_earnings_range(self):
        for _ in range(20):
            task = self.bot.run_income_bot(self.hub.hub_id, "Test")
            assert 10.0 <= task.earnings_usd <= 500.0

    def test_run_income_bot_status_completed(self):
        task = self.bot.run_income_bot(self.hub.hub_id, "Test")
        assert task.status == "completed"

    def test_run_asset_bot_returns_task(self):
        task = self.bot.run_asset_bot(self.hub.hub_id, "Tokenized real estate")
        assert isinstance(task, BotTask)

    def test_run_asset_bot_type(self):
        task = self.bot.run_asset_bot(self.hub.hub_id, "Tokenized real estate")
        assert task.bot_type == BotType.ASSET

    def test_run_asset_bot_earnings_range(self):
        for _ in range(20):
            task = self.bot.run_asset_bot(self.hub.hub_id, "Test")
            assert 50.0 <= task.earnings_usd <= 1000.0

    def test_run_trading_bot_requires_enterprise(self):
        with pytest.raises(WealthSystemBotTierError):
            self.bot.run_trading_bot(self.hub.hub_id, "Trade algo")

    def test_run_trading_bot_enterprise(self):
        ent_bot = _make_bot(Tier.ENTERPRISE)
        hub = _make_hub(ent_bot)
        task = ent_bot.run_trading_bot(hub.hub_id, "Trade algo")
        assert isinstance(task, BotTask)
        assert task.bot_type == BotType.FINANCE

    def test_run_trading_bot_earnings_range(self):
        ent_bot = _make_bot(Tier.ENTERPRISE)
        hub = _make_hub(ent_bot)
        for _ in range(20):
            task = ent_bot.run_trading_bot(hub.hub_id, "Test")
            assert 20.0 <= task.earnings_usd <= 2000.0

    def test_list_bot_tasks_empty(self):
        assert self.bot.list_bot_tasks(self.hub.hub_id) == []

    def test_list_bot_tasks_returns_all(self):
        self.bot.run_income_bot(self.hub.hub_id, "Task 1")
        self.bot.run_income_bot(self.hub.hub_id, "Task 2")
        self.bot.run_asset_bot(self.hub.hub_id, "Task 3")
        assert len(self.bot.list_bot_tasks(self.hub.hub_id)) == 3

    def test_get_total_bot_earnings(self):
        t1 = self.bot.run_income_bot(self.hub.hub_id, "T1")
        t2 = self.bot.run_asset_bot(self.hub.hub_id, "T2")
        total = self.bot.get_total_bot_earnings(self.hub.hub_id)
        assert total == pytest.approx(t1.earnings_usd + t2.earnings_usd)

    def test_get_total_bot_earnings_empty(self):
        assert self.bot.get_total_bot_earnings(self.hub.hub_id) == 0.0

    def test_income_bot_requires_pro_tier(self):
        free_bot = _make_bot(Tier.FREE)
        hub = _make_hub(free_bot)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.run_income_bot(hub.hub_id, "Test")

    def test_asset_bot_requires_pro_tier(self):
        free_bot = _make_bot(Tier.FREE)
        hub = _make_hub(free_bot)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.run_asset_bot(hub.hub_id, "Test")


# ===========================================================================
# 11. Referral System
# ===========================================================================

class TestReferralSystem:
    def setup_method(self):
        self.bot = _make_bot(Tier.PRO)
        self.hub = _make_hub(self.bot)

    def test_generate_referral_link_returns_string(self):
        link = self.bot.generate_referral_link(self.hub.hub_id, "user_1")
        assert isinstance(link, str)

    def test_generate_referral_link_contains_hub_id(self):
        link = self.bot.generate_referral_link(self.hub.hub_id, "user_1")
        assert self.hub.hub_id in link

    def test_generate_referral_link_contains_user_id(self):
        link = self.bot.generate_referral_link(self.hub.hub_id, "user_1")
        assert "user_1" in link

    def test_generate_referral_link_is_url(self):
        link = self.bot.generate_referral_link(self.hub.hub_id, "user_1")
        assert link.startswith("https://")

    def test_generate_referral_link_unique(self):
        link1 = self.bot.generate_referral_link(self.hub.hub_id, "user_1")
        link2 = self.bot.generate_referral_link(self.hub.hub_id, "user_1")
        assert link1 != link2

    def test_referral_requires_pro_tier(self):
        free_bot = _make_bot(Tier.FREE)
        hub = _make_hub(free_bot)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.generate_referral_link(hub.hub_id, "user_1")


# ===========================================================================
# 12. Analytics
# ===========================================================================

class TestAnalytics:
    def setup_method(self):
        self.bot = _make_bot(Tier.ENTERPRISE)
        self.hub = _make_hub(self.bot)
        m1 = self.bot.add_member(self.hub.hub_id, "user_1")
        m2 = self.bot.add_member(self.hub.hub_id, "user_2")
        self.bot.contribute(m1.member_id, 5000.0)
        self.bot.contribute(m2.member_id, 3000.0)
        self.m1 = m1
        self.m2 = m2

    def test_get_hub_analytics_returns_dict(self):
        result = self.bot.get_hub_analytics(self.hub.hub_id)
        assert isinstance(result, dict)

    def test_get_hub_analytics_has_treasury_balance(self):
        result = self.bot.get_hub_analytics(self.hub.hub_id)
        assert result["treasury_balance"] == 8000.0

    def test_get_hub_analytics_member_count(self):
        result = self.bot.get_hub_analytics(self.hub.hub_id)
        assert result["member_count"] == 2

    def test_get_hub_analytics_total_contributions(self):
        result = self.bot.get_hub_analytics(self.hub.hub_id)
        assert result["total_contributions"] == 8000.0

    def test_get_hub_analytics_bot_earnings(self):
        self.bot.run_income_bot(self.hub.hub_id, "Task")
        result = self.bot.get_hub_analytics(self.hub.hub_id)
        assert result["total_bot_earnings"] > 0

    def test_get_hub_analytics_with_allocation(self):
        self.bot.set_asset_allocation(self.hub.hub_id, 40, 40, 20, {})
        result = self.bot.get_hub_analytics(self.hub.hub_id)
        assert result["allocation_summary"] is not None
        assert result["allocation_summary"]["stability_pct"] == 40

    def test_get_hub_analytics_no_allocation(self):
        result = self.bot.get_hub_analytics(self.hub.hub_id)
        assert result["allocation_summary"] is None

    def test_get_hub_analytics_total_dividends(self):
        self.bot.distribute_dividends(self.hub.hub_id, 500.0, PayoutSchedule.MONTHLY)
        result = self.bot.get_hub_analytics(self.hub.hub_id)
        assert result["total_dividends_distributed"] == 500.0

    def test_analytics_requires_enterprise_tier(self):
        pro_bot = _make_bot(Tier.PRO)
        hub = _make_hub(pro_bot)
        with pytest.raises(WealthSystemBotTierError):
            pro_bot.get_hub_analytics(hub.hub_id)

    def test_analytics_requires_enterprise_from_free(self):
        free_bot = _make_bot(Tier.FREE)
        hub = _make_hub(free_bot)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.get_hub_analytics(hub.hub_id)


# ===========================================================================
# 13. Chat and process interface
# ===========================================================================

class TestChatAndProcess:
    def setup_method(self):
        self.bot = _make_bot(Tier.FREE)
        self.hub = _make_hub(self.bot)

    def test_chat_returns_string(self):
        result = self.bot.chat("hello")
        assert isinstance(result, str)

    def test_chat_mentions_hub(self):
        result = self.bot.chat("tell me about wealth hub")
        assert "hub" in result.lower()

    def test_chat_mentions_member(self):
        result = self.bot.chat("how do I add a member?")
        assert "member" in result.lower()

    def test_chat_mentions_compliance(self):
        result = self.bot.chat("what is kyc compliance?")
        assert "kyc" in result.lower() or "compliance" in result.lower()

    def test_chat_mentions_dividend(self):
        result = self.bot.chat("how do dividends work?")
        assert "dividend" in result.lower()

    def test_chat_mentions_bot_tasks(self):
        result = self.bot.chat("tell me about income bots")
        assert "bot" in result.lower()

    def test_chat_mentions_analytics(self):
        result = self.bot.chat("show me analytics")
        assert "analytics" in result.lower()

    def test_chat_default_mentions_tier(self):
        result = self.bot.chat("random question")
        assert self.bot.tier.value in result

    def test_process_register_hub(self):
        result = self.bot.process({
            "action": "register_hub",
            "owner_id": "u1",
            "name": "Process Hub",
            "city": "Miami",
            "state": "FL",
            "country": "USA",
            "region": "north_america",
            "language": "en",
            "currency": "USD",
        })
        assert result["success"] is True
        assert isinstance(result["data"], WealthHub)

    def test_process_get_hub(self):
        result = self.bot.process({
            "action": "get_hub",
            "hub_id": self.hub.hub_id,
        })
        assert result["success"] is True

    def test_process_get_hub_not_found(self):
        result = self.bot.process({"action": "get_hub", "hub_id": "bad_id"})
        assert result["success"] is False

    def test_process_list_hubs(self):
        result = self.bot.process({"action": "list_hubs"})
        assert result["success"] is True
        assert isinstance(result["data"], list)

    def test_process_add_member(self):
        result = self.bot.process({
            "action": "add_member",
            "hub_id": self.hub.hub_id,
            "user_id": "user_proc",
        })
        assert result["success"] is True

    def test_process_contribute(self):
        m = self.bot.add_member(self.hub.hub_id, "user_c")
        result = self.bot.process({
            "action": "contribute",
            "member_id": m.member_id,
            "amount_usd": 500.0,
        })
        assert result["success"] is True

    def test_process_chat(self):
        result = self.bot.process({"action": "chat", "message": "hello"})
        assert result["success"] is True

    def test_process_unknown_action(self):
        result = self.bot.process({"action": "unknown_action"})
        assert result["success"] is False

    def test_process_missing_action(self):
        result = self.bot.process({})
        assert result["success"] is False


# ===========================================================================
# 14. Tier restrictions
# ===========================================================================

class TestTierRestrictions:
    def test_free_governance_blocked(self):
        bot = _make_bot(Tier.FREE)
        hub = _make_hub(bot)
        with pytest.raises(WealthSystemBotTierError):
            bot.create_proposal(hub.hub_id, "p", "T", "D")

    def test_free_dividend_blocked(self):
        bot = _make_bot(Tier.FREE)
        hub = _make_hub(bot)
        with pytest.raises(WealthSystemBotTierError):
            bot.distribute_dividends(hub.hub_id, 100.0, PayoutSchedule.MONTHLY)

    def test_free_dreamcoin_blocked(self):
        bot = _make_bot(Tier.FREE)
        hub = _make_hub(bot)
        m = bot.add_member(hub.hub_id, "u")
        with pytest.raises(WealthSystemBotTierError):
            bot.stake_dreamcoin(m.member_id, 10.0)

    def test_free_asset_allocation_blocked(self):
        bot = _make_bot(Tier.FREE)
        hub = _make_hub(bot)
        with pytest.raises(WealthSystemBotTierError):
            bot.set_asset_allocation(hub.hub_id, 40, 40, 20, {})

    def test_free_income_bot_blocked(self):
        bot = _make_bot(Tier.FREE)
        hub = _make_hub(bot)
        with pytest.raises(WealthSystemBotTierError):
            bot.run_income_bot(hub.hub_id, "T")

    def test_free_asset_bot_blocked(self):
        bot = _make_bot(Tier.FREE)
        hub = _make_hub(bot)
        with pytest.raises(WealthSystemBotTierError):
            bot.run_asset_bot(hub.hub_id, "T")

    def test_free_referral_blocked(self):
        bot = _make_bot(Tier.FREE)
        hub = _make_hub(bot)
        with pytest.raises(WealthSystemBotTierError):
            bot.generate_referral_link(hub.hub_id, "u")

    def test_pro_trading_bot_blocked(self):
        bot = _make_bot(Tier.PRO)
        hub = _make_hub(bot)
        with pytest.raises(WealthSystemBotTierError):
            bot.run_trading_bot(hub.hub_id, "T")

    def test_pro_analytics_blocked(self):
        bot = _make_bot(Tier.PRO)
        hub = _make_hub(bot)
        with pytest.raises(WealthSystemBotTierError):
            bot.get_hub_analytics(hub.hub_id)

    def test_tier_error_is_wealth_system_bot_error(self):
        assert issubclass(WealthSystemBotTierError, WealthSystemBotError)

    def test_not_found_error_is_wealth_system_bot_error(self):
        assert issubclass(WealthSystemBotNotFoundError, WealthSystemBotError)

    def test_enterprise_has_white_label(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_WHITE_LABEL)

    def test_pro_has_stripe_billing(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_STRIPE_BILLING)

    def test_free_lacks_white_label(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_WHITE_LABEL)
