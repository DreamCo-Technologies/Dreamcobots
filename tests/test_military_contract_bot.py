"""
Comprehensive tests for the Military Contract Bot.

Covers:
- Tier configuration
- Contract search and filtering
- AI opportunity analysis
- Compliance checking (CMMC, FAR/DFARS, ITAR/EAR)
- Security module (encryption, RBAC, audit trail)
- Performance analytics
- Proposal submission
- API module
- Manual override system
"""

from __future__ import annotations

import sys
import os
import time
import pytest

# Set up path so local imports work
BOT_DIR = os.path.join(os.path.dirname(__file__), "..", "bots", "military-contract-bot")
sys.path.insert(0, BOT_DIR)

from military_contract_bot import (
    MilitaryContractBot,
    MilitaryContractBotTierError,
    Tier,
    TIER_LIMITS,
    TIER_PRICES,
    BOT_FEATURES,
    ContractStatus,
    MOCK_MILITARY_CONTRACTS,
)
from mil_security import (
    SecurityRole,
    User,
    AuditTrail,
    AuthorizationError,
    encrypt_data,
    decrypt_data,
    compute_hmac,
    verify_hmac,
)
from mil_compliance import (
    check_cmmc_compliance,
    CMMC_PRACTICES,
    classify_contract_value,
    validate_clauses,
    parse_solicitation,
    screen_export_control,
)
from mil_analytics import PerformanceTracker


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def free_bot():
    return MilitaryContractBot(tier=Tier.FREE)


@pytest.fixture
def pro_bot():
    return MilitaryContractBot(tier=Tier.PRO)


@pytest.fixture
def enterprise_bot():
    return MilitaryContractBot(tier=Tier.ENTERPRISE)


@pytest.fixture
def admin_user():
    return User(user_id="test_admin", role=SecurityRole.ADMIN, clearance_level=5)


@pytest.fixture
def officer_user():
    return User(user_id="test_officer", role=SecurityRole.OFFICER, clearance_level=3)


@pytest.fixture
def analyst_user():
    return User(user_id="test_analyst", role=SecurityRole.ANALYST, clearance_level=1)


@pytest.fixture
def viewer_user():
    return User(user_id="test_viewer", role=SecurityRole.VIEWER, clearance_level=0)


@pytest.fixture
def tracker():
    return PerformanceTracker()


@pytest.fixture
def audit():
    return AuditTrail()


# ---------------------------------------------------------------------------
# Tier configuration tests
# ---------------------------------------------------------------------------

class TestTierConfig:
    def test_tier_enum_values(self):
        assert Tier.FREE.value == "free"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_tier_limits_defined(self):
        for tier in Tier:
            assert tier in TIER_LIMITS

    def test_free_tier_limit(self):
        assert TIER_LIMITS[Tier.FREE]["results_per_search"] == 5

    def test_enterprise_tier_unlimited(self):
        assert TIER_LIMITS[Tier.ENTERPRISE]["results_per_search"] is None

    def test_tier_prices(self):
        assert TIER_PRICES[Tier.FREE] == 0
        assert TIER_PRICES[Tier.PRO] == 199
        assert TIER_PRICES[Tier.ENTERPRISE] == 499

    def test_enterprise_has_all_pro_features(self):
        pro = set(BOT_FEATURES[Tier.PRO])
        enterprise = set(BOT_FEATURES[Tier.ENTERPRISE])
        assert pro.issubset(enterprise)


# ---------------------------------------------------------------------------
# Bot initialisation tests
# ---------------------------------------------------------------------------

class TestBotInit:
    def test_default_tier_is_free(self):
        bot = MilitaryContractBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self, pro_bot):
        assert pro_bot.tier == Tier.PRO

    def test_enterprise_tier(self, enterprise_bot):
        assert enterprise_bot.tier == Tier.ENTERPRISE

    def test_has_analytics(self, free_bot):
        assert free_bot.analytics is not None

    def test_has_audit(self, free_bot):
        assert free_bot.audit is not None

    def test_has_override(self, free_bot):
        assert free_bot.override is not None

    def test_name_set(self, free_bot):
        assert free_bot.name == "MilitaryContractBot"

    def test_description_set(self, free_bot):
        assert len(free_bot.description) > 0

    def test_string_tier_coerced(self):
        bot = MilitaryContractBot(tier="pro")
        assert bot.tier == Tier.PRO


