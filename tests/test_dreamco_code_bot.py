"""Tests for bots/dreamco_code_bot — DreamCo cloud code platform."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.dreamco_code_bot.dreamco_code_bot import (
    DreamCoCodeBot,
    DreamCoCodeBotTierError,
    DreamCoCodeBotError,
    CodeSession,
    ExecutionResult,
)
from bots.dreamco_code_bot.tiers import get_bot_tier_info, BOT_FEATURES


# ===========================================================================
# Tier tests
# ===========================================================================

class TestDreamCoCodeBotTiers:
    def test_three_tiers_have_features(self):
        for tier in (Tier.FREE, Tier.PRO, Tier.ENTERPRISE):
            assert len(BOT_FEATURES[tier.value]) > 0

    def test_free_tier_features_subset(self):
        free = BOT_FEATURES[Tier.FREE.value]
        assert any("100" in f or "2 languages" in f for f in free)

    def test_enterprise_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_get_bot_tier_info_returns_dict(self):
        info = get_bot_tier_info(Tier.FREE)
        assert isinstance(info, dict)
        for key in ("tier", "name", "price_usd_monthly", "features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0


# ===========================================================================
# Instantiation tests
# ===========================================================================

class TestDreamCoCodeBotInstantiation:
    def test_default_tier_is_free(self):
        bot = DreamCoCodeBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = DreamCoCodeBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = DreamCoCodeBot()
        assert bot.config is not None

    def test_custom_user_id(self):
        bot = DreamCoCodeBot(user_id="alice")
        assert bot.user_id == "alice"


# ===========================================================================
# Language support tests
# ===========================================================================

class TestLanguageSupport:
    def test_free_lists_2_languages(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        assert len(bot.list_languages()) == 2

    def test_free_supports_python(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        assert bot.supports_language("python")

    def test_free_supports_javascript(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        assert bot.supports_language("javascript")

    def test_free_does_not_support_go(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        assert not bot.supports_language("go")

    def test_pro_lists_10_languages(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        assert len(bot.list_languages()) == 10

    def test_pro_supports_go(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        assert bot.supports_language("go")

    def test_enterprise_lists_more_than_10_languages(self):
        bot = DreamCoCodeBot(tier=Tier.ENTERPRISE)
        assert len(bot.list_languages()) > 10

    def test_language_check_is_case_insensitive(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        assert bot.supports_language("Python")
        assert bot.supports_language("JAVASCRIPT")


# ===========================================================================
# Code execution tests
# ===========================================================================

class TestCodeExecution:
    def test_execute_python_free(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        result = bot.execute("print('hello')", "python")
        assert isinstance(result, ExecutionResult)
        assert result.success

    def test_execute_returns_stdout(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        result = bot.execute("print('hi')", "python")
        assert isinstance(result.stdout, str)
        assert len(result.stdout) > 0

    def test_execute_returns_execution_time(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        result = bot.execute("print('hi')", "python")
        assert result.execution_time_ms > 0

    def test_execute_to_dict(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        result = bot.execute("print('hi')", "python")
        d = result.to_dict()
        for key in ("stdout", "stderr", "exit_code", "success", "language"):
            assert key in d

    def test_free_cannot_execute_restricted_language(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCodeBotTierError):
            bot.execute("fmt.Println('hi')", "go")

    def test_pro_can_execute_go(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        result = bot.execute("fmt.Println('hi')", "go")
        assert result.success

    def test_execution_count_increments(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        bot.execute("print('a')", "python")
        bot.execute("print('b')", "python")
        stats = bot.get_execution_stats()
        assert stats["executions_used"] == 2

    def test_execution_limit_enforced(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        bot._execution_count = 100
        with pytest.raises(DreamCoCodeBotTierError):
            bot.execute("print('hi')", "python")

    def test_enterprise_has_no_execution_limit(self):
        bot = DreamCoCodeBot(tier=Tier.ENTERPRISE)
        assert bot.EXECUTION_LIMITS[Tier.ENTERPRISE] is None


# ===========================================================================
# Package management tests
# ===========================================================================

class TestPackageManagement:
    def test_free_cannot_install_packages(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCodeBotTierError):
            bot.install_package("requests")

    def test_pro_can_install_packages(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        result = bot.install_package("requests")
        assert result["status"] == "installed"
        assert result["package"] == "requests"

    def test_enterprise_can_install_packages(self):
        bot = DreamCoCodeBot(tier=Tier.ENTERPRISE)
        result = bot.install_package("numpy")
        assert result["status"] == "installed"

    def test_install_package_tracks_in_session(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        session = bot.create_session("python")
        bot.install_package("flask", session_id=session.session_id)
        s = bot.get_session(session.session_id)
        assert "flask" in s.packages


# ===========================================================================
# Session management tests
# ===========================================================================

class TestSessionManagement:
    def test_free_cannot_create_sessions(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCodeBotTierError):
            bot.create_session("python")

    def test_pro_can_create_session(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        session = bot.create_session("python")
        assert isinstance(session, CodeSession)
        assert session.language == "python"

    def test_session_has_id(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        session = bot.create_session("python")
        assert len(session.session_id) > 0

    def test_get_session_by_id(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        session = bot.create_session("python")
        retrieved = bot.get_session(session.session_id)
        assert retrieved.session_id == session.session_id

    def test_get_missing_session_raises(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        with pytest.raises(DreamCoCodeBotError):
            bot.get_session("nonexistent-id")

    def test_list_sessions(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        bot.create_session("python")
        bot.create_session("javascript")
        sessions = bot.list_sessions()
        assert len(sessions) == 2

    def test_session_history_tracked(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        session = bot.create_session("python")
        bot.execute("print('hi')", "python", session_id=session.session_id)
        assert len(session.history) == 1

    def test_session_to_dict(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        session = bot.create_session("python")
        d = session.to_dict()
        for key in ("session_id", "language", "user_id", "history_count"):
            assert key in d


# ===========================================================================
# Snippet sharing tests
# ===========================================================================

class TestSnippetSharing:
    def test_free_cannot_share_snippets(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCodeBotTierError):
            bot.share_snippet("print('hi')", "python")

    def test_pro_can_share_snippet(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        snippet = bot.share_snippet("print('hi')", "python", title="Hello World")
        assert "snippet_id" in snippet
        assert "url" in snippet

    def test_snippet_url_is_string(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        snippet = bot.share_snippet("x = 1", "python")
        assert snippet["url"].startswith("https://")


# ===========================================================================
# AI suggestion tests
# ===========================================================================

class TestAISuggestions:
    def test_free_cannot_get_suggestions(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCodeBotTierError):
            bot.get_ai_suggestion("print('hi')", "python")

    def test_pro_gets_suggestions(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        result = bot.get_ai_suggestion("def foo():\n pass", "python")
        assert "suggestions" in result
        assert isinstance(result["suggestions"], list)
        assert len(result["suggestions"]) > 0

    def test_suggestion_has_quality_score(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        result = bot.get_ai_suggestion("x = 1", "python")
        assert "quality_score" in result
        assert isinstance(result["quality_score"], (int, float))


# ===========================================================================
# CI/CD Pipeline tests (ENTERPRISE)
# ===========================================================================

class TestCICDPipelines:
    def test_free_cannot_create_pipeline(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCodeBotTierError):
            bot.create_pipeline("My Pipeline", ["install", "test", "deploy"])

    def test_pro_cannot_create_pipeline(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        with pytest.raises(DreamCoCodeBotTierError):
            bot.create_pipeline("My Pipeline", ["install", "test"])

    def test_enterprise_can_create_pipeline(self):
        bot = DreamCoCodeBot(tier=Tier.ENTERPRISE)
        pipeline = bot.create_pipeline("CI Pipeline", ["npm install", "npm test", "npm run build"])
        assert "pipeline_id" in pipeline
        assert pipeline["name"] == "CI Pipeline"
        assert pipeline["status"] == "created"

    def test_pipeline_steps_preserved(self):
        bot = DreamCoCodeBot(tier=Tier.ENTERPRISE)
        steps = ["install", "test", "deploy"]
        pipeline = bot.create_pipeline("My Pipeline", steps)
        assert pipeline["steps"] == steps


# ===========================================================================
# Stats tests
# ===========================================================================

class TestExecutionStats:
    def test_initial_stats(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        stats = bot.get_execution_stats()
        assert stats["executions_used"] == 0
        assert stats["sessions_active"] == 0
        assert stats["snippets_shared"] == 0

    def test_stats_reflect_executions(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        bot.execute("print('hi')", "python")
        stats = bot.get_execution_stats()
        assert stats["executions_used"] == 1

    def test_enterprise_remaining_is_none(self):
        bot = DreamCoCodeBot(tier=Tier.ENTERPRISE)
        stats = bot.get_execution_stats()
        assert stats["executions_remaining"] is None


# ===========================================================================
# Chat interface tests
# ===========================================================================

class TestChatInterface:
    def test_default_chat_response(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        result = bot.chat("hello")
        assert "message" in result
        assert "data" in result

    def test_chat_languages_query(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        result = bot.chat("what languages are supported")
        assert "data" in result
        assert isinstance(result["data"], list)

    def test_chat_execute_intent(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        result = bot.chat("run python code")
        assert "data" in result

    def test_chat_stats_query(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        result = bot.chat("show my stats")
        assert "data" in result

    def test_chat_tier_query(self):
        bot = DreamCoCodeBot(tier=Tier.FREE)
        result = bot.chat("what tier am I on")
        assert "data" in result

    def test_chat_returns_dict(self):
        bot = DreamCoCodeBot(tier=Tier.PRO)
        result = bot.chat("hello")
        assert isinstance(result, dict)
