"""Tests for bots/auto_scaler/auto_scaler_bot.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.auto_scaler.auto_scaler_bot import (
    AutoScalerBot,
    BotMetrics,
    CloneRecord,
    AutoScalerError,
    DEFAULT_REVENUE_THRESHOLD,
)


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------


class TestAutoScalerInstantiation:
    def test_default_threshold(self):
        scaler = AutoScalerBot()
        assert scaler.revenue_threshold == DEFAULT_REVENUE_THRESHOLD

    def test_custom_threshold(self):
        scaler = AutoScalerBot(revenue_threshold=500.0)
        assert scaler.revenue_threshold == 500.0

    def test_dry_run_default_false(self):
        scaler = AutoScalerBot()
        assert scaler.dry_run is False

    def test_dry_run_true(self):
        scaler = AutoScalerBot(dry_run=True)
        assert scaler.dry_run is True


# ---------------------------------------------------------------------------
# Bot registration
# ---------------------------------------------------------------------------


class TestBotRegistration:
    def test_register_returns_metrics(self):
        scaler = AutoScalerBot()
        metrics = scaler.register_bot("bot_a", "BotA")
        assert isinstance(metrics, BotMetrics)

    def test_register_sets_bot_id(self):
        scaler = AutoScalerBot()
        metrics = scaler.register_bot("bot_a", "BotA")
        assert metrics.bot_id == "bot_a"

    def test_register_sets_bot_name(self):
        scaler = AutoScalerBot()
        metrics = scaler.register_bot("bot_a", "BotA")
        assert metrics.bot_name == "BotA"

    def test_register_initial_revenue_zero(self):
        scaler = AutoScalerBot()
        metrics = scaler.register_bot("bot_a", "BotA")
        assert metrics.revenue_usd == 0.0

    def test_register_initial_clone_count_zero(self):
        scaler = AutoScalerBot()
        metrics = scaler.register_bot("bot_a", "BotA")
        assert metrics.clone_count == 0

    def test_list_metrics_empty_initially(self):
        scaler = AutoScalerBot()
        assert scaler.list_metrics() == []

    def test_list_metrics_after_register(self):
        scaler = AutoScalerBot()
        scaler.register_bot("bot_a", "BotA")
        scaler.register_bot("bot_b", "BotB")
        assert len(scaler.list_metrics()) == 2


# ---------------------------------------------------------------------------
# Revenue recording
# ---------------------------------------------------------------------------


class TestRevenueRecording:
    def setup_method(self):
        self.scaler = AutoScalerBot()
        self.scaler.register_bot("rev_bot", "RevBot")

    def test_record_revenue_increases_total(self):
        self.scaler.record_revenue("rev_bot", 50.0)
        metrics = self.scaler.get_metrics("rev_bot")
        assert metrics.revenue_usd == pytest.approx(50.0)

    def test_record_revenue_accumulates(self):
        self.scaler.record_revenue("rev_bot", 60.0)
        self.scaler.record_revenue("rev_bot", 80.0)
        metrics = self.scaler.get_metrics("rev_bot")
        assert metrics.revenue_usd == pytest.approx(140.0)

    def test_record_revenue_unknown_bot_raises(self):
        with pytest.raises(AutoScalerError):
            self.scaler.record_revenue("nonexistent", 100.0)

    def test_get_metrics_unknown_bot_raises(self):
        with pytest.raises(AutoScalerError):
            self.scaler.get_metrics("nonexistent")


# ---------------------------------------------------------------------------
# Auto-scaling (check_and_scale)
# ---------------------------------------------------------------------------


class TestCheckAndScale:
    def test_below_threshold_no_clones(self):
        scaler = AutoScalerBot(revenue_threshold=100.0, dry_run=True)
        scaler.register_bot("low_bot", "LowBot")
        scaler.record_revenue("low_bot", 50.0)
        clones = scaler.check_and_scale()
        assert clones == []

    def test_above_threshold_creates_clone(self):
        scaler = AutoScalerBot(revenue_threshold=100.0, dry_run=True)
        scaler.register_bot("rich_bot", "RichBot")
        scaler.record_revenue("rich_bot", 150.0)
        clones = scaler.check_and_scale()
        assert len(clones) == 1

    def test_clone_has_correct_source(self):
        scaler = AutoScalerBot(revenue_threshold=50.0, dry_run=True)
        scaler.register_bot("src_bot", "SrcBot")
        scaler.record_revenue("src_bot", 100.0)
        clones = scaler.check_and_scale()
        assert clones[0].source_bot == "src_bot"

    def test_clone_increments_clone_count(self):
        scaler = AutoScalerBot(revenue_threshold=50.0, dry_run=True)
        scaler.register_bot("cnt_bot", "CntBot")
        scaler.record_revenue("cnt_bot", 100.0)
        scaler.check_and_scale()
        metrics = scaler.get_metrics("cnt_bot")
        assert metrics.clone_count == 1

    def test_dry_run_clone_status(self):
        scaler = AutoScalerBot(revenue_threshold=50.0, dry_run=True)
        scaler.register_bot("dry_bot", "DryBot")
        scaler.record_revenue("dry_bot", 100.0)
        clones = scaler.check_and_scale()
        assert clones[0].status == "dry_run"

    def test_no_bots_returns_empty(self):
        scaler = AutoScalerBot(dry_run=True)
        clones = scaler.check_and_scale()
        assert clones == []


# ---------------------------------------------------------------------------
# Manual clone
# ---------------------------------------------------------------------------


class TestManualClone:
    def test_clone_bot_returns_record(self):
        scaler = AutoScalerBot(dry_run=True)
        scaler.register_bot("src", "Src")
        record = scaler.clone_bot("src", "new_york")
        assert isinstance(record, CloneRecord)

    def test_clone_bot_target_niche(self):
        scaler = AutoScalerBot(dry_run=True)
        scaler.register_bot("src", "Src")
        record = scaler.clone_bot("src", "new_york")
        assert record.target_niche == "new_york"

    def test_clone_bot_increments_clone_count(self):
        scaler = AutoScalerBot(dry_run=True)
        scaler.register_bot("src", "Src")
        scaler.clone_bot("src", "miami")
        assert scaler.get_metrics("src").clone_count == 1

    def test_clone_unknown_bot_raises(self):
        scaler = AutoScalerBot(dry_run=True)
        with pytest.raises(AutoScalerError):
            scaler.clone_bot("nonexistent", "miami")

    def test_get_clone(self):
        scaler = AutoScalerBot(dry_run=True)
        scaler.register_bot("src", "Src")
        record = scaler.clone_bot("src", "miami")
        fetched = scaler.get_clone(record.clone_id)
        assert fetched.clone_id == record.clone_id

    def test_get_unknown_clone_raises(self):
        scaler = AutoScalerBot(dry_run=True)
        with pytest.raises(AutoScalerError):
            scaler.get_clone("clone-nonexistent")

    def test_list_clones(self):
        scaler = AutoScalerBot(dry_run=True)
        scaler.register_bot("src", "Src")
        scaler.clone_bot("src", "miami")
        scaler.clone_bot("src", "atlanta")
        assert len(scaler.list_clones()) == 2


# ---------------------------------------------------------------------------
# Scale summary
# ---------------------------------------------------------------------------


class TestScaleSummary:
    def test_summary_keys(self):
        scaler = AutoScalerBot()
        summary = scaler.scale_summary()
        assert "registered_bots" in summary
        assert "profitable_bots" in summary
        assert "total_clones" in summary
        assert "total_revenue_usd" in summary
        assert "revenue_threshold_usd" in summary

    def test_summary_counts_profitable_bots(self):
        scaler = AutoScalerBot(revenue_threshold=100.0, dry_run=True)
        scaler.register_bot("rich", "Rich")
        scaler.register_bot("poor", "Poor")
        scaler.record_revenue("rich", 200.0)
        scaler.record_revenue("poor", 10.0)
        summary = scaler.scale_summary()
        assert summary["profitable_bots"] == 1

    def test_summary_total_revenue(self):
        scaler = AutoScalerBot()
        scaler.register_bot("b1", "B1")
        scaler.register_bot("b2", "B2")
        scaler.record_revenue("b1", 75.0)
        scaler.record_revenue("b2", 50.0)
        assert scaler.scale_summary()["total_revenue_usd"] == pytest.approx(125.0)


# ---------------------------------------------------------------------------
# Data model tests
# ---------------------------------------------------------------------------


class TestBotMetrics:
    def test_to_dict_keys(self):
        m = BotMetrics(bot_id="b1", bot_name="B1", revenue_usd=99.9)
        d = m.to_dict()
        assert "bot_id" in d
        assert "bot_name" in d
        assert "revenue_usd" in d
        assert "clone_count" in d

    def test_revenue_rounded_to_two_decimals(self):
        m = BotMetrics(bot_id="b1", bot_name="B1", revenue_usd=99.999)
        d = m.to_dict()
        assert d["revenue_usd"] == round(99.999, 2)


class TestCloneRecord:
    def test_to_dict_keys(self):
        r = CloneRecord(
            clone_id="c1",
            source_bot="src",
            target_niche="miami",
            deployed_path="/bots/miami",
            status="deployed",
        )
        d = r.to_dict()
        assert "clone_id" in d
        assert "source_bot" in d
        assert "target_niche" in d
        assert "deployed_path" in d
        assert "status" in d
        assert "created_at" in d


# ---------------------------------------------------------------------------
# Scale log
# ---------------------------------------------------------------------------


class TestScaleLog:
    def test_scale_log_populated_on_clone(self):
        scaler = AutoScalerBot(dry_run=True)
        scaler.register_bot("b", "B")
        scaler.clone_bot("b", "miami")
        log = scaler.get_scale_log()
        assert len(log) >= 1
        events = [entry["event"] for entry in log]
        assert "bot_cloned" in events