# ---------------------------------------------------------------------------
# Mock data tests
# ---------------------------------------------------------------------------

class TestMockData:
    def test_contracts_exist(self):
        assert len(MOCK_MILITARY_CONTRACTS) > 0

    def test_all_contracts_have_required_fields(self):
        required = {"id", "title", "agency", "type", "value", "naics", "deadline", "set_aside"}
        for c in MOCK_MILITARY_CONTRACTS:
            assert required.issubset(c.keys()), f"Missing fields in {c['id']}"

    def test_all_values_positive(self):
        for c in MOCK_MILITARY_CONTRACTS:
            assert c["value"] >= 0

    def test_has_dod_contracts(self):
        dod = [c for c in MOCK_MILITARY_CONTRACTS if "Defense" in c["agency"] or "Army" in c["agency"]]
        assert len(dod) > 0

    def test_has_grants(self):
        grants = [c for c in MOCK_MILITARY_CONTRACTS if c["type"] == "grant"]
        assert len(grants) > 0

    def test_has_cmmc_levels(self):
        for c in MOCK_MILITARY_CONTRACTS:
            assert "cmmc_level" in c
            assert 0 <= c["cmmc_level"] <= 3


# ---------------------------------------------------------------------------
# Search tests
# ---------------------------------------------------------------------------

class TestSearchContracts:
    def test_search_returns_list(self, enterprise_bot):
        results = enterprise_bot.search_contracts()
        assert isinstance(results, list)

    def test_free_tier_respects_limit(self, free_bot):
        results = free_bot.search_contracts()
        assert len(results) <= 5

    def test_keyword_filter(self, enterprise_bot):
        results = enterprise_bot.search_contracts(keyword="cybersecurity")
        assert all(
            "cybersecurity" in r["title"].lower() or "cybersecurity" in r["description"].lower()
            for r in results
        )

    def test_agency_filter(self, enterprise_bot):
        results = enterprise_bot.search_contracts(agency="DARPA")
        assert all("darpa" in r["agency"].lower() or "defense advanced" in r["agency"].lower() for r in results)

    def test_naics_filter(self, enterprise_bot):
        results = enterprise_bot.search_contracts(naics="5415")
        assert all(r["naics"].startswith("5415") for r in results)

    def test_min_value_filter(self, enterprise_bot):
        results = enterprise_bot.search_contracts(min_value=50_000_000)
        assert all(r["value"] >= 50_000_000 for r in results)

    def test_max_value_filter(self, enterprise_bot):
        results = enterprise_bot.search_contracts(max_value=10_000_000)
        assert all(r["value"] <= 10_000_000 for r in results)

    def test_set_aside_filter(self, enterprise_bot):
        results = enterprise_bot.search_contracts(set_aside="Small Business")
        assert all("small business" in r["set_aside"].lower() for r in results)

    def test_cmmc_level_filter(self, enterprise_bot):
        results = enterprise_bot.search_contracts(cmmc_level=3)
        assert all(r["cmmc_level"] >= 3 for r in results)

    def test_type_filter_contracts_only(self, enterprise_bot):
        results = enterprise_bot.search_contracts(opportunity_type="contract")
        assert all(r["type"] == "contract" for r in results)

    def test_no_results_for_nonsense_keyword(self, enterprise_bot):
        results = enterprise_bot.search_contracts(keyword="xyzzy123nonsense")
        assert results == []

    def test_empty_keyword_returns_all_within_limit(self, enterprise_bot):
        results = enterprise_bot.search_contracts()
        assert len(results) == len(MOCK_MILITARY_CONTRACTS)

    def test_analytics_incremented(self, enterprise_bot):
        before = enterprise_bot.analytics._counters.get("searches", 0)
        enterprise_bot.search_contracts()
        assert enterprise_bot.analytics._counters.get("searches", 0) == before + 1


# ---------------------------------------------------------------------------
# Get opportunity tests
# ---------------------------------------------------------------------------

