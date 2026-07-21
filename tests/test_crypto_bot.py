"""Tests for bots/crypto_bot/ — cryptocurrency management system."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, "models"))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.crypto_bot.crypto_bot import CryptoBot, CryptoBotError
from bots.crypto_bot.crypto_database import (
    CRYPTO_DATABASE,
    get_coin,
    list_coins,
    list_mineable_coins,
    search_coins,
    list_categories,
)
from bots.crypto_bot.price_feed import (
    get_price,
    get_prices,
    get_price_change_24h,
    get_market_summary,
)
from bots.crypto_bot.portfolio import Portfolio, PortfolioError, TransactionType
from bots.crypto_bot.trading import TradingEngine, TradingError
from bots.crypto_bot.mining import (
    simulate_mining,
    mining_leaderboard,
    calculate_break_even,
    get_mining_profile,
)
from bots.crypto_bot.prospectus import (
    get_coin_prospectus,
    list_all_prospectuses,
    prospectus_text,
)
from bots.crypto_bot.dashboard import (
    render_portfolio,
    render_market_overview,
    render_transactions,
    render_full_dashboard,
)


# ===========================================================================
# crypto_database
# ===========================================================================

class TestCryptoDatabase:
    def test_database_has_entries(self):
        assert len(CRYPTO_DATABASE) >= 50

    def test_btc_present(self):
        assert "BTC" in CRYPTO_DATABASE

    def test_eth_present(self):
        assert "ETH" in CRYPTO_DATABASE

    def test_get_coin_returns_dict(self):
        coin = get_coin("BTC")
        assert isinstance(coin, dict)

    def test_get_coin_case_insensitive(self):
        assert get_coin("btc") == get_coin("BTC")

    def test_get_coin_unknown_returns_none(self):
        assert get_coin("NOTACOIN") is None

    def test_coin_has_required_fields(self):
        coin = get_coin("ETH")
        for field in ("symbol", "name", "category", "price_usd", "mineable"):
            assert field in coin, f"Missing field: {field}"

    def test_list_coins_returns_list(self):
        assert isinstance(list_coins(), list)

    def test_list_coins_category_filter(self):
        defi = list_coins(category="DeFi")
        assert all(c["category"] == "DeFi" for c in defi)

    def test_list_mineable_coins(self):
        mineable = list_mineable_coins()
        assert len(mineable) > 0
        assert all(c["mineable"] for c in mineable)

    def test_btc_is_mineable(self):
        assert get_coin("BTC")["mineable"] is True

    def test_eth_is_not_mineable(self):
        assert get_coin("ETH")["mineable"] is False

    def test_search_returns_btc(self):
        results = search_coins("bitcoin")
        assert any(c["symbol"] == "BTC" for c in results)

    def test_search_by_symbol(self):
        results = search_coins("ETH")
        assert any(c["symbol"] == "ETH" for c in results)

    def test_list_categories_returns_list(self):
        cats = list_categories()
        assert isinstance(cats, list)
        assert len(cats) > 0

    def test_list_categories_includes_layer1(self):
        assert "Layer 1" in list_categories()


# ===========================================================================
# price_feed
# ===========================================================================

class TestPriceFeed:
    def test_get_price_btc_returns_float(self):
        price = get_price("BTC")
        assert isinstance(price, float)
        assert price > 0

    def test_get_price_case_insensitive(self):
        assert get_price("btc") == get_price("BTC")

    def test_get_price_unknown_returns_none(self):
        assert get_price("NOTACOIN") is None

    def test_get_prices_returns_dict(self):
        prices = get_prices(["BTC", "ETH"])
        assert isinstance(prices, dict)
        assert "BTC" in prices
        assert "ETH" in prices

    def test_get_prices_all_positive(self):
        prices = get_prices(["BTC", "ETH", "SOL", "LTC"])
        for sym, price in prices.items():
            assert price > 0, f"{sym} price should be positive"

    def test_get_price_change_24h_returns_float(self):
        change = get_price_change_24h("BTC")
        assert isinstance(change, float)

    def test_get_price_change_in_range(self):
        change = get_price_change_24h("ETH")
        assert -100.0 <= change <= 100.0

    def test_get_market_summary_returns_list(self):
        summary = get_market_summary(["BTC", "ETH"])
        assert isinstance(summary, list)
        assert len(summary) == 2

    def test_market_summary_has_required_keys(self):
        summary = get_market_summary(["BTC"])
        item = summary[0]
        for key in ("symbol", "name", "price_usd", "change_24h_pct", "market_cap_usd"):
            assert key in item


# ===========================================================================
# portfolio
# ===========================================================================

class TestPortfolio:
    def test_default_balance(self):
        p = Portfolio()
        assert p.usd_balance == 10_000.0

    def test_custom_initial_balance(self):
        p = Portfolio(initial_usd_balance=5_000.0)
        assert p.usd_balance == 5_000.0

    def test_deposit_increases_balance(self):
        p = Portfolio(initial_usd_balance=1_000.0)
        p.deposit_usd(500.0)
        assert p.usd_balance == 1_500.0

    def test_deposit_negative_raises(self):
        p = Portfolio()
        with pytest.raises(PortfolioError):
            p.deposit_usd(-100.0)

    def test_withdraw_decreases_balance(self):
        p = Portfolio(initial_usd_balance=1_000.0)
        p.withdraw_usd(300.0)
        assert p.usd_balance == 700.0

    def test_withdraw_insufficient_raises(self):
        p = Portfolio(initial_usd_balance=100.0)
        with pytest.raises(PortfolioError):
            p.withdraw_usd(200.0)

    def test_buy_creates_holding(self):
        p = Portfolio(initial_usd_balance=10_000.0)
        p.buy("BTC", amount=0.1, price_usd=60_000.0)
        assert "BTC" in p.holdings
        assert p.holdings["BTC"].total_amount == pytest.approx(0.1, rel=1e-6)

    def test_buy_deducts_balance(self):
        p = Portfolio(initial_usd_balance=10_000.0)
        p.buy("BTC", amount=0.1, price_usd=60_000.0, fee_pct=0.001)
        cost = 0.1 * 60_000.0 * 1.001
        assert p.usd_balance == pytest.approx(10_000.0 - cost, rel=1e-6)

    def test_buy_insufficient_balance_raises(self):
        p = Portfolio(initial_usd_balance=100.0)
        with pytest.raises(PortfolioError):
            p.buy("BTC", amount=1.0, price_usd=60_000.0)

    def test_sell_reduces_holding(self):
        p = Portfolio(initial_usd_balance=10_000.0)
        p.buy("ETH", amount=1.0, price_usd=3_000.0)
        p.sell("ETH", amount=0.5, price_usd=3_200.0)
        assert p.holdings["ETH"].total_amount == pytest.approx(0.5, rel=1e-6)

    def test_sell_increases_balance(self):
        p = Portfolio(initial_usd_balance=10_000.0)
        p.buy("ETH", amount=1.0, price_usd=3_000.0)
        before = p.usd_balance
        p.sell("ETH", amount=1.0, price_usd=3_200.0)
        assert p.usd_balance > before

    def test_sell_insufficient_raises(self):
        p = Portfolio()
        with pytest.raises(PortfolioError):
            p.sell("BTC", amount=1.0, price_usd=60_000.0)

    def test_add_mined_credits_holding(self):
        p = Portfolio()
        p.add_mined("BTC", amount=0.001, cost_usd=5.0)
        assert "BTC" in p.holdings
        assert p.holdings["BTC"].total_amount == pytest.approx(0.001, rel=1e-6)

    def test_sell_records_realised_pnl(self):
        p = Portfolio(initial_usd_balance=100_000.0)
        p.buy("BTC", amount=1.0, price_usd=50_000.0, fee_pct=0.0)
        result = p.sell("BTC", amount=1.0, price_usd=55_000.0, fee_pct=0.0)
        assert result["realised_pnl_usd"] == pytest.approx(5_000.0, rel=1e-6)

    def test_portfolio_summary_keys(self):
        p = Portfolio()
        summary = p.summary()
        for key in ("usd_balance", "total_market_value_usd", "holdings", "num_transactions"):
            assert key in summary

    def test_transaction_history(self):
        p = Portfolio(initial_usd_balance=10_000.0)
        p.buy("BTC", amount=0.1, price_usd=60_000.0)
        txs = p.get_transactions()
        assert len(txs) == 1
        assert txs[0]["tx_type"] == TransactionType.BUY

    def test_transaction_filter_by_type(self):
        p = Portfolio(initial_usd_balance=10_000.0)
        p.buy("BTC", amount=0.1, price_usd=60_000.0)
        p.add_mined("LTC", 0.5)
        buys = p.get_transactions(tx_type=TransactionType.BUY)
        assert all(t["tx_type"] == TransactionType.BUY for t in buys)


# ===========================================================================
# trading
# ===========================================================================

class TestTradingEngine:
    def _engine(self):
        p = Portfolio(initial_usd_balance=100_000.0)
        return TradingEngine(p, fee_pct=0.001, use_live=False)

    def test_market_buy_returns_dict(self):
        eng = self._engine()
        result = eng.market_buy("BTC", usd_amount=1_000.0)
        assert isinstance(result, dict)
        assert result["order_type"] == "market_buy"

    def test_market_buy_creates_holding(self):
        eng = self._engine()
        eng.market_buy("BTC", usd_amount=1_000.0)
        assert "BTC" in eng.portfolio.holdings

    def test_market_sell_returns_dict(self):
        eng = self._engine()
        eng.market_buy("ETH", usd_amount=5_000.0)
        holding = eng.portfolio.holdings["ETH"]
        result = eng.market_sell("ETH", amount=holding.total_amount / 2)
        assert result["order_type"] == "market_sell"

    def test_sell_all(self):
        eng = self._engine()
        eng.market_buy("SOL", usd_amount=1_000.0)
        eng.sell_all("SOL")
        assert eng.portfolio.holdings["SOL"].total_amount == pytest.approx(0.0, abs=1e-8)

    def test_market_buy_zero_raises(self):
        eng = self._engine()
        with pytest.raises(TradingError):
            eng.market_buy("BTC", usd_amount=0.0)

    def test_sell_nothing_raises(self):
        eng = self._engine()
        with pytest.raises(TradingError):
            eng.sell_all("BTC")

    def test_limit_buy_fills_when_price_low(self):
        eng = self._engine()
        btc_price = get_price("BTC")
        result = eng.limit_buy("BTC", amount=0.001, limit_price=btc_price * 2)
        # price is below limit, so it fills
        assert result["status"] == "filled"

    def test_limit_buy_pending_when_price_high(self):
        eng = self._engine()
        result = eng.limit_buy("BTC", amount=0.001, limit_price=1.0)
        assert result["status"] == "pending"

    def test_pnl_report_keys(self):
        eng = self._engine()
        eng.market_buy("BTC", usd_amount=5_000.0)
        report = eng.pnl_report()
        for key in ("holdings", "total_pnl_usd", "total_realised_pnl_usd", "usd_balance"):
            assert key in report


# ===========================================================================
# mining
# ===========================================================================

class TestMining:
    def test_simulate_mining_btc_returns_dict(self):
        result = simulate_mining("BTC", duration_hours=1.0)
        assert isinstance(result, dict)

    def test_simulate_mining_keys(self):
        result = simulate_mining("BTC", duration_hours=24.0)
        for key in ("coins_mined", "revenue_usd", "electricity_cost_usd", "net_profit_usd"):
            assert key in result

    def test_coins_mined_positive(self):
        result = simulate_mining("BTC", duration_hours=1.0)
        assert result["coins_mined"] > 0

    def test_simulate_ltc(self):
        result = simulate_mining("LTC", duration_hours=24.0)
        assert result["coins_mined"] > 0

    def test_simulate_xmr(self):
        result = simulate_mining("XMR", duration_hours=24.0)
        assert result["coins_mined"] > 0

    def test_simulate_non_mineable_raises(self):
        with pytest.raises(ValueError):
            simulate_mining("ETH", duration_hours=1.0)

    def test_simulate_unknown_raises(self):
        with pytest.raises(ValueError):
            simulate_mining("NOTACOIN")

    def test_longer_duration_more_coins(self):
        r1 = simulate_mining("BTC", duration_hours=1.0)
        r24 = simulate_mining("BTC", duration_hours=24.0)
        assert r24["coins_mined"] > r1["coins_mined"]

    def test_mining_leaderboard_returns_list(self):
        lb = mining_leaderboard(symbols=["BTC", "LTC", "DOGE"], top_n=3)
        assert isinstance(lb, list)
        assert len(lb) <= 3

    def test_mining_leaderboard_sorted(self):
        lb = mining_leaderboard(symbols=["BTC", "LTC", "DOGE"], top_n=3)
        profits = [r["daily_profit_usd"] for r in lb]
        assert profits == sorted(profits, reverse=True)

    def test_break_even_profitable(self):
        result = calculate_break_even("BTC", hardware_cost_usd=1_000.0)
        assert isinstance(result, dict)
        assert "break_even_days" in result

    def test_mining_profile_btc(self):
        profile = get_mining_profile("BTC")
        assert "algorithm" in profile
        assert profile["algorithm"] == "SHA-256"

    def test_mining_profile_generic_fallback(self):
        profile = get_mining_profile("UNKNOWNCOIN")
        assert "algorithm" in profile


# ===========================================================================
# prospectus
# ===========================================================================

class TestProspectus:
    def test_get_coin_prospectus_btc(self):
        p = get_coin_prospectus("BTC")
        assert p["symbol"] == "BTC"
        assert p["name"] == "Bitcoin"

    def test_prospectus_has_required_keys(self):
        p = get_coin_prospectus("ETH")
        for key in (
            "symbol", "name", "category", "current_price_usd",
            "price_change_24h_pct", "market_cap_usd", "investment_thesis",
            "risk_label", "tags",
        ):
            assert key in p

    def test_prospectus_unknown_raises(self):
        with pytest.raises(ValueError):
            get_coin_prospectus("NOTACOIN")

    def test_prospectus_price_positive(self):
        p = get_coin_prospectus("SOL")
        assert p["current_price_usd"] > 0

    def test_prospectus_text_returns_string(self):
        text = prospectus_text("BTC")
        assert isinstance(text, str)
        assert "Bitcoin" in text

    def test_prospectus_text_contains_price(self):
        text = prospectus_text("BTC")
        assert "Price" in text

    def test_list_all_prospectuses_returns_list(self):
        prosp = list_all_prospectuses(category="Stablecoin")
        assert isinstance(prosp, list)
        assert all(p["category"] == "Stablecoin" for p in prosp)

    def test_stablecoin_risk_very_low(self):
        p = get_coin_prospectus("USDT")
        assert p["risk_label"] == "Very Low"

    def test_prospectus_tags_not_empty(self):
        p = get_coin_prospectus("XMR")
        assert len(p["tags"]) > 0

    def test_btc_investment_thesis_not_empty(self):
        p = get_coin_prospectus("BTC")
        assert len(p["investment_thesis"]) > 0


# ===========================================================================
# dashboard
# ===========================================================================

class TestDashboard:
    def _portfolio(self):
        p = Portfolio(initial_usd_balance=10_000.0)
        p.buy("BTC", amount=0.1, price_usd=60_000.0)
        p.buy("ETH", amount=1.0, price_usd=3_200.0)
        return p

    def test_render_portfolio_returns_string(self):
        p = self._portfolio()
        text = render_portfolio(p)
        assert isinstance(text, str)

    def test_render_portfolio_contains_btc(self):
        p = self._portfolio()
        text = render_portfolio(p)
        assert "BTC" in text

    def test_render_market_overview_returns_string(self):
        text = render_market_overview(symbols=["BTC", "ETH"])
        assert isinstance(text, str)
        assert "BTC" in text

    def test_render_transactions_returns_string(self):
        p = self._portfolio()
        text = render_transactions(p)
        assert isinstance(text, str)

    def test_render_full_dashboard_returns_string(self):
        p = self._portfolio()
        text = render_full_dashboard(p, market_symbols=["BTC", "ETH"])
        assert isinstance(text, str)
        assert "PORTFOLIO" in text.upper()


# ===========================================================================
# CryptoBot (main class)
# ===========================================================================

class TestCryptoBotInstantiation:
    def test_default_tier_is_free(self):
        bot = CryptoBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = CryptoBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = CryptoBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_initial_balance(self):
        bot = CryptoBot(initial_usd_balance=5_000.0)
        summary = bot.portfolio_summary()
        assert summary["usd_balance"] == 5_000.0


class TestCryptoBotTracking:
    def test_default_tracked_coins(self):
        bot = CryptoBot()
        coins = bot.get_tracked_coins()
        assert isinstance(coins, list)
        assert len(coins) > 0

    def test_track_adds_coin(self):
        bot = CryptoBot()
        bot.track("SOL")
        assert "SOL" in bot.get_tracked_coins()

    def test_untrack_removes_coin(self):
        bot = CryptoBot()
        bot.track("SOL")
        bot.untrack("SOL")
        assert "SOL" not in bot.get_tracked_coins()

    def test_track_unknown_raises(self):
        bot = CryptoBot()
        with pytest.raises(CryptoBotError):
            bot.track("NOTACOIN")

    def test_free_tier_track_limit(self):
        bot = CryptoBot(tier=Tier.FREE)
        # Already has 5 default coins; adding another should fail
        bot._tracked_coins = ["BTC", "ETH", "SOL", "ADA", "DOT"]
        with pytest.raises(CryptoBotError):
            bot.track("XRP")

    def test_pro_tier_larger_limit(self):
        bot = CryptoBot(tier=Tier.PRO)
        bot._tracked_coins = []
        for sym in ["BTC", "ETH", "SOL", "ADA", "DOT", "XRP"]:
            bot.track(sym)
        assert len(bot.get_tracked_coins()) == 6

    def test_price_returns_dict(self):
        bot = CryptoBot()
        result = bot.price("BTC")
        assert "price_usd" in result
        assert result["price_usd"] > 0

    def test_search_returns_results(self):
        bot = CryptoBot()
        results = bot.search("bitcoin")
        assert len(results) > 0

    def test_list_all_coins(self):
        bot = CryptoBot()
        coins = bot.list_all_coins()
        assert len(coins) >= 50

    def test_market_overview_returns_list(self):
        bot = CryptoBot()
        overview = bot.market_overview()
        assert isinstance(overview, list)


class TestCryptoBotTrading:
    def _pro_bot(self):
        return CryptoBot(tier=Tier.PRO, initial_usd_balance=50_000.0)

    def test_free_cannot_buy(self):
        bot = CryptoBot(tier=Tier.FREE)
        with pytest.raises(CryptoBotError):
            bot.buy("BTC", usd_amount=100.0)

    def test_pro_can_buy(self):
        bot = self._pro_bot()
        result = bot.buy("BTC", usd_amount=1_000.0)
        assert "tx" in result

    def test_pro_can_sell(self):
        bot = self._pro_bot()
        bot.buy("ETH", usd_amount=2_000.0)
        holding = bot._portfolio.holdings["ETH"]
        result = bot.sell("ETH", amount=holding.total_amount / 2)
        assert "tx" in result

    def test_deposit(self):
        bot = self._pro_bot()
        before = bot.portfolio_summary()["usd_balance"]
        bot.deposit(500.0)
        after = bot.portfolio_summary()["usd_balance"]
        assert after == pytest.approx(before + 500.0, rel=1e-6)

    def test_withdraw(self):
        bot = self._pro_bot()
        before = bot.portfolio_summary()["usd_balance"]
        bot.withdraw(1_000.0)
        after = bot.portfolio_summary()["usd_balance"]
        assert after == pytest.approx(before - 1_000.0, rel=1e-6)

    def test_pnl_report_requires_pro(self):
        bot = CryptoBot(tier=Tier.FREE)
        with pytest.raises(CryptoBotError):
            bot.pnl_report()

    def test_pnl_report_pro(self):
        bot = self._pro_bot()
        bot.buy("BTC", usd_amount=5_000.0)
        report = bot.pnl_report()
        assert "total_pnl_usd" in report

    def test_transaction_history_requires_pro(self):
        bot = CryptoBot(tier=Tier.FREE)
        with pytest.raises(CryptoBotError):
            bot.transaction_history()

    def test_transaction_history_pro(self):
        bot = self._pro_bot()
        bot.buy("BTC", usd_amount=1_000.0)
        txs = bot.transaction_history()
        assert len(txs) >= 1


class TestCryptoBotMining:
    def test_free_can_mine_btc(self):
        bot = CryptoBot(tier=Tier.FREE)
        result = bot.mine("BTC", hours=1.0)
        assert "coins_mined" in result

    def test_free_cannot_mine_eth(self):
        bot = CryptoBot(tier=Tier.FREE)
        with pytest.raises(CryptoBotError):
            bot.mine("ETH", hours=1.0)

    def test_free_cannot_mine_ltc(self):
        bot = CryptoBot(tier=Tier.FREE)
        with pytest.raises(CryptoBotError):
            bot.mine("LTC", hours=1.0)

    def test_pro_can_mine_ltc(self):
        bot = CryptoBot(tier=Tier.PRO)
        result = bot.mine("LTC", hours=1.0)
        assert result["coins_mined"] > 0

    def test_mine_credits_portfolio(self):
        bot = CryptoBot(tier=Tier.FREE)
        bot.mine("BTC", hours=24.0, credit_to_portfolio=True)
        assert "BTC" in bot._portfolio.holdings

    def test_mine_no_credit(self):
        bot = CryptoBot(tier=Tier.FREE)
        before = len(bot._portfolio.holdings)
        bot.mine("BTC", hours=1.0, credit_to_portfolio=False)
        assert len(bot._portfolio.holdings) == before

    def test_mining_leaderboard_returns_list(self):
        bot = CryptoBot(tier=Tier.PRO)
        lb = bot.mining_leaderboard(top_n=5)
        assert isinstance(lb, list)

    def test_break_even_returns_dict(self):
        bot = CryptoBot(tier=Tier.FREE)
        result = bot.break_even("BTC", hardware_cost_usd=1_000.0)
        assert "break_even_days" in result


class TestCryptoBotProspectus:
    def test_prospectus_returns_string(self):
        bot = CryptoBot()
        text = bot.prospectus("BTC")
        assert isinstance(text, str)
        assert "Bitcoin" in text

    def test_prospectus_dict_returns_dict(self):
        bot = CryptoBot()
        p = bot.prospectus_dict("ETH")
        assert p["symbol"] == "ETH"

    def test_all_prospectuses_requires_enterprise(self):
        bot = CryptoBot(tier=Tier.PRO)
        with pytest.raises(CryptoBotError):
            bot.all_prospectuses()

    def test_all_prospectuses_with_category_pro_ok(self):
        bot = CryptoBot(tier=Tier.PRO)
        # Filtered category is allowed on all tiers
        prosp = bot.all_prospectuses(category="Stablecoin")
        assert isinstance(prosp, list)

    def test_all_prospectuses_enterprise(self):
        bot = CryptoBot(tier=Tier.ENTERPRISE)
        prosp = bot.all_prospectuses()
        assert isinstance(prosp, list)
        assert len(prosp) >= 50


class TestCryptoBotDashboard:
    def _pro_bot(self):
        bot = CryptoBot(tier=Tier.PRO, initial_usd_balance=10_000.0)
        bot.buy("BTC", usd_amount=1_000.0)
        return bot

    def test_dashboard_requires_pro(self):
        bot = CryptoBot(tier=Tier.FREE)
        with pytest.raises(CryptoBotError):
            bot.dashboard()

    def test_dashboard_returns_string(self):
        bot = self._pro_bot()
        text = bot.dashboard()
        assert isinstance(text, str)
        assert len(text) > 100

    def test_market_board_available_on_free(self):
        bot = CryptoBot(tier=Tier.FREE)
        text = bot.market_board()
        assert isinstance(text, str)
        assert "BTC" in text

    def test_describe_tier_free(self):
        bot = CryptoBot(tier=Tier.FREE)
        text = bot.describe_tier()
        assert "Free" in text

    def test_describe_tier_enterprise(self):
        bot = CryptoBot(tier=Tier.ENTERPRISE)
        text = bot.describe_tier()
        assert "Enterprise" in text
