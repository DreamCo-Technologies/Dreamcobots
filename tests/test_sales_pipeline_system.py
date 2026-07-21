"""
Tests for the sales pipeline bot system:
  - core.ai_brain          : find_opportunity, decide_bot_type, analyze_market
  - core.system_brain      : load_bots, update_metrics, evaluate_bots
  - core.system_builder    : create_bot, generate_from_gap
  - core.sales_pipeline    : run_pipeline (end-to-end)
  - bots.LeadGenBot        : get_leads
  - bots.EnrichmentBot     : enrich
  - bots.OutreachBot       : outreach, run
  - bots.FollowUpBot       : follow_up
  - bots.CloserBot         : qualify_lead, attempt_close
  - scripts.bot_validator  : scan_repo, _validate, _is_bot_folder
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest


# ===========================================================================
# core/ai_brain
# ===========================================================================


class TestAIBrain:
    def setup_method(self):
        from core.ai_brain import MARKETS, BOT_TYPE_MAP
        self.MARKETS = MARKETS
        self.BOT_TYPE_MAP = BOT_TYPE_MAP

    def test_find_opportunity_returns_known_market(self):
        from core.ai_brain import find_opportunity
        result = find_opportunity()
        assert result in self.MARKETS

    def test_decide_bot_type_known_market(self):
        from core.ai_brain import decide_bot_type
        assert decide_bot_type("real estate") == "LeadGenBot_RealEstate"

    def test_decide_bot_type_auto_repair(self):
        from core.ai_brain import decide_bot_type
        assert decide_bot_type("auto repair") == "LeadGenBot_Auto"

    def test_decide_bot_type_unknown_market(self):
        from core.ai_brain import decide_bot_type
        result = decide_bot_type("unknown market")
        assert "LeadGenBot" in result

    def test_analyze_market_returns_dict(self):
        from core.ai_brain import analyze_market
        result = analyze_market("real estate")
        assert isinstance(result, dict)

    def test_analyze_market_keys(self):
        from core.ai_brain import analyze_market
        result = analyze_market("auto repair")
        assert {"market", "bot_type", "score", "recommendation"} <= result.keys()

    def test_analyze_market_score_in_range(self):
        from core.ai_brain import analyze_market
        result = analyze_market("restaurants")
        assert 0 <= result["score"] <= 100

    def test_analyze_market_recommendation_values(self):
        from core.ai_brain import analyze_market
        result = analyze_market("HVAC")
        assert result["recommendation"] in ("build", "monitor")

    def test_analyze_market_no_args_selects_random(self):
        from core.ai_brain import analyze_market
        result = analyze_market()
        assert result["market"] in self.MARKETS

    def test_framework_marker_present(self):
        path = os.path.join(REPO_ROOT, "core", "ai_brain.py")
        with open(path) as fh:
            text = fh.read()
        assert "GlobalAISourcesFlow" in text or "GLOBAL AI SOURCES FLOW" in text


# ===========================================================================
# core/system_brain
# ===========================================================================


class TestSystemBrain:
    def setup_method(self):
        import importlib
        import core.system_brain as sb
        importlib.reload(sb)
        self.sb = sb

    def test_load_bots_registers_entry(self, tmp_path):
        # Create a fake bot directory with config.json
        bot_dir = tmp_path / "TestBot"
        bot_dir.mkdir()
        (bot_dir / "config.json").write_text(json.dumps({"name": "TestBot"}))

        self.sb.BOT_REGISTRY.clear()
        self.sb.load_bots(root=str(tmp_path))
        assert any("TestBot" in k for k in self.sb.BOT_REGISTRY)

    def test_load_bots_ignores_invalid_json(self, tmp_path):
        bot_dir = tmp_path / "BrokenBot"
        bot_dir.mkdir()
        (bot_dir / "config.json").write_text("not valid json")

        self.sb.BOT_REGISTRY.clear()
        self.sb.load_bots(root=str(tmp_path))
        # Should not raise; broken entry is silently skipped
        assert not any("BrokenBot" in k for k in self.sb.BOT_REGISTRY)

    def test_update_metrics_increases_revenue(self, tmp_path):
        bot_dir = tmp_path / "RevenueBot"
        bot_dir.mkdir()
        (bot_dir / "config.json").write_text(json.dumps({"name": "RevenueBot"}))

        self.sb.BOT_REGISTRY.clear()
        self.sb.load_bots(root=str(tmp_path))

        path = str(bot_dir)
        self.sb.update_metrics(path, 500)
        self.sb.update_metrics(path, 200)
        assert self.sb.BOT_REGISTRY[path]["revenue"] == 700

    def test_evaluate_bots_scale_action(self, tmp_path):
        bot_dir = tmp_path / "ScaleBot"
        bot_dir.mkdir()
        (bot_dir / "config.json").write_text(json.dumps({"name": "ScaleBot"}))

        self.sb.BOT_REGISTRY.clear()
        self.sb.load_bots(root=str(tmp_path))

        path = str(bot_dir)
        self.sb.BOT_REGISTRY[path]["revenue"] = 2000
        actions = self.sb.evaluate_bots()
        assert any("Scaling" in a for a in actions)

    def test_evaluate_bots_kill_action(self, tmp_path):
        bot_dir = tmp_path / "DeadBot"
        bot_dir.mkdir()
        (bot_dir / "config.json").write_text(json.dumps({"name": "DeadBot"}))

        self.sb.BOT_REGISTRY.clear()
        self.sb.load_bots(root=str(tmp_path))

        path = str(bot_dir)
        self.sb.BOT_REGISTRY[path]["revenue"] = -100
        actions = self.sb.evaluate_bots()
        assert any("Killing" in a for a in actions)
        assert self.sb.BOT_REGISTRY[path]["status"] == "disabled"

    def test_get_registry_returns_copy(self):
        self.sb.BOT_REGISTRY.clear()
        registry = self.sb.get_registry()
        registry["fake"] = {}
        assert "fake" not in self.sb.BOT_REGISTRY

    def test_framework_marker_present(self):
        path = os.path.join(REPO_ROOT, "core", "system_brain.py")
        with open(path) as fh:
            text = fh.read()
        assert "GlobalAISourcesFlow" in text or "GLOBAL AI SOURCES FLOW" in text


# ===========================================================================
# core/system_builder
# ===========================================================================


class TestSystemBuilder:
    def test_create_bot_creates_directory(self, tmp_path):
        from core.system_builder import create_bot
        create_bot("TestGenBot", bots_dir=str(tmp_path))
        assert (tmp_path / "TestGenBot").is_dir()

    def test_create_bot_creates_required_files(self, tmp_path):
        from core.system_builder import create_bot
        create_bot("TestGenBot", bots_dir=str(tmp_path))
        bot_path = tmp_path / "TestGenBot"
        for fname in ("config.json", "main.py", "metrics.py", "README.md"):
            assert (bot_path / fname).exists(), f"Missing {fname}"

    def test_create_bot_replaces_name_in_config(self, tmp_path):
        from core.system_builder import create_bot
        create_bot("MyBot", bots_dir=str(tmp_path))
        with open(tmp_path / "MyBot" / "config.json") as fh:
            config = json.load(fh)
        assert config["name"] == "MyBot"

    def test_create_bot_is_idempotent(self, tmp_path):
        from core.system_builder import create_bot
        create_bot("IdempotentBot", bots_dir=str(tmp_path))
        create_bot("IdempotentBot", bots_dir=str(tmp_path))
        assert (tmp_path / "IdempotentBot").is_dir()

    def test_generate_from_gap_returns_string(self, tmp_path):
        from core.system_builder import generate_from_gap
        result = generate_from_gap(bots_dir=str(tmp_path))
        assert isinstance(result, str)
        assert "LeadGenBot" in result

    def test_framework_marker_present(self):
        path = os.path.join(REPO_ROOT, "core", "system_builder.py")
        with open(path) as fh:
            text = fh.read()
        assert "GlobalAISourcesFlow" in text or "GLOBAL AI SOURCES FLOW" in text


# ===========================================================================
# bots/LeadGenBot
# ===========================================================================


class TestLeadGenBot:
    def test_get_leads_returns_list(self):
        from bots.LeadGenBot.main import get_leads
        leads = get_leads()
        assert isinstance(leads, list)

    def test_get_leads_nonempty(self):
        from bots.LeadGenBot.main import get_leads
        assert len(get_leads()) > 0

    def test_lead_has_required_keys(self):
        from bots.LeadGenBot.main import get_leads
        for lead in get_leads():
            assert "name" in lead
            assert "email" in lead

    def test_framework_marker_present(self):
        path = os.path.join(REPO_ROOT, "bots", "LeadGenBot", "main.py")
        with open(path) as fh:
            text = fh.read()
        assert "GlobalAISourcesFlow" in text or "GLOBAL AI SOURCES FLOW" in text


# ===========================================================================
# bots/EnrichmentBot
# ===========================================================================


class TestEnrichmentBot:
    def test_enrich_adds_score(self):
        from bots.EnrichmentBot.main import enrich
        lead = {"name": "Test", "email": "t@t.com", "business": "HVAC"}
        enriched = enrich(lead)
        assert "score" in enriched

    def test_enrich_adds_needs(self):
        from bots.EnrichmentBot.main import enrich
        lead = {"name": "Test", "email": "t@t.com", "business": "HVAC"}
        enriched = enrich(lead)
        assert "needs" in enriched

    def test_enrich_returns_same_object(self):
        from bots.EnrichmentBot.main import enrich
        lead = {"name": "Test", "email": "t@t.com"}
        result = enrich(lead)
        assert result is lead

    def test_framework_marker_present(self):
        path = os.path.join(REPO_ROOT, "bots", "EnrichmentBot", "main.py")
        with open(path) as fh:
            text = fh.read()
        assert "GlobalAISourcesFlow" in text or "GLOBAL AI SOURCES FLOW" in text


# ===========================================================================
# bots/OutreachBot
# ===========================================================================


class TestOutreachBot:
    def test_outreach_returns_true(self, capsys):
        from bots.OutreachBot.main import outreach
        lead = {"name": "John", "email": "john@test.com", "business": "Auto"}
        result = outreach(lead)
        assert result is True

    def test_outreach_prints_email(self, capsys):
        from bots.OutreachBot.main import outreach
        lead = {"name": "John", "email": "john@test.com", "business": "Auto"}
        outreach(lead)
        captured = capsys.readouterr()
        assert "john@test.com" in captured.out

    def test_run_returns_sent_count(self, capsys):
        from bots.OutreachBot.main import run
        from bots.LeadGenBot.main import get_leads
        count = run(get_leads())
        assert count == len(get_leads())

    def test_framework_marker_present(self):
        path = os.path.join(REPO_ROOT, "bots", "OutreachBot", "main.py")
        with open(path) as fh:
            text = fh.read()
        assert "GlobalAISourcesFlow" in text or "GLOBAL AI SOURCES FLOW" in text


# ===========================================================================
# bots/FollowUpBot
# ===========================================================================


class TestFollowUpBot:
    def test_follow_up_returns_list(self):
        from bots.FollowUpBot.main import follow_up
        lead = {"email": "test@test.com"}
        result = follow_up(lead)
        assert isinstance(result, list)

    def test_follow_up_sends_messages(self):
        from bots.FollowUpBot.main import follow_up, _MESSAGES
        lead = {"email": "test@test.com"}
        sent = follow_up(lead)
        assert len(sent) == len(_MESSAGES)

    def test_follow_up_prints_messages(self, capsys):
        from bots.FollowUpBot.main import follow_up
        lead = {"email": "test@test.com"}
        follow_up(lead)
        captured = capsys.readouterr()
        assert "test@test.com" in captured.out

    def test_framework_marker_present(self):
        path = os.path.join(REPO_ROOT, "bots", "FollowUpBot", "main.py")
        with open(path) as fh:
            text = fh.read()
        assert "GlobalAISourcesFlow" in text or "GLOBAL AI SOURCES FLOW" in text


# ===========================================================================
# bots/CloserBot
# ===========================================================================


class TestCloserBot:
    def test_qualify_lead_high_score(self):
        from bots.CloserBot.main import qualify_lead
        lead = {"name": "Test", "score": 90}
        assert qualify_lead(lead) == "high"

    def test_qualify_lead_low_score(self):
        from bots.CloserBot.main import qualify_lead
        lead = {"name": "Test", "score": 30}
        assert qualify_lead(lead) == "medium"

    def test_qualify_lead_auto_heuristic(self):
        from bots.CloserBot.main import qualify_lead
        lead = {"name": "Auto Shop", "score": 0}
        assert qualify_lead(lead) == "high"

    def test_attempt_close_high_returns_true(self, capsys):
        from bots.CloserBot.main import attempt_close
        lead = {"name": "High Value", "score": 95}
        assert attempt_close(lead) is True

    def test_attempt_close_medium_returns_false(self, capsys):
        from bots.CloserBot.main import attempt_close
        lead = {"name": "Low Value", "score": 20}
        assert attempt_close(lead) is False

    def test_framework_marker_present(self):
        path = os.path.join(REPO_ROOT, "bots", "CloserBot", "main.py")
        with open(path) as fh:
            text = fh.read()
        assert "GlobalAISourcesFlow" in text or "GLOBAL AI SOURCES FLOW" in text


# ===========================================================================
# core/sales_pipeline
# ===========================================================================


class TestSalesPipeline:
    def test_run_pipeline_returns_dict(self):
        from core.sales_pipeline import run_pipeline
        result = run_pipeline()
        assert isinstance(result, dict)

    def test_run_pipeline_keys(self):
        from core.sales_pipeline import run_pipeline
        result = run_pipeline()
        assert {"leads_total", "closed", "nurtured"} <= result.keys()

    def test_run_pipeline_totals_match(self):
        from core.sales_pipeline import run_pipeline
        result = run_pipeline()
        assert result["closed"] + result["nurtured"] == result["leads_total"]

    def test_run_pipeline_leads_total_positive(self):
        from core.sales_pipeline import run_pipeline
        result = run_pipeline()
        assert result["leads_total"] > 0

    def test_framework_marker_present(self):
        path = os.path.join(REPO_ROOT, "core", "sales_pipeline.py")
        with open(path) as fh:
            text = fh.read()
        assert "GlobalAISourcesFlow" in text or "GLOBAL AI SOURCES FLOW" in text


# ===========================================================================
# scripts/bot_validator
# ===========================================================================


class TestBotValidator:
    def _make_valid_bot(self, tmp_path, name: str = "TestBot") -> str:
        bot_dir = tmp_path / name
        bot_dir.mkdir()
        (bot_dir / "config.json").write_text('{"name": "TestBot"}')
        (bot_dir / "main.py").write_text("print('running')")
        (bot_dir / "metrics.py").write_text("def track(): pass")
        (bot_dir / "README.md").write_text("# TestBot")
        return str(bot_dir)

    def test_is_bot_folder_true(self):
        from scripts.bot_validator import _is_bot_folder
        assert _is_bot_folder("./bots/MyBot") is True

    def test_is_bot_folder_false(self):
        from scripts.bot_validator import _is_bot_folder
        assert _is_bot_folder("./core/engine") is False

    def test_validate_passes_complete_bot(self, tmp_path):
        from scripts.bot_validator import _validate
        self._make_valid_bot(tmp_path)
        errors = _validate(str(tmp_path / "TestBot"))
        assert errors == []

    def test_validate_fails_missing_config(self, tmp_path):
        from scripts.bot_validator import _validate
        bot_dir = tmp_path / "IncompleteBot"
        bot_dir.mkdir()
        (bot_dir / "main.py").write_text("print('hi')")
        (bot_dir / "metrics.py").write_text("def track(): pass")
        (bot_dir / "README.md").write_text("# IncompleteBot")
        errors = _validate(str(bot_dir))
        assert any("config.json" in str(e) for e in errors)

    def test_scan_repo_returns_false_for_valid_tree(self, tmp_path):
        from scripts.bot_validator import scan_repo
        self._make_valid_bot(tmp_path)
        failed = scan_repo(root=str(tmp_path), auto_fix=False)
        assert failed is False

    def test_scan_repo_returns_true_for_invalid_tree(self, tmp_path):
        from scripts.bot_validator import scan_repo
        bot_dir = tmp_path / "BrokenBot"
        bot_dir.mkdir()
        # Only main.py — missing config, metrics, README
        (bot_dir / "main.py").write_text("print('hi')")
        failed = scan_repo(root=str(tmp_path), auto_fix=False)
        assert failed is True

    def test_auto_fix_creates_missing_files(self, tmp_path):
        from scripts.bot_validator import scan_repo
        bot_dir = tmp_path / "FixedBot"
        bot_dir.mkdir()
        failed = scan_repo(root=str(tmp_path), auto_fix=True)
        assert (bot_dir / "config.json").exists()
        assert (bot_dir / "main.py").exists()
        assert (bot_dir / "metrics.py").exists()
        assert (bot_dir / "README.md").exists()
        assert failed is False
