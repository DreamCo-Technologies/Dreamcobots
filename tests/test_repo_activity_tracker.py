"""Tests for bots/repo_bot/tiers.py and bots/repo_bot/repo_activity_tracker.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.repo_bot.repo_activity_tracker import (
    RepoActivityTracker,
    RepoActivityTrackerTierError,
    CATEGORY_KEYWORDS,
    ISSUE_SCAN_LIMITS,
    PR_SCAN_LIMITS,
    _mock_issues,
    _mock_pull_requests,
)
from bots.repo_bot.tiers import get_bot_tier_info, BOT_FEATURES


# ---------------------------------------------------------------------------
# Tier info
# ---------------------------------------------------------------------------

class TestTierInfo:
    def test_free_tier_info(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert isinstance(info["features"], list)
        assert len(info["features"]) > 0

    def test_pro_tier_info(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] > 0

    def test_enterprise_tier_info(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["tier"] == "enterprise"

    def test_all_tiers_have_features(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert len(info["features"]) > 0


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestRepoActivityTrackerInstantiation:
    def test_default_tier_is_free(self):
        tracker = RepoActivityTracker()
        assert tracker.tier == Tier.FREE

    def test_pro_tier(self):
        tracker = RepoActivityTracker(tier=Tier.PRO)
        assert tracker.tier == Tier.PRO

    def test_enterprise_tier(self):
        tracker = RepoActivityTracker(tier=Tier.ENTERPRISE)
        assert tracker.tier == Tier.ENTERPRISE

    def test_default_repo_name(self):
        tracker = RepoActivityTracker()
        assert tracker.repo_name == "ireanjordan24/Dreamcobots"

    def test_custom_repo_name(self):
        tracker = RepoActivityTracker(repo_name="org/my-repo")
        assert tracker.repo_name == "org/my-repo"

    def test_config_loaded(self):
        tracker = RepoActivityTracker()
        assert tracker.config is not None

    def test_scan_log_empty_on_init(self):
        tracker = RepoActivityTracker()
        assert tracker._scan_log == []


# ---------------------------------------------------------------------------
# categorise_item
# ---------------------------------------------------------------------------

class TestCategoriseItem:
    def test_bug_category(self):
        tracker = RepoActivityTracker()
        cat = tracker.categorise_item("Fix crash in scraper")
        assert cat == "bug"

    def test_feature_category(self):
        tracker = RepoActivityTracker()
        cat = tracker.categorise_item("Add new LinkedIn bot feature")
        assert cat == "feature"

    def test_bot_request_category(self):
        tracker = RepoActivityTracker()
        cat = tracker.categorise_item("Create a new scraper bot for Instagram")
        assert cat == "bot_request"

    def test_documentation_category(self):
        tracker = RepoActivityTracker()
        cat = tracker.categorise_item("Update README with setup guide")
        assert cat == "documentation"

    def test_performance_category(self):
        tracker = RepoActivityTracker()
        cat = tracker.categorise_item("Optimize slow performance in decision engine")
        assert cat == "performance"

    def test_security_category(self):
        tracker = RepoActivityTracker()
        cat = tracker.categorise_item("Security vulnerability in token handling")
        assert cat == "security"

    def test_general_fallback(self):
        tracker = RepoActivityTracker()
        cat = tracker.categorise_item("Hello world")
        assert cat == "general"

    def test_body_text_is_considered(self):
        tracker = RepoActivityTracker()
        cat = tracker.categorise_item("Ticket 1234", body="There is a crash in production")
        assert cat == "bug"


# ---------------------------------------------------------------------------
# scan_issues
# ---------------------------------------------------------------------------

class TestScanIssues:
    def test_returns_list(self):
        tracker = RepoActivityTracker()
        issues = tracker.scan_issues()
        assert isinstance(issues, list)
        assert len(issues) > 0

    def test_each_issue_has_category(self):
        tracker = RepoActivityTracker()
        for issue in tracker.scan_issues():
            assert "category" in issue

    def test_each_issue_has_priority(self):
        tracker = RepoActivityTracker()
        for issue in tracker.scan_issues():
            assert issue["priority"] in ("high", "medium", "low")

    def test_free_tier_limited_to_10(self):
        tracker = RepoActivityTracker(tier=Tier.FREE)
        big_list = _mock_issues() * 5  # 25 issues
        issues = tracker.scan_issues(raw_issues=big_list)
        assert len(issues) <= ISSUE_SCAN_LIMITS[Tier.FREE]

    def test_pro_tier_limited_to_50(self):
        tracker = RepoActivityTracker(tier=Tier.PRO)
        big_list = _mock_issues() * 20  # 100 issues
        issues = tracker.scan_issues(raw_issues=big_list)
        assert len(issues) <= ISSUE_SCAN_LIMITS[Tier.PRO]

    def test_enterprise_tier_has_no_limit(self):
        tracker = RepoActivityTracker(tier=Tier.ENTERPRISE)
        big_list = _mock_issues() * 20  # 100 issues
        issues = tracker.scan_issues(raw_issues=big_list)
        assert len(issues) == len(big_list)

    def test_custom_issues_passed_directly(self):
        tracker = RepoActivityTracker()
        custom = [{"number": 999, "title": "Fix a bug in the system", "labels": []}]
        issues = tracker.scan_issues(raw_issues=custom)
        assert issues[0]["number"] == 999
        assert issues[0]["category"] == "bug"

    def test_urgent_label_gives_high_priority(self):
        tracker = RepoActivityTracker()
        custom = [{"number": 1, "title": "Something happened", "labels": [{"name": "urgent"}]}]
        issues = tracker.scan_issues(raw_issues=custom)
        assert issues[0]["priority"] == "high"


# ---------------------------------------------------------------------------
# scan_pull_requests
# ---------------------------------------------------------------------------

class TestScanPullRequests:
    def test_returns_list(self):
        tracker = RepoActivityTracker()
        prs = tracker.scan_pull_requests()
        assert isinstance(prs, list)
        assert len(prs) > 0

    def test_each_pr_has_category(self):
        tracker = RepoActivityTracker()
        for pr in tracker.scan_pull_requests():
            assert "category" in pr

    def test_each_pr_has_review_status(self):
        tracker = RepoActivityTracker()
        for pr in tracker.scan_pull_requests():
            assert "review_status" in pr

    def test_free_tier_limited_to_5(self):
        tracker = RepoActivityTracker(tier=Tier.FREE)
        big_list = _mock_pull_requests() * 10  # 30 PRs
        prs = tracker.scan_pull_requests(raw_prs=big_list)
        assert len(prs) <= PR_SCAN_LIMITS[Tier.FREE]

    def test_enterprise_tier_has_no_limit(self):
        tracker = RepoActivityTracker(tier=Tier.ENTERPRISE)
        big_list = _mock_pull_requests() * 20  # 60 PRs
        prs = tracker.scan_pull_requests(raw_prs=big_list)
        assert len(prs) == len(big_list)

    def test_default_review_status_is_pending(self):
        tracker = RepoActivityTracker()
        custom = [{"number": 201, "title": "Add feature", "labels": []}]
        prs = tracker.scan_pull_requests(raw_prs=custom)
        assert prs[0]["review_status"] == "pending"


# ---------------------------------------------------------------------------
# generate_action_items
# ---------------------------------------------------------------------------

class TestGenerateActionItems:
    def test_returns_list(self):
        tracker = RepoActivityTracker()
        issues = tracker.scan_issues()
        prs = tracker.scan_pull_requests()
        items = tracker.generate_action_items(issues, prs)
        assert isinstance(items, list)

    def test_items_cover_issues_and_prs(self):
        tracker = RepoActivityTracker()
        issues = tracker.scan_issues()
        prs = tracker.scan_pull_requests()
        items = tracker.generate_action_items(issues, prs)
        types = {item["type"] for item in items}
        assert "issue" in types
        assert "pull_request" in types

    def test_each_item_has_required_keys(self):
        tracker = RepoActivityTracker()
        issues = tracker.scan_issues()
        prs = tracker.scan_pull_requests()
        for item in tracker.generate_action_items(issues, prs):
            assert "type" in item
            assert "number" in item
            assert "title" in item
            assert "category" in item
            assert "priority" in item
            assert "action" in item

    def test_high_priority_items_sorted_first(self):
        tracker = RepoActivityTracker()
        issues = tracker.scan_issues()
        prs = tracker.scan_pull_requests()
        items = tracker.generate_action_items(issues, prs)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        priorities = [priority_order[i["priority"]] for i in items]
        assert priorities == sorted(priorities)

    def test_empty_inputs_return_empty_list(self):
        tracker = RepoActivityTracker()
        assert tracker.generate_action_items([], []) == []

    def test_action_is_non_empty_string(self):
        tracker = RepoActivityTracker()
        issues = tracker.scan_issues()
        prs = tracker.scan_pull_requests()
        for item in tracker.generate_action_items(issues, prs):
            assert isinstance(item["action"], str)
            assert len(item["action"]) > 0


# ---------------------------------------------------------------------------
# auto_create_bot_stubs (ENTERPRISE only)
# ---------------------------------------------------------------------------

class TestAutoCreateBotStubs:
    def test_raises_on_free_tier(self):
        tracker = RepoActivityTracker(tier=Tier.FREE)
        with pytest.raises(RepoActivityTrackerTierError):
            tracker.auto_create_bot_stubs([])

    def test_raises_on_pro_tier(self):
        tracker = RepoActivityTracker(tier=Tier.PRO)
        with pytest.raises(RepoActivityTrackerTierError):
            tracker.auto_create_bot_stubs([])

    def test_enterprise_returns_stubs_for_bot_requests(self):
        tracker = RepoActivityTracker(tier=Tier.ENTERPRISE)
        issues = [
            {"number": 102, "title": "Add a new Instagram bot", "category": "bot_request"},
        ]
        stubs = tracker.auto_create_bot_stubs(issues)
        assert len(stubs) == 1
        assert stubs[0]["issue_number"] == 102
        assert "bot_name" in stubs[0]
        assert "stub_content" in stubs[0]

    def test_non_bot_request_issues_are_skipped(self):
        tracker = RepoActivityTracker(tier=Tier.ENTERPRISE)
        issues = [
            {"number": 101, "title": "Fix a crash", "category": "bug"},
        ]
        stubs = tracker.auto_create_bot_stubs(issues)
        assert len(stubs) == 0

    def test_stub_content_contains_framework_reference(self):
        tracker = RepoActivityTracker(tier=Tier.ENTERPRISE)
        issues = [
            {"number": 105, "title": "Build a Twitter bot", "category": "bot_request"},
        ]
        stubs = tracker.auto_create_bot_stubs(issues)
        assert "GlobalAISourcesFlow" in stubs[0]["stub_content"]

    def test_stub_content_has_run_method(self):
        tracker = RepoActivityTracker(tier=Tier.ENTERPRISE)
        issues = [
            {"number": 106, "title": "Create a lead gen bot", "category": "bot_request"},
        ]
        stubs = tracker.auto_create_bot_stubs(issues)
        assert "def run(" in stubs[0]["stub_content"]


# ---------------------------------------------------------------------------
# scan_activity
# ---------------------------------------------------------------------------

class TestScanActivity:
    def test_returns_dict_with_required_keys(self):
        tracker = RepoActivityTracker()
        result = tracker.scan_activity()
        for key in ("repo", "tier", "issues", "pull_requests", "action_items",
                    "issues_scanned", "prs_scanned", "timestamp"):
            assert key in result

    def test_counts_match_list_lengths(self):
        tracker = RepoActivityTracker()
        result = tracker.scan_activity()
        assert result["issues_scanned"] == len(result["issues"])
        assert result["prs_scanned"] == len(result["pull_requests"])

    def test_scan_log_updated(self):
        tracker = RepoActivityTracker()
        tracker.scan_activity()
        assert len(tracker._scan_log) == 1

    def test_multiple_scans_accumulate_log(self):
        tracker = RepoActivityTracker()
        tracker.scan_activity()
        tracker.scan_activity()
        assert len(tracker._scan_log) == 2

    def test_timestamp_is_string(self):
        tracker = RepoActivityTracker()
        result = tracker.scan_activity()
        assert isinstance(result["timestamp"], str)


# ---------------------------------------------------------------------------
# get_scan_log
# ---------------------------------------------------------------------------

class TestGetScanLog:
    def test_empty_before_any_scan(self):
        tracker = RepoActivityTracker()
        assert tracker.get_scan_log() == []

    def test_populated_after_scan(self):
        tracker = RepoActivityTracker()
        tracker.scan_activity()
        log = tracker.get_scan_log()
        assert len(log) == 1
        assert "issues_scanned" in log[0]
        assert "prs_scanned" in log[0]


# ---------------------------------------------------------------------------
# run() method
# ---------------------------------------------------------------------------

class TestRunMethod:
    def test_run_returns_string(self):
        tracker = RepoActivityTracker()
        result = tracker.run()
        assert isinstance(result, str)

    def test_run_contains_scanned_summary(self):
        tracker = RepoActivityTracker()
        result = tracker.run()
        assert "action items" in result.lower() or "scanned" in result.lower()

    def test_run_works_on_all_tiers(self):
        for tier in Tier:
            tracker = RepoActivityTracker(tier=tier)
            result = tracker.run()
            assert isinstance(result, str)