class TestGetOpportunity:
    def test_returns_dict_for_valid_id(self, free_bot):
        valid_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        result = free_bot.get_opportunity(valid_id)
        assert result is not None
        assert result["id"] == valid_id

    def test_returns_none_for_invalid_id(self, free_bot):
        assert free_bot.get_opportunity("DOES-NOT-EXIST") is None

    def test_records_analytics(self, enterprise_bot):
        valid_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        before = enterprise_bot.analytics._counters.get("opportunities_viewed", 0)
        enterprise_bot.get_opportunity(valid_id)
        assert enterprise_bot.analytics._counters["opportunities_viewed"] == before + 1


# ---------------------------------------------------------------------------
# Deadline tests
# ---------------------------------------------------------------------------

class TestUpcomingDeadlines:
    def test_returns_list(self, enterprise_bot):
        results = enterprise_bot.get_upcoming_deadlines(days=9999)
        assert isinstance(results, list)

    def test_all_results_within_window(self, enterprise_bot):
        import datetime
        results = enterprise_bot.get_upcoming_deadlines(days=9999)
        today = datetime.date.today()
        for r in results:
            deadline = datetime.date.fromisoformat(r["deadline"])
            assert deadline >= today

    def test_sorted_by_days_remaining(self, enterprise_bot):
        results = enterprise_bot.get_upcoming_deadlines(days=9999)
        days = [r["days_remaining"] for r in results]
        assert days == sorted(days)

    def test_free_tier_respects_limit(self, free_bot):
        results = free_bot.get_upcoming_deadlines(days=9999)
        assert len(results) <= 5


# ---------------------------------------------------------------------------
# Analysis tests
# ---------------------------------------------------------------------------

class TestAnalyzeOpportunity:
    def test_analysis_requires_pro_tier(self, free_bot):
        opp_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        with pytest.raises(MilitaryContractBotTierError):
            free_bot.analyze_opportunity(opp_id)

    def test_analysis_returns_dict(self, pro_bot):
        opp_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        result = pro_bot.analyze_opportunity(opp_id)
        assert "analysis" in result
        assert "opportunity" in result

    def test_win_probability_in_range(self, pro_bot):
        opp_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        result = pro_bot.analyze_opportunity(opp_id)
        prob = result["analysis"]["win_probability_pct"]
        assert 0 <= prob <= 100

    def test_roi_score_in_range(self, pro_bot):
        opp_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        result = pro_bot.analyze_opportunity(opp_id)
        roi = result["analysis"]["roi_score"]
        assert 0.0 <= roi <= 10.0

    def test_recommended_action_valid(self, pro_bot):
        for opp in MOCK_MILITARY_CONTRACTS:
            result = pro_bot.analyze_opportunity(opp["id"])
            assert result["analysis"]["recommended_action"] in ("bid", "monitor", "skip")

    def test_key_requirements_list(self, pro_bot):
        opp_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        result = pro_bot.analyze_opportunity(opp_id)
        assert isinstance(result["analysis"]["key_requirements"], list)

    def test_solicitation_parsed(self, pro_bot):
        opp_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        result = pro_bot.analyze_opportunity(opp_id)
        assert "solicitation_parsed" in result["analysis"]

    def test_export_control_present(self, pro_bot):
        opp_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        result = pro_bot.analyze_opportunity(opp_id)
        assert "export_control" in result["analysis"]

    def test_invalid_id_returns_error(self, pro_bot):
        result = pro_bot.analyze_opportunity("INVALID-ID")
        assert "error" in result


# ---------------------------------------------------------------------------
# Compliance tests
# ---------------------------------------------------------------------------

class TestCMMCCompliance:
    def test_empty_controls_not_compliant_level1(self):
        result = check_cmmc_compliance([], 1)
        assert not result["compliant"]
        assert result["level"] == 1
        assert len(result["missing"]) > 0

    def test_full_controls_compliant_level1(self):
        controls = list(CMMC_PRACTICES[1])
        result = check_cmmc_compliance(controls, 1)
        assert result["compliant"]
        assert result["score_pct"] == 100.0

    def test_partial_controls_score(self):
        controls = list(CMMC_PRACTICES[1])[:3]
        result = check_cmmc_compliance(controls, 1)
        assert 0 < result["score_pct"] < 100

    def test_level2_requires_level1_and_level2(self):
        result = check_cmmc_compliance([], 2)
        total_required = len(CMMC_PRACTICES[1]) + len(CMMC_PRACTICES[2])
        assert result["total_required"] == total_required


