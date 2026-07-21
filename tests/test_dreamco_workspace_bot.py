"""Tests for bots/dreamco_workspace_bot — DreamCo GitHub Codespaces competitor."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.dreamco_workspace_bot.dreamco_workspace_bot import (
    DreamCoWorkspaceBot,
    DreamCoWorkspaceBotTierError,
    DreamCoWorkspaceBotError,
    WorkspaceEnvironment,
)
from bots.dreamco_workspace_bot.tiers import get_bot_tier_info, BOT_FEATURES


# ===========================================================================
# Tier tests
# ===========================================================================

class TestDreamCoWorkspaceBotTiers:
    def test_three_tiers_have_features(self):
        for tier in (Tier.FREE, Tier.PRO, Tier.ENTERPRISE):
            assert len(BOT_FEATURES[tier.value]) > 0

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

class TestDreamCoWorkspaceBotInstantiation:
    def test_default_tier_is_free(self):
        bot = DreamCoWorkspaceBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = DreamCoWorkspaceBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = DreamCoWorkspaceBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = DreamCoWorkspaceBot()
        assert bot.config is not None

    def test_custom_user_id(self):
        bot = DreamCoWorkspaceBot(user_id="bob")
        assert bot.user_id == "bob"


# ===========================================================================
# Workspace creation tests
# ===========================================================================

class TestWorkspaceCreation:
    def test_create_workspace_returns_environment(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("My Workspace")
        assert isinstance(env, WorkspaceEnvironment)

    def test_workspace_has_env_id(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("Test")
        assert len(env.env_id) > 0

    def test_workspace_name_preserved(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("Dev Env")
        assert env.name == "Dev Env"

    def test_workspace_has_access_url(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("Dev")
        d = env.to_dict()
        assert d["access_url"].startswith("https://")

    def test_workspace_default_status_running(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("Dev")
        assert env.status == "running"

    def test_free_limited_to_1_workspace(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        bot.create_workspace("First")
        with pytest.raises(DreamCoWorkspaceBotTierError):
            bot.create_workspace("Second")

    def test_pro_can_create_5_workspaces(self):
        bot = DreamCoWorkspaceBot(tier=Tier.PRO)
        for i in range(5):
            bot.create_workspace(f"Workspace {i}")
        assert len(bot.list_workspaces()) == 5

    def test_pro_limited_to_5_workspaces(self):
        bot = DreamCoWorkspaceBot(tier=Tier.PRO)
        for i in range(5):
            bot.create_workspace(f"Workspace {i}")
        with pytest.raises(DreamCoWorkspaceBotTierError):
            bot.create_workspace("Workspace 6")

    def test_enterprise_has_no_workspace_limit(self):
        assert DreamCoWorkspaceBot.WORKSPACE_LIMITS[Tier.ENTERPRISE] is None

    def test_create_workspace_with_repo(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("Dev", repo_url="https://github.com/user/repo")
        assert env.repo_url == "https://github.com/user/repo"

    def test_create_workspace_custom_image(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("Python Dev", image="dreamco/python-3.11")
        assert env.image == "dreamco/python-3.11"


# ===========================================================================
# Workspace retrieval tests
# ===========================================================================

class TestWorkspaceRetrieval:
    def test_get_workspace_by_id(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("Dev")
        retrieved = bot.get_workspace(env.env_id)
        assert retrieved.env_id == env.env_id

    def test_get_missing_workspace_raises(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        with pytest.raises(DreamCoWorkspaceBotError):
            bot.get_workspace("nonexistent-id")

    def test_list_workspaces_empty_initially(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        assert bot.list_workspaces() == []

    def test_list_workspaces_after_creation(self):
        bot = DreamCoWorkspaceBot(tier=Tier.PRO)
        bot.create_workspace("W1")
        bot.create_workspace("W2")
        assert len(bot.list_workspaces()) == 2

    def test_workspace_to_dict(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("Test")
        d = env.to_dict()
        for key in ("env_id", "name", "image", "status", "access_url"):
            assert key in d


# ===========================================================================
# Workspace lifecycle tests
# ===========================================================================

class TestWorkspaceLifecycle:
    def test_stop_workspace(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("Dev")
        result = bot.stop_workspace(env.env_id)
        assert result["status"] == "stopped"
        assert env.status == "stopped"

    def test_delete_workspace(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("Dev")
        result = bot.delete_workspace(env.env_id)
        assert result["deleted"] is True
        assert len(bot.list_workspaces()) == 0

    def test_delete_missing_workspace_raises(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        with pytest.raises(DreamCoWorkspaceBotError):
            bot.delete_workspace("nonexistent-id")


# ===========================================================================
# Port forwarding tests
# ===========================================================================

class TestPortForwarding:
    def test_free_cannot_forward_ports(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("Dev")
        with pytest.raises(DreamCoWorkspaceBotTierError):
            bot.forward_port(env.env_id, 3000)

    def test_pro_can_forward_port(self):
        bot = DreamCoWorkspaceBot(tier=Tier.PRO)
        env = bot.create_workspace("Dev")
        result = bot.forward_port(env.env_id, 3000)
        assert "public_url" in result
        assert result["port"] == 3000

    def test_port_forwarding_public_url_is_string(self):
        bot = DreamCoWorkspaceBot(tier=Tier.PRO)
        env = bot.create_workspace("Dev")
        result = bot.forward_port(env.env_id, 8080)
        assert result["public_url"].startswith("https://")

    def test_forwarded_port_tracked_on_env(self):
        bot = DreamCoWorkspaceBot(tier=Tier.PRO)
        env = bot.create_workspace("Dev")
        bot.forward_port(env.env_id, 5000)
        assert 5000 in env.ports


# ===========================================================================
# Dotfiles tests
# ===========================================================================

class TestDotfiles:
    def test_free_cannot_set_dotfiles(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        env = bot.create_workspace("Dev")
        with pytest.raises(DreamCoWorkspaceBotTierError):
            bot.set_dotfiles(env.env_id, "https://github.com/user/dotfiles")

    def test_pro_can_set_dotfiles(self):
        bot = DreamCoWorkspaceBot(tier=Tier.PRO)
        env = bot.create_workspace("Dev")
        result = bot.set_dotfiles(env.env_id, "https://github.com/user/dotfiles")
        assert result["status"] == "configured"

    def test_dotfiles_tracked_on_env(self):
        bot = DreamCoWorkspaceBot(tier=Tier.PRO)
        env = bot.create_workspace("Dev")
        bot.set_dotfiles(env.env_id, "https://github.com/user/dotfiles")
        assert env.dotfiles_repo == "https://github.com/user/dotfiles"


# ===========================================================================
# Custom images tests
# ===========================================================================

class TestCustomImages:
    def test_free_cannot_create_custom_image(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        with pytest.raises(DreamCoWorkspaceBotTierError):
            bot.create_custom_image("my-image", "FROM ubuntu:22.04")

    def test_pro_cannot_create_custom_image(self):
        bot = DreamCoWorkspaceBot(tier=Tier.PRO)
        with pytest.raises(DreamCoWorkspaceBotTierError):
            bot.create_custom_image("my-image", "FROM ubuntu:22.04")

    def test_enterprise_can_create_custom_image(self):
        bot = DreamCoWorkspaceBot(tier=Tier.ENTERPRISE)
        result = bot.create_custom_image("my-python", "FROM python:3.11")
        assert "build_id" in result
        assert result["image_name"] == "my-python"

    def test_list_images_enterprise_includes_gpu(self):
        bot = DreamCoWorkspaceBot(tier=Tier.ENTERPRISE)
        images = bot.list_images()
        assert any("gpu" in img.lower() for img in images)

    def test_list_images_free_no_gpu(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        images = bot.list_images()
        assert not any("gpu" in img.lower() for img in images)


# ===========================================================================
# Workspace stats tests
# ===========================================================================

class TestWorkspaceStats:
    def test_initial_stats(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        stats = bot.get_workspace_stats()
        assert stats["workspaces_used"] == 0
        assert stats["workspaces_limit"] == 1

    def test_stats_after_creation(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        bot.create_workspace("Dev")
        stats = bot.get_workspace_stats()
        assert stats["workspaces_used"] == 1

    def test_enterprise_remaining_is_none(self):
        bot = DreamCoWorkspaceBot(tier=Tier.ENTERPRISE)
        stats = bot.get_workspace_stats()
        assert stats["workspaces_remaining"] is None


# ===========================================================================
# Chat interface tests
# ===========================================================================

class TestChatInterface:
    def test_default_chat_response(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        result = bot.chat("hello")
        assert "message" in result
        assert "data" in result

    def test_chat_create_workspace_intent(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        result = bot.chat("create workspace")
        assert "data" in result
        assert "access_url" in result["data"]

    def test_chat_list_workspaces_intent(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        result = bot.chat("list my workspaces")
        assert "data" in result
        assert isinstance(result["data"], list)

    def test_chat_images_query(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        result = bot.chat("what images are available")
        assert "data" in result
        assert isinstance(result["data"], list)

    def test_chat_stats_query(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        result = bot.chat("show stats")
        assert "data" in result

    def test_chat_tier_query(self):
        bot = DreamCoWorkspaceBot(tier=Tier.FREE)
        result = bot.chat("what tier am I on")
        assert "data" in result

    def test_chat_returns_dict(self):
        bot = DreamCoWorkspaceBot(tier=Tier.PRO)
        result = bot.chat("hello")
        assert isinstance(result, dict)
