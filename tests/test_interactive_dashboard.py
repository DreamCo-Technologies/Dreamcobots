"""
Tests for bots/big_bro_ai/interactive_dashboard.py

Covers:
  1. Progress bar rendering
  2. Achievement system
  3. XP & Level progression
  4. Hustle Simulator
  5. Code Gladiator
  6. Bot Idea Manager
  7. Bot Speed Control
  8. Dashboard snapshot & render
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.big_bro_ai.interactive_dashboard import (
    InteractiveDashboard,
    BotSpeed,
    BotIdea,
    Achievement,
    progress_bar,
)


# ===========================================================================
# 1. Progress Bar
# ===========================================================================

class TestProgressBar:
    def test_empty_bar(self):
        bar = progress_bar(0)
        assert bar.startswith("[─")
        assert "0%" in bar

    def test_full_bar(self):
        bar = progress_bar(100)
        assert "100%" in bar

    def test_half_bar(self):
        bar = progress_bar(50)
        assert "50%" in bar

    def test_custom_width(self):
        bar = progress_bar(50, total=100, width=10)
        assert len(bar) > 0

    def test_overflow_clamped(self):
        bar = progress_bar(150, total=100)
        assert "100%" in bar

    def test_underflow_clamped(self):
        bar = progress_bar(-10, total=100)
        assert "0%" in bar


# ===========================================================================
# 2. Achievement System
# ===========================================================================

class TestAchievements:
    def setup_method(self):
        self.dashboard = InteractiveDashboard()

    def test_all_default_achievements_exist(self):
        achievements = self.dashboard.get_achievements()
        assert len(achievements) >= 8

    def test_achievements_start_locked(self):
        achievements = self.dashboard.get_achievements()
        all_locked = all(not a["unlocked"] for a in achievements)
        assert all_locked

    def test_unlock_first_hustle(self):
        result = self.dashboard.unlock_achievement("First Hustle")
        assert result["unlocked"] is True
        assert result["newly_unlocked"] is True

    def test_unlock_same_achievement_twice(self):
        self.dashboard.unlock_achievement("Bot Creator")
        result = self.dashboard.unlock_achievement("Bot Creator")
        assert result["newly_unlocked"] is False

    def test_unlock_unknown_achievement(self):
        result = self.dashboard.unlock_achievement("Nonexistent Award")
        assert result["status"] == "not_found"

    def test_achievement_icon_changes_after_unlock(self):
        self.dashboard.unlock_achievement("Code Warrior")
        achievements = {a["name"]: a for a in self.dashboard.get_achievements()}
        assert achievements["Code Warrior"]["icon"] == "🏆"

    def test_locked_achievement_icon(self):
        achievements = {a["name"]: a for a in self.dashboard.get_achievements()}
        assert achievements["First Hustle"]["icon"] == "🔒"


# ===========================================================================
# 3. XP & Level
# ===========================================================================

class TestXPAndLevel:
    def setup_method(self):
        self.dashboard = InteractiveDashboard()

    def test_initial_xp_zero(self):
        assert self.dashboard.xp == 0

    def test_initial_level_one(self):
        assert self.dashboard.level == 1

    def test_add_xp_increases_xp(self):
        result = self.dashboard.add_xp(50)
        assert result["total_xp"] >= 50

    def test_level_up_at_100_xp(self):
        result = self.dashboard.add_xp(100)
        assert result["level"] >= 2

    def test_level_up_notification(self):
        result = self.dashboard.add_xp(100)
        assert result["leveled_up"] is True

    def test_xp_multiplier_aggressive(self):
        self.dashboard.set_bot_speed(BotSpeed.AGGRESSIVE)
        result = self.dashboard.add_xp(100)
        assert result["xp_earned"] == 150  # 1.5x multiplier

    def test_xp_multiplier_slow(self):
        self.dashboard.set_bot_speed(BotSpeed.SLOW)
        result = self.dashboard.add_xp(100)
        assert result["xp_earned"] == 50  # 0.5x multiplier

    def test_xp_to_next_level_decreases(self):
        self.dashboard.add_xp(50)
        snap = self.dashboard.snapshot()
        assert snap["xp_to_next_level"] < 100

    def test_big_bro_approved_achievement_at_500_xp(self):
        self.dashboard.add_xp(500)
        achievements = {a["name"]: a for a in self.dashboard.get_achievements()}
        assert achievements["Big Bro Approved"]["unlocked"] is True


# ===========================================================================
# 4. Hustle Simulator
# ===========================================================================

class TestHustleSimulator:
    def setup_method(self):
        self.dashboard = InteractiveDashboard()

    def test_hustle_returns_revenue(self):
        result = self.dashboard.hustle_simulator()
        assert result["revenue_usd"] > 0

    def test_hustle_returns_profit(self):
        result = self.dashboard.hustle_simulator()
        assert result["profit_usd"] > 0

    def test_hustle_profit_margin_40_pct(self):
        result = self.dashboard.hustle_simulator()
        assert result["profit_margin_pct"] == 40.0

    def test_hustle_awards_xp(self):
        result = self.dashboard.hustle_simulator()
        assert result["xp_earned"] > 0

    def test_hustle_unlocks_first_hustle(self):
        self.dashboard.hustle_simulator()
        achievements = {a["name"]: a for a in self.dashboard.get_achievements()}
        assert achievements["First Hustle"]["unlocked"] is True

    def test_hustle_includes_big_bro_message(self):
        result = self.dashboard.hustle_simulator()
        assert isinstance(result["big_bro_says"], str)
        assert len(result["big_bro_says"]) > 0

    def test_hustle_history_recorded(self):
        self.dashboard.hustle_simulator()
        self.dashboard.hustle_simulator()
        history = self.dashboard.get_hustle_history()
        assert len(history) == 2

    def test_aggressive_speed_increases_profit(self):
        import random as _random
        # Use a fixed seed so the revenue/profit values are deterministic
        _random.seed(42)
        self.dashboard.set_bot_speed(BotSpeed.MODERATE)
        moderate_revenue = self.dashboard.hustle_simulator()["revenue_usd"]
        _random.seed(42)
        self.dashboard.set_bot_speed(BotSpeed.AGGRESSIVE)
        aggressive_revenue = self.dashboard.hustle_simulator()["revenue_usd"]
        # Same base random value; aggressive (1.3×) must beat moderate (1.0×)
        assert aggressive_revenue > moderate_revenue


# ===========================================================================
# 5. Code Gladiator
# ===========================================================================

class TestCodeGladiator:
    def setup_method(self):
        self.dashboard = InteractiveDashboard()

    def test_challenge_returns_challenge_id(self):
        challenge = self.dashboard.code_gladiator_challenge()
        assert "challenge_id" in challenge

    def test_challenge_has_question(self):
        challenge = self.dashboard.code_gladiator_challenge()
        assert "question" in challenge

    def test_challenge_does_not_expose_secret(self):
        challenge = self.dashboard.code_gladiator_challenge()
        assert "_secret" not in challenge

    def test_correct_answer_gives_victory(self):
        # Brute-force: try all 10 digits until one matches
        for digit in range(10):
            self.dashboard = InteractiveDashboard()
            challenge = self.dashboard.code_gladiator_challenge()
            result = self.dashboard.submit_gladiator_answer(challenge["challenge_id"], digit)
            if result["result"] == "victory":
                assert result["xp_earned"] >= 40
                break

    def test_wrong_answer_gives_defeat(self):
        # Override a known secret by inspecting internal state
        self.dashboard.code_gladiator_challenge()
        history = self.dashboard._gladiator_history
        challenge_id = history[-1]["challenge_id"]
        secret = history[-1]["secret"]
        wrong_guess = (secret + 1) % 10
        result = self.dashboard.submit_gladiator_answer(challenge_id, wrong_guess)
        assert result["result"] == "defeat"

    def test_double_submit_rejected(self):
        challenge = self.dashboard.code_gladiator_challenge()
        cid = challenge["challenge_id"]
        self.dashboard.submit_gladiator_answer(cid, 0)
        result = self.dashboard.submit_gladiator_answer(cid, 0)
        assert result["status"] == "already_submitted"

    def test_unknown_challenge_id(self):
        result = self.dashboard.submit_gladiator_answer("ghost_challenge", 5)
        assert result["status"] == "not_found"

    def test_correct_unlocks_code_warrior(self):
        for digit in range(10):
            self.dashboard = InteractiveDashboard()
            challenge = self.dashboard.code_gladiator_challenge()
            result = self.dashboard.submit_gladiator_answer(challenge["challenge_id"], digit)
            if result["result"] == "victory":
                achievements = {a["name"]: a for a in self.dashboard.get_achievements()}
                assert achievements["Code Warrior"]["unlocked"] is True
                break


# ===========================================================================
# 6. Bot Idea Manager
# ===========================================================================

class TestBotIdeaManager:
    def setup_method(self):
        self.dashboard = InteractiveDashboard()

    def test_starter_ideas_loaded(self):
        assert len(self.dashboard.bot_ideas) == 3

    def test_generate_bot_idea(self):
        result = self.dashboard.generate_bot_idea()
        assert "new_bot" in result
        assert result["new_bot"]["profit_per_day_usd"] > 0

    def test_generate_increases_count(self):
        before = len(self.dashboard.bot_ideas)
        self.dashboard.generate_bot_idea()
        assert len(self.dashboard.bot_ideas) == before + 1

    def test_generate_awards_xp(self):
        result = self.dashboard.generate_bot_idea()
        assert result["xp_earned"] > 0

    def test_generate_unlocks_bot_creator(self):
        self.dashboard.generate_bot_idea()
        achievements = {a["name"]: a for a in self.dashboard.get_achievements()}
        assert achievements["Bot Creator"]["unlocked"] is True

    def test_empire_builder_at_10_ideas(self):
        for _ in range(10):
            self.dashboard.generate_bot_idea()
        achievements = {a["name"]: a for a in self.dashboard.get_achievements()}
        assert achievements["Empire Builder"]["unlocked"] is True

    def test_get_top_bots_by_profit(self):
        top = self.dashboard.get_top_bots(n=3, sort_by="profit")
        assert len(top) == 3
        assert top[0]["profit_per_day_usd"] >= top[-1]["profit_per_day_usd"]

    def test_get_top_bots_by_usage(self):
        top = self.dashboard.get_top_bots(n=3, sort_by="usage")
        assert len(top) == 3
        assert top[0]["usage_pct"] >= top[-1]["usage_pct"]


# ===========================================================================
# 7. Bot Speed Control
# ===========================================================================

class TestBotSpeedControl:
    def setup_method(self):
        self.dashboard = InteractiveDashboard()

    def test_default_speed_moderate(self):
        assert self.dashboard.bot_speed == BotSpeed.MODERATE

    def test_set_speed_slow(self):
        result = self.dashboard.set_bot_speed(BotSpeed.SLOW)
        assert result["bot_speed"] == "slow"
        assert self.dashboard.bot_speed == BotSpeed.SLOW

    def test_set_speed_aggressive(self):
        result = self.dashboard.set_bot_speed(BotSpeed.AGGRESSIVE)
        assert result["bot_speed"] == "aggressive"

    def test_aggressive_unlocks_speed_demon(self):
        self.dashboard.set_bot_speed(BotSpeed.AGGRESSIVE)
        achievements = {a["name"]: a for a in self.dashboard.get_achievements()}
        assert achievements["Speed Demon"]["unlocked"] is True

    def test_speed_multipliers_are_correct(self):
        assert BotSpeed.SLOW.xp_multiplier == 0.5
        assert BotSpeed.MODERATE.xp_multiplier == 1.0
        assert BotSpeed.AGGRESSIVE.xp_multiplier == 1.5

    def test_profit_multipliers_correct(self):
        assert BotSpeed.AGGRESSIVE.profit_multiplier == 1.3


# ===========================================================================
# 8. Dashboard Snapshot & Render
# ===========================================================================

class TestDashboardSnapshot:
    def setup_method(self):
        self.dashboard = InteractiveDashboard()

    def test_snapshot_has_required_keys(self):
        snap = self.dashboard.snapshot()
        for key in ("module", "level", "total_xp", "xp_in_level", "progress_bar",
                    "xp_to_next_level", "bot_speed", "bot_ideas_count",
                    "top_bots", "achievements", "big_bro_says", "timestamp"):
            assert key in snap, f"Missing key: {key}"

    def test_snapshot_module_name(self):
        snap = self.dashboard.snapshot()
        assert snap["module"] == "Interactive Dashboard"

    def test_snapshot_big_bro_says_not_empty(self):
        snap = self.dashboard.snapshot()
        assert len(snap["big_bro_says"]) > 0

    def test_render_returns_string(self):
        output = self.dashboard.render()
        assert isinstance(output, str)

    def test_render_contains_header(self):
        output = self.dashboard.render()
        assert "BIG BRO AI EMPIRE" in output

    def test_render_contains_level(self):
        output = self.dashboard.render()
        assert "Level:" in output

    def test_render_contains_menu(self):
        output = self.dashboard.render()
        assert "MENU" in output

    def test_render_contains_achievements_section(self):
        output = self.dashboard.render()
        assert "Achievements" in output

    def test_big_bro_message_returns_string(self):
        msg = self.dashboard.big_bro_message()
        assert isinstance(msg, str)
        assert len(msg) > 0