class TestFARDFARSValidation:
    def test_classify_micro_purchase(self):
        assert classify_contract_value(5_000) == "micro_purchase"

    def test_classify_simplified_acquisition(self):
        assert classify_contract_value(100_000) == "simplified_acquisition"

    def test_classify_standard(self):
        assert classify_contract_value(5_000_000) == "standard"

    def test_classify_large(self):
        assert classify_contract_value(50_000_000) == "large"

    def test_validate_clauses_compliant(self):
        all_required = [
            "FAR 52.204-21", "FAR 52.222-26", "FAR 52.222-41",
            "FAR 52.232-33", "DFARS 252.204-7012",
        ]
        result = validate_clauses(all_required, 5_000_000)
        assert result["compliant"]

    def test_validate_clauses_missing(self):
        result = validate_clauses([], 5_000_000)
        assert not result["compliant"]
        assert len(result["missing"]) > 0


class TestSolicitationParser:
    def test_parses_milspecs(self):
        text = "Comply with MIL-STD-461 and MIL-HDBK-61 requirements."
        result = parse_solicitation(text)
        assert len(result.mil_specs) > 0

    def test_parses_naics(self):
        text = "NAICS: 541519"
        result = parse_solicitation(text)
        assert "541519" in result.naics_codes

    def test_parses_set_aside(self):
        text = "This is a Small Business set-aside."
        result = parse_solicitation(text)
        assert any("small business" in s.lower() for s in result.set_asides)

    def test_parses_clearance(self):
        text = "Requires Top Secret clearance."
        result = parse_solicitation(text)
        assert len(result.clearance_requirements) > 0

    def test_to_dict_returns_dict(self):
        text = "MIL-STD-461, NAICS 541519"
        result = parse_solicitation(text)
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "mil_specs" in d


class TestExportControl:
    def test_low_risk_no_flags(self):
        result = screen_export_control("Office cleaning services")
        assert result["risk_level"] == "low"
        assert not result["requires_review"]

    def test_itar_flags_munitions(self):
        result = screen_export_control("Production of missiles and munitions")
        assert len(result["itar_flags"]) > 0
        assert result["risk_level"] == "high"

    def test_ear_flags_encryption(self):
        result = screen_export_control("Cryptographic software development")
        assert len(result["ear_flags"]) > 0

    def test_both_flags(self):
        result = screen_export_control("Encryption for missiles")
        assert result["requires_review"]


# ---------------------------------------------------------------------------
# Bot compliance integration
# ---------------------------------------------------------------------------

class TestBotComplianceCheck:
    def test_compliance_check_requires_pro(self, free_bot):
        opp_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        with pytest.raises(MilitaryContractBotTierError):
            free_bot.run_compliance_check(opp_id)

    def test_compliance_check_returns_result(self, pro_bot, officer_user):
        opp_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        result = pro_bot.run_compliance_check(opp_id, user=officer_user)
        assert "cmmc_compliance" in result
        assert "clause_validation" in result
        assert "overall_ready" in result

    def test_compliance_check_invalid_id(self, pro_bot):
        result = pro_bot.run_compliance_check("INVALID")
        assert "error" in result

    def test_solicitation_parser_requires_pro(self, free_bot):
        with pytest.raises(MilitaryContractBotTierError):
            free_bot.parse_solicitation_text("test")

    def test_solicitation_parser_returns_dict(self, pro_bot):
        result = pro_bot.parse_solicitation_text("MIL-STD-461 compliance required. NAICS 541519.")
        assert "parsed" in result
        assert "export_control" in result


# ---------------------------------------------------------------------------
# Security tests
# ---------------------------------------------------------------------------

class TestEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        plaintext = "TOP SECRET: contract value $50M"
        encrypted = encrypt_data(plaintext, "test_passphrase")
        decrypted = decrypt_data(encrypted, "test_passphrase")
        assert decrypted == plaintext

    def test_different_passphrases_produce_different_ciphertext(self):
        enc1 = encrypt_data("hello", "pass1")
        enc2 = encrypt_data("hello", "pass2")
        assert enc1["ciphertext"] != enc2["ciphertext"]

    def test_encrypted_fields_are_hex(self):
        enc = encrypt_data("test", "pass")
        assert all(c in "0123456789abcdef" for c in enc["ciphertext"])

    def test_wrong_passphrase_gives_wrong_result(self):
        enc = encrypt_data("sensitive", "correct_pass")
        try:
            wrong = decrypt_data(enc, "wrong_pass")
            assert wrong != "sensitive"
        except (UnicodeDecodeError, ValueError):
            pass  # Wrong key produces garbage bytes — that's expected


class TestHMAC:
    def test_hmac_verify_valid(self):
        data = "contract data"
        secret = "my_secret"
        mac = compute_hmac(data, secret)
        assert verify_hmac(data, mac, secret)

    def test_hmac_verify_tampered_data(self):
        data = "contract data"
        secret = "my_secret"
        mac = compute_hmac(data, secret)
        assert not verify_hmac("tampered data", mac, secret)

    def test_hmac_verify_wrong_secret(self):
        data = "contract data"
        mac = compute_hmac(data, "secret1")
        assert not verify_hmac(data, mac, "secret2")


class TestUserAuthorization:
    def test_admin_can_all(self, admin_user):
        for feature in ["search_contracts", "analyze_opportunity", "submit_proposal",
                        "run_compliance_check", "manage_users", "modify_system_config"]:
            assert admin_user.can(feature)

    def test_viewer_limited(self, viewer_user):
        assert viewer_user.can("search_contracts")
        assert viewer_user.can("view_opportunity")
        assert not viewer_user.can("submit_proposal")
        assert not viewer_user.can("manage_users")

    def test_analyst_can_analyze(self, analyst_user):
        assert analyst_user.can("analyze_opportunity")
        assert analyst_user.can("export_data")
        assert not analyst_user.can("submit_proposal")

    def test_officer_can_compliance(self, officer_user):
        assert officer_user.can("run_compliance_check")
        assert officer_user.can("access_classified_details")
        assert not officer_user.can("manage_users")

    def test_require_raises_on_insufficient_role(self, viewer_user):
        with pytest.raises(AuthorizationError):
            viewer_user.require("submit_proposal")

    def test_require_passes_on_sufficient_role(self, admin_user):
        admin_user.require("manage_users")  # Should not raise

    def test_session_token_unique(self):
        u1 = User("u1", SecurityRole.VIEWER)
        u2 = User("u2", SecurityRole.VIEWER)
        assert u1.session_token != u2.session_token


class TestAuditTrail:
    def test_record_creates_entry(self, audit, admin_user):
        entry = audit.record(admin_user, "search", "contracts")
        assert entry["user_id"] == "test_admin"
        assert entry["action"] == "search"
        assert "hmac" in entry

    def test_verify_entry_valid(self, audit, admin_user):
        entry = audit.record(admin_user, "search", "contracts")
        assert audit.verify_entry(entry)

    def test_verify_entry_tampered(self, audit, admin_user):
        entry = audit.record(admin_user, "search", "contracts")
        entry["action"] = "tampered_action"
        assert not audit.verify_entry(entry)

    def test_get_log_returns_all(self, audit, admin_user):
        audit.record(admin_user, "action1", "resource1")
        audit.record(admin_user, "action2", "resource2")
        log = audit.get_log()
        assert len(log) == 2

    def test_get_user_log_filters(self, audit, admin_user, viewer_user):
        audit.record(admin_user, "admin_action", "res")
        audit.record(viewer_user, "view_action", "res")
        admin_log = audit.get_user_log("test_admin")
        assert len(admin_log) == 1
        assert admin_log[0]["user_id"] == "test_admin"

    def test_enterprise_bot_audit_trail(self, enterprise_bot, admin_user):
        log = enterprise_bot.get_audit_log(user=admin_user)
        assert isinstance(log, list)

    def test_non_enterprise_cannot_view_audit(self, pro_bot):
        with pytest.raises(MilitaryContractBotTierError):
            pro_bot.get_audit_log()


