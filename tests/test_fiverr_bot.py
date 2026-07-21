"""
Tests for bots/fiverr_bot/fiverr_bot.py

Covers:
  1. Tiers (including service_fee_pct)
  2. Gig management (create, update, deactivate, list, featured)
  3. Order management (receive, start, deliver, complete, cancel)
  4. Inbox automation & bulk messaging
  5. Review collection
  6. Pricing optimizer (rules-based + AI tier)
  7. Analytics & revenue summary
  8. CRM export
  9. Chat & process interfaces
  10. run() helper
  11. Freelancer & client registration
  12. Job postings & filtering
  13. Freelancer-client matching
  14. Proposals
  15. Stripe payment intents (mock mode)
  16. Milestones (add, fund, release)
  17. Featured gigs
  18. Admin dashboard
  19. Service-fee tracking
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.fiverr_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_GIG_LISTING,
    FEATURE_ORDER_TRACKING,
    FEATURE_INBOX_AUTOMATION,
    FEATURE_REVIEW_COLLECTION,
    FEATURE_ANALYTICS,
    FEATURE_PRICING_OPTIMIZER,
    FEATURE_CRM_EXPORT,
    FEATURE_AI_PRICING,
    FEATURE_WHITE_LABEL,
    FEATURE_FREELANCER_MATCHING,
    FEATURE_JOB_POSTINGS,
    FEATURE_PROPOSALS,
    FEATURE_STRIPE_PAYMENTS,
    FEATURE_MILESTONES,
    FEATURE_ADMIN_DASHBOARD,
    FEATURE_FEATURED_GIGS,
)
from bots.fiverr_bot.fiverr_bot import (
    FiverrBot,
    FiverrBotError,
    FiverrBotTierError,
    GigCategory,
    OrderStatus,
    ProposalStatus,
    MilestoneStatus,
)


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestFiverrBotTiers:
    def test_three_tiers(self):
        assert len(list_tiers()) == 3

    def test_free_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_gig_limit(self):
        assert get_tier_config(Tier.FREE).max_gigs == 5

    def test_pro_gig_limit(self):
        assert get_tier_config(Tier.PRO).max_gigs == 50

    def test_enterprise_unlimited_gigs(self):
        assert get_tier_config(Tier.ENTERPRISE).max_gigs is None
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_gigs() is True

    def test_free_has_gig_listing(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_GIG_LISTING)

    def test_free_lacks_inbox_automation(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_INBOX_AUTOMATION)

    def test_pro_has_inbox_automation(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_INBOX_AUTOMATION)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feat in [
            FEATURE_GIG_LISTING, FEATURE_ORDER_TRACKING, FEATURE_INBOX_AUTOMATION,
            FEATURE_REVIEW_COLLECTION, FEATURE_ANALYTICS, FEATURE_PRICING_OPTIMIZER,
            FEATURE_CRM_EXPORT, FEATURE_AI_PRICING, FEATURE_WHITE_LABEL,
            FEATURE_FREELANCER_MATCHING, FEATURE_JOB_POSTINGS, FEATURE_PROPOSALS,
            FEATURE_STRIPE_PAYMENTS, FEATURE_MILESTONES,
            FEATURE_ADMIN_DASHBOARD, FEATURE_FEATURED_GIGS,
        ]:
            assert cfg.has_feature(feat), f"Missing feature: {feat}"

    def test_free_service_fee_pct(self):
        assert get_tier_config(Tier.FREE).service_fee_pct == 20.0

    def test_pro_service_fee_pct(self):
        assert get_tier_config(Tier.PRO).service_fee_pct == 10.0

    def test_enterprise_service_fee_pct(self):
        assert get_tier_config(Tier.ENTERPRISE).service_fee_pct == 5.0

    def test_free_lacks_matching(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_FREELANCER_MATCHING)

    def test_pro_has_matching(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_FREELANCER_MATCHING)

    def test_free_lacks_admin_dashboard(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_ADMIN_DASHBOARD)

    def test_enterprise_has_admin_dashboard(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_ADMIN_DASHBOARD)

    def test_upgrade_from_free_to_pro(self):
        next_tier = get_upgrade_path(Tier.FREE)
        assert next_tier.tier == Tier.PRO

    def test_upgrade_from_pro_to_enterprise(self):
        next_tier = get_upgrade_path(Tier.PRO)
        assert next_tier.tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None


# ===========================================================================
# 2. Gig management
# ===========================================================================

class TestGigManagement:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)

    def test_create_gig_returns_dict(self):
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        assert isinstance(gig, dict)
        assert "gig_id" in gig

    def test_create_gig_uses_template(self):
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        assert "data" in gig["title"].lower() or "entry" in gig["title"].lower()

    def test_create_gig_custom_title(self):
        gig = self.bot.create_gig(GigCategory.RESEARCH, title="Custom Research Gig")
        assert gig["title"] == "Custom Research Gig"

    def test_create_gig_custom_price(self):
        gig = self.bot.create_gig(GigCategory.CONTENT_WRITING, price_usd=99.0)
        assert gig["price_usd"] == 99.0

    def test_create_gig_increments_id(self):
        g1 = self.bot.create_gig(GigCategory.DATA_ENTRY)
        g2 = self.bot.create_gig(GigCategory.RESEARCH)
        assert g1["gig_id"] != g2["gig_id"]

    def test_create_gig_active_by_default(self):
        gig = self.bot.create_gig(GigCategory.SEO)
        assert gig["active"] is True

    def test_free_tier_gig_limit(self):
        bot = FiverrBot(tier=Tier.FREE)
        for cat in [GigCategory.DATA_ENTRY, GigCategory.RESEARCH,
                    GigCategory.CONTENT_WRITING, GigCategory.ANALYTICS,
                    GigCategory.SEO]:
            bot.create_gig(cat)
        with pytest.raises(FiverrBotTierError):
            bot.create_gig(GigCategory.SOCIAL_MEDIA)

    def test_update_gig_price(self):
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        updated = self.bot.update_gig_price(gig["gig_id"], 99.99)
        assert updated["price_usd"] == 99.99

    def test_deactivate_gig(self):
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        result = self.bot.deactivate_gig(gig["gig_id"])
        assert result["active"] is False

    def test_get_gigs_returns_list(self):
        self.bot.create_gig(GigCategory.DATA_ENTRY)
        self.bot.create_gig(GigCategory.RESEARCH)
        gigs = self.bot.get_gigs()
        assert len(gigs) == 2

    def test_get_gigs_active_only(self):
        g1 = self.bot.create_gig(GigCategory.DATA_ENTRY)
        g2 = self.bot.create_gig(GigCategory.RESEARCH)
        self.bot.deactivate_gig(g1["gig_id"])
        active = self.bot.get_gigs(active_only=True)
        assert len(active) == 1
        assert active[0]["gig_id"] == g2["gig_id"]

    def test_get_unknown_gig_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.update_gig_price("gig_9999", 10.0)

    def test_free_tier_cannot_use_analytics(self):
        bot = FiverrBot(tier=Tier.FREE)
        bot.create_gig(GigCategory.DATA_ENTRY)
        with pytest.raises(FiverrBotTierError):
            bot.get_analytics()


# ===========================================================================
# 3. Order management
# ===========================================================================

class TestOrderManagement:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        self.gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        self.gig_id = self.gig["gig_id"]

    def test_receive_order_returns_dict(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        assert isinstance(order, dict)
        assert "order_id" in order

    def test_receive_order_status_pending(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        assert order["status"] == OrderStatus.PENDING.value

    def test_receive_order_price_matches_gig(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        assert order["amount_usd"] == self.gig["price_usd"]

    def test_start_order_changes_status(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        started = self.bot.start_order(order["order_id"])
        assert started["status"] == OrderStatus.IN_PROGRESS.value

    def test_deliver_order(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        self.bot.start_order(order["order_id"])
        delivered = self.bot.deliver_order(order["order_id"], "Here is your file.")
        assert delivered["status"] == OrderStatus.DELIVERED.value
        assert delivered["deliverable"] == "Here is your file."

    def test_complete_order(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        self.bot.deliver_order(order["order_id"], "Done!")
        completed = self.bot.complete_order(order["order_id"])
        assert completed["status"] == OrderStatus.COMPLETED.value

    def test_complete_order_logs_revenue(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        self.bot.deliver_order(order["order_id"], "Done!")
        self.bot.complete_order(order["order_id"])
        rev = self.bot.get_revenue_summary()
        assert rev["total_revenue_usd"] > 0

    def test_cancel_order(self):
        order = self.bot.receive_order(self.gig_id, "buyer123")
        cancelled = self.bot.cancel_order(order["order_id"])
        assert cancelled["status"] == OrderStatus.CANCELLED.value

    def test_get_orders_all(self):
        self.bot.receive_order(self.gig_id, "buyer1")
        self.bot.receive_order(self.gig_id, "buyer2")
        orders = self.bot.get_orders()
        assert len(orders) == 2

    def test_get_orders_filtered(self):
        o1 = self.bot.receive_order(self.gig_id, "buyer1")
        o2 = self.bot.receive_order(self.gig_id, "buyer2")
        self.bot.complete_order(o1["order_id"])
        completed = self.bot.get_orders(status=OrderStatus.COMPLETED)
        assert len(completed) == 1

    def test_get_unknown_order_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.start_order("ord_9999")


# ===========================================================================
# 4. Inbox automation & bulk messaging
# ===========================================================================

class TestInboxAutomation:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)

    def test_send_message(self):
        result = self.bot.send_message("buyer123", "Hello!")
        assert result["status"] == "sent"
        assert result["to"] == "buyer123"

    def test_inbox_records_message(self):
        self.bot.send_message("buyer1", "Hi!")
        self.bot.send_message("buyer2", "Hey!")
        assert len(self.bot.get_inbox()) == 2

    def test_auto_respond_inquiry(self):
        result = self.bot.auto_respond_inquiry("buyer123", "Can you help me?")
        assert result["status"] == "sent"
        assert "buyer123" in result["message"]

    def test_bulk_message(self):
        result = self.bot.bulk_message(["a", "b", "c"], "Promo!")
        assert result["recipients"] == 3
        assert len(result["messages"]) == 3

    def test_free_tier_cannot_send_message(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.send_message("buyer", "Hello")

    def test_free_tier_cannot_bulk_message(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.bulk_message(["a", "b"], "Hi")


# ===========================================================================
# 5. Review collection
# ===========================================================================

class TestReviewCollection:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        self.gig_id = gig["gig_id"]
        order = self.bot.receive_order(self.gig_id, "buyer123")
        self.order_id = order["order_id"]
        self.bot.deliver_order(self.order_id, "Done!")
        self.bot.complete_order(self.order_id)

    def test_request_review(self):
        result = self.bot.request_review(self.order_id)
        assert result["status"] == "sent"

    def test_record_review(self):
        review = self.bot.record_review(self.order_id, rating=5.0, comment="Great!")
        assert review["rating"] == 5.0
        assert review["comment"] == "Great!"

    def test_invalid_rating_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.record_review(self.order_id, rating=6.0)

    def test_rating_below_1_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.record_review(self.order_id, rating=0.5)

    def test_gig_rating_updated(self):
        self.bot.record_review(self.order_id, rating=4.5)
        gigs = self.bot.get_gigs()
        gig = next(g for g in gigs if g["gig_id"] == self.gig_id)
        assert gig["rating"] == 4.5
        assert gig["review_count"] == 1

    def test_get_reviews_all(self):
        self.bot.record_review(self.order_id, rating=4.0)
        assert len(self.bot.get_reviews()) == 1

    def test_get_reviews_by_gig(self):
        self.bot.record_review(self.order_id, rating=4.0)
        reviews = self.bot.get_reviews(gig_id=self.gig_id)
        assert len(reviews) == 1

    def test_request_review_on_non_completed_order_raises(self):
        gig = self.bot.create_gig(GigCategory.RESEARCH)
        order = self.bot.receive_order(gig["gig_id"], "buyer456")
        with pytest.raises(FiverrBotError):
            self.bot.request_review(order["order_id"])

    def test_free_tier_cannot_collect_reviews(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.record_review("ord_0001", rating=5.0)


# ===========================================================================
# 6. Pricing optimizer
# ===========================================================================

class TestPricingOptimizer:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        self.gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        self.gig_id = self.gig["gig_id"]

    def test_optimize_returns_dict(self):
        result = self.bot.optimize_price(self.gig_id)
        assert "optimized_price_usd" in result

    def test_optimize_includes_current_price(self):
        result = self.bot.optimize_price(self.gig_id)
        assert result["current_price_usd"] == self.gig["price_usd"]

    def test_optimize_method_rules_based(self):
        result = self.bot.optimize_price(self.gig_id)
        assert result["optimization_method"] == "rules-based"

    def test_enterprise_uses_ai_pricing(self):
        bot = FiverrBot(tier=Tier.ENTERPRISE)
        gig = bot.create_gig(GigCategory.DATA_ENTRY)
        result = bot.optimize_price(gig["gig_id"])
        assert result["optimization_method"] == "AI demand modeling"

    def test_free_tier_cannot_optimize_price(self):
        bot = FiverrBot(tier=Tier.FREE)
        gig = bot.create_gig(GigCategory.DATA_ENTRY)
        with pytest.raises(FiverrBotTierError):
            bot.optimize_price(gig["gig_id"])


# ===========================================================================
# 7. Analytics & revenue summary
# ===========================================================================

class TestAnalytics:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        gig = self.bot.create_gig(GigCategory.ANALYTICS)
        self.gig_id = gig["gig_id"]
        order = self.bot.receive_order(self.gig_id, "buyer_a")
        self.bot.deliver_order(order["order_id"], "Dashboard ready!")
        self.bot.complete_order(order["order_id"])

    def test_analytics_returns_dict(self):
        result = self.bot.get_analytics()
        assert isinstance(result, dict)

    def test_analytics_has_required_keys(self):
        result = self.bot.get_analytics()
        for key in ("total_gigs", "total_orders", "completed_orders",
                    "total_revenue_usd", "avg_rating", "conversion_rate_pct"):
            assert key in result, f"Missing key: {key}"

    def test_analytics_counts_correct(self):
        result = self.bot.get_analytics()
        assert result["total_gigs"] == 1
        assert result["completed_orders"] == 1

    def test_analytics_revenue_positive(self):
        result = self.bot.get_analytics()
        assert result["total_revenue_usd"] > 0

    def test_revenue_summary_structure(self):
        rev = self.bot.get_revenue_summary()
        assert "total_revenue_usd" in rev
        assert "completed_orders" in rev
        assert "by_gig" in rev
        assert "revenue_log" in rev

    def test_revenue_by_gig(self):
        rev = self.bot.get_revenue_summary()
        assert self.gig_id in rev["by_gig"]


# ===========================================================================
# 8. CRM export
# ===========================================================================

class TestCRMExport:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.ENTERPRISE)
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        order = self.bot.receive_order(gig["gig_id"], "buyer_crm")
        self.bot.deliver_order(order["order_id"], "Data done!")
        self.bot.complete_order(order["order_id"])

    def test_export_returns_dict(self):
        result = self.bot.export_to_crm("HubSpot")
        assert isinstance(result, dict)

    def test_export_crm_name(self):
        result = self.bot.export_to_crm("Salesforce")
        assert result["crm"] == "Salesforce"

    def test_export_record_count(self):
        result = self.bot.export_to_crm()
        assert result["records_exported"] >= 1

    def test_export_status_success(self):
        result = self.bot.export_to_crm()
        assert result["status"] == "success"

    def test_pro_tier_cannot_export_crm(self):
        bot = FiverrBot(tier=Tier.PRO)
        with pytest.raises(FiverrBotTierError):
            bot.export_to_crm()


# ===========================================================================
# 9. Chat & process interfaces
# ===========================================================================

class TestChatAndProcess:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)

    def test_chat_summary(self):
        result = self.bot.chat("show me the summary")
        assert "data" in result

    def test_chat_gigs(self):
        self.bot.create_gig(GigCategory.DATA_ENTRY)
        result = self.bot.chat("list my gigs")
        assert "data" in result

    def test_chat_orders(self):
        result = self.bot.chat("show orders")
        assert "data" in result

    def test_chat_revenue(self):
        result = self.bot.chat("revenue please")
        assert "data" in result

    def test_chat_unknown(self):
        result = self.bot.chat("something random XYZ")
        assert "message" in result

    def test_process_create_gig(self):
        result = self.bot.process({
            "action": "create_gig",
            "category": "data_entry",
            "price_usd": 20.0,
        })
        assert "gig_id" in result

    def test_process_receive_order(self):
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        result = self.bot.process({
            "action": "receive_order",
            "gig_id": gig["gig_id"],
            "buyer_username": "testbuyer",
        })
        assert "order_id" in result

    def test_process_get_analytics(self):
        result = self.bot.process({"action": "get_analytics"})
        assert "total_gigs" in result

    def test_process_default_returns_summary(self):
        result = self.bot.process({})
        assert "tier" in result


# ===========================================================================
# 10. run() helper
# ===========================================================================

class TestRunHelper:
    def test_run_returns_string(self):
        bot = FiverrBot(tier=Tier.FREE)
        result = bot.run()
        assert isinstance(result, str)

    def test_run_contains_tier(self):
        bot = FiverrBot(tier=Tier.PRO)
        result = bot.run()
        assert "pro" in result

    def test_run_contains_gig_count(self):
        bot = FiverrBot(tier=Tier.PRO)
        bot.create_gig(GigCategory.DATA_ENTRY)
        result = bot.run()
        assert "1 gig" in result

    def test_describe_tier(self):
        bot = FiverrBot(tier=Tier.PRO)
        output = bot.describe_tier()
        assert "Pro" in output
        assert "$49.00" in output


# ===========================================================================
# 11. Freelancer & client registration
# ===========================================================================

class TestFreelancerClientRegistration:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)

    def test_register_freelancer_returns_dict(self):
        result = self.bot.register_freelancer("alice", ["python", "web_development"])
        assert isinstance(result, dict)
        assert result["username"] == "alice"

    def test_register_freelancer_stores_skills_lowercase(self):
        result = self.bot.register_freelancer("bob", ["Python", "SEO"])
        assert "python" in result["skills"]
        assert "seo" in result["skills"]

    def test_register_freelancer_hourly_rate(self):
        result = self.bot.register_freelancer("carol", ["writing"], hourly_rate_usd=50.0)
        assert result["hourly_rate_usd"] == 50.0

    def test_register_duplicate_freelancer_raises(self):
        self.bot.register_freelancer("dave", ["design"])
        with pytest.raises(FiverrBotError):
            self.bot.register_freelancer("dave", ["design"])

    def test_get_freelancer(self):
        self.bot.register_freelancer("eve", ["seo"])
        result = self.bot.get_freelancer("eve")
        assert result["username"] == "eve"

    def test_get_unknown_freelancer_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.get_freelancer("nobody")

    def test_register_client_returns_dict(self):
        result = self.bot.register_client("acme_corp", company_name="ACME Corp")
        assert result["username"] == "acme_corp"
        assert result["company_name"] == "ACME Corp"

    def test_register_duplicate_client_raises(self):
        self.bot.register_client("bigco")
        with pytest.raises(FiverrBotError):
            self.bot.register_client("bigco")

    def test_free_tier_cannot_register_freelancer(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.register_freelancer("free_user", ["data_entry"])

    def test_free_tier_cannot_register_client(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.register_client("free_client")


# ===========================================================================
# 12. Job postings & filtering
# ===========================================================================

class TestJobPostings:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        self.bot.register_client("client1", company_name="Test Co")

    def test_post_job_returns_dict(self):
        result = self.bot.post_job(
            client_username="client1",
            title="Need SEO help",
            description="Audit our site",
            category=GigCategory.SEO,
            budget_usd=200.0,
            skills_required=["seo", "keyword research"],
        )
        assert isinstance(result, dict)
        assert "job_id" in result

    def test_post_job_stores_category(self):
        result = self.bot.post_job(
            client_username="client1",
            title="Logo design needed",
            description="New brand identity",
            category=GigCategory.GRAPHIC_DESIGN,
            budget_usd=150.0,
        )
        assert result["category"] == GigCategory.GRAPHIC_DESIGN.value

    def test_post_job_unregistered_client_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.post_job(
                client_username="ghost_client",
                title="Test job",
                description="Desc",
                category=GigCategory.DATA_ENTRY,
                budget_usd=50.0,
            )

    def test_get_jobs_returns_list(self):
        self.bot.post_job(
            client_username="client1",
            title="Content",
            description="Write articles",
            category=GigCategory.CONTENT_WRITING,
            budget_usd=100.0,
        )
        jobs = self.bot.get_jobs()
        assert len(jobs) == 1

    def test_get_jobs_filter_by_category(self):
        self.bot.post_job(
            "client1", "SEO job", "desc", GigCategory.SEO, 50.0, ["seo"]
        )
        self.bot.post_job(
            "client1", "Writing job", "desc", GigCategory.CONTENT_WRITING, 50.0
        )
        seo_jobs = self.bot.get_jobs(category=GigCategory.SEO)
        assert len(seo_jobs) == 1
        assert seo_jobs[0]["category"] == GigCategory.SEO.value

    def test_get_jobs_filter_by_skills(self):
        self.bot.post_job(
            "client1", "Python job", "desc", GigCategory.WEB_DEVELOPMENT, 300.0,
            skills_required=["python", "django"],
        )
        self.bot.post_job(
            "client1", "Design job", "desc", GigCategory.GRAPHIC_DESIGN, 100.0,
            skills_required=["illustrator"],
        )
        python_jobs = self.bot.get_jobs(skills=["python"])
        assert len(python_jobs) == 1

    def test_jobs_default_status_open(self):
        self.bot.post_job(
            "client1", "Open job", "desc", GigCategory.DATA_ENTRY, 30.0
        )
        jobs = self.bot.get_jobs(status="open")
        assert len(jobs) == 1

    def test_free_tier_cannot_post_job(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.get_jobs()


# ===========================================================================
# 13. Freelancer-client matching
# ===========================================================================

class TestFreelancerMatching:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        self.bot.register_client("client_a")
        self.bot.register_freelancer("fl_seo", ["seo", "keyword research", "analytics"])
        self.bot.register_freelancer("fl_dev", ["python", "web_development", "django"])
        self.bot.register_freelancer("fl_design", ["logo design", "illustrator"])
        self.job = self.bot.post_job(
            client_username="client_a",
            title="SEO + analytics",
            description="Need SEO and analytics",
            category=GigCategory.SEO,
            budget_usd=200.0,
            skills_required=["seo", "analytics"],
        )
        self.job_id = self.job["job_id"]

    def test_match_freelancers_returns_list(self):
        matches = self.bot.match_freelancers(self.job_id)
        assert isinstance(matches, list)

    def test_match_finds_seo_freelancer(self):
        matches = self.bot.match_freelancers(self.job_id)
        usernames = [m["username"] for m in matches]
        assert "fl_seo" in usernames

    def test_match_excludes_unrelated_freelancer(self):
        matches = self.bot.match_freelancers(self.job_id)
        usernames = [m["username"] for m in matches]
        assert "fl_design" not in usernames

    def test_match_includes_match_score(self):
        matches = self.bot.match_freelancers(self.job_id)
        for m in matches:
            assert "match_score" in m
            assert m["match_score"] > 0

    def test_match_sorted_by_score_desc(self):
        matches = self.bot.match_freelancers(self.job_id)
        scores = [m["match_score"] for m in matches]
        assert scores == sorted(scores, reverse=True)

    def test_match_unknown_job_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.match_freelancers("job_9999")

    def test_free_tier_cannot_match(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.match_freelancers("job_0001")


# ===========================================================================
# 14. Proposals
# ===========================================================================

class TestProposals:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        self.bot.register_client("buyer_co")
        self.bot.register_freelancer("writer_fl", ["content_writing", "seo"])
        self.bot.register_freelancer("writer_fl2", ["content_writing"])
        self.job = self.bot.post_job(
            client_username="buyer_co",
            title="Blog writing",
            description="Need 10 articles",
            category=GigCategory.CONTENT_WRITING,
            budget_usd=300.0,
            skills_required=["content_writing"],
        )
        self.job_id = self.job["job_id"]

    def test_submit_proposal_returns_dict(self):
        result = self.bot.submit_proposal(
            job_id=self.job_id,
            freelancer_username="writer_fl",
            cover_letter="I can write great articles.",
            rate_usd=30.0,
            delivery_days=7,
        )
        assert isinstance(result, dict)
        assert "proposal_id" in result

    def test_proposal_initial_status_pending(self):
        result = self.bot.submit_proposal(
            self.job_id, "writer_fl", "Great fit!", 30.0, 5
        )
        assert result["status"] == ProposalStatus.PENDING.value

    def test_get_proposals_for_job(self):
        self.bot.submit_proposal(self.job_id, "writer_fl", "Letter 1", 30.0, 5)
        self.bot.submit_proposal(self.job_id, "writer_fl2", "Letter 2", 25.0, 7)
        proposals = self.bot.get_proposals(self.job_id)
        assert len(proposals) == 2

    def test_accept_proposal_changes_status(self):
        prop = self.bot.submit_proposal(
            self.job_id, "writer_fl", "Best writer", 30.0, 5
        )
        accepted = self.bot.accept_proposal(prop["proposal_id"])
        assert accepted["status"] == ProposalStatus.ACCEPTED.value

    def test_accept_proposal_rejects_others(self):
        p1 = self.bot.submit_proposal(self.job_id, "writer_fl", "Letter A", 30.0, 5)
        p2 = self.bot.submit_proposal(self.job_id, "writer_fl2", "Letter B", 25.0, 7)
        self.bot.accept_proposal(p1["proposal_id"])
        proposals = self.bot.get_proposals(self.job_id)
        other = next(p for p in proposals if p["proposal_id"] == p2["proposal_id"])
        assert other["status"] == ProposalStatus.REJECTED.value

    def test_accept_proposal_closes_job(self):
        prop = self.bot.submit_proposal(self.job_id, "writer_fl", "Let's go", 30.0, 5)
        self.bot.accept_proposal(prop["proposal_id"])
        jobs = self.bot.get_jobs(status="in_progress")
        assert any(j["job_id"] == self.job_id for j in jobs)

    def test_submit_proposal_unknown_job_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.submit_proposal("job_9999", "writer_fl", "x", 30.0, 5)

    def test_submit_proposal_unknown_freelancer_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.submit_proposal(self.job_id, "ghost_fl", "x", 30.0, 5)

    def test_accept_unknown_proposal_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.accept_proposal("prop_9999")

    def test_free_tier_cannot_submit_proposal(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.submit_proposal("job_0001", "fl", "x", 10.0, 1)


# ===========================================================================
# 15. Stripe payment intents (mock mode)
# ===========================================================================

class TestStripePaymentIntents:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        self.order = self.bot.receive_order(gig["gig_id"], "buyer_stripe")
        self.order_id = self.order["order_id"]

    def test_create_payment_intent_returns_dict(self):
        result = self.bot.create_payment_intent(self.order_id)
        assert isinstance(result, dict)

    def test_create_payment_intent_has_id(self):
        result = self.bot.create_payment_intent(self.order_id)
        assert "id" in result

    def test_create_payment_intent_mock_flag(self):
        result = self.bot.create_payment_intent(self.order_id)
        # In test environment STRIPE_SECRET_KEY is not set → mock mode
        assert result.get("mock") is True

    def test_create_payment_intent_amount_matches_order(self):
        result = self.bot.create_payment_intent(self.order_id)
        expected_cents = int(round(self.order["amount_usd"] * 100))
        assert result["amount"] == expected_cents

    def test_create_payment_intent_custom_amount(self):
        result = self.bot.create_payment_intent(self.order_id, amount_usd=50.0)
        assert result["amount"] == 5000

    def test_create_payment_intent_includes_order_id(self):
        result = self.bot.create_payment_intent(self.order_id)
        assert result["order_id"] == self.order_id

    def test_create_payment_intent_unknown_order_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.create_payment_intent("ord_9999")

    def test_free_tier_cannot_create_payment_intent(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.create_payment_intent("ord_0001")


# ===========================================================================
# 16. Milestones
# ===========================================================================

class TestMilestones:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        gig = self.bot.create_gig(GigCategory.WEB_DEVELOPMENT)
        order = self.bot.receive_order(gig["gig_id"], "client_ms")
        self.order_id = order["order_id"]

    def test_add_milestone_returns_dict(self):
        result = self.bot.add_milestone(self.order_id, "Design phase", 100.0)
        assert isinstance(result, dict)
        assert "milestone_id" in result

    def test_add_milestone_initial_status_pending(self):
        result = self.bot.add_milestone(self.order_id, "Phase 1", 50.0)
        assert result["status"] == MilestoneStatus.PENDING.value

    def test_add_milestone_unknown_order_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.add_milestone("ord_9999", "Phantom", 50.0)

    def test_fund_milestone_changes_status(self):
        ms = self.bot.add_milestone(self.order_id, "Dev phase", 200.0)
        funded = self.bot.fund_milestone(ms["milestone_id"])
        assert funded["status"] == MilestoneStatus.FUNDED.value

    def test_fund_milestone_assigns_payment_intent(self):
        ms = self.bot.add_milestone(self.order_id, "Dev phase", 200.0)
        funded = self.bot.fund_milestone(ms["milestone_id"])
        assert funded["payment_intent_id"] is not None

    def test_fund_already_funded_milestone_raises(self):
        ms = self.bot.add_milestone(self.order_id, "Twice funded", 50.0)
        self.bot.fund_milestone(ms["milestone_id"])
        with pytest.raises(FiverrBotError):
            self.bot.fund_milestone(ms["milestone_id"])

    def test_release_milestone_changes_status(self):
        ms = self.bot.add_milestone(self.order_id, "Final", 150.0)
        self.bot.fund_milestone(ms["milestone_id"])
        released = self.bot.release_milestone(ms["milestone_id"])
        assert released["status"] == MilestoneStatus.RELEASED.value

    def test_release_milestone_includes_transfer(self):
        ms = self.bot.add_milestone(self.order_id, "Final", 150.0)
        self.bot.fund_milestone(ms["milestone_id"])
        result = self.bot.release_milestone(ms["milestone_id"])
        assert "transfer" in result

    def test_release_unfunded_milestone_raises(self):
        ms = self.bot.add_milestone(self.order_id, "Unfunded", 100.0)
        with pytest.raises(FiverrBotError):
            self.bot.release_milestone(ms["milestone_id"])

    def test_release_records_service_fee(self):
        ms = self.bot.add_milestone(self.order_id, "Fee check", 100.0)
        self.bot.fund_milestone(ms["milestone_id"])
        self.bot.release_milestone(ms["milestone_id"])
        # PRO tier = 10% fee → payout = $90
        assert len(self.bot._service_fee_log) >= 1
        fee_entry = self.bot._service_fee_log[-1]
        assert fee_entry["fee_pct"] == 10.0
        assert fee_entry["net_usd"] == 90.0

    def test_get_milestones_returns_list(self):
        self.bot.add_milestone(self.order_id, "M1", 50.0)
        self.bot.add_milestone(self.order_id, "M2", 75.0)
        milestones = self.bot.get_milestones(self.order_id)
        assert len(milestones) == 2

    def test_get_milestones_filter_by_order(self):
        gig2 = self.bot.create_gig(GigCategory.SEO)
        order2 = self.bot.receive_order(gig2["gig_id"], "other_buyer")
        self.bot.add_milestone(self.order_id, "For order 1", 50.0)
        self.bot.add_milestone(order2["order_id"], "For order 2", 75.0)
        milestones = self.bot.get_milestones(self.order_id)
        assert all(m["order_id"] == self.order_id for m in milestones)

    def test_free_tier_cannot_add_milestone(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.add_milestone("ord_0001", "Test", 100.0)


# ===========================================================================
# 17. Featured gigs
# ===========================================================================

class TestFeaturedGigs:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.ENTERPRISE)
        gig = self.bot.create_gig(GigCategory.DATA_ENTRY)
        self.gig_id = gig["gig_id"]

    def test_feature_gig_returns_dict(self):
        result = self.bot.feature_gig(self.gig_id, days=7)
        assert isinstance(result, dict)
        assert result["featured"] is True

    def test_feature_gig_includes_until_date(self):
        result = self.bot.feature_gig(self.gig_id, days=7)
        assert "featured_until" in result
        assert result["featured_until"] is not None

    def test_feature_gig_invalid_days_raises(self):
        with pytest.raises(FiverrBotError):
            self.bot.feature_gig(self.gig_id, days=0)

    def test_get_featured_gigs(self):
        self.bot.feature_gig(self.gig_id, days=3)
        featured = self.bot.get_featured_gigs()
        assert len(featured) == 1
        assert featured[0]["gig_id"] == self.gig_id

    def test_get_featured_gigs_only_featured(self):
        gig2 = self.bot.create_gig(GigCategory.SEO)
        self.bot.feature_gig(self.gig_id, days=3)
        featured = self.bot.get_featured_gigs()
        gig_ids = [g["gig_id"] for g in featured]
        assert gig2["gig_id"] not in gig_ids

    def test_featured_flag_in_gig_dict(self):
        self.bot.feature_gig(self.gig_id, days=1)
        gig_data = self.bot.get_gigs()
        target = next(g for g in gig_data if g["gig_id"] == self.gig_id)
        assert target["featured"] is True

    def test_pro_tier_cannot_feature_gig(self):
        bot = FiverrBot(tier=Tier.PRO)
        gig = bot.create_gig(GigCategory.DATA_ENTRY)
        with pytest.raises(FiverrBotTierError):
            bot.feature_gig(gig["gig_id"], days=7)

    def test_free_tier_cannot_feature_gig(self):
        bot = FiverrBot(tier=Tier.FREE)
        gig = bot.create_gig(GigCategory.DATA_ENTRY)
        with pytest.raises(FiverrBotTierError):
            bot.feature_gig(gig["gig_id"], days=7)


# ===========================================================================
# 18. Admin dashboard
# ===========================================================================

class TestAdminDashboard:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.ENTERPRISE)
        # Register users
        self.bot.register_client("corp1")
        self.bot.register_freelancer("fl1", ["seo", "analytics"])
        # Create gig & order
        gig = self.bot.create_gig(GigCategory.SEO)
        order = self.bot.receive_order(gig["gig_id"], "corp1")
        self.bot.deliver_order(order["order_id"], "SEO audit done")
        self.bot.complete_order(order["order_id"])
        # Post job & proposal
        job = self.bot.post_job("corp1", "SEO project", "Need SEO", GigCategory.SEO, 500.0, ["seo"])
        self.bot.submit_proposal(job["job_id"], "fl1", "I can do this", 50.0, 7)
        # Milestone
        gig2 = self.bot.create_gig(GigCategory.ANALYTICS)
        order2 = self.bot.receive_order(gig2["gig_id"], "corp1")
        ms = self.bot.add_milestone(order2["order_id"], "Phase 1", 100.0)
        self.bot.fund_milestone(ms["milestone_id"])
        self.bot.release_milestone(ms["milestone_id"])

    def test_admin_dashboard_returns_dict(self):
        result = self.bot.get_admin_dashboard()
        assert isinstance(result, dict)

    def test_admin_dashboard_has_required_sections(self):
        result = self.bot.get_admin_dashboard()
        for key in ("users", "gigs", "orders", "job_postings", "proposals",
                    "milestones", "revenue", "reviews"):
            assert key in result, f"Missing section: {key}"

    def test_admin_dashboard_users_count(self):
        result = self.bot.get_admin_dashboard()
        assert result["users"]["clients"] == 1
        assert result["users"]["freelancers"] == 1

    def test_admin_dashboard_revenue_structure(self):
        result = self.bot.get_admin_dashboard()
        rev = result["revenue"]
        assert "gross_usd" in rev
        assert "service_fees_usd" in rev
        assert "net_usd" in rev
        assert rev["service_fee_pct"] == 5.0  # ENTERPRISE

    def test_admin_dashboard_service_fees_deducted(self):
        result = self.bot.get_admin_dashboard()
        rev = result["revenue"]
        assert rev["service_fees_usd"] > 0
        assert rev["net_usd"] < rev["gross_usd"]

    def test_admin_dashboard_job_postings_count(self):
        result = self.bot.get_admin_dashboard()
        assert result["job_postings"]["total"] == 1

    def test_admin_dashboard_proposals_count(self):
        result = self.bot.get_admin_dashboard()
        assert result["proposals"]["total"] == 1

    def test_admin_dashboard_milestone_released(self):
        result = self.bot.get_admin_dashboard()
        ms_breakdown = result["milestones"]["by_status"]
        assert ms_breakdown.get(MilestoneStatus.RELEASED.value, 0) >= 1

    def test_pro_tier_cannot_access_admin_dashboard(self):
        bot = FiverrBot(tier=Tier.PRO)
        with pytest.raises(FiverrBotTierError):
            bot.get_admin_dashboard()

    def test_free_tier_cannot_access_admin_dashboard(self):
        bot = FiverrBot(tier=Tier.FREE)
        with pytest.raises(FiverrBotTierError):
            bot.get_admin_dashboard()


# ===========================================================================
# 19. Service-fee tracking on order completion
# ===========================================================================

class TestServiceFeeTracking:
    def test_complete_order_records_service_fee(self):
        bot = FiverrBot(tier=Tier.PRO)  # 10% fee
        gig = bot.create_gig(GigCategory.DATA_ENTRY, price_usd=100.0)
        order = bot.receive_order(gig["gig_id"], "buyer_fee")
        bot.deliver_order(order["order_id"], "done")
        bot.complete_order(order["order_id"])
        assert len(bot._service_fee_log) == 1
        entry = bot._service_fee_log[0]
        assert entry["fee_pct"] == 10.0
        assert entry["fee_usd"] == 10.0
        assert entry["net_usd"] == 90.0

    def test_enterprise_lower_service_fee(self):
        bot = FiverrBot(tier=Tier.ENTERPRISE)  # 5% fee
        gig = bot.create_gig(GigCategory.DATA_ENTRY, price_usd=200.0)
        order = bot.receive_order(gig["gig_id"], "buyer_ent")
        bot.deliver_order(order["order_id"], "done")
        bot.complete_order(order["order_id"])
        entry = bot._service_fee_log[0]
        assert entry["fee_pct"] == 5.0
        assert entry["fee_usd"] == 10.0
        assert entry["net_usd"] == 190.0

    def test_free_tier_higher_service_fee(self):
        bot = FiverrBot(tier=Tier.FREE)  # 20% fee
        gig = bot.create_gig(GigCategory.DATA_ENTRY, price_usd=50.0)
        order = bot.receive_order(gig["gig_id"], "buyer_free")
        bot.deliver_order(order["order_id"], "done")
        bot.complete_order(order["order_id"])
        entry = bot._service_fee_log[0]
        assert entry["fee_pct"] == 20.0
        assert entry["fee_usd"] == 10.0
        assert entry["net_usd"] == 40.0

    def test_get_summary_includes_service_fees(self):
        bot = FiverrBot(tier=Tier.PRO)
        gig = bot.create_gig(GigCategory.DATA_ENTRY, price_usd=100.0)
        order = bot.receive_order(gig["gig_id"], "buyer_sum")
        bot.deliver_order(order["order_id"], "done")
        bot.complete_order(order["order_id"])
        summary = bot.get_summary()
        assert "total_service_fees_usd" in summary
        assert summary["total_service_fees_usd"] == 10.0

    def test_describe_tier_includes_service_fee(self):
        bot = FiverrBot(tier=Tier.PRO)
        output = bot.describe_tier()
        assert "10%" in output


# ===========================================================================
# 20. Process interface — new actions
# ===========================================================================

class TestProcessNewActions:
    def setup_method(self):
        self.bot = FiverrBot(tier=Tier.PRO)
        self.bot.register_client("proc_client")
        self.bot.register_freelancer("proc_fl", ["seo"])

    def test_process_post_job(self):
        result = self.bot.process({
            "action": "post_job",
            "client_username": "proc_client",
            "title": "SEO needed",
            "category": "seo",
            "budget_usd": 100.0,
            "skills_required": ["seo"],
        })
        assert "job_id" in result

    def test_process_submit_proposal(self):
        job = self.bot.process({
            "action": "post_job",
            "client_username": "proc_client",
            "title": "SEO needed",
            "category": "seo",
            "budget_usd": 100.0,
            "skills_required": ["seo"],
        })
        result = self.bot.process({
            "action": "submit_proposal",
            "job_id": job["job_id"],
            "freelancer_username": "proc_fl",
            "cover_letter": "I can help!",
            "rate_usd": 20.0,
            "delivery_days": 5,
        })
        assert "proposal_id" in result

    def test_process_match_freelancers(self):
        job = self.bot.process({
            "action": "post_job",
            "client_username": "proc_client",
            "title": "SEO project",
            "category": "seo",
            "budget_usd": 150.0,
            "skills_required": ["seo"],
        })
        result = self.bot.process({
            "action": "match_freelancers",
            "job_id": job["job_id"],
        })
        assert "matches" in result

    def test_process_get_admin_dashboard_enterprise(self):
        bot = FiverrBot(tier=Tier.ENTERPRISE)
        result = bot.process({"action": "get_admin_dashboard"})
        assert "users" in result
