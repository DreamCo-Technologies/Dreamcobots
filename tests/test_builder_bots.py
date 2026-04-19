"""
Tests for the builder bots fleet:
  - OrchestrationBuilderBot
  - VoiceEngineBuilderBot
  - ImageVideoBuilderBot
  - MarketplaceBuilderBot
  - CreativeStudioBuilderBot
  - BotTesterIntegrator
"""

import os
import sys
import tempfile
import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)


# ---------------------------------------------------------------------------
# TimestampButton
# ---------------------------------------------------------------------------

from core.timestamp_button import TimestampButton, Milestone


class TestTimestampButton:
    def test_stamp_returns_milestone(self, tmp_path):
        ts = TimestampButton(log_path=tmp_path / "test.log")
        ms = ts.stamp(event="test_event", detail="hello")
        assert isinstance(ms, Milestone)
        assert ms.event == "test_event"
        assert ms.detail == "hello"

    def test_stamp_increments_count(self, tmp_path):
        ts = TimestampButton(log_path=tmp_path / "test.log")
        ts.stamp("e1")
        ts.stamp("e2")
        assert len(ts.get_milestones()) == 2

    def test_stamp_writes_to_log(self, tmp_path):
        log = tmp_path / "ms.log"
        ts = TimestampButton(log_path=log)
        ts.stamp("event_x", "details here")
        content = log.read_text(encoding="utf-8")
        assert "event_x" in content
        assert "details here" in content

    def test_dashboard_returns_string(self, tmp_path):
        ts = TimestampButton(log_path=tmp_path / "test.log")
        ts.stamp("ev1")
        dashboard = ts.dashboard()
        assert isinstance(dashboard, str)
        assert "DreamCobots" in dashboard

    def test_dashboard_dict(self, tmp_path):
        ts = TimestampButton(log_path=tmp_path / "test.log")
        ts.stamp("ev1")
        d = ts.dashboard_dict()
        assert d["total"] == 1
        assert len(d["milestones"]) == 1

    def test_clear_resets(self, tmp_path):
        ts = TimestampButton(log_path=tmp_path / "test.log")
        ts.stamp("ev")
        ts.clear()
        assert len(ts.get_milestones()) == 0

    def test_milestone_to_dict(self, tmp_path):
        ts = TimestampButton(log_path=tmp_path / "test.log")
        ms = ts.stamp("ev", "detail")
        d = ms.to_dict()
        assert "milestone_id" in d
        assert d["event"] == "ev"


# ---------------------------------------------------------------------------
# OrchestrationBuilderBot
# ---------------------------------------------------------------------------

from bots.builder_bots.orchestration_builder_bot import OrchestrationBuilderBot


class TestOrchestrationBuilderBot:
    def test_run_returns_success(self, tmp_path):
        bot = OrchestrationBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        result = bot.run({"num_tasks": 2, "ideas_log": str(tmp_path / "ideas.txt")})
        assert result["status"] == "success"
        assert result["bot"] == bot.name

    def test_build_async_pipeline(self, tmp_path):
        bot = OrchestrationBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        result = bot.build_async_pipeline([lambda: "ok", lambda: "ok2"])
        assert result["status"] == "completed"
        assert result["total"] == 2

    def test_celery_scaffold_queue(self, tmp_path):
        bot = OrchestrationBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        task_id = bot.queue_celery_task("test.task", args=[1, 2])
        assert isinstance(task_id, str)
        status = bot.get_queue_status()
        assert status["pending"] >= 1

    def test_generate_placeholders(self, tmp_path):
        bot = OrchestrationBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        placeholders = bot.generate_placeholders()
        assert isinstance(placeholders, list)
        assert len(placeholders) > 0

    def test_log_bot_ideas(self, tmp_path):
        bot = OrchestrationBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        ideas_path = str(tmp_path / "ideas.txt")
        bot.log_bot_ideas(ideas_path)
        with open(ideas_path, encoding="utf-8") as fh:
            content = fh.read()
        assert bot.name in content


# ---------------------------------------------------------------------------
# VoiceEngineBuilderBot
# ---------------------------------------------------------------------------

from bots.builder_bots.voice_engine_builder_bot import VoiceEngineBuilderBot


