"""Tests for bots/car_flipping_bot/tiers.py and bots/car_flipping_bot/car_flipping_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.car_flipping_bot.car_flipping_bot import CarFlippingBot, CarFlippingBotTierError


class TestCarFlippingBotInstantiation:
    def test_default_tier_is_free(self):
        bot = CarFlippingBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = CarFlippingBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = CarFlippingBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = CarFlippingBot()
        assert bot.config is not None


class TestSearchCars:
    def test_returns_list(self):
        bot = CarFlippingBot(tier=Tier.PRO)
        result = bot.search_cars("Toyota", 30000)
        assert isinstance(result, list)

    def test_results_under_budget(self):
        bot = CarFlippingBot(tier=Tier.PRO)
        budget = 20000
        results = bot.search_cars("Toyota", budget)
        for car in results:
            assert car["buy_price"] <= budget

    def test_free_limited_to_5_results(self):
        bot = CarFlippingBot(tier=Tier.FREE)
        result = bot.search_cars("Toyota", 50000)
        assert len(result) <= 5

    def test_pro_limited_to_20_results(self):
        bot = CarFlippingBot(tier=Tier.PRO)
        result = bot.search_cars("Toyota", 100000)
        assert len(result) <= 20

    def test_free_one_make_limit(self):
        bot = CarFlippingBot(tier=Tier.FREE)
        bot.search_cars("Toyota", 30000)
        with pytest.raises(CarFlippingBotTierError):
            bot.search_cars("Honda", 20000)

    def test_pro_can_search_multiple_makes(self):
        bot = CarFlippingBot(tier=Tier.PRO)
        bot.search_cars("Toyota", 30000)
        result = bot.search_cars("Honda", 25000)
        assert isinstance(result, list)


class TestEvaluateCar:
    def test_returns_dict(self):
        bot = CarFlippingBot(tier=Tier.FREE)
        car = {"id": "c001", "year": 2018, "make": "Toyota", "model": "Camry",
               "buy_price": 10000, "market_value": 16000, "condition": "Good", "repair_cost": 500}
        result = bot.evaluate_car(car)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = CarFlippingBot(tier=Tier.FREE)
        car = {"id": "c001", "year": 2018, "make": "Toyota", "model": "Camry",
               "buy_price": 10000, "market_value": 16000, "condition": "Good", "repair_cost": 500}
        result = bot.evaluate_car(car)
        for key in ("condition_score", "flip_potential", "estimated_flip_profit"):
            assert key in result

    def test_pro_has_vehicle_history(self):
        bot = CarFlippingBot(tier=Tier.PRO)
        car = {"id": "c001", "year": 2018, "make": "Toyota", "model": "Camry",
               "buy_price": 10000, "market_value": 16000, "condition": "Good", "repair_cost": 500}
        result = bot.evaluate_car(car)
        assert "vehicle_history" in result

    def test_enterprise_has_market_prediction(self):
        bot = CarFlippingBot(tier=Tier.ENTERPRISE)
        car = {"id": "c001", "year": 2018, "make": "Toyota", "model": "Camry",
               "buy_price": 10000, "market_value": 16000, "condition": "Good", "repair_cost": 500}
        result = bot.evaluate_car(car)
        assert "market_prediction_90d" in result


class TestEstimateFlipProfit:
    def test_returns_float(self):
        bot = CarFlippingBot(tier=Tier.FREE)
        car = {"buy_price": 10000, "market_value": 16000, "repair_cost": 500}
        result = bot.estimate_flip_profit(car)
        assert isinstance(result, float)

    def test_correct_formula(self):
        bot = CarFlippingBot(tier=Tier.FREE)
        car = {"buy_price": 10000, "market_value": 16000, "repair_cost": 500}
        expected = (16000 - 10000 - 500) * 0.92
        assert abs(bot.estimate_flip_profit(car) - expected) < 0.01


class TestGetBestOpportunities:
    def test_returns_list(self):
        bot = CarFlippingBot(tier=Tier.PRO)
        result = bot.get_best_opportunities(limit=5)
        assert isinstance(result, list)

    def test_sorted_by_profit_descending(self):
        bot = CarFlippingBot(tier=Tier.PRO)
        result = bot.get_best_opportunities(limit=5)
        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i]["flip_profit_est"] >= result[i + 1]["flip_profit_est"]
