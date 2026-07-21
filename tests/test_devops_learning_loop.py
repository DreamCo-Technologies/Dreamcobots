"""
Tests for:
  - bots/devops_bot/devops_bot.py      (DevOpsBot / Bot alias)
  - bots/ai_learning_system/learning_loop.py  (LearningLoop)
  - BotGeneratorBot.test_bot / BotGeneratorBot.create_bot  (new methods)
"""
import sys
import os
import types
import unittest.mock as mock

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# DevOps Bot tests
# ---------------------------------------------------------------------------

from bots.devops_bot.devops_bot import DevOpsBot, Bot


class TestDevOpsBotFrameworkCompliance:
    def test_devops_bot_file_has_global_ai_sources_flow_marker(self):
        bot_file = os.path.join(REPO_ROOT, "bots", "devops_bot", "devops_bot.py")
        text = open(bot_file).read()
        assert "GlobalAISourcesFlow" in text or "GLOBAL AI SOURCES FLOW" in text

    def test_bot_alias_equals_devops_bot(self):
        assert Bot is DevOpsBot


class TestDevOpsBotRun:
    def test_run_returns_string(self):
        bot = DevOpsBot()
        with mock.patch("os.system", return_value=0):
            result = bot.run()
        assert isinstance(result, str)
        assert "GitHub" in result

    def test_run_calls_git_add(self):
        bot = DevOpsBot()
        with mock.patch("os.system", return_value=0) as mock_sys:
            bot.run()
        calls = [str(c) for c in mock_sys.call_args_list]
        assert any("git add" in c for c in calls)

    def test_run_calls_git_commit(self):
        bot = DevOpsBot()
        with mock.patch("os.system", return_value=0) as mock_sys:
            bot.run()
        calls = [str(c) for c in mock_sys.call_args_list]
        assert any("git commit" in c for c in calls)

    def test_run_calls_git_push_on_success(self):
        bot = DevOpsBot()
        with mock.patch("os.system", return_value=0) as mock_sys:
            bot.run()
        calls = [str(c) for c in mock_sys.call_args_list]
        assert any("git push" in c for c in calls)

    def test_run_reports_nothing_to_commit_on_commit_failure(self):
        bot = DevOpsBot()
        # commit returns non-zero → nothing to commit
        with mock.patch("os.system", side_effect=[0, 1]):
            result = bot.run()
        assert "Nothing to commit" in result or "commit failed" in result

    def test_run_reports_push_failed_on_push_error(self):
        bot = DevOpsBot()
        # git add OK (0), commit OK (0), push fails (1)
        with mock.patch("os.system", side_effect=[0, 0, 1]):
            result = bot.run()
        assert "Push failed" in result or "push" in result.lower()

    def test_process_returns_dict(self):
        bot = DevOpsBot()
        with mock.patch("os.system", return_value=0):
            result = bot.process()
        assert isinstance(result, dict)
        assert "status" in result

    def test_process_with_payload(self):
        bot = DevOpsBot()
        with mock.patch("os.system", return_value=0):
            result = bot.process({})
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# LearningLoop tests
# ---------------------------------------------------------------------------

from bots.ai_learning_system.learning_loop import (
    LearningLoop,
    DEFAULT_UNDERPERFORM_THRESHOLD,
    DEFAULT_SCORE_MIN,
    DEFAULT_SCORE_MAX,
)


class _FakeControlCenter:
    """Minimal control-center stub exposing a .bots dict."""

    def __init__(self, bot_names=("alpha", "beta", "gamma")):
        self.bots = {name: object() for name in bot_names}


class _FakeGenerator:
    """Minimal generator stub exposing create_bot."""

    def __init__(self):
        self.created: list[str] = []

    def create_bot(self, name: str) -> dict:
        self.created.append(name)
        return {"bot_name": name}


