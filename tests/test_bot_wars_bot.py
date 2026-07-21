"""
Tests for the DreamCo Bot Wars Bot package.

Covers:
  - Tiers (3 tiers, prices, features)
  - CompetitionEngine (create, list, submit, score, leaderboard, winner)
  - ChallengeManager (create, list_active, join, submit_solution, stats)
  - DragDropBuilder (create project, add component, connect, validate, export)
  - BotWarsBot main class (tier enforcement, delegations, tier info, chat)
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.bot_wars_bot.tiers import (
    Tier,
    TierConfig,
    TIER_CATALOGUE,
    get_tier_config,
    list_tiers,
    get_upgrade_path,
    FREE_FEATURES,
    PRO_FEATURES,
    ENTERPRISE_FEATURES,
    FEATURE_VIEW_COMPETITIONS,
    FEATURE_JOIN_COMPETITIONS,
    FEATURE_HOST_PRIVATE_TOURNAMENTS,
)
from bots.bot_wars_bot.competition_engine import CompetitionEngine, CompetitionEngineError
from bots.bot_wars_bot.challenge_manager import (
    ChallengeManager,
    ChallengeManagerError,
    CHALLENGE_TYPES,
)
from bots.bot_wars_bot.drag_drop_builder import (
    DragDropBuilder,
    DragDropBuilderError,
    BOT_COMPONENT_TYPES,
)
from bots.bot_wars_bot.bot_wars_bot import BotWarsBot, BotWarsTierError


# ===========================================================================
# Tiers
# ===========================================================================


class TestTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_tier_enum_values(self):
        assert Tier.FREE.value == "free"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_free_tier_price(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_free_submission_limit(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_bot_submissions == 1

    def test_pro_submission_limit(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_bot_submissions == 10

    def test_enterprise_unlimited_submissions(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_submissions() is True

    def test_free_has_view_feature(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_VIEW_COMPETITIONS)

    def test_free_lacks_join_feature(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_JOIN_COMPETITIONS)

    def test_pro_has_join_feature(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_JOIN_COMPETITIONS)

    def test_enterprise_has_private_tournaments(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_HOST_PRIVATE_TOURNAMENTS)

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        upgrade = get_upgrade_path(Tier.ENTERPRISE)
        assert upgrade is None

    def test_list_tiers_returns_all(self):
        tiers = list_tiers()
        tier_values = [t.tier for t in tiers]
        assert Tier.FREE in tier_values
        assert Tier.PRO in tier_values
        assert Tier.ENTERPRISE in tier_values


# ===========================================================================
# CompetitionEngine
# ===========================================================================


class TestCompetitionEngine:
    def setup_method(self):
        self.engine = CompetitionEngine()

    def test_create_competition_returns_dict(self):
        comp = self.engine.create_competition(
            "Bot Royale", "creativity", "Most creative bot wins!", 100.0
        )
        assert isinstance(comp, dict)
        assert comp["name"] == "Bot Royale"

    def test_create_competition_has_id(self):
        comp = self.engine.create_competition("Test", "learning", "desc", 0)
        assert "id" in comp and len(comp["id"]) > 0

    def test_create_competition_invalid_category_raises(self):
        with pytest.raises(CompetitionEngineError):
            self.engine.create_competition("Test", "invalid_cat", "desc", 0)

    def test_create_competition_empty_name_raises(self):
        with pytest.raises(CompetitionEngineError):
            self.engine.create_competition("", "creativity", "desc", 0)

    def test_list_competitions_empty(self):
        assert self.engine.list_competitions() == []

    def test_list_competitions_returns_created(self):
        self.engine.create_competition("A", "student", "desc", 0)
        self.engine.create_competition("B", "hobbyist", "desc", 0)
        assert len(self.engine.list_competitions()) == 2

    def test_list_competitions_filter_by_category(self):
        self.engine.create_competition("A", "creativity", "desc", 0)
        self.engine.create_competition("B", "learning", "desc", 0)
        result = self.engine.list_competitions(category="creativity")
        assert len(result) == 1
        assert result[0]["category"] == "creativity"

    def test_submit_bot_returns_dict(self):
        comp = self.engine.create_competition("RC", "community", "desc", 0)
        sub = self.engine.submit_bot(comp["id"], "user1", "MyBot", "A cool bot")
        assert isinstance(sub, dict)
        assert sub["bot_name"] == "MyBot"

    def test_submit_bot_invalid_competition_raises(self):
        with pytest.raises(CompetitionEngineError):
            self.engine.submit_bot("nonexistent", "u1", "Bot", "desc")

    def test_score_submission_calculates_total(self):
        comp = self.engine.create_competition("SC", "problem_solving", "desc", 0)
        sub = self.engine.submit_bot(comp["id"], "u1", "ScoreBot", "desc")
        scored = self.engine.score_submission(
            comp["id"],
            sub["id"],
            {"creativity": 80, "accuracy": 90, "speed": 70, "innovation": 60},
        )
        assert scored["total_score"] == pytest.approx(75.0)

    def test_score_submission_missing_key_raises(self):
        comp = self.engine.create_competition("MS", "corporate", "desc", 0)
        sub = self.engine.submit_bot(comp["id"], "u1", "Bot", "desc")
        with pytest.raises(CompetitionEngineError):
            self.engine.score_submission(comp["id"], sub["id"], {"creativity": 50})

    def test_score_out_of_range_raises(self):
        comp = self.engine.create_competition("OR", "creativity", "desc", 0)
        sub = self.engine.submit_bot(comp["id"], "u1", "Bot", "desc")
        with pytest.raises(CompetitionEngineError):
            self.engine.score_submission(
                comp["id"], sub["id"],
                {"creativity": 150, "accuracy": 50, "speed": 50, "innovation": 50},
            )

    def test_get_leaderboard_sorted(self):
        comp = self.engine.create_competition("LB", "creativity", "desc", 0)
        sub1 = self.engine.submit_bot(comp["id"], "u1", "Bot1", "desc")
        sub2 = self.engine.submit_bot(comp["id"], "u2", "Bot2", "desc")
        self.engine.score_submission(
            comp["id"], sub1["id"],
            {"creativity": 50, "accuracy": 50, "speed": 50, "innovation": 50},
        )
        self.engine.score_submission(
            comp["id"], sub2["id"],
            {"creativity": 90, "accuracy": 90, "speed": 90, "innovation": 90},
        )
        board = self.engine.get_leaderboard(comp["id"])
        assert board[0]["id"] == sub2["id"]

    def test_get_winner_returns_top(self):
        comp = self.engine.create_competition("WN", "creativity", "desc", 0)
        sub = self.engine.submit_bot(comp["id"], "u1", "WinBot", "desc")
        self.engine.score_submission(
            comp["id"], sub["id"],
            {"creativity": 100, "accuracy": 100, "speed": 100, "innovation": 100},
        )
        winner = self.engine.get_winner(comp["id"])
        assert winner["id"] == sub["id"]

    def test_get_winner_no_submissions_returns_empty(self):
        comp = self.engine.create_competition("EW", "student", "desc", 0)
        assert self.engine.get_winner(comp["id"]) == {}


# ===========================================================================
# ChallengeManager
# ===========================================================================


class TestChallengeManager:
    def setup_method(self):
        self.manager = ChallengeManager()

    def test_create_challenge_returns_dict(self):
        ch = self.manager.create_challenge(
            "Speed Sprint", "creativity_sprint", "Build fast!", 7, 500
        )
        assert isinstance(ch, dict)
        assert ch["title"] == "Speed Sprint"

    def test_create_challenge_has_id(self):
        ch = self.manager.create_challenge("T", "bot_showdown", "d", 1, 100)
        assert "id" in ch and len(ch["id"]) > 0

    def test_create_challenge_invalid_type_raises(self):
        with pytest.raises(ChallengeManagerError):
            self.manager.create_challenge("T", "bad_type", "d", 1, 100)

    def test_create_challenge_empty_title_raises(self):
        with pytest.raises(ChallengeManagerError):
            self.manager.create_challenge("", "bot_showdown", "d", 1, 100)

    def test_create_challenge_zero_duration_raises(self):
        with pytest.raises(ChallengeManagerError):
            self.manager.create_challenge("T", "bot_showdown", "d", 0, 100)

    def test_list_active_challenges(self):
        self.manager.create_challenge("A", "regional_challenge", "d", 5, 200)
        self.manager.create_challenge("B", "industry_challenge", "d", 10, 300)
        assert len(self.manager.list_active_challenges()) == 2

    def test_join_challenge_returns_dict(self):
        ch = self.manager.create_challenge("Join Test", "real_world_solver", "d", 3, 100)
        participant = self.manager.join_challenge(ch["id"], "user42")
        assert participant["user_id"] == "user42"

    def test_join_challenge_twice_raises(self):
        ch = self.manager.create_challenge("DupJoin", "bot_showdown", "d", 3, 100)
        self.manager.join_challenge(ch["id"], "userX")
        with pytest.raises(ChallengeManagerError):
            self.manager.join_challenge(ch["id"], "userX")

    def test_submit_solution_returns_dict(self):
        ch = self.manager.create_challenge("SolTest", "creativity_sprint", "d", 5, 100)
        self.manager.join_challenge(ch["id"], "userA")
        sol = self.manager.submit_solution(ch["id"], "userA", "My solution")
        assert sol["user_id"] == "userA"
        assert "id" in sol

    def test_submit_solution_without_join_raises(self):
        ch = self.manager.create_challenge("NoJoin", "bot_showdown", "d", 5, 100)
        with pytest.raises(ChallengeManagerError):
            self.manager.submit_solution(ch["id"], "unregistered", "solution")

    def test_get_challenge_stats(self):
        ch = self.manager.create_challenge("Stats", "industry_challenge", "d", 5, 250)
        self.manager.join_challenge(ch["id"], "u1")
        self.manager.join_challenge(ch["id"], "u2")
        self.manager.submit_solution(ch["id"], "u1", "sol1")
        stats = self.manager.get_challenge_stats(ch["id"])
        assert stats["participant_count"] == 2
        assert stats["submission_count"] == 1

    def test_challenge_types_list(self):
        assert "creativity_sprint" in CHALLENGE_TYPES
        assert "bot_showdown" in CHALLENGE_TYPES
        assert len(CHALLENGE_TYPES) == 5


# ===========================================================================
# DragDropBuilder
# ===========================================================================


class TestDragDropBuilder:
    def setup_method(self):
        self.builder = DragDropBuilder()

    def test_create_project_returns_dict(self):
        proj = self.builder.create_bot_project("user1", "MyBot", "A test bot")
        assert proj["bot_name"] == "MyBot"
        assert "id" in proj

    def test_create_project_empty_name_raises(self):
        with pytest.raises(DragDropBuilderError):
            self.builder.create_bot_project("user1", "", "desc")

    def test_add_component_returns_dict(self):
        proj = self.builder.create_bot_project("u1", "Bot", "desc")
        comp = self.builder.add_component(proj["id"], "trigger", {"event": "on_message"})
        assert comp["component_type"] == "trigger"
        assert "id" in comp

    def test_add_component_invalid_type_raises(self):
        proj = self.builder.create_bot_project("u1", "Bot", "desc")
        with pytest.raises(DragDropBuilderError):
            self.builder.add_component(proj["id"], "bad_type", {})

    def test_list_components(self):
        proj = self.builder.create_bot_project("u1", "Bot", "desc")
        self.builder.add_component(proj["id"], "trigger", {})
        self.builder.add_component(proj["id"], "action", {})
        components = self.builder.list_components(proj["id"])
        assert len(components) == 2

    def test_connect_components_returns_dict(self):
        proj = self.builder.create_bot_project("u1", "Bot", "desc")
        c1 = self.builder.add_component(proj["id"], "trigger", {})
        c2 = self.builder.add_component(proj["id"], "action", {})
        conn = self.builder.connect_components(proj["id"], c1["id"], c2["id"])
        assert conn["from_component_id"] == c1["id"]
        assert conn["to_component_id"] == c2["id"]

    def test_connect_component_to_itself_raises(self):
        proj = self.builder.create_bot_project("u1", "Bot", "desc")
        c1 = self.builder.add_component(proj["id"], "trigger", {})
        with pytest.raises(DragDropBuilderError):
            self.builder.connect_components(proj["id"], c1["id"], c1["id"])

    def test_validate_bot_no_components(self):
        proj = self.builder.create_bot_project("u1", "Bot", "desc")
        result = self.builder.validate_bot(proj["id"])
        assert result["valid"] is False
        assert len(result["issues"]) > 0

    def test_validate_bot_missing_trigger(self):
        proj = self.builder.create_bot_project("u1", "Bot", "desc")
        self.builder.add_component(proj["id"], "action", {})
        result = self.builder.validate_bot(proj["id"])
        assert result["valid"] is False
        assert any("TRIGGER" in issue for issue in result["issues"])

    def test_validate_bot_valid(self):
        proj = self.builder.create_bot_project("u1", "Bot", "desc")
        self.builder.add_component(proj["id"], "trigger", {})
        self.builder.add_component(proj["id"], "action", {})
        result = self.builder.validate_bot(proj["id"])
        assert result["valid"] is True
        assert result["issues"] == []

    def test_export_bot_valid(self):
        proj = self.builder.create_bot_project("u1", "ExportBot", "desc")
        self.builder.add_component(proj["id"], "trigger", {})
        self.builder.add_component(proj["id"], "output", {})
        exported = self.builder.export_bot(proj["id"])
        assert exported["valid"] is True
        assert exported["bot_name"] == "ExportBot"
        assert exported["status"] == "exported"

    def test_export_bot_invalid_keeps_draft_status(self):
        proj = self.builder.create_bot_project("u1", "BadBot", "desc")
        exported = self.builder.export_bot(proj["id"])
        assert exported["valid"] is False
        assert exported["status"] == "draft"

    def test_bot_component_types_list(self):
        assert "trigger" in BOT_COMPONENT_TYPES
        assert "action" in BOT_COMPONENT_TYPES
        assert len(BOT_COMPONENT_TYPES) == 8


# ===========================================================================
# BotWarsBot (main class)
# ===========================================================================


class TestBotWarsBot:
    def test_free_tier_init(self):
        bot = BotWarsBot(tier=Tier.FREE)
        assert bot.tier == Tier.FREE

    def test_pro_tier_init(self):
        bot = BotWarsBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier_init(self):
        bot = BotWarsBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_free_can_list_competitions(self):
        bot = BotWarsBot(tier=Tier.FREE)
        result = bot.list_competitions()
        assert isinstance(result, list)

    def test_free_cannot_create_competition(self):
        bot = BotWarsBot(tier=Tier.FREE)
        with pytest.raises(BotWarsTierError):
            bot.create_competition("X", "creativity", "desc", 0)

    def test_free_cannot_submit_bot(self):
        bot = BotWarsBot(tier=Tier.FREE)
        with pytest.raises(BotWarsTierError):
            bot.submit_bot("fake-id", "u1", "Bot", "desc")

    def test_pro_can_create_competition(self):
        bot = BotWarsBot(tier=Tier.PRO)
        comp = bot.create_competition("Pro Battle", "creativity", "desc", 50)
        assert comp["name"] == "Pro Battle"

    def test_pro_can_submit_bot(self):
        bot = BotWarsBot(tier=Tier.PRO)
        comp = bot.create_competition("Sub Test", "learning", "desc", 0)
        sub = bot.submit_bot(comp["id"], "u1", "ProBot", "desc")
        assert sub["bot_name"] == "ProBot"

    def test_pro_can_score_submission(self):
        bot = BotWarsBot(tier=Tier.PRO)
        comp = bot.create_competition("Score Test", "student", "desc", 0)
        sub = bot.submit_bot(comp["id"], "u1", "SBot", "desc")
        scored = bot.score_submission(
            comp["id"], sub["id"],
            {"creativity": 80, "accuracy": 70, "speed": 60, "innovation": 90},
        )
        assert "total_score" in scored

    def test_free_can_get_leaderboard(self):
        # FREE tier should be able to call get_leaderboard (no tier check)
        bot = BotWarsBot(tier=Tier.FREE)
        # Directly create a competition in the engine to bypass tier gate
        comp = bot.competition_engine.create_competition("LBTest", "community", "desc", 0)
        board = bot.get_leaderboard(comp["id"])
        assert isinstance(board, list)

    def test_pro_cannot_host_private_tournament(self):
        bot = BotWarsBot(tier=Tier.PRO)
        with pytest.raises(BotWarsTierError):
            bot.host_private_tournament("Corp Finals", "desc", 1000)

    def test_enterprise_can_host_private_tournament(self):
        bot = BotWarsBot(tier=Tier.ENTERPRISE)
        tournament = bot.host_private_tournament("Corp Finals", "Private event", 2000)
        assert tournament["name"] == "Corp Finals"

    def test_get_tier_info_returns_dict(self):
        bot = BotWarsBot(tier=Tier.PRO)
        info = bot.get_tier_info()
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] == 49.0

    def test_get_upgrade_info_from_free(self):
        bot = BotWarsBot(tier=Tier.FREE)
        upgrade = bot.get_upgrade_info()
        assert upgrade is not None
        assert upgrade["tier"] == "pro"

    def test_get_upgrade_info_from_enterprise_is_none(self):
        bot = BotWarsBot(tier=Tier.ENTERPRISE)
        assert bot.get_upgrade_info() is None

    def test_pro_can_create_challenge(self):
        bot = BotWarsBot(tier=Tier.PRO)
        ch = bot.create_challenge("Hack Week", "bot_showdown", "desc", 7, 300)
        assert ch["title"] == "Hack Week"

    def test_free_cannot_create_challenge(self):
        bot = BotWarsBot(tier=Tier.FREE)
        with pytest.raises(BotWarsTierError):
            bot.create_challenge("Hack Week", "bot_showdown", "desc", 7, 300)

    def test_pro_can_build_bot_project(self):
        bot = BotWarsBot(tier=Tier.PRO)
        proj = bot.build_bot_project("u1", "VizBot", "no-code bot")
        assert proj["bot_name"] == "VizBot"

    def test_pro_can_validate_bot(self):
        bot = BotWarsBot(tier=Tier.PRO)
        proj = bot.build_bot_project("u1", "ValBot", "desc")
        bot.add_component(proj["id"], "trigger", {})
        bot.add_component(proj["id"], "action", {})
        result = bot.validate_bot(proj["id"])
        assert result["valid"] is True

    def test_chat_response_is_string(self):
        bot = BotWarsBot(tier=Tier.FREE)
        response = bot.chat("hello")
        assert isinstance(response, str)

    def test_chat_competition_keyword(self):
        bot = BotWarsBot(tier=Tier.FREE)
        response = bot.chat("show me competitions")
        assert "competition" in response.lower()

    def test_chat_upgrade_keyword(self):
        bot = BotWarsBot(tier=Tier.FREE)
        response = bot.chat("upgrade my plan")
        assert "upgrade" in response.lower() or "pro" in response.lower()
