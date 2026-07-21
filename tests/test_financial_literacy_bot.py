"""
Tests for bots/financial_literacy_bot/financial_literacy_bot.py

Covers:
  1. Tiers
  2. Credit Building Assistance (tips, profile analysis, alerts)
  3. OPM / Leverage Strategies
  4. Investment Calculators
  5. Bank / Credit Bureau Integration (mock)
  6. Automated Reminders
  7. Education Module
  8. Community Platform
  9. Analytics
  10. Chat & process interface
  11. run() helper (skipped — pragma: no cover)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.financial_literacy_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_CREDIT_TIPS,
    FEATURE_CREDIT_ALERTS,
    FEATURE_OPM_STRATEGIES,
    FEATURE_INVESTMENT_CALCULATOR,
    FEATURE_BANK_INTEGRATION,
    FEATURE_AUTOMATED_REMINDERS,
    FEATURE_EDUCATION_PATHS,
    FEATURE_COMMUNITY_READ,
    FEATURE_COMMUNITY_POST,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
    FEATURE_STRIPE_BILLING,
    FEATURE_PRODUCT_MATCHING,
)
from bots.financial_literacy_bot.financial_literacy_bot import (
    FinancialLiteracyBot,
    FinancialLiteracyBotError,
    FinancialLiteracyBotTierError,
    FinancialLiteracyBotNotFoundError,
    InvestmentType,
    CreditScoreRange,
    EducationLevel,
    ReminderType,
    EDUCATION_CATALOGUE,
    PRODUCT_CATALOGUE,
    OPM_STRATEGIES,
    CREDIT_TIPS,
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
        assert get_tier_config(Tier.PRO).price_usd_monthly == 29.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 99.0

    def test_free_has_credit_tips(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_CREDIT_TIPS)

    def test_free_lacks_credit_alerts(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_CREDIT_ALERTS)

    def test_free_lacks_opm(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_OPM_STRATEGIES)

    def test_pro_has_credit_alerts(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_CREDIT_ALERTS)

    def test_pro_has_opm(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_OPM_STRATEGIES)

    def test_pro_has_bank_integration(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_BANK_INTEGRATION)

    def test_pro_has_reminders(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_AUTOMATED_REMINDERS)

    def test_pro_lacks_community_post(self):
        assert not get_tier_config(Tier.PRO).has_feature(FEATURE_COMMUNITY_POST)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feat in [
            FEATURE_CREDIT_TIPS, FEATURE_CREDIT_ALERTS, FEATURE_OPM_STRATEGIES,
            FEATURE_INVESTMENT_CALCULATOR, FEATURE_BANK_INTEGRATION,
            FEATURE_AUTOMATED_REMINDERS, FEATURE_EDUCATION_PATHS,
            FEATURE_COMMUNITY_READ, FEATURE_COMMUNITY_POST,
            FEATURE_ANALYTICS, FEATURE_WHITE_LABEL, FEATURE_STRIPE_BILLING,
            FEATURE_PRODUCT_MATCHING,
        ]:
            assert cfg.has_feature(feat), f"Missing: {feat}"

    def test_free_module_limit(self):
        assert get_tier_config(Tier.FREE).max_education_modules == 3

    def test_pro_module_limit(self):
        assert get_tier_config(Tier.PRO).max_education_modules == 20

    def test_enterprise_unlimited_modules(self):
        assert get_tier_config(Tier.ENTERPRISE).max_education_modules is None
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_modules() is True

    def test_upgrade_free_to_pro(self):
        assert get_upgrade_path(Tier.FREE).tier == Tier.PRO

    def test_upgrade_pro_to_enterprise(self):
        assert get_upgrade_path(Tier.PRO).tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None


# ===========================================================================
# 2. Credit Building Assistance
# ===========================================================================

class TestCreditTips:
    def setup_method(self):
        self.bot = FinancialLiteracyBot(tier=Tier.FREE)

    def test_get_credit_tips_returns_list(self):
        tips = self.bot.get_credit_tips()
        assert isinstance(tips, list)
        assert len(tips) > 0

    def test_get_credit_tips_count(self):
        tips = self.bot.get_credit_tips(count=3)
        assert len(tips) == 3

    def test_get_credit_tips_count_one(self):
        tips = self.bot.get_credit_tips(count=1)
        assert len(tips) == 1

    def test_get_credit_tips_max_clamp(self):
        tips = self.bot.get_credit_tips(count=9999)
        assert len(tips) == len(CREDIT_TIPS)

    def test_get_credit_tips_are_strings(self):
        for tip in self.bot.get_credit_tips(5):
            assert isinstance(tip, str)
            assert len(tip) > 0

    def test_get_credit_tips_no_duplicates(self):
        tips = self.bot.get_credit_tips(5)
        assert len(tips) == len(set(tips))


class TestCreditProfileAnalysis:
    def setup_method(self):
        self.bot = FinancialLiteracyBot(tier=Tier.FREE)

    def test_analyze_returns_dict(self):
        result = self.bot.analyze_credit_profile(720, 10000, 2000)
        assert isinstance(result, dict)

    def test_analyze_returns_profile_id(self):
        result = self.bot.analyze_credit_profile(720, 10000, 2000)
        assert "profile_id" in result

    def test_analyze_returns_score_range(self):
        result = self.bot.analyze_credit_profile(720, 10000, 2000)
        assert result["score_range"] == "good"

    def test_analyze_exceptional_score(self):
        result = self.bot.analyze_credit_profile(820, 20000, 1000)
        assert result["score_range"] == "exceptional"

    def test_analyze_poor_score(self):
        result = self.bot.analyze_credit_profile(520, 5000, 4500)
        assert result["score_range"] == "poor"

    def test_analyze_high_utilization_advice(self):
        result = self.bot.analyze_credit_profile(680, 10000, 5000)
        assert result["utilization_rate"] == 0.5
        assert any("utilization" in a.lower() for a in result["advice"])

    def test_analyze_low_utilization_advice(self):
        result = self.bot.analyze_credit_profile(760, 20000, 500)
        assert any("excellent" in a.lower() or "below" in a.lower() for a in result["advice"])

    def test_analyze_missed_payments_advice(self):
        result = self.bot.analyze_credit_profile(650, 10000, 2000, missed_payments=2)
        assert any("missed" in a.lower() for a in result["advice"])

    def test_analyze_short_history_advice(self):
        result = self.bot.analyze_credit_profile(700, 10000, 1000, oldest_account_years=0.5)
        assert any("history" in a.lower() for a in result["advice"])

    def test_analyze_invalid_score_low(self):
        with pytest.raises(FinancialLiteracyBotError):
            self.bot.analyze_credit_profile(100, 10000, 2000)

    def test_analyze_invalid_score_high(self):
        with pytest.raises(FinancialLiteracyBotError):
            self.bot.analyze_credit_profile(900, 10000, 2000)

    def test_analyze_negative_limit_raises(self):
        with pytest.raises(FinancialLiteracyBotError):
            self.bot.analyze_credit_profile(700, -100, 200)

    def test_analyze_negative_balance_raises(self):
        with pytest.raises(FinancialLiteracyBotError):
            self.bot.analyze_credit_profile(700, 10000, -100)

    def test_analyze_stores_profile(self):
        result = self.bot.analyze_credit_profile(720, 10000, 2000)
        assert result["profile_id"] in self.bot._credit_profiles


class TestCreditAlerts:
    def setup_method(self):
        self.bot = FinancialLiteracyBot(tier=Tier.PRO)

    def test_alerts_returns_list(self):
        r = self.bot.analyze_credit_profile(700, 10000, 2000)
        alerts = self.bot.get_credit_alerts(r["profile_id"])
        assert isinstance(alerts, list)
        assert len(alerts) > 0

    def test_high_utilization_alert(self):
        r = self.bot.analyze_credit_profile(700, 10000, 4000)
        alerts = self.bot.get_credit_alerts(r["profile_id"])
        types = [a["type"] for a in alerts]
        assert "utilization_warning" in types

    def test_missed_payment_alert(self):
        r = self.bot.analyze_credit_profile(650, 10000, 1000, missed_payments=1)
        alerts = self.bot.get_credit_alerts(r["profile_id"])
        types = [a["type"] for a in alerts]
        assert "missed_payment" in types

    def test_low_score_alert(self):
        r = self.bot.analyze_credit_profile(600, 10000, 1000)
        alerts = self.bot.get_credit_alerts(r["profile_id"])
        types = [a["type"] for a in alerts]
        assert "score_at_risk" in types

    def test_healthy_profile_all_clear(self):
        r = self.bot.analyze_credit_profile(780, 20000, 1000)
        alerts = self.bot.get_credit_alerts(r["profile_id"])
        assert alerts[0]["type"] == "all_clear"

    def test_alerts_not_found_raises(self):
        with pytest.raises(FinancialLiteracyBotNotFoundError):
            self.bot.get_credit_alerts("nonexistent_id")

    def test_free_tier_cannot_get_alerts(self):
        bot = FinancialLiteracyBot(tier=Tier.FREE)
        with pytest.raises(FinancialLiteracyBotTierError):
            bot.get_credit_alerts("any_id")

    def test_alerts_have_severity(self):
        r = self.bot.analyze_credit_profile(700, 10000, 4000)
        alerts = self.bot.get_credit_alerts(r["profile_id"])
        for alert in alerts:
            assert "severity" in alert


# ===========================================================================
# 3. OPM Strategies
# ===========================================================================

class TestOPMStrategies:
    def setup_method(self):
        self.bot = FinancialLiteracyBot(tier=Tier.PRO)

    def test_get_strategies_returns_list(self):
        strategies = self.bot.get_opm_strategies(700)
        assert isinstance(strategies, list)
        assert len(strategies) > 0

    def test_low_score_fewer_strategies(self):
        high = self.bot.get_opm_strategies(800)
        low = self.bot.get_opm_strategies(400)
        assert len(high) >= len(low)

    def test_strategies_have_required_fields(self):
        for s in self.bot.get_opm_strategies(700):
            assert "strategy_id" in s
            assert "name" in s
            assert "description" in s
            assert "risk_level" in s
            assert "estimated_return_pct" in s

    def test_invalid_score_raises(self):
        with pytest.raises(FinancialLiteracyBotError):
            self.bot.get_opm_strategies(100)

    def test_free_tier_blocked(self):
        bot = FinancialLiteracyBot(tier=Tier.FREE)
        with pytest.raises(FinancialLiteracyBotTierError):
            bot.get_opm_strategies(700)

    def test_min_score_strategy(self):
        # The lowest min score strategy should appear for very low scores
        strategies = self.bot.get_opm_strategies(660)
        assert len(strategies) >= 1


# ===========================================================================
# 4. Investment Calculators
# ===========================================================================

class TestInvestmentCalculator:
    def setup_method(self):
        self.bot = FinancialLiteracyBot(tier=Tier.PRO)

    def test_calculate_roi_returns_dict(self):
        result = self.bot.calculate_roi(InvestmentType.REAL_ESTATE, 10000, 8.0, 5)
        assert isinstance(result, dict)

    def test_calculate_roi_has_required_fields(self):
        result = self.bot.calculate_roi(InvestmentType.STOCKS, 5000, 10.0, 3)
        for key in ("calc_id", "total_value", "net_profit", "roi_pct"):
            assert key in result

    def test_calculate_roi_positive_return(self):
        result = self.bot.calculate_roi(InvestmentType.STOCKS, 1000, 10.0, 10)
        assert result["total_value"] > 1000
        assert result["roi_pct"] > 0

    def test_calculate_roi_with_credit_cost(self):
        result = self.bot.calculate_roi(InvestmentType.REAL_ESTATE, 10000, 8.0, 5, credit_rate_pct=3.0)
        # Net profit should be lower than with 0% credit rate
        result_no_cost = self.bot.calculate_roi(InvestmentType.REAL_ESTATE, 10000, 8.0, 5, credit_rate_pct=0.0)
        assert result["net_profit"] < result_no_cost["net_profit"]

    def test_calculate_roi_compound_growth(self):
        result = self.bot.calculate_roi(InvestmentType.INDEX_FUND, 1000, 10.0, 1)
        assert abs(result["total_value"] - 1100.0) < 0.01

    def test_calculate_roi_negative_principal_raises(self):
        with pytest.raises(FinancialLiteracyBotError):
            self.bot.calculate_roi(InvestmentType.STOCKS, -1000, 10.0, 5)

    def test_calculate_roi_zero_years_raises(self):
        with pytest.raises(FinancialLiteracyBotError):
            self.bot.calculate_roi(InvestmentType.STOCKS, 1000, 10.0, 0)

    def test_free_tier_limited_calculations(self):
        bot = FinancialLiteracyBot(tier=Tier.FREE)
        bot.calculate_roi(InvestmentType.STOCKS, 1000, 8.0, 5)
        with pytest.raises(FinancialLiteracyBotTierError):
            bot.calculate_roi(InvestmentType.REAL_ESTATE, 1000, 8.0, 5)

    def test_get_calculations_returns_list(self):
        self.bot.calculate_roi(InvestmentType.STOCKS, 1000, 8.0, 5)
        calcs = self.bot.get_calculations()
        assert isinstance(calcs, list)
        assert len(calcs) == 1

    def test_multiple_calculations_stored(self):
        for i in range(3):
            self.bot.calculate_roi(InvestmentType.STARTUP, 1000 * (i + 1), 12.0, 3)
        calcs = self.bot.get_calculations()
        assert len(calcs) == 3

    def test_unique_calc_ids(self):
        self.bot.calculate_roi(InvestmentType.STOCKS, 1000, 8.0, 5)
        self.bot.calculate_roi(InvestmentType.REAL_ESTATE, 2000, 9.0, 7)
        calcs = self.bot.get_calculations()
        ids = [c["calc_id"] for c in calcs]
        assert len(ids) == len(set(ids))


# ===========================================================================
# 5. Bank / Credit Bureau Integration
# ===========================================================================

class TestBankIntegration:
    def setup_method(self):
        self.bot = FinancialLiteracyBot(tier=Tier.PRO)

    def test_fetch_credit_score_returns_dict(self):
        result = self.bot.fetch_credit_score("user123")
        assert isinstance(result, dict)

    def test_fetch_credit_score_has_score(self):
        result = self.bot.fetch_credit_score("user123")
        assert "credit_score" in result
        assert 300 <= result["credit_score"] <= 850

    def test_fetch_credit_score_deterministic(self):
        r1 = self.bot.fetch_credit_score("alice")
        r2 = self.bot.fetch_credit_score("alice")
        assert r1["credit_score"] == r2["credit_score"]

    def test_fetch_credit_score_different_users(self):
        r1 = self.bot.fetch_credit_score("alice")
        r2 = self.bot.fetch_credit_score("bob_different")
        # May differ (hash-based)
        assert isinstance(r1["credit_score"], int)
        assert isinstance(r2["credit_score"], int)

    def test_fetch_credit_score_empty_id_raises(self):
        with pytest.raises(FinancialLiteracyBotError):
            self.bot.fetch_credit_score("")

    def test_fetch_credit_score_free_tier_blocked(self):
        bot = FinancialLiteracyBot(tier=Tier.FREE)
        with pytest.raises(FinancialLiteracyBotTierError):
            bot.fetch_credit_score("user123")

    def test_match_products_returns_list(self):
        products = self.bot.match_financial_products(700)
        assert isinstance(products, list)

    def test_match_products_score_300_gets_secured_card(self):
        products = self.bot.match_financial_products(300)
        names = [p["name"] for p in products]
        assert any("secured" in n.lower() or "builder" in n.lower() for n in names)

    def test_match_products_high_score_more_options(self):
        low = self.bot.match_financial_products(580)
        high = self.bot.match_financial_products(800)
        assert len(high) >= len(low)

    def test_match_products_have_required_fields(self):
        for p in self.bot.match_financial_products(700):
            assert "product_id" in p
            assert "name" in p
            assert "apr_pct" in p

    def test_match_products_invalid_score(self):
        with pytest.raises(FinancialLiteracyBotError):
            self.bot.match_financial_products(200)

    def test_match_products_free_tier_blocked(self):
        bot = FinancialLiteracyBot(tier=Tier.FREE)
        with pytest.raises(FinancialLiteracyBotTierError):
            bot.match_financial_products(700)


# ===========================================================================
# 6. Automated Reminders
# ===========================================================================

class TestAutomatedReminders:
    def setup_method(self):
        self.bot = FinancialLiteracyBot(tier=Tier.PRO)

    def test_create_reminder_returns_dict(self):
        rem = self.bot.create_reminder(ReminderType.PAYMENT_DUE, "Pay your credit card bill!")
        assert isinstance(rem, dict)
        assert "reminder_id" in rem

    def test_create_reminder_not_sent(self):
        rem = self.bot.create_reminder(ReminderType.UTILIZATION_CHECK, "Check utilization!")
        assert rem["sent"] is False

    def test_create_reminder_with_due_date(self):
        rem = self.bot.create_reminder(ReminderType.PAYMENT_DUE, "Bill due", due_date="2026-04-01")
        assert rem["due_date"] == "2026-04-01"

    def test_send_reminders_marks_sent(self):
        self.bot.create_reminder(ReminderType.PAYMENT_DUE, "Pay bill!")
        sent = self.bot.send_reminders()
        assert len(sent) == 1
        assert "sent_at" in sent[0]

    def test_send_reminders_only_unsent(self):
        self.bot.create_reminder(ReminderType.PAYMENT_DUE, "First")
        self.bot.send_reminders()
        self.bot.create_reminder(ReminderType.CREDIT_REPORT, "Second")
        sent = self.bot.send_reminders()
        assert len(sent) == 1

    def test_get_reminders_returns_all(self):
        self.bot.create_reminder(ReminderType.PAYMENT_DUE, "A")
        self.bot.create_reminder(ReminderType.INVESTMENT_REVIEW, "B")
        all_rems = self.bot.get_reminders()
        assert len(all_rems) == 2

    def test_get_reminders_unsent_only(self):
        self.bot.create_reminder(ReminderType.PAYMENT_DUE, "A")
        self.bot.send_reminders()
        self.bot.create_reminder(ReminderType.CREDIT_REPORT, "B")
        unsent = self.bot.get_reminders(unsent_only=True)
        assert len(unsent) == 1

    def test_free_tier_blocked_create(self):
        bot = FinancialLiteracyBot(tier=Tier.FREE)
        with pytest.raises(FinancialLiteracyBotTierError):
            bot.create_reminder(ReminderType.PAYMENT_DUE, "Pay!")

    def test_free_tier_blocked_send(self):
        bot = FinancialLiteracyBot(tier=Tier.FREE)
        with pytest.raises(FinancialLiteracyBotTierError):
            bot.send_reminders()

    def test_multiple_reminders_unique_ids(self):
        r1 = self.bot.create_reminder(ReminderType.PAYMENT_DUE, "A")
        r2 = self.bot.create_reminder(ReminderType.CREDIT_REPORT, "B")
        assert r1["reminder_id"] != r2["reminder_id"]


# ===========================================================================
# 7. Education Module
# ===========================================================================

class TestEducationModule:
    def setup_method(self):
        self.free_bot = FinancialLiteracyBot(tier=Tier.FREE)
        self.pro_bot = FinancialLiteracyBot(tier=Tier.PRO)
        self.enterprise_bot = FinancialLiteracyBot(tier=Tier.ENTERPRISE)

    def test_free_tier_limited_modules(self):
        modules = self.free_bot.get_education_modules()
        assert len(modules) <= 3

    def test_pro_tier_more_modules(self):
        modules = self.pro_bot.get_education_modules()
        assert len(modules) > 3

    def test_enterprise_gets_all_modules(self):
        modules = self.enterprise_bot.get_education_modules()
        assert len(modules) == len(EDUCATION_CATALOGUE)

    def test_filter_by_level(self):
        modules = self.enterprise_bot.get_education_modules(level=EducationLevel.BEGINNER)
        for m in modules:
            assert m["level"] == "beginner"

    def test_filter_by_topic(self):
        modules = self.enterprise_bot.get_education_modules(topic="credit")
        for m in modules:
            assert "credit" in m["topic"].lower()

    def test_modules_have_required_fields(self):
        for m in self.pro_bot.get_education_modules():
            for key in ("module_id", "title", "level", "topic", "content_summary",
                        "estimated_minutes", "tags"):
                assert key in m

    def test_complete_module_returns_progress(self):
        result = self.pro_bot.complete_module("edu_001")
        assert result["completed"] is True
        assert "progress_pct" in result

    def test_complete_module_twice_no_duplicate(self):
        self.pro_bot.complete_module("edu_001")
        self.pro_bot.complete_module("edu_001")
        assert self.pro_bot._completed_modules.count("edu_001") == 1

    def test_complete_nonexistent_module_raises(self):
        with pytest.raises(FinancialLiteracyBotNotFoundError):
            self.pro_bot.complete_module("edu_9999")

    def test_complete_module_free_tier_blocked(self):
        with pytest.raises(FinancialLiteracyBotTierError):
            self.free_bot.complete_module("edu_001")

    def test_get_education_path_returns_dict(self):
        path = self.pro_bot.get_education_path()
        assert isinstance(path, dict)
        assert "next_modules" in path

    def test_get_education_path_excludes_completed(self):
        self.pro_bot.complete_module("edu_001")
        path = self.pro_bot.get_education_path()
        completed_ids = path["completed_modules"]
        assert "edu_001" in completed_ids
        next_ids = [m["module_id"] for m in path["next_modules"]]
        assert "edu_001" not in next_ids

    def test_get_education_path_free_tier_blocked(self):
        with pytest.raises(FinancialLiteracyBotTierError):
            self.free_bot.get_education_path()

    def test_next_modules_ordered_by_level(self):
        path = self.pro_bot.get_education_path()
        levels = [m["level"] for m in path["next_modules"]]
        level_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        ordered = sorted(levels, key=lambda l: level_order.get(l, 99))
        assert levels == ordered


# ===========================================================================
# 8. Community Platform
# ===========================================================================

class TestCommunityPlatform:
    def setup_method(self):
        self.free_bot = FinancialLiteracyBot(tier=Tier.FREE)
        self.enterprise_bot = FinancialLiteracyBot(tier=Tier.ENTERPRISE)

    def _seed_post(self):
        return self.enterprise_bot.create_community_post(
            "How I improved my credit score by 100 points",
            "I focused on paying down utilization first...",
            tags=["credit", "success"],
        )

    def test_get_posts_free_returns_list(self):
        posts = self.free_bot.get_community_posts()
        assert isinstance(posts, list)

    def test_create_post_enterprise(self):
        post = self._seed_post()
        assert "post_id" in post

    def test_create_post_free_tier_blocked(self):
        with pytest.raises(FinancialLiteracyBotTierError):
            self.free_bot.create_community_post("Title", "Body")

    def test_create_post_empty_title_raises(self):
        with pytest.raises(FinancialLiteracyBotError):
            self.enterprise_bot.create_community_post("", "Body text")

    def test_create_post_empty_body_raises(self):
        with pytest.raises(FinancialLiteracyBotError):
            self.enterprise_bot.create_community_post("Title", "")

    def test_get_posts_shows_created(self):
        self._seed_post()
        posts = self.enterprise_bot.get_community_posts()
        assert len(posts) == 1

    def test_get_posts_filter_by_tag(self):
        self._seed_post()
        self.enterprise_bot.create_community_post("OPM Story", "I used HELOC...", tags=["opm"])
        tagged = self.enterprise_bot.get_community_posts(tag="credit")
        assert len(tagged) == 1

    def test_reply_to_post(self):
        post = self._seed_post()
        reply = self.enterprise_bot.reply_to_post(post["post_id"], "Great strategy!")
        assert "reply_id" in reply

    def test_reply_to_nonexistent_post_raises(self):
        with pytest.raises(FinancialLiteracyBotNotFoundError):
            self.enterprise_bot.reply_to_post("post_9999", "Hello!")

    def test_reply_empty_body_raises(self):
        post = self._seed_post()
        with pytest.raises(FinancialLiteracyBotError):
            self.enterprise_bot.reply_to_post(post["post_id"], "")

    def test_reply_increments_count(self):
        post = self._seed_post()
        self.enterprise_bot.reply_to_post(post["post_id"], "Reply 1")
        self.enterprise_bot.reply_to_post(post["post_id"], "Reply 2")
        posts = self.enterprise_bot.get_community_posts()
        assert posts[0]["reply_count"] == 2

    def test_upvote_post(self):
        post = self._seed_post()
        result = self.enterprise_bot.upvote_post(post["post_id"])
        assert result["upvotes"] == 1

    def test_upvote_increments(self):
        post = self._seed_post()
        self.enterprise_bot.upvote_post(post["post_id"])
        result = self.enterprise_bot.upvote_post(post["post_id"])
        assert result["upvotes"] == 2

    def test_upvote_nonexistent_post_raises(self):
        with pytest.raises(FinancialLiteracyBotNotFoundError):
            self.enterprise_bot.upvote_post("post_9999")

    def test_upvote_available_on_free_tier(self):
        # Seed a post via enterprise bot, then copy it to free bot's store
        # to verify that free-tier can exercise the upvote (community read) feature.
        post = self._seed_post()
        post_obj = self.enterprise_bot._community_posts[0]
        self.free_bot._community_posts.append(post_obj)
        result = self.free_bot.upvote_post(post["post_id"])
        assert result["upvotes"] >= 1


# ===========================================================================
# 9. Analytics
# ===========================================================================

class TestAnalytics:
    def setup_method(self):
        self.bot = FinancialLiteracyBot(tier=Tier.ENTERPRISE)

    def test_get_analytics_returns_dict(self):
        result = self.bot.get_analytics()
        assert isinstance(result, dict)

    def test_analytics_has_required_fields(self):
        result = self.bot.get_analytics()
        for key in ("total_calculations", "total_reminders", "completed_modules",
                    "community_posts", "credit_profiles", "tier"):
            assert key in result

    def test_analytics_initial_zeros(self):
        result = self.bot.get_analytics()
        assert result["total_calculations"] == 0
        assert result["total_reminders"] == 0
        assert result["community_posts"] == 0

    def test_analytics_reflects_activity(self):
        self.bot.calculate_roi(InvestmentType.STOCKS, 1000, 8.0, 5)
        self.bot.create_community_post("Title", "Body")
        result = self.bot.get_analytics()
        assert result["total_calculations"] == 1
        assert result["community_posts"] == 1

    def test_sent_reminders_counted(self):
        self.bot.create_reminder(ReminderType.PAYMENT_DUE, "Pay!")
        self.bot.send_reminders()
        result = self.bot.get_analytics()
        assert result["sent_reminders"] == 1

    def test_free_tier_blocked(self):
        bot = FinancialLiteracyBot(tier=Tier.FREE)
        with pytest.raises(FinancialLiteracyBotTierError):
            bot.get_analytics()

    def test_pro_tier_blocked(self):
        bot = FinancialLiteracyBot(tier=Tier.PRO)
        with pytest.raises(FinancialLiteracyBotTierError):
            bot.get_analytics()


# ===========================================================================
# 10. Chat Interface
# ===========================================================================

class TestChatInterface:
    def setup_method(self):
        self.bot = FinancialLiteracyBot(tier=Tier.PRO)

    def test_chat_credit_tip(self):
        result = self.bot.chat("give me credit tips")
        assert isinstance(result, dict)
        assert "message" in result

    def test_chat_opm(self):
        result = self.bot.chat("tell me about OPM strategies")
        assert isinstance(result, dict)

    def test_chat_opm_free_tier_blocked_message(self):
        bot = FinancialLiteracyBot(tier=Tier.FREE)
        result = bot.chat("OPM leverage investing")
        assert "pro" in result["message"].lower() or "upgrade" in result["message"].lower()

    def test_chat_calculator(self):
        result = self.bot.chat("calculate my ROI")
        assert "calculate_roi" in result["message"]

    def test_chat_education(self):
        result = self.bot.chat("show me education modules")
        assert isinstance(result, dict)
        assert result["data"] is not None

    def test_chat_community(self):
        result = self.bot.chat("community posts")
        assert isinstance(result, dict)

    def test_chat_unknown(self):
        result = self.bot.chat("random unrelated message")
        assert "DreamCo Financial Literacy Bot" in result["message"]

    def test_chat_returns_tier_info(self):
        result = self.bot.chat("hello")
        assert "pro" in result["message"].lower()


# ===========================================================================
# 11. get_summary
# ===========================================================================

class TestGetSummary:
    def test_summary_returns_dict(self):
        bot = FinancialLiteracyBot(tier=Tier.FREE)
        summary = bot.get_summary()
        assert isinstance(summary, dict)

    def test_summary_has_tier(self):
        bot = FinancialLiteracyBot(tier=Tier.PRO)
        assert bot.get_summary()["tier"] == "pro"

    def test_summary_has_user_id(self):
        bot = FinancialLiteracyBot(user_id="test_user_42")
        assert bot.get_summary()["user_id"] == "test_user_42"

    def test_summary_initial_zeros(self):
        bot = FinancialLiteracyBot(tier=Tier.FREE)
        s = bot.get_summary()
        assert s["calculations_run"] == 0
        assert s["reminders_created"] == 0
        assert s["modules_completed"] == 0


# ===========================================================================
# 12. CreditProfile data class
# ===========================================================================

class TestCreditProfileModel:
    def test_utilization_rate_calculation(self):
        from bots.financial_literacy_bot.financial_literacy_bot import CreditProfile
        profile = CreditProfile(
            profile_id="p1", user_id="u1",
            credit_score=700, total_credit_limit=10000,
            total_balance=3000, on_time_payments=24,
            missed_payments=0, oldest_account_years=5.0,
        )
        assert abs(profile.utilization_rate - 0.30) < 0.001

    def test_utilization_rate_zero_limit(self):
        from bots.financial_literacy_bot.financial_literacy_bot import CreditProfile
        profile = CreditProfile(
            profile_id="p2", user_id="u1",
            credit_score=500, total_credit_limit=0,
            total_balance=0, on_time_payments=0,
            missed_payments=0, oldest_account_years=0.0,
        )
        assert profile.utilization_rate == 0.0

    def test_score_range_exceptional(self):
        from bots.financial_literacy_bot.financial_literacy_bot import CreditProfile
        profile = CreditProfile(
            profile_id="p3", user_id="u1",
            credit_score=820, total_credit_limit=50000,
            total_balance=1000, on_time_payments=100,
            missed_payments=0, oldest_account_years=10.0,
        )
        assert profile.score_range == CreditScoreRange.EXCEPTIONAL
