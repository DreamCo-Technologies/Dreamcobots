"""Tests for bots/dreamco_cloud_bot — DreamCo AWS competitor."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.dreamco_cloud_bot.dreamco_cloud_bot import (
    DreamCoCloudBot,
    DreamCoCloudBotTierError,
    DreamCoCloudBotError,
    ServerInstance,
    DatabaseInstance,
)
from bots.dreamco_cloud_bot.tiers import get_bot_tier_info, BOT_FEATURES


# ===========================================================================
# Tier tests
# ===========================================================================

class TestDreamCoCloudBotTiers:
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

class TestDreamCoCloudBotInstantiation:
    def test_default_tier_is_free(self):
        bot = DreamCoCloudBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = DreamCoCloudBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = DreamCoCloudBot()
        assert bot.config is not None

    def test_custom_user_id(self):
        bot = DreamCoCloudBot(user_id="carol")
        assert bot.user_id == "carol"


# ===========================================================================
# Server instance tests
# ===========================================================================

class TestServerInstances:
    def test_launch_instance_returns_server(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        inst = bot.launch_instance("My Server")
        assert isinstance(inst, ServerInstance)

    def test_instance_has_id(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        inst = bot.launch_instance("Server1")
        assert len(inst.instance_id) > 0

    def test_instance_name_preserved(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        inst = bot.launch_instance("Test Server")
        assert inst.name == "Test Server"

    def test_instance_default_region(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        inst = bot.launch_instance("Server")
        assert inst.region == "us-east-1"

    def test_instance_status_running(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        inst = bot.launch_instance("Server")
        assert inst.status == "running"

    def test_instance_has_ip_address(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        inst = bot.launch_instance("Server")
        assert len(inst.ip_address) > 0

    def test_free_limited_to_1_instance(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        bot.launch_instance("Server1")
        with pytest.raises(DreamCoCloudBotTierError):
            bot.launch_instance("Server2")

    def test_pro_can_launch_10_instances(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        for i in range(10):
            bot.launch_instance(f"Server{i}")
        assert len(bot.list_instances()) == 10

    def test_pro_limited_to_10_instances(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        for i in range(10):
            bot.launch_instance(f"Server{i}")
        with pytest.raises(DreamCoCloudBotTierError):
            bot.launch_instance("Server11")

    def test_enterprise_has_no_instance_limit(self):
        assert DreamCoCloudBot.INSTANCE_LIMITS[Tier.ENTERPRISE] is None

    def test_free_limited_to_us_east_1_region(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCloudBotTierError):
            bot.launch_instance("Server", region="eu-west-1")

    def test_pro_can_use_multiple_regions(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        inst = bot.launch_instance("EU Server", region="eu-west-1")
        assert inst.region == "eu-west-1"

    def test_free_cannot_use_large_instance_type(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCloudBotTierError):
            bot.launch_instance("Server", instance_type="dc2.xlarge")

    def test_instance_to_dict(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        inst = bot.launch_instance("Server")
        d = inst.to_dict()
        for key in ("instance_id", "name", "region", "instance_type", "status", "ip_address"):
            assert key in d


# ===========================================================================
# Instance retrieval / lifecycle tests
# ===========================================================================

class TestInstanceLifecycle:
    def test_get_instance_by_id(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        inst = bot.launch_instance("Server")
        retrieved = bot.get_instance(inst.instance_id)
        assert retrieved.instance_id == inst.instance_id

    def test_get_missing_instance_raises(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCloudBotError):
            bot.get_instance("nonexistent-id")

    def test_list_instances_empty_initially(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        assert bot.list_instances() == []

    def test_stop_instance(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        inst = bot.launch_instance("Server")
        result = bot.stop_instance(inst.instance_id)
        assert result["status"] == "stopped"
        assert inst.status == "stopped"

    def test_terminate_instance(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        inst = bot.launch_instance("Server")
        result = bot.terminate_instance(inst.instance_id)
        assert result["terminated"] is True
        assert len(bot.list_instances()) == 0

    def test_terminate_missing_instance_raises(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCloudBotError):
            bot.terminate_instance("nonexistent-id")


# ===========================================================================
# Region and instance type tests
# ===========================================================================

class TestRegionsAndInstanceTypes:
    def test_free_has_1_region(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        assert len(bot.list_regions()) == 1

    def test_pro_has_multiple_regions(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        assert len(bot.list_regions()) > 1

    def test_enterprise_has_many_regions(self):
        bot = DreamCoCloudBot(tier=Tier.ENTERPRISE)
        assert len(bot.list_regions()) >= 8

    def test_free_has_1_instance_type(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        assert len(bot.list_instance_types()) == 1

    def test_pro_has_multiple_instance_types(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        assert len(bot.list_instance_types()) > 1


# ===========================================================================
# Static site hosting tests
# ===========================================================================

class TestStaticSiteHosting:
    def test_deploy_static_site(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        result = bot.deploy_static_site("My Site")
        assert "url" in result
        assert result["ssl"] is True
        assert result["status"] == "deployed"

    def test_deploy_site_with_custom_domain(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        result = bot.deploy_static_site("My Site", domain="example.com")
        assert result["custom_domain"] == "example.com"

    def test_deploy_site_url_is_https(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        result = bot.deploy_static_site("Test Site")
        assert result["url"].startswith("https://")


# ===========================================================================
# Managed database tests
# ===========================================================================

class TestManagedDatabases:
    def test_free_cannot_create_database(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCloudBotTierError):
            bot.create_database("MyDB")

    def test_pro_can_create_database(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        db = bot.create_database("MyDB")
        assert isinstance(db, DatabaseInstance)

    def test_database_has_endpoint(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        db = bot.create_database("MyDB")
        assert len(db.endpoint) > 0

    def test_database_engine_preserved(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        db = bot.create_database("MyDB", engine="mysql")
        assert db.engine == "mysql"

    def test_database_invalid_engine_raises(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        with pytest.raises(DreamCoCloudBotError):
            bot.create_database("MyDB", engine="oracle")

    def test_database_to_dict(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        db = bot.create_database("TestDB")
        d = db.to_dict()
        for key in ("db_id", "name", "engine", "status", "endpoint"):
            assert key in d

    def test_pro_limited_to_3_databases(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        for i in range(3):
            bot.create_database(f"DB{i}")
        with pytest.raises(DreamCoCloudBotTierError):
            bot.create_database("DB4")

    def test_enterprise_has_no_db_limit(self):
        assert DreamCoCloudBot.DB_LIMITS[Tier.ENTERPRISE] is None

    def test_list_databases(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        bot.create_database("DB1")
        bot.create_database("DB2")
        dbs = bot.list_databases()
        assert len(dbs) == 2

    def test_get_database_by_id(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        db = bot.create_database("TestDB")
        retrieved = bot.get_database(db.db_id)
        assert retrieved.db_id == db.db_id

    def test_get_missing_database_raises(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        with pytest.raises(DreamCoCloudBotError):
            bot.get_database("nonexistent-id")


# ===========================================================================
# Load balancer tests
# ===========================================================================

class TestLoadBalancer:
    def test_free_cannot_create_load_balancer(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCloudBotTierError):
            bot.create_load_balancer("LB", ["inst-1", "inst-2"])

    def test_pro_can_create_load_balancer(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        lb = bot.create_load_balancer("My LB", ["inst-1", "inst-2"])
        assert "lb_id" in lb
        assert "dns" in lb
        assert lb["status"] == "active"

    def test_load_balancer_instance_ids_preserved(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        ids = ["inst-1", "inst-2", "inst-3"]
        lb = bot.create_load_balancer("LB", ids)
        assert lb["instance_ids"] == ids


# ===========================================================================
# Serverless functions tests
# ===========================================================================

class TestServerlessFunctions:
    def test_free_cannot_deploy_function(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        with pytest.raises(DreamCoCloudBotTierError):
            bot.deploy_function("handler", "python3.11", "def handler(): pass")

    def test_pro_cannot_deploy_function(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        with pytest.raises(DreamCoCloudBotTierError):
            bot.deploy_function("handler", "python3.11", "def handler(): pass")

    def test_enterprise_can_deploy_function(self):
        bot = DreamCoCloudBot(tier=Tier.ENTERPRISE)
        fn = bot.deploy_function("my_handler", "python3.11", "def my_handler(): return 'ok'")
        assert "function_id" in fn
        assert fn["status"] == "deployed"
        assert "invoke_url" in fn

    def test_function_invoke_url_is_https(self):
        bot = DreamCoCloudBot(tier=Tier.ENTERPRISE)
        fn = bot.deploy_function("handler", "node18", "exports.handler = () => 'ok'")
        assert fn["invoke_url"].startswith("https://")


# ===========================================================================
# Cloud stats tests
# ===========================================================================

class TestCloudStats:
    def test_initial_stats(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        stats = bot.get_cloud_stats()
        assert stats["instances_used"] == 0
        assert stats["databases_used"] == 0

    def test_stats_after_launch(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        bot.launch_instance("Server")
        stats = bot.get_cloud_stats()
        assert stats["instances_used"] == 1

    def test_enterprise_remaining_instances_none(self):
        bot = DreamCoCloudBot(tier=Tier.ENTERPRISE)
        stats = bot.get_cloud_stats()
        assert stats["instances_remaining"] is None

    def test_regions_available_count(self):
        bot_free = DreamCoCloudBot(tier=Tier.FREE)
        bot_ent = DreamCoCloudBot(tier=Tier.ENTERPRISE)
        assert bot_ent.get_cloud_stats()["regions_available"] > bot_free.get_cloud_stats()["regions_available"]


# ===========================================================================
# Chat interface tests
# ===========================================================================

class TestChatInterface:
    def test_default_chat_response(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        result = bot.chat("hello")
        assert "message" in result
        assert "data" in result

    def test_chat_launch_server_intent(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        result = bot.chat("launch a new server")
        assert "data" in result
        assert "ip_address" in result["data"]

    def test_chat_list_servers_intent(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        result = bot.chat("list my servers")
        assert "data" in result
        assert isinstance(result["data"], list)

    def test_chat_regions_query(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        result = bot.chat("available regions")
        assert "data" in result
        assert isinstance(result["data"], list)

    def test_chat_database_intent_free(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        result = bot.chat("create a database")
        assert "upgrade_required" in result["data"]

    def test_chat_database_intent_pro(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        result = bot.chat("create a new database")
        assert "data" in result
        assert "endpoint" in result["data"]

    def test_chat_stats_query(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        result = bot.chat("show resource stats")
        assert "data" in result

    def test_chat_tier_query(self):
        bot = DreamCoCloudBot(tier=Tier.FREE)
        result = bot.chat("what tier am I on")
        assert "data" in result

    def test_chat_returns_dict(self):
        bot = DreamCoCloudBot(tier=Tier.PRO)
        result = bot.chat("hello")
        assert isinstance(result, dict)
