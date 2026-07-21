"""Tests for bots/mining_bot/tiers.py and bots/mining_bot/mining_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.mining_bot.mining_bot import MiningBot, MiningBotTierError


class TestMiningBotInstantiation:
    def test_default_tier_is_free(self):
        bot = MiningBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = MiningBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = MiningBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = MiningBot()
        assert bot.config is not None


class TestScanCoins:
    def test_returns_list(self):
        bot = MiningBot(tier=Tier.FREE)
        result = bot.scan_coins()
        assert isinstance(result, list)

    def test_free_returns_only_btc(self):
        bot = MiningBot(tier=Tier.FREE)
        result = bot.scan_coins()
        assert len(result) == 1
        assert result[0]["coin"] == "BTC"

    def test_pro_returns_5_coins(self):
        bot = MiningBot(tier=Tier.PRO)
        result = bot.scan_coins()
        assert len(result) == 5

    def test_enterprise_returns_all_coins(self):
        bot = MiningBot(tier=Tier.ENTERPRISE)
        result = bot.scan_coins()
        assert len(result) == 10


class TestGetCurrentCoin:
    def test_returns_string(self):
        bot = MiningBot(tier=Tier.FREE)
        result = bot.get_current_coin()
        assert isinstance(result, str)

    def test_default_is_btc(self):
        bot = MiningBot(tier=Tier.FREE)
        assert bot.get_current_coin() == "BTC"


class TestSwitchCoin:
    def test_returns_dict(self):
        bot = MiningBot(tier=Tier.PRO)
        result = bot.switch_coin("ETH")
        assert isinstance(result, dict)

    def test_switch_updates_current_coin(self):
        bot = MiningBot(tier=Tier.PRO)
        bot.switch_coin("ETH")
        assert bot.get_current_coin() == "ETH"

    def test_free_cannot_switch_to_eth(self):
        bot = MiningBot(tier=Tier.FREE)
        with pytest.raises(MiningBotTierError):
            bot.switch_coin("ETH")

    def test_pro_can_switch_to_allowed_coin(self):
        bot = MiningBot(tier=Tier.PRO)
        result = bot.switch_coin("LTC")
        assert result["switched_to"] == "LTC"

    def test_enterprise_can_switch_to_xmr(self):
        bot = MiningBot(tier=Tier.ENTERPRISE)
        result = bot.switch_coin("XMR")
        assert result["switched_to"] == "XMR"


class TestAutoWithdraw:
    def test_pro_can_set_auto_withdraw(self):
        bot = MiningBot(tier=Tier.PRO)
        result = bot.auto_withdraw(50.0)
        assert result["auto_withdraw_enabled"] is True
        assert result["threshold_usd"] == 50.0

    def test_free_auto_withdraw_raises(self):
        bot = MiningBot(tier=Tier.FREE)
        with pytest.raises(MiningBotTierError):
            bot.auto_withdraw(50.0)


class TestMultiExchangeRoute:
    def test_enterprise_returns_routing(self):
        bot = MiningBot(tier=Tier.ENTERPRISE)
        result = bot.multi_exchange_route(1000.0)
        assert isinstance(result, dict)
        assert "routing" in result
        assert len(result["routing"]) > 0

    def test_pro_cannot_use_multi_exchange(self):
        bot = MiningBot(tier=Tier.PRO)
        with pytest.raises(MiningBotTierError):
            bot.multi_exchange_route(1000.0)