class TestVoiceEngineBuilderBot:
    def test_run_returns_success(self, tmp_path):
        bot = VoiceEngineBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        result = bot.run({"ideas_log": str(tmp_path / "ideas.txt")})
        assert result["status"] == "success"

    def test_create_pipeline(self, tmp_path):
        bot = VoiceEngineBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        pipeline = bot.create_pipeline("Test Pipeline", language="en-US", tone="warm")
        assert pipeline.language == "en-US"
        assert pipeline.tone == "warm"

    def test_invalid_language_raises(self, tmp_path):
        bot = VoiceEngineBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        with pytest.raises(ValueError):
            bot.create_pipeline("Bad", language="klingon")

    def test_invalid_tone_raises(self, tmp_path):
        bot = VoiceEngineBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        with pytest.raises(ValueError):
            bot.create_pipeline("Bad", tone="robotic")

    def test_synthesize(self, tmp_path):
        bot = VoiceEngineBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        pipeline = bot.create_pipeline("P1")
        job = bot.synthesize(pipeline.pipeline_id, "Hello world")
        assert job.status == "completed"
        assert job.duration_seconds > 0

    def test_list_pipelines(self, tmp_path):
        bot = VoiceEngineBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        bot.create_pipeline("P1")
        bot.create_pipeline("P2", language="fr-FR")
        listings = bot.list_pipelines()
        assert len(listings) == 2

    def test_placeholders(self, tmp_path):
        bot = VoiceEngineBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        placeholders = bot.generate_placeholders()
        assert len(placeholders) > 0


# ---------------------------------------------------------------------------
# ImageVideoBuilderBot
# ---------------------------------------------------------------------------

from bots.builder_bots.image_video_builder_bot import ImageVideoBuilderBot, AvatarType


class TestImageVideoBuilderBot:
    def test_run_returns_success(self, tmp_path):
        bot = ImageVideoBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        result = bot.run({"ideas_log": str(tmp_path / "ideas.txt")})
        assert result["status"] == "success"

    def test_create_pipeline(self, tmp_path):
        bot = ImageVideoBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        pipeline = bot.create_pipeline("Avatar Pipeline", avatar_type=AvatarType.VIDEO_AVATAR)
        assert pipeline.avatar_type == AvatarType.VIDEO_AVATAR

    def test_generate_job(self, tmp_path):
        bot = ImageVideoBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        pipeline = bot.create_pipeline("P1")
        job = bot.generate(pipeline.pipeline_id, "Professional headshot")
        assert job.status == "completed"
        assert job.image_ref.startswith("asset:")

    def test_missing_pipeline_raises(self, tmp_path):
        bot = ImageVideoBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        with pytest.raises(KeyError):
            bot.generate("nonexistent", "prompt")

    def test_placeholders(self, tmp_path):
        bot = ImageVideoBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        placeholders = bot.generate_placeholders()
        assert len(placeholders) > 0


# ---------------------------------------------------------------------------
# MarketplaceBuilderBot
# ---------------------------------------------------------------------------

from bots.builder_bots.marketplace_builder_bot import MarketplaceBuilderBot, PricingTier


class TestMarketplaceBuilderBot:
    def test_run_returns_success(self, tmp_path):
        bot = MarketplaceBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        result = bot.run({"ideas_log": str(tmp_path / "ideas.txt")})
        assert result["status"] == "success"

    def test_add_product(self, tmp_path):
        bot = MarketplaceBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        product = bot.add_product(
            name="TestBot",
            description="desc",
            category="voice",
            pricing_tier=PricingTier.PRO,
            price_usd=9.99,
        )
        assert product.name == "TestBot"
        assert product.pricing_tier == PricingTier.PRO

    def test_create_subscription(self, tmp_path):
        bot = MarketplaceBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        product = bot.add_product("P", "d", "cat")
        sub = bot.create_subscription("user_1", product.product_id)
        assert sub.user_id == "user_1"
        assert sub.product_id == product.product_id

    def test_generate_python_sdk(self, tmp_path):
        bot = MarketplaceBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        product = bot.add_product("MyBot", "desc", "tools")
        stub = bot.generate_sdk_stub(product.product_id, language="python")
        assert stub.language == "python"

    def test_generate_nodejs_sdk(self, tmp_path):
        bot = MarketplaceBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        product = bot.add_product("MyBot", "desc", "tools")
        stub = bot.generate_sdk_stub(product.product_id, language="nodejs")
        assert stub.language == "nodejs"

    def test_unsupported_sdk_language_raises(self, tmp_path):
        bot = MarketplaceBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        product = bot.add_product("B", "d", "c")
        with pytest.raises(ValueError):
            bot.generate_sdk_stub(product.product_id, language="ruby")

    def test_list_products(self, tmp_path):
        bot = MarketplaceBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        bot.add_product("A", "d", "cat")
        bot.add_product("B", "d", "cat")
        listings = bot.list_products()
        assert len(listings) == 2