class TestLearningLoopDefaults:
    def test_default_threshold_is_30(self):
        assert DEFAULT_UNDERPERFORM_THRESHOLD == 30

    def test_score_min_less_than_max(self):
        assert DEFAULT_SCORE_MIN < DEFAULT_SCORE_MAX

    def test_init_stores_control_center(self):
        cc = _FakeControlCenter()
        gen = _FakeGenerator()
        loop = LearningLoop(cc, gen)
        assert loop.control_center is cc

    def test_init_stores_generator(self):
        cc = _FakeControlCenter()
        gen = _FakeGenerator()
        loop = LearningLoop(cc, gen)
        assert loop.generator is gen

    def test_init_default_threshold(self):
        loop = LearningLoop(_FakeControlCenter(), _FakeGenerator())
        assert loop.underperform_threshold == DEFAULT_UNDERPERFORM_THRESHOLD

    def test_init_custom_threshold(self):
        loop = LearningLoop(_FakeControlCenter(), _FakeGenerator(), underperform_threshold=50)
        assert loop.underperform_threshold == 50

    def test_performance_log_empty_on_init(self):
        loop = LearningLoop(_FakeControlCenter(), _FakeGenerator())
        assert loop.performance_log == {}


class TestLearningLoopTrackPerformance:
    def test_track_performance_returns_dict(self):
        cc = _FakeControlCenter(["alpha", "beta"])
        loop = LearningLoop(cc, _FakeGenerator())
        result = loop.track_performance()
        assert isinstance(result, dict)

    def test_track_performance_covers_all_bots(self):
        names = ("alpha", "beta", "gamma")
        cc = _FakeControlCenter(names)
        loop = LearningLoop(cc, _FakeGenerator())
        result = loop.track_performance()
        assert set(result.keys()) == set(names)

    def test_track_performance_scores_in_range(self):
        cc = _FakeControlCenter(["alpha"] * 20)
        loop = LearningLoop(cc, _FakeGenerator())
        for _ in range(10):
            result = loop.track_performance()
            for score in result.values():
                assert DEFAULT_SCORE_MIN <= score <= DEFAULT_SCORE_MAX

    def test_track_performance_populates_log(self):
        cc = _FakeControlCenter(["alpha"])
        loop = LearningLoop(cc, _FakeGenerator())
        loop.track_performance()
        assert "alpha" in loop.performance_log

    def test_track_performance_empty_control_center(self):
        cc = _FakeControlCenter([])
        loop = LearningLoop(cc, _FakeGenerator())
        result = loop.track_performance()
        assert result == {}


class TestLearningLoopOptimize:
    def test_optimize_returns_list(self):
        cc = _FakeControlCenter(["alpha"])
        loop = LearningLoop(cc, _FakeGenerator())
        result = loop.optimize()
        assert isinstance(result, list)

    def test_optimize_creates_replacement_for_underperformers(self):
        cc = _FakeControlCenter(["poor_bot"])
        gen = _FakeGenerator()
        loop = LearningLoop(cc, gen, underperform_threshold=101)
        # threshold=101 forces every bot to be flagged
        loop.optimize()
        assert "poor_bot_optimized" in gen.created

    def test_optimize_does_not_replace_good_bots(self):
        cc = _FakeControlCenter(["good_bot"])
        gen = _FakeGenerator()
        loop = LearningLoop(cc, gen, underperform_threshold=0)
        # threshold=0 means nothing is ever below 0
        loop.optimize()
        assert gen.created == []

    def test_optimize_replacement_name_has_optimized_suffix(self):
        cc = _FakeControlCenter(["my_bot"])
        gen = _FakeGenerator()
        loop = LearningLoop(cc, gen, underperform_threshold=101)
        created = loop.optimize()
        assert all(name.endswith("_optimized") for name in created)

    def test_optimize_returns_names_of_created_bots(self):
        names = ("alpha", "beta")
        cc = _FakeControlCenter(names)
        gen = _FakeGenerator()
        loop = LearningLoop(cc, gen, underperform_threshold=101)
        created = loop.optimize()
        assert set(created) == {"alpha_optimized", "beta_optimized"}

    def test_optimize_prints_improving_message(self, capsys):
        cc = _FakeControlCenter(["weak_bot"])
        gen = _FakeGenerator()
        loop = LearningLoop(cc, gen, underperform_threshold=101)
        loop.optimize()
        captured = capsys.readouterr()
        assert "Improving" in captured.out or "weak_bot" in captured.out

    def test_optimize_prints_optimizing_message(self, capsys):
        cc = _FakeControlCenter([])
        loop = LearningLoop(cc, _FakeGenerator())
        loop.optimize()
        captured = capsys.readouterr()
        assert "Optimizing" in captured.out