# ---------------------------------------------------------------------------
# Analytics tests
# ---------------------------------------------------------------------------

class TestPerformanceTracker:
    def test_initial_state(self, tracker):
        summary = tracker.get_summary()
        assert summary["total_events"] == 0
        assert summary["win_rate_pct"] == 0.0

    def test_record_event(self, tracker):
        tracker.record_event("test_event")
        assert tracker._counters["test_event"] == 1

    def test_record_timing(self, tracker):
        tracker.record_timing("operation_x", 0.123)
        assert tracker.avg_timing("operation_x") == pytest.approx(0.123)

    def test_win_rate_calculation(self, tracker):
        tracker.record_contract_won("OPP-001", 100_000)
        tracker.record_contract_won("OPP-002", 200_000)
        tracker.record_contract_lost("OPP-003")
        assert tracker.win_rate() == pytest.approx(66.7, abs=0.1)

    def test_record_proposal(self, tracker):
        tracker.record_proposal_submitted("OPP-001")
        assert tracker._counters["proposals_submitted"] == 1

    def test_uptime_increases(self, tracker):
        t1 = tracker.uptime_seconds()
        time.sleep(0.05)
        t2 = tracker.uptime_seconds()
        assert t2 > t1

    def test_get_recent_events(self, tracker):
        for i in range(25):
            tracker.record_event(f"event_{i}")
        recent = tracker.get_recent_events(limit=10)
        assert len(recent) == 10

    def test_reset_clears_state(self, tracker):
        tracker.record_event("event")
        tracker.reset()
        assert tracker._counters == {}
        assert tracker._events == []

    def test_bot_analytics_summary(self, enterprise_bot):
        enterprise_bot.search_contracts(keyword="cyber")
        summary = enterprise_bot.analytics.get_summary()
        assert summary["counters"]["searches"] >= 1


# ---------------------------------------------------------------------------
# Proposals tests
# ---------------------------------------------------------------------------

class TestProposals:
    def test_submit_requires_pro(self, free_bot):
        opp_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        with pytest.raises(MilitaryContractBotTierError):
            free_bot.submit_proposal(opp_id, {})

    def test_submit_valid_proposal(self, pro_bot):
        opp_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        result = pro_bot.submit_proposal(opp_id, {"technical_volume": "details"})
        assert result["submitted"]
        assert "proposal" in result
        assert result["proposal"]["opportunity_id"] == opp_id

    def test_submit_invalid_opportunity(self, pro_bot):
        result = pro_bot.submit_proposal("INVALID", {})
        assert "error" in result

    def test_list_proposals(self, pro_bot):
        opp_id = MOCK_MILITARY_CONTRACTS[0]["id"]
        pro_bot.submit_proposal(opp_id, {})
        proposals = pro_bot.list_proposals()
        assert len(proposals) >= 1

    def test_proposal_ids_unique(self, pro_bot):
        opp1 = MOCK_MILITARY_CONTRACTS[0]["id"]
        opp2 = MOCK_MILITARY_CONTRACTS[1]["id"]
        r1 = pro_bot.submit_proposal(opp1, {})
        r2 = pro_bot.submit_proposal(opp2, {})
        assert r1["proposal"]["id"] != r2["proposal"]["id"]


# ---------------------------------------------------------------------------
# Alerts and saved searches tests
# ---------------------------------------------------------------------------

class TestAlerts:
    def test_add_alert_requires_pro(self, free_bot):
        with pytest.raises(MilitaryContractBotTierError):
            free_bot.add_alert_keyword("cybersecurity")

    def test_add_alert_pro(self, pro_bot):
        result = pro_bot.add_alert_keyword("CMMC")
        assert result["added"]
        assert result["keyword"] == "CMMC"

    def test_get_alerts(self, pro_bot):
        pro_bot.add_alert_keyword("autonomous")
        alerts = pro_bot.get_alerts()
        assert "autonomous" in alerts

    def test_alert_limit_enforced(self, pro_bot):
        limit = TIER_LIMITS[Tier.PRO]["alert_keywords"]
        for i in range(limit):
            pro_bot.add_alert_keyword(f"keyword_{i}")
        with pytest.raises(MilitaryContractBotTierError):
            pro_bot.add_alert_keyword("one_too_many")

    def test_enterprise_unlimited_alerts(self, enterprise_bot):
        for i in range(50):
            enterprise_bot.add_alert_keyword(f"kw_{i}")
        assert len(enterprise_bot.get_alerts()) == 50