# ---------------------------------------------------------------------------
# CreativeStudioBuilderBot
# ---------------------------------------------------------------------------

from bots.builder_bots.creative_studio_builder_bot import CreativeStudioBuilderBot


class TestCreativeStudioBuilderBot:
    def test_run_returns_success(self, tmp_path):
        bot = CreativeStudioBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        result = bot.run({"ideas_log": str(tmp_path / "ideas.txt")})
        assert result["status"] == "success"

    def test_create_ad(self, tmp_path):
        bot = CreativeStudioBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        job = bot.create_ad("ACME Corp", "Widgets", platform="youtube")
        assert job.status == "completed"
        assert job.platform == "youtube"

    def test_ad_invalid_platform_raises(self, tmp_path):
        bot = CreativeStudioBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        with pytest.raises(ValueError):
            bot.create_ad("Co", "P", platform="myspace")

    def test_create_cinematic_project(self, tmp_path):
        bot = CreativeStudioBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        project = bot.create_cinematic_project("Epic", "thriller", "A spy thriller.")
        assert project.status == "in_production"
        assert project.genre == "thriller"

    def test_invalid_genre_raises(self, tmp_path):
        bot = CreativeStudioBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        with pytest.raises(ValueError):
            bot.create_cinematic_project("F", "mumblecore", "Synopsis")

    def test_ad_includes_music(self, tmp_path):
        bot = CreativeStudioBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        job = bot.create_ad("Co", "P", include_music=True)
        assert job.music_ref.startswith("music:")

    def test_placeholders(self, tmp_path):
        bot = CreativeStudioBuilderBot(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        placeholders = bot.generate_placeholders()
        assert len(placeholders) > 0


# ---------------------------------------------------------------------------
# BotTesterIntegrator
# ---------------------------------------------------------------------------

from bots.builder_bots.bot_tester_integrator import BotTesterIntegrator


class _FakeBot:
    name = "FakeBot"

    def run(self, task=None):
        return {"status": "success", "msg": "ok"}


class _BrokenBot:
    name = "BrokenBot"

    def run(self, task=None):
        raise RuntimeError("simulated failure")


class TestBotTesterIntegrator:
    def test_probe_passing_bot(self, tmp_path):
        integrator = BotTesterIntegrator(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        result = integrator.probe_bot(_FakeBot())
        assert result.passed is True

    def test_probe_failing_bot(self, tmp_path):
        integrator = BotTesterIntegrator(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        result = integrator.probe_bot(_BrokenBot())
        assert result.passed is False
        assert "simulated failure" in result.error

    def test_probe_all(self, tmp_path):
        integrator = BotTesterIntegrator(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        results = integrator.probe_all([_FakeBot(), _BrokenBot()])
        assert len(results) == 2

    def test_summary(self, tmp_path):
        integrator = BotTesterIntegrator(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        integrator.probe_all([_FakeBot(), _FakeBot(), _BrokenBot()])
        summary = integrator.summary()
        assert summary["total"] == 3
        assert summary["passed"] == 2
        assert summary["failed"] == 1

    def test_run_returns_success(self, tmp_path):
        integrator = BotTesterIntegrator(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        result = integrator.run({"ideas_log": str(tmp_path / "ideas.txt")})
        assert result["status"] == "success"

    def test_placeholders(self, tmp_path):
        integrator = BotTesterIntegrator(
            timestamp_button=TimestampButton(log_path=tmp_path / "log.txt")
        )
        placeholders = integrator.generate_placeholders()
        assert len(placeholders) > 0
