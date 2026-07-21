"""
Tests for the Research Analyzer Bot.

Validates:
  1. Tiers — feature flags, page limits, daily limits, tier info
  2. ResearchAnalyzerBot — ingest_documents, semantic_search, answer_question,
     summarize, build_insights, get_research_dashboard
  3. Tier gating — FREE page cap, ENTERPRISE large corpus
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.research_analyzer_bot.tiers import (
    Tier,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    BOT_FEATURES,
    DAILY_LIMITS,
    get_bot_tier_info,
    FEATURE_BASIC_SEARCH,
    FEATURE_SUMMARIZATION,
    FEATURE_SEMANTIC_SEARCH,
    FEATURE_QA_ENGINE,
    FEATURE_LARGE_CORPUS_INDEXING,
    FEATURE_DATA_SYNTHESIS,
    FEATURE_AUTOMATION,
    FEATURE_PAGE_LIMIT_100,
    FEATURE_PAGE_LIMIT_1000,
)
from bots.research_analyzer_bot.research_analyzer_bot import (
    ResearchAnalyzerBot,
    ResearchAnalyzerBotError,
)


# ===========================================================================
# Tier tests
# ===========================================================================

class TestTiers:
    def test_tier_enum_values(self):
        assert Tier.FREE.value == "free"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_free_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_upgrade_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_free_has_basic_search(self):
        assert FEATURE_BASIC_SEARCH in BOT_FEATURES[Tier.FREE.value]

    def test_free_has_summarization(self):
        assert FEATURE_SUMMARIZATION in BOT_FEATURES[Tier.FREE.value]

    def test_pro_has_semantic_search(self):
        assert FEATURE_SEMANTIC_SEARCH in BOT_FEATURES[Tier.PRO.value]

    def test_pro_has_qa_engine(self):
        assert FEATURE_QA_ENGINE in BOT_FEATURES[Tier.PRO.value]

    def test_enterprise_has_large_corpus(self):
        assert FEATURE_LARGE_CORPUS_INDEXING in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_enterprise_has_data_synthesis(self):
        assert FEATURE_DATA_SYNTHESIS in BOT_FEATURES[Tier.ENTERPRISE.value]

    def test_free_lacks_large_corpus(self):
        assert FEATURE_LARGE_CORPUS_INDEXING not in BOT_FEATURES[Tier.FREE.value]

    def test_page_limit_free_via_feature_flag(self):
        assert FEATURE_PAGE_LIMIT_100 in BOT_FEATURES[Tier.FREE.value]

    def test_page_limit_pro_via_feature_flag(self):
        assert FEATURE_PAGE_LIMIT_1000 in BOT_FEATURES[Tier.PRO.value]

    def test_free_lacks_page_limit_1000(self):
        assert FEATURE_PAGE_LIMIT_1000 not in BOT_FEATURES[Tier.FREE.value]

    def test_daily_limit_free(self):
        assert DAILY_LIMITS[Tier.FREE.value] == 20

    def test_daily_limit_enterprise_unlimited(self):
        assert DAILY_LIMITS[Tier.ENTERPRISE.value] is None

    def test_get_bot_tier_info_returns_dict(self):
        info = get_bot_tier_info(Tier.PRO)
        assert isinstance(info, dict)
        assert "features" in info
        assert "daily_limit" in info


# ===========================================================================
# ResearchAnalyzerBot — instantiation
# ===========================================================================

class TestResearchAnalyzerBotInit:
    def test_default_tier_is_free(self):
        bot = ResearchAnalyzerBot()
        assert bot.tier == Tier.FREE

    def test_daily_count_starts_zero(self):
        bot = ResearchAnalyzerBot()
        assert bot._daily_count == 0

    def test_documents_dict_starts_empty(self):
        bot = ResearchAnalyzerBot()
        assert len(bot._documents) == 0


# ===========================================================================
# ingest_documents
# ===========================================================================

class TestIngestDocuments:
    def setup_method(self):
        self.bot = ResearchAnalyzerBot(tier=Tier.PRO)

    def test_returns_dict(self):
        result = self.bot.ingest_documents(["doc1.pdf"])
        assert isinstance(result, dict)

    def test_ingested_field(self):
        result = self.bot.ingest_documents(["doc1.pdf", "doc2.pdf"])
        assert result["ingested"] == 2

    def test_document_ids_count(self):
        result = self.bot.ingest_documents(["a.pdf", "b.pdf", "c.pdf"])
        assert len(result["document_ids"]) == 3

    def test_has_total_pages(self):
        result = self.bot.ingest_documents(["doc.pdf"])
        assert "total_pages" in result
        assert isinstance(result["total_pages"], int)

    def test_updates_documents_indexed(self):
        self.bot.ingest_documents(["d1.pdf"])
        assert len(self.bot._documents) >= 1

    def test_free_page_limit_is_100(self):
        bot = ResearchAnalyzerBot(tier=Tier.FREE)
        assert bot._page_limit() == 100

    def test_pro_page_limit_is_1000(self):
        bot = ResearchAnalyzerBot(tier=Tier.PRO)
        assert bot._page_limit() == 1000


# ===========================================================================
# semantic_search
# ===========================================================================

class TestSemanticSearch:
    def test_pro_can_semantic_search(self):
        bot = ResearchAnalyzerBot(tier=Tier.PRO)
        result = bot.semantic_search("machine learning")
        assert isinstance(result, dict)
        assert "results" in result

    def test_results_count_respects_top_k(self):
        bot = ResearchAnalyzerBot(tier=Tier.PRO)
        result = bot.semantic_search("AI", top_k=3)
        assert len(result["results"]) == 3

    def test_query_is_echoed(self):
        bot = ResearchAnalyzerBot(tier=Tier.PRO)
        result = bot.semantic_search("deep learning")
        assert result["query"] == "deep learning"

    def test_free_cannot_semantic_search(self):
        bot = ResearchAnalyzerBot(tier=Tier.FREE)
        with pytest.raises(ResearchAnalyzerBotError):
            bot.semantic_search("query")


# ===========================================================================
# answer_question
# ===========================================================================

class TestAnswerQuestion:
    def test_pro_can_answer_question(self):
        bot = ResearchAnalyzerBot(tier=Tier.PRO)
        result = bot.answer_question("What is reinforcement learning?")
        assert isinstance(result, dict)
        assert "answer" in result

    def test_answer_has_confidence(self):
        bot = ResearchAnalyzerBot(tier=Tier.PRO)
        result = bot.answer_question("What is AI?")
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1.0

    def test_answer_has_sources(self):
        bot = ResearchAnalyzerBot(tier=Tier.PRO)
        result = bot.answer_question("What is ML?")
        assert "sources" in result

    def test_free_cannot_use_qa_engine(self):
        bot = ResearchAnalyzerBot(tier=Tier.FREE)
        with pytest.raises(ResearchAnalyzerBotError):
            bot.answer_question("What is AI?")


# ===========================================================================
# summarize
# ===========================================================================

class TestSummarize:
    def test_free_can_summarize(self):
        bot = ResearchAnalyzerBot(tier=Tier.FREE)
        result = bot.summarize()
        assert isinstance(result, dict)
        assert "summary" in result

    def test_contains_key_themes(self):
        bot = ResearchAnalyzerBot(tier=Tier.FREE)
        result = bot.summarize()
        assert "key_points" in result or "key_themes" in result

    def test_with_document_id(self):
        bot = ResearchAnalyzerBot(tier=Tier.PRO)
        result = bot.summarize(document_id="doc_001")
        assert "document_id" in result


# ===========================================================================
# build_insights
# ===========================================================================

class TestBuildInsights:
    def test_enterprise_can_build_insights(self):
        bot = ResearchAnalyzerBot(tier=Tier.ENTERPRISE)
        result = bot.build_insights("autonomous vehicles")
        assert isinstance(result, dict)
        assert "insights" in result

    def test_topic_echoed(self):
        bot = ResearchAnalyzerBot(tier=Tier.ENTERPRISE)
        result = bot.build_insights("robotics")
        assert result["topic"] == "robotics"

    def test_free_cannot_build_insights(self):
        bot = ResearchAnalyzerBot(tier=Tier.FREE)
        with pytest.raises(ResearchAnalyzerBotError):
            bot.build_insights("topic")

    def test_pro_cannot_build_insights(self):
        bot = ResearchAnalyzerBot(tier=Tier.PRO)
        with pytest.raises(ResearchAnalyzerBotError):
            bot.build_insights("topic")


# ===========================================================================
# get_research_dashboard
# ===========================================================================

class TestGetResearchDashboard:
    def test_returns_dict(self):
        bot = ResearchAnalyzerBot(tier=Tier.PRO)
        assert isinstance(bot.get_research_dashboard(), dict)

    def test_contains_bot_name(self):
        bot = ResearchAnalyzerBot(tier=Tier.PRO)
        assert bot.get_research_dashboard()["bot_name"] == "ResearchAnalyzerBot"

    def test_enterprise_remaining_is_unlimited(self):
        bot = ResearchAnalyzerBot(tier=Tier.ENTERPRISE)
        assert bot.get_research_dashboard()["remaining"] == "unlimited"

    def test_daily_limit_enforced(self):
        bot = ResearchAnalyzerBot(tier=Tier.FREE)
        bot._daily_count = 20
        with pytest.raises(ResearchAnalyzerBotError):
            bot.summarize()
