"""
Tests for the AI Marketplace components:
  - AIMarketplace
  - MonetizationAPI
  - SDKBuilder
"""

import sys
import os
import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

from AIMarketplace.marketplace import AIMarketplace, PricingTier
from AIMarketplace.monetization_api import MonetizationAPI
from AIMarketplace.sdk_builder import SDKBuilder


# ---------------------------------------------------------------------------
# AIMarketplace
# ---------------------------------------------------------------------------

class TestAIMarketplace:
    def test_add_product_returns_dict(self):
        market = AIMarketplace()
        product = market.add_product(
            name="VoiceBot",
            description="TTS bot",
            category="voice",
        )
        assert isinstance(product, dict)
        assert "product_id" in product
        assert product["name"] == "VoiceBot"

    def test_list_products(self):
        market = AIMarketplace()
        market.add_product("A", "desc", "cat1")
        market.add_product("B", "desc", "cat2")
        listings = market.list_products()
        assert len(listings) == 2

    def test_subscribe(self):
        market = AIMarketplace()
        product = market.add_product("P", "d", "c")
        sub = market.subscribe(user_id="u1", product_id=product["product_id"])
        assert sub["user_id"] == "u1"

    def test_subscribe_missing_product_raises(self):
        market = AIMarketplace()
        with pytest.raises(KeyError):
            market.subscribe("u1", "nonexistent")

    def test_search_by_category(self):
        market = AIMarketplace()
        market.add_product("A", "d", "voice")
        market.add_product("B", "d", "image")
        results = market.search(category="voice")
        assert len(results) == 1
        assert results[0]["category"] == "voice"

    def test_search_by_max_price(self):
        market = AIMarketplace()
        market.add_product("Cheap", "d", "c", price_usd=5.0)
        market.add_product("Expensive", "d", "c", price_usd=100.0)
        results = market.search(max_price=10.0)
        assert len(results) == 1
        assert results[0]["name"] == "Cheap"

    def test_search_by_tier(self):
        market = AIMarketplace()
        market.add_product("Free", "d", "c", pricing_tier=PricingTier.FREE)
        market.add_product("Pro", "d", "c", pricing_tier=PricingTier.PRO)
        results = market.search(tier=PricingTier.PRO)
        assert len(results) == 1
        assert results[0]["pricing_tier"] == "pro"

    def test_list_subscriptions_filtered(self):
        market = AIMarketplace()
        product = market.add_product("P", "d", "c")
        market.subscribe("u1", product["product_id"])
        market.subscribe("u2", product["product_id"])
        u1_subs = market.list_subscriptions(user_id="u1")
        assert len(u1_subs) == 1


# ---------------------------------------------------------------------------
# MonetizationAPI
# ---------------------------------------------------------------------------

class TestMonetizationAPI:
    def test_charge_returns_record(self):
        api = MonetizationAPI(provider="stripe")
        charge = api.charge("u1", 29.99, "Pro plan")
        assert charge["status"] == "succeeded"
        assert charge["amount_usd"] == 29.99

    def test_refund(self):
        api = MonetizationAPI()
        charge = api.charge("u1", 10.0)
        refunded = api.refund(charge["charge_id"])
        assert refunded["status"] == "refunded"

    def test_refund_missing_charge_raises(self):
        api = MonetizationAPI()
        with pytest.raises(KeyError):
            api.refund("ch_nonexistent")

    def test_negative_amount_raises(self):
        api = MonetizationAPI()
        with pytest.raises(ValueError):
            api.charge("u1", -5.0)

    def test_unsupported_provider_raises(self):
        with pytest.raises(ValueError):
            MonetizationAPI(provider="bitcoin")

    def test_paypal_provider(self):
        api = MonetizationAPI(provider="paypal")
        charge = api.charge("u1", 15.0)
        assert charge["provider"] == "paypal"

    def test_list_charges_filtered(self):
        api = MonetizationAPI()
        api.charge("u1", 10.0)
        api.charge("u2", 20.0)
        u1_charges = api.list_charges(user_id="u1")
        assert len(u1_charges) == 1


# ---------------------------------------------------------------------------
# SDKBuilder
# ---------------------------------------------------------------------------

class TestSDKBuilder:
    def test_generate_python_stub(self):
        builder = SDKBuilder()
        stub = builder.generate_python("p1", "my_bot")
        assert stub["language"] == "python"
        assert "my_bot" in stub["package_name"]
        assert "pip install" in stub["readme_snippet"]

    def test_generate_nodejs_stub(self):
        builder = SDKBuilder()
        stub = builder.generate_nodejs("p1", "my-bot")
        assert stub["language"] == "nodejs"
        assert "npm install" in stub["readme_snippet"]

    def test_list_stubs(self):
        builder = SDKBuilder()
        builder.generate_python("p1", "bot_a")
        builder.generate_nodejs("p2", "bot-b")
        assert len(builder.list_stubs()) == 2
