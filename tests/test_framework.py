"""
Tests for the DreamCObots framework and bot implementations.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Framework unit tests
# ---------------------------------------------------------------------------

class TestNLPEngine:
    def setup_method(self):
        from framework.nlp_engine import NLPEngine
        self.nlp = NLPEngine()

    def test_tokenize(self):
        result = self.nlp.process("Hello! I need a job.")
        assert "hello" in result["tokens"]
        assert "job" in result["tokens"]

    def test_sentiment_positive(self):
        result = self.nlp.process("This is great, I love it!")
        assert result["sentiment"] == "positive"
        assert result["sentiment_score"] > 0

    def test_sentiment_negative(self):
        result = self.nlp.process("This is terrible and I hate it.")
        assert result["sentiment"] == "negative"
        assert result["sentiment_score"] < 0

    def test_intent_job_search(self):
        result = self.nlp.process("I am looking for a job in engineering.")
        assert result["intent"] == "job_search"

    def test_intent_greeting(self):
        result = self.nlp.process("Hello! Hi there.")
        assert result["intent"] == "greeting"

    def test_intent_dataset_purchase(self):
        result = self.nlp.process("I want to buy a dataset.")
        assert result["intent"] == "dataset_purchase"

    def test_intent_invoice(self):
        result = self.nlp.process("Please generate an invoice for my client.")
        assert result["intent"] == "invoice"

    def test_entity_extraction_email(self):
        result = self.nlp.process("Contact me at test@example.com")
        assert "test@example.com" in result["entities"]["emails"]

    def test_entity_extraction_numbers(self):
        result = self.nlp.process("The price is 1500 dollars.")
        assert "1500" in result["entities"]["numbers"]

    def test_context_window(self):
        for msg in ["hello", "job search", "resume help"]:
            self.nlp.process(msg)
        context = self.nlp.get_context()
        assert len(context) <= self.nlp._context_window
        assert "hello" in context

    def test_clear_context(self):
        self.nlp.process("hello")
        self.nlp.clear_context()
        assert self.nlp.get_context() == []


class TestAdaptiveLearning:
    def setup_method(self):
        from framework.adaptive_learning import AdaptiveLearning
        self.al = AdaptiveLearning("test-bot")

    def test_record_interaction(self):
        self.al.record_interaction("u1", "hi", "greeting", "positive", 0.5, "Hello!")
        assert len(self.al._history) == 1

    def test_top_intents(self):
        for _ in range(3):
            self.al.record_interaction("u1", "job", "job_search", "neutral", 0.0, "Searching")
        self.al.record_interaction("u1", "hi", "greeting", "positive", 0.5, "Hi")
        top = self.al.top_intents(n=1)
        assert top[0] == "job_search"

    def test_sentiment_trend_improving(self):
        for score in [0.4, 0.5, 0.6]:
            self.al.record_interaction("u1", "msg", "general", "positive", score, "OK")
        assert self.al.user_sentiment_trend("u1") == "improving"

    def test_sentiment_trend_worsening(self):
        for score in [-0.4, -0.5, -0.6]:
            self.al.record_interaction("u1", "msg", "general", "negative", score, "OK")
        assert self.al.user_sentiment_trend("u1") == "worsening"

    def test_reinforce_increases_weight(self):
        base = self.al.get_response_weight("job_search")
        self.al.reinforce("job_search", reward=1.0)
        assert self.al.get_response_weight("job_search") > base

    def test_history_cap(self):
        for i in range(self.al.MAX_HISTORY + 50):
            self.al.record_interaction("u1", f"msg{i}", "general", "neutral", 0.0, "OK")
        assert len(self.al._history) == self.al.MAX_HISTORY

    def test_end_session_calls_decay(self):
        self.al._response_weights["test"] = 1.0
        self.al.end_session()
        assert self.al._response_weights["test"] < 1.0

    def test_serialisation(self, tmp_path):
        self.al.record_interaction("u1", "hi", "greeting", "positive", 0.5, "Hello!")
        filepath = str(tmp_path / "al_state.json")
        self.al.save(filepath)
        from framework.adaptive_learning import AdaptiveLearning
        loaded = AdaptiveLearning.load(filepath)
        assert loaded.bot_id == "test-bot"
        assert loaded._intent_freq["greeting"] == 1


class TestDatasetManager:
    def setup_method(self):
        from framework.dataset_manager import DatasetManager
        self.mgr = DatasetManager(owner_bot_id="test-bot")

    def _add_dataset(self, name="Test Dataset", ethical=True):
        return self.mgr.create_dataset(
            name=name,
            description="A test dataset.",
            domain="testing",
            size_mb=10.0,
            price_usd=99.00,
            license="CC-BY-4.0",
            tags=["test"],
            ethical_review_passed=ethical,
        )

    def test_create_dataset(self):
        ds = self._add_dataset()
        assert ds.name == "Test Dataset"
        assert ds.dataset_id in [d.dataset_id for d in self.mgr.list_datasets()]

    def test_list_datasets_by_domain(self):
        self._add_dataset()
        results = self.mgr.list_datasets(domain="testing")
        assert len(results) == 1

    def test_sell_dataset_success(self):
        ds = self._add_dataset(ethical=True)
        record = self.mgr.sell_dataset(ds.dataset_id, buyer_id="buyer-1")
        assert record is not None
        assert self.mgr.total_revenue() == 99.00

    def test_sell_dataset_no_ethical_review(self):
        ds = self._add_dataset(ethical=False)
        with pytest.raises(ValueError, match="ethical review"):
            self.mgr.sell_dataset(ds.dataset_id, buyer_id="buyer-1")

    def test_sell_unknown_dataset(self):
        result = self.mgr.sell_dataset("non-existent-id", buyer_id="buyer-1")
        assert result is None

    def test_remove_dataset(self):
        ds = self._add_dataset()
        assert self.mgr.remove_dataset(ds.dataset_id) is True
        assert self.mgr.get_dataset(ds.dataset_id) is None

    def test_sales_summary(self):
        ds = self._add_dataset()
        self.mgr.sell_dataset(ds.dataset_id, "buyer-1")
        summary = self.mgr.sales_summary()
        assert summary["total_sales"] == 1
        assert summary["total_revenue_usd"] == 99.00


class TestMonetizationManager:
    def setup_method(self):
        from framework.monetization import MonetizationManager, PricingPlan, PricingModel
        self.mm = MonetizationManager(bot_id="test-bot")
        self.mm.add_plan(PricingPlan(
            plan_id="basic",
            name="Basic",
            model=PricingModel.SUBSCRIPTION,
            price_usd=9.99,
            description="Basic plan",
        ))
        self.mm.add_plan(PricingPlan(
            plan_id="freemium",
            name="Freemium",
            model=PricingModel.FREEMIUM,
            price_usd=9.99,
            description="Freemium plan",
            free_tier_limit=3,
        ))

    def test_charge_subscription(self):
        tx = self.mm.charge("user-1", "basic")
        assert tx is not None
        assert tx.amount_usd == 9.99

    def test_freemium_free_tier(self):
        for _ in range(3):
            tx = self.mm.charge("user-freemium", "freemium")
            assert tx.amount_usd == 0.0

    def test_freemium_paid_after_limit(self):
        for _ in range(3):
            self.mm.charge("user-2", "freemium")
        tx = self.mm.charge("user-2", "freemium")
        assert tx.amount_usd == 9.99

    def test_revenue_tracking(self):
        self.mm.charge("user-1", "basic")
        self.mm.charge("user-2", "basic")
        assert self.mm.total_revenue() == 9.99 * 2

    def test_unknown_plan(self):
        tx = self.mm.charge("user-1", "nonexistent")
        assert tx is None

    def test_revenue_by_plan(self):
        self.mm.charge("u1", "basic")
        breakdown = self.mm.revenue_by_plan()
        assert "basic" in breakdown
        assert breakdown["basic"] == 9.99


# ---------------------------------------------------------------------------
# Bot integration tests
# ---------------------------------------------------------------------------

class TestJobSearchBot:
    def setup_method(self):
        from Occupational_bots.feature_1 import JobSearchBot
        self.bot = JobSearchBot()

    def test_chat_greeting(self):
        response = self.bot.chat("Hello!")
        assert len(response) > 0
        assert isinstance(response, str)

    def test_chat_job_intent(self):
        response = self.bot.chat("I need a job in software engineering.")
        assert "job" in response.lower() or "skill" in response.lower()

    def test_chat_dataset_intent(self):
        response = self.bot.chat("I want to buy your dataset.")
        assert "dataset" in response.lower()

    def test_status(self):
        status = self.bot.status()
        assert status["name"] == "JobSearch Bot"
        assert status["category"] == "occupational"
        assert status["datasets"]["datasets_available"] == 2

    def test_sell_dataset(self):
        datasets = self.bot.datasets.list_datasets()
        assert len(datasets) > 0
        ds = datasets[0]
        result = self.bot.sell_dataset(ds.dataset_id, "buyer-999")
        assert "Sale ID" in result


class TestInterviewPrepBot:
    def setup_method(self):
        from Occupational_bots.feature_3 import InterviewPrepBot
        self.bot = InterviewPrepBot()

    def test_interview_question_cycle(self):
        r1 = self.bot.chat("Give me an interview question.")
        r2 = self.bot.chat("Another question please.")
        # Both should contain a question
        assert "?" in r1 or "question" in r1.lower()

    def test_feedback_reinforcement(self):
        self.bot.chat("The answer was helpful, great!")
        weight_after = self.bot.learning.get_response_weight("interview_prep")
        assert weight_after >= 1.0


class TestInvoicingBot:
    def setup_method(self):
        from Business_bots.feature_3 import InvoicingBot
        self.bot = InvoicingBot()

    def test_invoice_number_increments(self):
        r1 = self.bot.chat("Invoice client for 500")
        r2 = self.bot.chat("Invoice another client for 1000")
        assert "INV-1000" in r1
        assert "INV-1001" in r2


class TestCustomerFeedbackBot:
    def setup_method(self):
        from Marketing_bots.feature_3 import CustomerFeedbackBot
        self.bot = CustomerFeedbackBot()

    def test_positive_feedback_recorded(self):
        response = self.bot.chat("The product is amazing and I love it!")
        assert "positive" in response.lower()
        assert self.bot._feedback_counts["positive"] == 1

    def test_negative_feedback_recorded(self):
        response = self.bot.chat("This is terrible and broken.")
        assert "negative" in response.lower()
        assert self.bot._feedback_counts["negative"] == 1


class TestBuddyAI:
    def setup_method(self):
        from BuddyAI.buddy_ai import BuddyAI
        from Occupational_bots.feature_1 import JobSearchBot
        from Business_bots.feature_1 import MeetingSchedulerBot
        from Marketing_bots.feature_1 import SocialMediaBot
        from Side_Hustle_bots.feature_1 import ContentCreatorBot

        self.buddy = BuddyAI()
        self.buddy.register(JobSearchBot())
        self.buddy.register(MeetingSchedulerBot())
        self.buddy.register(SocialMediaBot())
        self.buddy.register(ContentCreatorBot())

    def test_routes_job_query_to_occupational(self):
        response = self.buddy.chat("I'm looking for a job.", user_id="u1")
        assert "JobSearch Bot" in response

    def test_routes_meeting_query_to_business(self):
        response = self.buddy.chat("Schedule a meeting for my team.", user_id="u2")
        assert "Meeting Scheduler Bot" in response

    def test_routes_marketing_query(self):
        response = self.buddy.chat("I need to post on social media.", user_id="u3")
        assert "Social Media Bot" in response

    def test_session_persistence(self):
        self.buddy.chat("I need a job.", user_id="u4")
        # Second message should go to same bot (job search)
        response2 = self.buddy.chat("Tell me more.", user_id="u4")
        assert "JobSearch Bot" in response2

    def test_switch_bot(self):
        self.buddy.chat("Hello", user_id="u5")
        result = self.buddy.switch_bot("u5", "Meeting")
        assert "Meeting Scheduler Bot" in result

    def test_end_session(self):
        self.buddy.chat("Hi", user_id="u6")
        result = self.buddy.end_session("u6")
        assert "Session ended" in result

    def test_no_bots_registered(self):
        from BuddyAI.buddy_ai import BuddyAI
        empty = BuddyAI()
        response = empty.chat("Hello")
        assert "No bots" in response

    def test_platform_summary(self):
        summary = self.buddy.platform_summary()
        assert summary["registered_bots"] == 4
        assert summary["total_datasets_available"] > 0

    def test_list_bots(self):
        bots = self.buddy.list_bots()
        assert len(bots) == 4
        names = [b["name"] for b in bots]
        assert "JobSearch Bot" in names


class TestBaseBot:
    def setup_method(self):
        from Occupational_bots.feature_1 import JobSearchBot
        self.bot = JobSearchBot()

    def test_emotional_state_updates(self):
        initial = self.bot.current_emotion()
        self.bot.chat("This is wonderful and great!")
        updated = self.bot.current_emotion()
        # positive input should increase valence or result in a 'happy' emotional state
        assert updated["valence"] > initial["valence"] or updated["label"] == "happy"

    def test_end_session_clears_context(self):
        self.bot.chat("Hello, looking for a job.")
        self.bot.end_session("user-1")
        assert self.bot.nlp.get_context() == []

    def test_repr(self):
        assert "JobSearchBot" in repr(self.bot)
        assert "employment" in repr(self.bot)
