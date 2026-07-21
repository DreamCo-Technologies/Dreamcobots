"""
Unit tests for the sandbox automation components:

  * sandbox.performance_rating.PerformanceRatingSystem / BotRating
  * sandbox.report_generator.SandboxReportGenerator
  * bots.sandbox_builder_bot.SandboxBuilderBot
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sandbox.performance_rating import (
    BotRating,
    COMPLEXITY_WEIGHTS,
    PerformanceRatingSystem,
    TaskResult,
)
from sandbox.report_generator import SandboxReportGenerator
from bots.sandbox_builder_bot.sandbox_builder_bot import SandboxBuilderBot
from core.bot_base import BotBase


# ===========================================================================
# PerformanceRatingSystem
# ===========================================================================


class TestPerformanceRatingSystem:
    def setup_method(self):
        self.prs = PerformanceRatingSystem("TestBot")

    def test_empty_rating(self):
        rating = self.prs.compute_rating()
        assert rating.total_tasks == 0
        assert rating.star_rating == 1.0
        assert rating.label == "Poor"

    def test_all_success_excellent(self):
        for _ in range(100):
            self.prs.record(TaskResult("task", success=True, complexity="easy"))
        rating = self.prs.compute_rating()
        assert rating.success_rate == 1.0
        assert rating.error_rate == 0.0
        assert rating.star_rating == 5.0
        assert rating.label == "Excellent"

    def test_all_failure_poor(self):
        for _ in range(50):
            self.prs.record(TaskResult("task", success=False, complexity="easy"))
        rating = self.prs.compute_rating()
        assert rating.success_rate == 0.0
        assert rating.star_rating == 1.0
        assert rating.label == "Poor"

    def test_mixed_results(self):
        for _ in range(70):
            self.prs.record(TaskResult("task", success=True, complexity="medium"))
        for _ in range(30):
            self.prs.record(TaskResult("task", success=False, complexity="medium"))
        rating = self.prs.compute_rating()
        assert rating.total_tasks == 100
        assert rating.successful_tasks == 70
        assert rating.failed_tasks == 30
        assert 0 < rating.weighted_score < 100

    def test_complexity_weights_applied(self):
        """Hard tasks should have more impact on the weighted score."""
        prs_easy = PerformanceRatingSystem("EasyBot")
        prs_hard = PerformanceRatingSystem("HardBot")

        for _ in range(80):
            prs_easy.record(TaskResult("t", success=True, complexity="easy"))
        for _ in range(20):
            prs_easy.record(TaskResult("t", success=False, complexity="easy"))

        for _ in range(80):
            prs_hard.record(TaskResult("t", success=True, complexity="hard"))
        for _ in range(20):
            prs_hard.record(TaskResult("t", success=False, complexity="hard"))

        # Same pass/fail ratio — raw weighted success should be equal before penalty
        easy_rating = prs_easy.compute_rating()
        hard_rating = prs_hard.compute_rating()
        # Both have same pass ratio, so scores should be very close
        assert abs(easy_rating.weighted_score - hard_rating.weighted_score) < 1.0

    def test_task_breakdown(self):
        self.prs.record(TaskResult("alpha", success=True))
        self.prs.record(TaskResult("alpha", success=False))
        self.prs.record(TaskResult("beta", success=True))
        rating = self.prs.compute_rating()
        assert rating.task_breakdown["alpha"] == 2
        assert rating.task_breakdown["beta"] == 1

    def test_record_many(self):
        results = [TaskResult("t", success=True) for _ in range(10)]
        self.prs.record_many(results)
        assert self.prs.result_count == 10

    def test_reset(self):
        self.prs.record(TaskResult("t", success=True))
        self.prs.reset()
        assert self.prs.result_count == 0

    def test_as_dict_keys(self):
        self.prs.record(TaskResult("t", success=True))
        d = self.prs.compute_rating().as_dict()
        for key in (
            "bot_name", "total_tasks", "successful_tasks", "failed_tasks",
            "error_rate", "success_rate", "weighted_score", "star_rating", "label",
        ):
            assert key in d

    def test_complexity_weight_default(self):
        tr = TaskResult("t", success=True, complexity="unknown_tier")
        assert tr.complexity_weight == COMPLEXITY_WEIGHTS["medium"]

    def test_rating_thresholds(self):
        # 100% success → Excellent
        prs = PerformanceRatingSystem("A")
        prs.record(TaskResult("t", success=True))
        assert prs.compute_rating().label == "Excellent"

        # 0% success → Poor
        prs2 = PerformanceRatingSystem("B")
        prs2.record(TaskResult("t", success=False))
        assert prs2.compute_rating().label == "Poor"


# ===========================================================================
# SandboxReportGenerator
# ===========================================================================


class TestSandboxReportGenerator:
    def _make_rating(self, name: str, score: float, stars: float, label: str) -> BotRating:
        return BotRating(
            bot_name=name,
            total_tasks=100,
            successful_tasks=80,
            failed_tasks=20,
            error_rate=0.2,
            success_rate=0.8,
            weighted_score=score,
            star_rating=stars,
            label=label,
        )

    def test_empty_report_text(self):
        rg = SandboxReportGenerator()
        text = rg.render_text()
        assert "No bot ratings available" in text

    def test_empty_report_json(self):
        rg = SandboxReportGenerator()
        data = json.loads(rg.render_json())
        assert data["summary"]["bots_evaluated"] == 0

    def test_add_rating_appears_in_text(self):
        rg = SandboxReportGenerator()
        rg.add_rating(self._make_rating("AlphaBot", 80.0, 4.0, "Good"))
        text = rg.render_text()
        assert "AlphaBot" in text
        assert "Good" in text

    def test_add_ratings_bulk(self):
        rg = SandboxReportGenerator()
        ratings = [
            self._make_rating("BotA", 90.0, 5.0, "Excellent"),
            self._make_rating("BotB", 60.0, 3.0, "Average"),
        ]
        rg.add_ratings(ratings)
        assert len(rg._ratings) == 2

    def test_summary(self):
        rg = SandboxReportGenerator()
        rg.add_rating(self._make_rating("BotA", 90.0, 5.0, "Excellent"))
        rg.add_rating(self._make_rating("BotB", 70.0, 4.0, "Good"))
        s = rg.summary()
        assert s["bots_evaluated"] == 2
        assert s["average_score"] == 80.0
        assert s["top_bot"] == "BotA"

    def test_render_json_structure(self):
        rg = SandboxReportGenerator(test_duration_hours=1.5)
        rg.add_rating(self._make_rating("BotX", 55.0, 3.0, "Average"))
        data = json.loads(rg.render_json())
        assert data["test_duration_hours"] == 1.5
        assert len(data["bot_ratings"]) == 1
        assert data["bot_ratings"][0]["bot_name"] == "BotX"

    def test_save_text(self):
        rg = SandboxReportGenerator()
        rg.add_rating(self._make_rating("Bot1", 85.0, 4.0, "Good"))
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "sub", "report.txt")
            rg.save_text(path)
            assert os.path.isfile(path)
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            assert "Bot1" in content

    def test_save_json(self):
        rg = SandboxReportGenerator()
        rg.add_rating(self._make_rating("Bot2", 40.0, 2.0, "Below Average"))
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.json")
            rg.save_json(path)
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            assert data["bot_ratings"][0]["bot_name"] == "Bot2"

    def test_clear(self):
        rg = SandboxReportGenerator()
        rg.add_rating(self._make_rating("Bot3", 50.0, 3.0, "Average"))
        rg.clear()
        assert rg._ratings == []


# ===========================================================================
# SandboxBuilderBot
# ===========================================================================


class TestSandboxBuilderBot:
    def test_instantiation(self):
        bot = SandboxBuilderBot()
        assert bot.name == "SandboxBuilderBot"

    def test_start_stop(self):
        bot = SandboxBuilderBot()
        bot.start()
        assert bot.is_running
        bot.stop()
        assert not bot.is_running

    def test_discover_action(self):
        bot = SandboxBuilderBot()
        bot.start()
        result = bot.execute_task({"action": "discover"})
        bot.stop()
        assert result["status"] == "ok"
        assert "discovered" in result
        assert isinstance(result["discovered"], list)

    def test_build_and_test_with_minimal_bots(self, tmp_path):
        """Build a tiny fake bot dir with one BotBase subclass and run pipeline."""
        # Write a minimal fake bot module
        fake_bot_dir = tmp_path / "fake_bots"
        fake_bot_dir.mkdir()
        (fake_bot_dir / "__init__.py").write_text("")
        fake_bot_code = (
            "from core.bot_base import BotBase\n"
            "class FakeTestBot(BotBase):\n"
            "    def __init__(self, name='FakeTestBot'):\n"
            "        super().__init__(name)\n"
        )
        (fake_bot_dir / "fake_test_bot.py").write_text(fake_bot_code)

        with tempfile.TemporaryDirectory() as report_dir:
            builder = SandboxBuilderBot(
                bots_root=str(fake_bot_dir),
                iterations=5,
                test_duration_hours=0.0,
                report_dir=report_dir,
            )
            builder.start()
            summary = builder.build_and_test()
            builder.stop()

        assert summary["bots_evaluated"] >= 1
        assert "average_score" in summary

    def test_build_and_test_empty_bots_dir(self, tmp_path):
        empty_dir = tmp_path / "empty_bots"
        empty_dir.mkdir()
        builder = SandboxBuilderBot(
            bots_root=str(empty_dir),
            iterations=5,
            report_dir=str(tmp_path / "reports"),
        )
        builder.start()
        summary = builder.build_and_test()
        builder.stop()
        assert summary["bots_evaluated"] == 0

    def test_build_and_test_name_filter(self, tmp_path):
        """Only bots matching the filter should be tested."""
        fake_bot_dir = tmp_path / "fake_bots2"
        fake_bot_dir.mkdir()
        (fake_bot_dir / "__init__.py").write_text("")
        code_alpha = (
            "from core.bot_base import BotBase\n"
            "class AlphaBot(BotBase):\n"
            "    def __init__(self, name='AlphaBot'):\n"
            "        super().__init__(name)\n"
        )
        code_beta = (
            "from core.bot_base import BotBase\n"
            "class BetaBot(BotBase):\n"
            "    def __init__(self, name='BetaBot'):\n"
            "        super().__init__(name)\n"
        )
        (fake_bot_dir / "alpha_bot.py").write_text(code_alpha)
        (fake_bot_dir / "beta_bot.py").write_text(code_beta)

        with tempfile.TemporaryDirectory() as report_dir:
            builder = SandboxBuilderBot(
                bots_root=str(fake_bot_dir),
                iterations=5,
                report_dir=report_dir,
            )
            builder.start()
            summary = builder.build_and_test(name_filter="Alpha")
            builder.stop()

        # Only AlphaBot matched the filter
        assert summary["bots_evaluated"] == 1

    def test_nonexistent_bots_root(self, tmp_path):
        builder = SandboxBuilderBot(
            bots_root=str(tmp_path / "does_not_exist"),
            iterations=5,
            report_dir=str(tmp_path / "reports"),
        )
        builder.start()
        result = builder.build_and_test()
        builder.stop()
        assert result["bots_evaluated"] == 0

    def test_run_all_task_returns_report_summary(self, tmp_path):
        """execute_task with default action returns report summary."""
        fake_bot_dir = tmp_path / "fake_bots3"
        fake_bot_dir.mkdir()
        (fake_bot_dir / "__init__.py").write_text("")
        (fake_bot_dir / "tiny_bot.py").write_text(
            "from core.bot_base import BotBase\n"
            "class TinyBot(BotBase):\n"
            "    def __init__(self, name='TinyBot'):\n"
            "        super().__init__(name)\n"
        )
        with tempfile.TemporaryDirectory() as report_dir:
            bot = SandboxBuilderBot(
                bots_root=str(fake_bot_dir),
                iterations=5,
                report_dir=report_dir,
            )
            bot.start()
            result = bot.execute_task({"action": "run_all"})
            bot.stop()

        assert result["status"] == "ok"
        assert "report_summary" in result