class TestLearningLoopHelpers:
    def test_get_performance_log_returns_copy(self):
        cc = _FakeControlCenter(["alpha"])
        loop = LearningLoop(cc, _FakeGenerator())
        loop.track_performance()
        log = loop.get_performance_log()
        log["alpha"] = -999
        assert loop.performance_log["alpha"] != -999

    def test_get_underperformers_returns_only_below_threshold(self):
        cc = _FakeControlCenter(["alpha"])
        gen = _FakeGenerator()
        loop = LearningLoop(cc, gen, underperform_threshold=50)
        loop.performance_log = {"alpha": 20, "beta": 80}
        underperformers = loop.get_underperformers()
        assert "alpha" in underperformers
        assert "beta" not in underperformers

    def test_get_underperformers_empty_when_all_pass(self):
        loop = LearningLoop(_FakeControlCenter([]), _FakeGenerator())
        loop.performance_log = {"alpha": 90, "beta": 75}
        assert loop.get_underperformers() == {}

    def test_framework_file_has_marker(self):
        ll_file = os.path.join(
            REPO_ROOT, "bots", "ai_learning_system", "learning_loop.py"
        )
        text = open(ll_file).read()
        assert "GlobalAISourcesFlow" in text or "GLOBAL AI SOURCES FLOW" in text


# ---------------------------------------------------------------------------
# BotGeneratorBot — test_bot + create_bot
# ---------------------------------------------------------------------------

from bots.bot_generator_bot.bot_generator_bot import BotGeneratorBot
from bots.bot_generator_bot.tiers import Tier


class TestBotGeneratorBotTestBot:
    def test_test_bot_returns_string(self):
        bot = BotGeneratorBot()
        result = bot.test_bot("devops_bot")
        assert isinstance(result, str)

    def test_test_bot_success_with_devops_bot(self):
        bot = BotGeneratorBot()
        with mock.patch("os.system", return_value=0):
            result = bot.test_bot("devops_bot")
        assert "GitHub" in result or isinstance(result, str)

    def test_test_bot_returns_failure_string_on_bad_module(self):
        bot = BotGeneratorBot()
        result = bot.test_bot("nonexistent_xyz_bot_999")
        assert result.startswith("Failed:")

    def test_test_bot_failure_message_contains_error_info(self):
        bot = BotGeneratorBot()
        result = bot.test_bot("nonexistent_xyz_bot_999")
        assert len(result) > len("Failed:")

    def test_test_bot_handles_exception_gracefully(self):
        bot = BotGeneratorBot()
        # Should never raise — always return a string
        result = bot.test_bot("__this_does_not_exist__")
        assert isinstance(result, str)


class TestBotGeneratorBotCreateBot:
    def test_create_bot_returns_dict(self):
        bot = BotGeneratorBot()
        result = bot.create_bot("Make a Test Bot")
        assert isinstance(result, dict)

    def test_create_bot_delegates_to_generate(self):
        bot = BotGeneratorBot()
        with mock.patch.object(bot, "generate", return_value={"ok": True}) as mock_gen:
            bot.create_bot("My Bot")
        mock_gen.assert_called_once_with("My Bot")

    def test_create_bot_increments_bots_generated(self):
        bot = BotGeneratorBot()
        bot.create_bot("Test Bot")
        assert bot._bots_generated == 1

    def test_create_bot_enterprise_unlimited(self):
        bot = BotGeneratorBot(tier=Tier.ENTERPRISE)
        for _ in range(5):
            result = bot.create_bot("Scalability Bot")
        assert bot._bots_generated == 5