class TestSavedSearches:
    def test_save_search(self, pro_bot):
        result = pro_bot.save_search("Army IT", {"agency": "Army", "keyword": "IT"})
        assert result["saved"]

    def test_save_search_limit_enforced(self, pro_bot):
        limit = TIER_LIMITS[Tier.PRO]["saved_searches"]
        for i in range(limit):
            pro_bot.save_search(f"search_{i}", {})
        with pytest.raises(MilitaryContractBotTierError):
            pro_bot.save_search("one_too_many", {})


# ---------------------------------------------------------------------------
# Summary and reporting tests
# ---------------------------------------------------------------------------

class TestSummary:
    def test_summary_returns_dict(self, free_bot):
        s = free_bot.get_summary()
        assert isinstance(s, dict)

    def test_summary_total_opportunities(self, free_bot):
        s = free_bot.get_summary()
        assert s["total_opportunities"] == len(MOCK_MILITARY_CONTRACTS)

    def test_summary_contracts_plus_grants(self, free_bot):
        s = free_bot.get_summary()
        assert s["contracts"] + s["grants"] == s["total_opportunities"]

    def test_summary_tier_info(self, pro_bot):
        s = pro_bot.get_summary()
        assert s["tier"] == "pro"
        assert s["tier_price_monthly"] == 199

    def test_get_tier_info(self, enterprise_bot):
        info = enterprise_bot.get_tier_info()
        assert info["tier"] == "enterprise"
        assert "api_access" in info["features"]


# ---------------------------------------------------------------------------
# Manual override tests
# ---------------------------------------------------------------------------

class TestManualOverride:
    def test_set_and_get(self, enterprise_bot):
        enterprise_bot.override.set("max_results", 3, "testing")
        assert enterprise_bot.override.get("max_results") == 3

    def test_get_default(self, enterprise_bot):
        assert enterprise_bot.override.get("nonexistent", "default") == "default"

    def test_clear_override(self, enterprise_bot):
        enterprise_bot.override.set("key", "value")
        enterprise_bot.override.clear("key")
        assert enterprise_bot.override.get("key") is None

    def test_list_active(self, enterprise_bot):
        enterprise_bot.override.set("k1", "v1")
        enterprise_bot.override.set("k2", "v2")
        active = enterprise_bot.override.list_active()
        assert "k1" in active
        assert "k2" in active

    def test_override_log_recorded(self, enterprise_bot):
        enterprise_bot.override.set("test_key", "test_val", "unit test")
        log = enterprise_bot.override.get_log()
        assert any(e["key"] == "test_key" for e in log)

    def test_keyword_override_used_in_search(self, enterprise_bot):
        enterprise_bot.override.set("search_keyword_override", "cybersecurity")
        # Even with no keyword, override should apply
        results = enterprise_bot.search_contracts(keyword="")
        assert all(
            "cybersecurity" in r["title"].lower() or "cybersecurity" in r["description"].lower()
            for r in results
        )
        enterprise_bot.override.clear("search_keyword_override")


# ---------------------------------------------------------------------------
# Run / lifecycle tests
# ---------------------------------------------------------------------------

class TestLifecycle:
    def test_start_records_event(self, enterprise_bot):
        before = enterprise_bot.analytics._counters.get("startup", 0)
        enterprise_bot.start()
        assert enterprise_bot.analytics._counters.get("startup", 0) == before + 1

    def test_run_returns_dict(self, enterprise_bot):
        result = enterprise_bot.run()
        assert isinstance(result, dict)

    def test_create_user(self, enterprise_bot):
        user = enterprise_bot.create_user("alice", "analyst", clearance_level=2)
        assert user.user_id == "alice"
        assert user.role == SecurityRole.ANALYST
        assert user.clearance_level == 2


def test_module_level_run():
    from military_contract_bot import run
    result = run()
    assert result["status"] == "success"
    assert "leads" in result
