"""Tests for bots/legal_money_bot/tiers.py and bots/legal_money_bot/legal_money_bot.py"""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, "models"))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.legal_money_bot.legal_money_bot import LegalMoneyBot, LegalMoneyBotTierError
from bots.legal_money_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestInstantiation:
    def test_default_tier_is_free(self):
        bot = LegalMoneyBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = LegalMoneyBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = LegalMoneyBot()
        assert bot.config is not None

    def test_user_id_assigned_if_not_provided(self):
        bot = LegalMoneyBot()
        assert bot.user_id is not None
        assert len(bot.user_id) > 0

    def test_user_id_respected_if_provided(self):
        bot = LegalMoneyBot(user_id="test-user-123")
        assert bot.user_id == "test-user-123"

    def test_disclaimer_present(self):
        assert "LEGAL DISCLAIMER" in LegalMoneyBot.DISCLAIMER
        assert "not legal advice" in LegalMoneyBot.DISCLAIMER.lower() or \
               "NOT legal advice" in LegalMoneyBot.DISCLAIMER


# ---------------------------------------------------------------------------
# Tiers module
# ---------------------------------------------------------------------------

class TestTiersModule:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_free_features_is_list(self):
        assert isinstance(BOT_FEATURES[Tier.FREE.value], list)

    def test_pro_features_more_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_enterprise_features_nonempty(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) >= 1

    def test_get_bot_tier_info_free(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert "price_usd_monthly" in info
        assert isinstance(info["features"], list)
        assert info["price_usd_monthly"] == 0.0

    def test_get_bot_tier_info_pro(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] > 0

    def test_get_bot_tier_info_enterprise(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["tier"] == "enterprise"
        assert info["price_usd_monthly"] >= info["price_usd_monthly"]

    def test_support_level_present(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert "support_level" in info
            assert len(info["support_level"]) > 0


# ---------------------------------------------------------------------------
# Claim Finder
# ---------------------------------------------------------------------------

class TestClaimFinder:
    def test_free_returns_list(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.find_claims()
        assert isinstance(result, list)

    def test_free_limited_to_3(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.find_claims()
        assert len(result) <= 3

    def test_pro_returns_more_than_free(self):
        free_bot = LegalMoneyBot(tier=Tier.FREE)
        pro_bot = LegalMoneyBot(tier=Tier.PRO)
        free_result = free_bot.find_claims()
        pro_result = pro_bot.find_claims()
        assert len(pro_result) >= len(free_result)

    def test_enterprise_returns_all(self):
        bot = LegalMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.find_claims()
        assert len(result) >= 5

    def test_results_have_required_keys(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.find_claims()
        assert len(result) > 0
        for record in result:
            assert "case_id" in record
            assert "title" in record
            assert "source" in record
            assert "estimated_payout_usd" in record
            assert "disclaimer" in record

    def test_filter_by_category(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.find_claims(categories=["data_breach"])
        assert all(r["category"] == "data_breach" for r in result)

    def test_filter_by_source_pacer_requires_pro(self):
        bot_free = LegalMoneyBot(tier=Tier.FREE)
        with pytest.raises(LegalMoneyBotTierError):
            bot_free.find_claims(sources=["PACER"])

    def test_filter_by_source_pacer_pro_allowed(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.find_claims(sources=["PACER"])
        assert all(r["source"] == "PACER" for r in result)

    def test_filter_by_source_ftc_requires_pro(self):
        bot_free = LegalMoneyBot(tier=Tier.FREE)
        with pytest.raises(LegalMoneyBotTierError):
            bot_free.find_claims(sources=["FTC"])

    def test_filter_by_source_ftc_pro_allowed(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.find_claims(sources=["FTC"])
        assert all(r["source"] == "FTC" for r in result)

    def test_disclaimer_in_results(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.find_claims()
        for r in result:
            assert "LEGAL DISCLAIMER" in r["disclaimer"]

    def test_empty_category_filter_returns_nothing(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.find_claims(categories=["nonexistent_category"])
        assert result == []

    def test_tier_in_result(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.find_claims()
        for r in result:
            assert r["tier"] == "pro"


# ---------------------------------------------------------------------------
# Smart Questionnaire
# ---------------------------------------------------------------------------

class TestSmartQuestionnaire:
    def test_returns_questions_for_valid_case(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.run_eligibility_questionnaire("CA-2024-001")
        assert "questions" in result
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) > 0

    def test_returns_case_title(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.run_eligibility_questionnaire("CA-2024-001")
        assert "case_title" in result
        assert len(result["case_title"]) > 0

    def test_returns_eligibility_criteria(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.run_eligibility_questionnaire("CA-2024-001")
        assert "eligibility_criteria" in result
        assert isinstance(result["eligibility_criteria"], list)

    def test_disclaimer_in_result(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.run_eligibility_questionnaire("CA-2024-001")
        assert "disclaimer" in result

    def test_unknown_case_returns_error(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.run_eligibility_questionnaire("INVALID-CASE")
        assert "error" in result

    def test_free_limited_to_3_checks(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        for case_id in ["CA-2024-001", "CA-2024-002", "CA-2024-003"]:
            bot.run_eligibility_questionnaire(case_id)
        with pytest.raises(LegalMoneyBotTierError):
            bot.run_eligibility_questionnaire("CA-2024-004")

    def test_pro_unlimited_checks(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        for i in range(1, 9):
            case_id = f"CA-2024-00{i}"
            result = bot.run_eligibility_questionnaire(case_id)
            assert "questions" in result or "error" in result

    def test_score_guidance_present(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.run_eligibility_questionnaire("CA-2024-002")
        assert "score_guidance" in result


# ---------------------------------------------------------------------------
# Eligibility Scoring
# ---------------------------------------------------------------------------

class TestEligibilityScoring:
    def test_free_raises_tier_error(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        with pytest.raises(LegalMoneyBotTierError):
            bot.score_eligibility("CA-2024-001", {"q1": True})

    def test_pro_returns_score(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        answers = {"q1": True, "q2": True, "q3": False, "q4": True}
        result = bot.score_eligibility("CA-2024-001", answers)
        assert "eligibility_score" in result
        assert 0 <= result["eligibility_score"] <= 100

    def test_all_yes_gives_100(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        answers = {"q1": True, "q2": True, "q3": True, "q4": True}
        result = bot.score_eligibility("CA-2024-001", answers)
        assert result["eligibility_score"] == 100

    def test_all_no_gives_0(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        answers = {"q1": False, "q2": False, "q3": False, "q4": False}
        result = bot.score_eligibility("CA-2024-001", answers)
        assert result["eligibility_score"] == 0

    def test_estimated_payout_present(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        answers = {"q1": True, "q2": True}
        result = bot.score_eligibility("CA-2024-001", answers)
        assert "estimated_payout_usd" in result
        assert result["estimated_payout_usd"] >= 0

    def test_recommendation_present(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        answers = {"q1": True, "q2": True, "q3": True, "q4": True}
        result = bot.score_eligibility("CA-2024-001", answers)
        assert "recommendation" in result
        assert len(result["recommendation"]) > 0

    def test_invalid_case_returns_error(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.score_eligibility("INVALID", {"q1": True})
        assert "error" in result

    def test_empty_answers_returns_zero_score(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.score_eligibility("CA-2024-001", {})
        assert result["eligibility_score"] == 0

    def test_partial_score(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        answers = {"q1": True, "q2": False}
        result = bot.score_eligibility("CA-2024-001", answers)
        assert result["eligibility_score"] == 50

    def test_enterprise_can_score(self):
        bot = LegalMoneyBot(tier=Tier.ENTERPRISE)
        answers = {"q1": True, "q2": True}
        result = bot.score_eligibility("CA-2024-001", answers)
        assert "eligibility_score" in result


# ---------------------------------------------------------------------------
# Settlement Maximizer
# ---------------------------------------------------------------------------

class TestSettlementMaximizer:
    def test_free_raises_tier_error(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        with pytest.raises(LegalMoneyBotTierError):
            bot.get_settlement_tactics()

    def test_pro_returns_tactics(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.get_settlement_tactics()
        assert "tactics" in result
        assert isinstance(result["tactics"], list)
        assert len(result["tactics"]) > 0

    def test_tactics_have_required_keys(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.get_settlement_tactics()
        for tactic in result["tactics"]:
            assert "tactic" in tactic
            assert "description" in tactic
            assert "impact" in tactic

    def test_evidence_checklist_present(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.get_settlement_tactics()
        assert "evidence_checklist" in result
        assert isinstance(result["evidence_checklist"], list)
        assert len(result["evidence_checklist"]) > 0

    def test_case_specific_advice_with_case_id(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.get_settlement_tactics(case_id="CA-2024-001")
        assert "case_title" in result
        assert "estimated_payout_usd" in result
        assert "deadline" in result
        assert "category_specific_advice" in result

    def test_no_case_id_generic_result(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.get_settlement_tactics()
        assert "case_title" not in result

    def test_disclaimer_in_result(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.get_settlement_tactics()
        assert "disclaimer" in result

    def test_enterprise_can_access(self):
        bot = LegalMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.get_settlement_tactics()
        assert "tactics" in result


# ---------------------------------------------------------------------------
# Lawyer Matching
# ---------------------------------------------------------------------------

class TestLawyerMatching:
    def test_free_raises_tier_error(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        with pytest.raises(LegalMoneyBotTierError):
            bot.match_lawyers()

    def test_pro_returns_list(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.match_lawyers()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_results_have_required_keys(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.match_lawyers()
        for lawyer in result:
            assert "lawyer_id" in lawyer
            assert "name" in lawyer
            assert "contingency_fee_pct" in lawyer
            assert "rating" in lawyer
            assert "contingency_note" in lawyer

    def test_sorted_by_rating_desc(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.match_lawyers()
        ratings = [lw["rating"] for lw in result]
        assert ratings == sorted(ratings, reverse=True)

    def test_filter_by_state(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.match_lawyers(state="CA")
        for lw in result:
            assert "CA" in lw["licensed_states"]

    def test_filter_by_specialty(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.match_lawyers(specialty="data_breach")
        for lw in result:
            assert "data_breach" in lw["specialties"]

    def test_filter_by_case_id_uses_category(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.match_lawyers(case_id="CA-2024-001")
        for lw in result:
            assert "data_breach" in lw["specialties"]

    def test_no_match_returns_empty(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.match_lawyers(specialty="nonexistent_specialty")
        assert result == []

    def test_disclaimer_in_result(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.match_lawyers()
        for lw in result:
            assert "disclaimer" in lw

    def test_enterprise_can_match(self):
        bot = LegalMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.match_lawyers()
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Auto-Filing
# ---------------------------------------------------------------------------

class TestAutoFiling:
    def test_free_raises_tier_error(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        profile = {"name": "Jane Doe", "email": "jane@example.com"}
        with pytest.raises(LegalMoneyBotTierError):
            bot.prepare_claim_filing("CA-2024-001", profile)

    def test_pro_returns_filing_package(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        profile = {"name": "Jane Doe", "email": "jane@example.com"}
        result = bot.prepare_claim_filing("CA-2024-001", profile)
        assert "filing_id" in result
        assert "form_data" in result
        assert "submission_checklist" in result
        assert "estimated_payout_usd" in result

    def test_filing_id_format(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        profile = {"name": "Jane Doe", "email": "jane@example.com"}
        result = bot.prepare_claim_filing("CA-2024-001", profile)
        assert result["filing_id"].startswith("FILING-CA-2024-001-")

    def test_form_data_contains_user_info(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        profile = {"name": "Jane Doe", "email": "jane@example.com", "phone": "555-1234"}
        result = bot.prepare_claim_filing("CA-2024-001", profile)
        fd = result["form_data"]
        assert fd["claimant_name"] == "Jane Doe"
        assert fd["claimant_email"] == "jane@example.com"
        assert fd["claimant_phone"] == "555-1234"

    def test_missing_name_returns_error(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        profile = {"email": "jane@example.com"}
        result = bot.prepare_claim_filing("CA-2024-001", profile)
        assert "error" in result

    def test_missing_email_returns_error(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        profile = {"name": "Jane Doe"}
        result = bot.prepare_claim_filing("CA-2024-001", profile)
        assert "error" in result

    def test_invalid_case_returns_error(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        profile = {"name": "Jane Doe", "email": "jane@example.com"}
        result = bot.prepare_claim_filing("INVALID-CASE", profile)
        assert "error" in result

    def test_filing_added_to_session(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        profile = {"name": "Jane Doe", "email": "jane@example.com"}
        bot.prepare_claim_filing("CA-2024-001", profile)
        filings = bot.get_filed_claims()
        assert len(filings) == 1

    def test_multiple_filings_tracked(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        profile = {"name": "Jane Doe", "email": "jane@example.com"}
        bot.prepare_claim_filing("CA-2024-001", profile)
        bot.prepare_claim_filing("CA-2024-002", profile)
        assert len(bot.get_filed_claims()) == 2

    def test_get_filed_claims_requires_pro(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        with pytest.raises(LegalMoneyBotTierError):
            bot.get_filed_claims()

    def test_disclaimer_in_result(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        profile = {"name": "Jane Doe", "email": "jane@example.com"}
        result = bot.prepare_claim_filing("CA-2024-001", profile)
        assert "disclaimer" in result

    def test_submission_checklist_is_list(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        profile = {"name": "Jane Doe", "email": "jane@example.com"}
        result = bot.prepare_claim_filing("CA-2024-001", profile)
        assert isinstance(result["submission_checklist"], list)
        assert len(result["submission_checklist"]) > 0

    def test_notification_added_after_filing(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        profile = {"name": "Jane Doe", "email": "jane@example.com"}
        bot.prepare_claim_filing("CA-2024-001", profile)
        notifications = bot.get_notifications()
        assert len(notifications) >= 1


# ---------------------------------------------------------------------------
# Referral Tracking
# ---------------------------------------------------------------------------

class TestReferralTracking:
    def test_free_raises_tier_error(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        with pytest.raises(LegalMoneyBotTierError):
            bot.generate_referral_code()

    def test_pro_generates_code(self):
        bot = LegalMoneyBot(tier=Tier.PRO, user_id="abc12345")
        result = bot.generate_referral_code()
        assert "referral_code" in result
        assert result["referral_code"].startswith("LMB-")

    def test_same_code_on_repeat_call(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        r1 = bot.generate_referral_code()
        r2 = bot.generate_referral_code()
        assert r1["referral_code"] == r2["referral_code"]

    def test_reward_per_referral_present(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.generate_referral_code()
        assert "reward_per_referral_usd" in result
        assert result["reward_per_referral_usd"] > 0

    def test_record_referral_returns_dict(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.record_referral("other-user-id")
        assert "referral_id" in result
        assert "reward_usd" in result
        assert result["status"] == "confirmed"

    def test_enterprise_reward_higher(self):
        bot = LegalMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.record_referral("other-user-id", plan="enterprise")
        assert result["reward_usd"] > 10.0

    def test_referral_summary_totals(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        bot.record_referral("user-A")
        bot.record_referral("user-B")
        summary = bot.get_referral_summary()
        assert summary["total_referrals"] == 2
        assert summary["total_earned_usd"] == 20.0

    def test_referral_summary_free_raises(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        with pytest.raises(LegalMoneyBotTierError):
            bot.get_referral_summary()

    def test_notification_on_referral(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        bot.record_referral("friend-123")
        notifications = bot.get_notifications()
        assert any("Referral" in n["message"] for n in notifications)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class TestNotifications:
    def test_free_raises_tier_error(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        with pytest.raises(LegalMoneyBotTierError):
            bot.get_notifications()

    def test_empty_on_start(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.get_notifications()
        assert result == []

    def test_mark_read(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        bot.record_referral("user-x")
        notifications = bot.get_notifications()
        nid = notifications[0]["notification_id"]
        result = bot.mark_notification_read(nid)
        assert result["status"] == "ok"
        updated = bot.get_notifications()
        assert updated[0]["read"] is True

    def test_mark_unknown_notification_not_found(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.mark_notification_read("XXXX-UNKNOWN")
        assert result["status"] == "not_found"

    def test_mark_notification_read_requires_pro(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        with pytest.raises(LegalMoneyBotTierError):
            bot.mark_notification_read("ANY-ID")

    def test_notification_has_required_keys(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        bot.record_referral("user-x")
        notifications = bot.get_notifications()
        for n in notifications:
            assert "notification_id" in n
            assert "message" in n
            assert "created_at" in n
            assert "read" in n


# ---------------------------------------------------------------------------
# Analytics (ENTERPRISE+)
# ---------------------------------------------------------------------------

class TestAnalytics:
    def test_free_raises_tier_error(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        with pytest.raises(LegalMoneyBotTierError):
            bot.get_analytics()

    def test_pro_raises_tier_error(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        with pytest.raises(LegalMoneyBotTierError):
            bot.get_analytics()

    def test_enterprise_returns_analytics(self):
        bot = LegalMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.get_analytics()
        assert "total_active_cases" in result
        assert "total_potential_payout_usd" in result
        assert "cases_by_category" in result

    def test_total_active_cases_positive(self):
        bot = LegalMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.get_analytics()
        assert result["total_active_cases"] > 0

    def test_total_potential_payout_positive(self):
        bot = LegalMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.get_analytics()
        assert result["total_potential_payout_usd"] > 0

    def test_cases_by_category_is_dict(self):
        bot = LegalMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.get_analytics()
        assert isinstance(result["cases_by_category"], dict)

    def test_analytics_reflects_filings(self):
        bot = LegalMoneyBot(tier=Tier.ENTERPRISE)
        profile = {"name": "Jane", "email": "jane@example.com"}
        bot.prepare_claim_filing("CA-2024-001", profile)
        result = bot.get_analytics()
        assert result["claims_filed_this_session"] == 1


# ---------------------------------------------------------------------------
# Summary & describe_tier
# ---------------------------------------------------------------------------

class TestSummary:
    def test_get_summary_all_tiers(self):
        for tier in Tier:
            bot = LegalMoneyBot(tier=tier)
            summary = bot.get_summary()
            assert "user_id" in summary
            assert "tier" in summary
            assert "features" in summary
            assert "disclaimer" in summary

    def test_active_cases_in_summary(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        summary = bot.get_summary()
        assert "active_cases_available" in summary
        assert summary["active_cases_available"] >= 1

    def test_describe_tier_returns_string(self):
        for tier in Tier:
            bot = LegalMoneyBot(tier=tier)
            desc = bot.describe_tier()
            assert isinstance(desc, str)
            assert "LegalMoneyBot" in desc

    def test_describe_tier_contains_price(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        desc = bot.describe_tier()
        assert "$" in desc

    def test_describe_tier_contains_features(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        desc = bot.describe_tier()
        assert "✓" in desc or "\u2713" in desc


# ---------------------------------------------------------------------------
# Chat interface
# ---------------------------------------------------------------------------

class TestChatInterface:
    def test_claim_search_message(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.chat("find claims for me")
        assert "message" in result
        assert "data" in result

    def test_eligibility_message(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.chat("am I eligible for any class action?")
        assert "message" in result

    def test_settlement_message_free_upsell(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.chat("how do I maximize my settlement?")
        assert "PRO" in result["message"] or "upgrade" in result["message"].lower()

    def test_settlement_message_pro_returns_tactics(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.chat("show me settlement tactics")
        assert "data" in result
        assert result["data"] is not None

    def test_lawyer_message_free_upsell(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.chat("I need a lawyer")
        assert "PRO" in result["message"] or "upgrade" in result["message"].lower()

    def test_lawyer_message_pro_returns_lawyers(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.chat("find me an attorney")
        assert result["data"] is not None

    def test_referral_message_free_upsell(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.chat("referral code please")
        assert "PRO" in result["message"] or "upgrade" in result["message"].lower()

    def test_referral_message_pro_returns_code(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.chat("I want to refer a friend")
        assert result["data"] is not None

    def test_notification_message_free_upsell(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.chat("show my notifications")
        assert "PRO" in result["message"] or "upgrade" in result["message"].lower()

    def test_unknown_message_returns_summary(self):
        bot = LegalMoneyBot(tier=Tier.FREE)
        result = bot.chat("what is DreamCo?")
        assert "data" in result
        assert result["data"] is not None

    def test_notification_message_pro(self):
        bot = LegalMoneyBot(tier=Tier.PRO)
        result = bot.chat("what are my notifications?")
        assert "message" in result


# ---------------------------------------------------------------------------
# Bot Library registration
# ---------------------------------------------------------------------------

class TestBotLibraryRegistration:
    def test_legal_money_bot_in_library(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        bot_ids = [e["bot_id"] for e in lib.list_bots()]
        assert "legal_money_bot" in bot_ids

    def test_legal_money_bot_capabilities(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("legal_money_bot")
        assert "claim_finder" in entry.capabilities
        assert "settlement_maximizer" in entry.capabilities
        assert "lawyer_matching" in entry.capabilities
        assert "auto_filing" in entry.capabilities

    def test_legal_money_bot_category(self):
        from bots.global_bot_network.bot_library import BotLibrary, BotCategory
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("legal_money_bot")
        assert entry.category == BotCategory.FINANCE
