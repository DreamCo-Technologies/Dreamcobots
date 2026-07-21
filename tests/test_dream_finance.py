"""Tests for all 25 DreamFinance bots."""
import sys
import os

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DF_ROOT = os.path.join(REPO_ROOT, "DreamFinance")
sys.path.insert(0, REPO_ROOT)

import importlib
import pytest


def _load_bot(subdir, module_name, class_name):
    """Dynamically load a bot class from DreamFinance."""
    bot_dir = os.path.join(DF_ROOT, subdir)
    spec = importlib.util.spec_from_file_location(
        f"dreamfinance_{subdir}",
        os.path.join(bot_dir, f"{module_name}.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, class_name)


# ──────────────────────────────────────────────────────────────────────────────
# 1. MarketSentimentAnalyzer
# ──────────────────────────────────────────────────────────────────────────────
class TestMarketSentimentAnalyzer:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("market_sentiment_analyzer", "market_sentiment_analyzer", "MarketSentimentAnalyzer")
        self.bot = cls(tier="pro")

    def test_instantiation(self):
        assert self.bot.tier == "pro"

    def test_analyze_news_returns_dict(self):
        result = self.bot.analyze_news(["Stock rallies", "Market drops"])
        assert isinstance(result, dict)
        assert "sentiment_scores" in result

    def test_track_social_returns_dict(self):
        result = self.bot.track_social(["Bullish on AAPL", "Sell everything"])
        assert isinstance(result, dict)
        assert "pulse" in result

    def test_analyze_filing_returns_dict(self):
        result = self.bot.analyze_filing("Company reported strong profit and revenue growth.")
        assert isinstance(result, dict)
        assert "keywords_found" in result

    def test_run_returns_string(self):
        assert "MarketSentimentAnalyzer" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 2. MarketAnomalyFinder
# ──────────────────────────────────────────────────────────────────────────────
class TestMarketAnomalyFinder:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("market_anomaly_finder", "market_anomaly_finder", "MarketAnomalyFinder")
        self.bot = cls(tier="enterprise")

    def test_instantiation(self):
        assert self.bot.tier == "enterprise"

    def test_detect_anomaly_returns_dict(self):
        result = self.bot.detect_anomaly({"value": 150, "mean": 100, "std": 10})
        assert isinstance(result, dict)
        assert "z_score" in result
        assert result["is_anomaly"] is True

    def test_alert_dark_pool(self):
        result = self.bot.alert_dark_pool({"size": 5_000_000, "threshold": 1_000_000})
        assert result["alert"] is True

    def test_flag_options(self):
        result = self.bot.flag_options({"volume": 10000, "open_interest": 100})
        assert result["flagged"] is True

    def test_run_returns_string(self):
        assert "MarketAnomalyFinder" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 3. CreditUnderwriter
# ──────────────────────────────────────────────────────────────────────────────
class TestCreditUnderwriter:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("credit_underwriter", "credit_underwriter", "CreditUnderwriter")
        self.bot = cls(tier="enterprise")

    def test_instantiation(self):
        assert self.bot.tier == "enterprise"

    def test_score_credit_in_range(self):
        result = self.bot.score_credit({"income": 80000, "credit_history_years": 10, "debt_ratio": 0.2})
        assert isinstance(result, dict)
        assert 300 <= result["credit_score"] <= 850

    def test_estimate_default_probability(self):
        result = self.bot.estimate_default({"debt_ratio": 0.4, "credit_history_years": 2})
        assert 0.0 <= result["default_probability"] <= 1.0

    def test_detect_fraud(self):
        result = self.bot.detect_fraud({"amount": 50000, "avg_transaction": 200})
        assert result["fraud_flag"] is True

    def test_run_returns_string(self):
        assert "CreditUnderwriter" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 4. InsuranceFraudDetector
# ──────────────────────────────────────────────────────────────────────────────
class TestInsuranceFraudDetector:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("insurance_fraud_detector", "insurance_fraud_detector", "InsuranceFraudDetector")
        self.bot = cls(tier="enterprise")

    def test_instantiation(self):
        assert self.bot.tier == "enterprise"

    def test_score_claim_returns_dict(self):
        result = self.bot.score_claim({"amount": 50000, "historical_avg": 5000})
        assert isinstance(result, dict)
        assert "fraud_score" in result

    def test_analyze_network(self):
        result = self.bot.analyze_network({"connections": [{"suspicious": True}, {"suspicious": False}]})
        assert result["flagged_nodes"] == 1

    def test_verify_document_all_pass(self):
        result = self.bot.verify_document({"signature": "yes", "date": "2024-01-01", "issuer": "hospital"})
        assert result["verified"] is True

    def test_run_returns_string(self):
        assert "InsuranceFraudDetector" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 5. ESGOptimizer
# ──────────────────────────────────────────────────────────────────────────────
class TestESGOptimizer:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("esg_optimizer", "esg_optimizer", "ESGOptimizer")
        self.bot = cls(tier="enterprise")

    def test_instantiation(self):
        assert self.bot.tier == "enterprise"

    def test_score_esg_returns_dict(self):
        result = self.bot.score_esg({"environmental_score": 80, "social_score": 70, "governance_score": 90})
        assert isinstance(result, dict)
        assert "total_esg" in result
        assert result["grade"] == "A"

    def test_track_carbon(self):
        portfolio = [{"carbon_tons": 100}, {"carbon_tons": 200}]
        result = self.bot.track_carbon(portfolio)
        assert result["total_carbon_tons"] == 300.0

    def test_measure_impact(self):
        portfolio = [{"impact_score": 60}, {"impact_score": 40}]
        result = self.bot.measure_impact(portfolio)
        assert result["avg_impact_score"] == 50.0

    def test_run_returns_string(self):
        assert "ESGOptimizer" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 6. ETFRotator
# ──────────────────────────────────────────────────────────────────────────────
class TestETFRotator:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("etf_rotator", "etf_rotator", "ETFRotator")
        self.bot = cls(tier="pro")

    def test_instantiation(self):
        assert self.bot.tier == "pro"

    def test_score_momentum_returns_dict(self):
        etfs = [{"ticker": "SPY", "return_1m": 0.02, "return_3m": 0.05, "return_6m": 0.08},
                {"ticker": "QQQ", "return_1m": 0.03, "return_3m": 0.06, "return_6m": 0.10}]
        result = self.bot.score_momentum(etfs)
        assert "ranked" in result
        assert len(result["ranked"]) == 2

    def test_generate_signal(self):
        portfolio = {"current": {"SPY": 0.55, "QQQ": 0.45}, "targets": {"SPY": 0.60, "QQQ": 0.40}}
        result = self.bot.generate_signal(portfolio)
        assert result["signal"] in ("rebalance", "hold")

    def test_run_returns_string(self):
        assert "ETFRotator" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 7. BondIncomeBot
# ──────────────────────────────────────────────────────────────────────────────
class TestBondIncomeBot:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("bond_income_bot", "bond_income_bot", "BondIncomeBot")
        self.bot = cls(tier="pro")

    def test_instantiation(self):
        assert self.bot.tier == "pro"

    def test_screen_bonds_returns_list(self):
        criteria = {
            "min_yield": 3.0, "max_duration": 10,
            "universe": [{"yield": 4.0, "duration": 7}, {"yield": 1.5, "duration": 5}]
        }
        result = self.bot.screen_bonds(criteria)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_analyze_yield_curve(self):
        result = self.bot.analyze_yield_curve({"2y": 4.5, "10y": 3.8})
        assert result["shape"] == "inverted"

    def test_match_duration(self):
        bonds = [{"duration": 5}, {"duration": 8}, {"duration": 3}]
        result = self.bot.match_duration(5.0, bonds)
        assert result[0]["duration"] == 5

    def test_run_returns_string(self):
        assert "BondIncomeBot" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 8. DividendInvestor
# ──────────────────────────────────────────────────────────────────────────────
class TestDividendInvestor:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("dividend_investor", "dividend_investor", "DividendInvestor")
        self.bot = cls(tier="pro")

    def test_instantiation(self):
        assert self.bot.tier == "pro"

    def test_screen_aristocrats(self):
        stocks = [{"ticker": "JNJ", "consecutive_dividend_years": 60},
                  {"ticker": "XYZ", "consecutive_dividend_years": 5}]
        result = self.bot.screen_aristocrats(stocks)
        assert len(result) == 1
        assert result[0]["ticker"] == "JNJ"

    def test_score_sustainability(self):
        result = self.bot.score_sustainability({"payout_ratio": 0.4, "fcf_coverage": 2.0})
        assert result["safe"] is True

    def test_automate_drip(self):
        portfolio = {"holdings": [{"annual_dividend": 2.0, "shares": 100}]}
        result = self.bot.automate_drip(portfolio)
        assert result["annual_dividends"] == 200.0

    def test_run_returns_string(self):
        assert "DividendInvestor" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 9. CryptoStakingOptimizer
# ──────────────────────────────────────────────────────────────────────────────
class TestCryptoStakingOptimizer:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("crypto_staking_optimizer", "crypto_staking_optimizer", "CryptoStakingOptimizer")
        self.bot = cls(tier="pro")

    def test_instantiation(self):
        assert self.bot.tier == "pro"

    def test_find_staking_pools(self):
        result = self.bot.find_staking_pools(["ETH", "SOL", "DOT"])
        assert isinstance(result, list)
        assert len(result) == 3

    def test_select_validator(self):
        validators = [{"name": "V1", "uptime": 0.99, "commission": 0.05},
                      {"name": "V2", "uptime": 0.95, "commission": 0.10}]
        result = self.bot.select_validator("ETH", validators)
        assert "selected" in result

    def test_compound_rewards(self):
        stakes = [{"chain": "ETH", "pending_rewards": 0.5}, {"chain": "SOL", "pending_rewards": 1.0}]
        result = self.bot.compound_rewards(stakes)
        assert result["total_compounded"] == pytest.approx(1.5, rel=1e-5)

    def test_run_returns_string(self):
        assert "CryptoStakingOptimizer" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 10. DeFiYieldFarmer
# ──────────────────────────────────────────────────────────────────────────────
class TestDeFiYieldFarmer:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("defi_yield_farmer", "defi_yield_farmer", "DeFiYieldFarmer")
        self.bot = cls(tier="pro")

    def test_instantiation(self):
        assert self.bot.tier == "pro"

    def test_manage_position(self):
        result = self.bot.manage_position({"name": "ETH-USDC", "tvl": 1_000_000, "apy": 0.12})
        assert result["status"] == "active"

    def test_calculate_il_no_change(self):
        entry = {"price_a": 1000, "price_b": 1}
        current = {"price_a": 1000, "price_b": 1}
        result = self.bot.calculate_il(entry, current)
        assert result["impermanent_loss"] == pytest.approx(0.0, abs=1e-4)

    def test_schedule_harvest_returns_list(self):
        positions = [{"name": "ETH-USDC", "apy": 50}, {"name": "BTC-USDT", "apy": 20}]
        result = self.bot.schedule_harvest(positions)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_run_returns_string(self):
        assert "DeFiYieldFarmer" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 11. PortfolioRebalancer
# ──────────────────────────────────────────────────────────────────────────────
class TestPortfolioRebalancer:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("portfolio_rebalancer", "portfolio_rebalancer", "PortfolioRebalancer")
        self.bot = cls(tier="pro")

    def test_instantiation(self):
        assert self.bot.tier == "pro"

    def test_check_drift_needs_rebalance(self):
        result = self.bot.check_drift(
            {"SPY": 0.50, "BND": 0.50},
            {"SPY": 0.60, "BND": 0.40},
        )
        assert result["needs_rebalance"] is True

    def test_check_drift_no_rebalance(self):
        result = self.bot.check_drift(
            {"SPY": 0.60, "BND": 0.40},
            {"SPY": 0.60, "BND": 0.40},
        )
        assert result["needs_rebalance"] is False

    def test_rebalance_returns_orders(self):
        orders = self.bot.rebalance(
            {"SPY": 0.50, "BND": 0.50},
            {"SPY": 0.60, "BND": 0.40},
        )
        assert isinstance(orders, list)
        tickers = [o["ticker"] for o in orders]
        assert "SPY" in tickers

    def test_run_returns_string(self):
        assert "PortfolioRebalancer" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 12. RoboAdvisor
# ──────────────────────────────────────────────────────────────────────────────
class TestRoboAdvisor:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("robo_advisor", "robo_advisor", "RoboAdvisor")
        self.bot = cls(tier="enterprise")

    def test_instantiation(self):
        assert self.bot.tier == "enterprise"

    def test_profile_risk_returns_dict(self):
        result = self.bot.profile_risk({"risk_tolerance": 5, "time_horizon": 5, "income_volatility": 1})
        assert "profile" in result
        assert result["profile"] in ("aggressive", "moderate", "conservative")

    def test_construct_portfolio_returns_allocation(self):
        profile = {"profile": "moderate"}
        goal = {"name": "retirement"}
        result = self.bot.construct_portfolio(profile, goal)
        assert "allocation" in result
        alloc = result["allocation"]
        assert abs(sum(alloc.values()) - 1.0) < 1e-6

    def test_run_returns_string(self):
        assert "RoboAdvisor" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 13. TaxOptimizer
# ──────────────────────────────────────────────────────────────────────────────
class TestTaxOptimizer:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("tax_optimizer", "tax_optimizer", "TaxOptimizer")
        self.bot = cls(tier="pro")

    def test_instantiation(self):
        assert self.bot.tier == "pro"

    def test_harvest_losses_finds_loss(self):
        portfolio = {
            "AAPL": {"cost_basis": 200, "current_value": 150},
            "MSFT": {"cost_basis": 100, "current_value": 120},
        }
        result = self.bot.harvest_losses(portfolio)
        assert len(result) == 1
        assert result[0]["ticker"] == "AAPL"

    def test_defer_gains_returns_dict(self):
        portfolio = {
            "TSLA": {"holding_days": 100, "cost_basis": 200, "current_value": 300},
        }
        result = self.bot.defer_gains(portfolio)
        assert "TSLA" in result["deferrable_positions"]

    def test_check_wash_sales_empty(self):
        result = self.bot.check_wash_sales([])
        assert result == []

    def test_run_returns_string(self):
        assert "TaxOptimizer" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 14. AlgoTradingBot
# ──────────────────────────────────────────────────────────────────────────────
class TestAlgoTradingBot:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("algo_trading_bot", "algo_trading_bot", "AlgoTradingBot")
        self.bot = cls(tier="elite")

    def test_instantiation(self):
        assert self.bot.tier == "elite"

    def test_execute_order_returns_dict(self):
        result = self.bot.execute_order({"symbol": "AAPL", "price": 150, "qty": 10})
        assert result["status"] == "filled"
        assert "order_id" in result

    def test_backtest_returns_summary(self):
        result = self.bot.backtest({"name": "sma_cross", "edge": 0.05}, list(range(100)))
        assert "win_rate" in result
        assert "total_trades" in result

    def test_size_position(self):
        result = self.bot.size_position({"stop_distance": 2.0}, {"capital": 100000, "risk_pct": 0.01})
        assert result["position_size"] == pytest.approx(500.0, rel=1e-3)

    def test_run_returns_string(self):
        assert "AlgoTradingBot" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 15. HedgeFundStrategy
# ──────────────────────────────────────────────────────────────────────────────
class TestHedgeFundStrategy:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("hedge_fund_strategy", "hedge_fund_strategy", "HedgeFundStrategy")
        self.bot = cls(tier="elite")

    def test_instantiation(self):
        assert self.bot.tier == "elite"

    def test_generate_long_short(self):
        universe = [{"ticker": "AAPL"}, {"ticker": "MSFT"}, {"ticker": "TSLA"}, {"ticker": "AMZN"}]
        result = self.bot.generate_long_short(universe)
        assert "long" in result
        assert "short" in result

    def test_find_alpha_returns_list(self):
        events = [{"type": "earnings", "ticker": "AAPL"}, {"type": "merger", "ticker": "MSFT"}]
        result = self.bot.find_alpha(events)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_analyze_factors(self):
        portfolio = {"holdings": [{"pb_ratio": 2.5, "momentum": 0.1}]}
        result = self.bot.analyze_factors(portfolio)
        assert "value_tilt" in result

    def test_run_returns_string(self):
        assert "HedgeFundStrategy" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 16. HFTMarketMaker
# ──────────────────────────────────────────────────────────────────────────────
class TestHFTMarketMaker:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("hft_market_maker", "hft_market_maker", "HFTMarketMaker")
        self.bot = cls(tier="elite")

    def test_instantiation(self):
        assert self.bot.tier == "elite"

    def test_quote_spread_returns_bid_ask(self):
        result = self.bot.quote_spread("AAPL", {"best_bid": 149.9, "best_ask": 150.1})
        assert result["bid"] < result["ask"]
        assert result["symbol"] == "AAPL"

    def test_optimize_spread_returns_dict(self):
        result = self.bot.optimize_spread("AAPL", [{"spread": 0.02}, {"spread": 0.03}])
        assert "optimal_spread" in result

    def test_detect_latency_arb(self):
        feeds = [{"exchange": "NYSE", "price": 150.0}, {"exchange": "NASDAQ", "price": 150.1}]
        result = self.bot.detect_latency_arb(feeds)
        assert isinstance(result, list)

    def test_run_returns_string(self):
        assert "HFTMarketMaker" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 17. DerivativesStrategy
# ──────────────────────────────────────────────────────────────────────────────
class TestDerivativesStrategy:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("derivatives_strategy", "derivatives_strategy", "DerivativesStrategy")
        self.bot = cls(tier="elite")

    def test_instantiation(self):
        assert self.bot.tier == "elite"

    def test_price_option_returns_dict(self):
        result = self.bot.price_option({"spot": 100, "strike": 105, "time_to_expiry": 0.25, "rate": 0.05, "vol": 0.2})
        assert "call_price" in result
        assert "put_price" in result

    def test_calculate_greeks(self):
        result = self.bot.calculate_greeks({"vol": 0.2, "time_to_expiry": 0.25, "spot": 100})
        assert "delta" in result
        assert "gamma" in result
        assert "theta" in result
        assert "vega" in result

    def test_build_vol_surface(self):
        data = [{"expiry": "1m", "strike": 100, "implied_vol": 0.2},
                {"expiry": "3m", "strike": 105, "implied_vol": 0.22}]
        result = self.bot.build_vol_surface(data)
        assert "surface" in result
        assert "1m" in result["tenors"]

    def test_run_returns_string(self):
        assert "DerivativesStrategy" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 18. FXArbitrageBot
# ──────────────────────────────────────────────────────────────────────────────
class TestFXArbitrageBot:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("fx_arbitrage_bot", "fx_arbitrage_bot", "FXArbitrageBot")
        self.bot = cls(tier="elite")

    def test_instantiation(self):
        assert self.bot.tier == "elite"

    def test_find_triangular_returns_list(self):
        rates = {"EURUSD": 1.1, "GBPUSD": 1.3, "EURGBP": 0.9}
        result = self.bot.find_triangular(rates)
        assert isinstance(result, list)

    def test_scan_discrepancies_returns_list(self):
        result = self.bot.scan_discrepancies({"EURUSD": 1.1})
        assert isinstance(result, list)

    def test_execute_arb(self):
        result = self.bot.execute_arb({"profit_factor": 1.002, "path": ["EURUSD", "GBPUSD", "EURGBP"]})
        assert result["executed"] is True

    def test_run_returns_string(self):
        assert "FXArbitrageBot" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 19. QuantBacktester
# ──────────────────────────────────────────────────────────────────────────────
class TestQuantBacktester:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("quant_backtester", "quant_backtester", "QuantBacktester")
        self.bot = cls(tier="enterprise")

    def test_instantiation(self):
        assert self.bot.tier == "enterprise"

    def test_walk_forward_returns_dict(self):
        result = self.bot.walk_forward({"name": "momentum"}, list(range(100)))
        assert "folds" in result
        assert "avg_return" in result

    def test_monte_carlo_returns_percentiles(self):
        returns = [0.01, -0.005, 0.008, 0.003, -0.002] * 20
        result = self.bot.monte_carlo(returns, simulations=100)
        assert "p5" in result
        assert "p95" in result

    def test_detect_regime_bull(self):
        prices = [100 + i for i in range(30)]
        result = self.bot.detect_regime(prices)
        assert result["regime"] == "bull"

    def test_run_returns_string(self):
        assert "QuantBacktester" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 20. OptionsTrader
# ──────────────────────────────────────────────────────────────────────────────
class TestOptionsTrader:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("options_trader", "options_trader", "OptionsTrader")
        self.bot = cls(tier="pro")

    def test_instantiation(self):
        assert self.bot.tier == "pro"

    def test_scan_chain_returns_list(self):
        result = self.bot.scan_chain("AAPL", "2024-03-15")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_build_iron_condor(self):
        result = self.bot.build_iron_condor("SPX", {"center_strike": 4500, "width": 50, "credit": 5.0})
        assert len(result["legs"]) == 4

    def test_build_spread(self):
        result = self.bot.build_spread("AAPL", "call_debit", {"strike1": 150, "strike2": 160})
        assert len(result["legs"]) == 2

    def test_run_returns_string(self):
        assert "OptionsTrader" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 21. ForexTrader
# ──────────────────────────────────────────────────────────────────────────────
class TestForexTrader:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("forex_trader", "forex_trader", "ForexTrader")
        self.bot = cls(tier="pro")

    def test_instantiation(self):
        assert self.bot.tier == "pro"

    def test_correlate_pairs(self):
        result = self.bot.correlate_pairs(["EURUSD", "GBPUSD", "USDJPY"])
        assert "correlation_matrix" in result

    def test_generate_signal_buy(self):
        result = self.bot.generate_signal("EURUSD", [1.1, 1.2])
        assert result["signal"] == "buy"

    def test_get_calendar_events(self):
        result = self.bot.get_calendar_events("2024-01-15")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_run_returns_string(self):
        assert "ForexTrader" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 22. PennyStockScanner
# ──────────────────────────────────────────────────────────────────────────────
class TestPennyStockScanner:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("penny_stock_scanner", "penny_stock_scanner", "PennyStockScanner")
        self.bot = cls(tier="pro")

    def test_instantiation(self):
        assert self.bot.tier == "pro"

    def test_screen_stocks_filters_correctly(self):
        criteria = {
            "max_price": 5.0, "min_volume": 100000,
            "universe": [
                {"ticker": "ABCD", "price": 1.5, "volume": 500000},
                {"ticker": "XYZ", "price": 10.0, "volume": 1000000},
            ]
        }
        result = self.bot.screen_stocks(criteria)
        assert len(result) == 1
        assert result[0]["ticker"] == "ABCD"

    def test_detect_volume_spike(self):
        volume_data = [100000, 110000, 120000, 500000]
        result = self.bot.detect_volume_spike("ABCD", volume_data)
        assert result["spike"] is True

    def test_get_filing_alerts(self):
        result = self.bot.get_filing_alerts(["ABCD", "EFGH"])
        assert isinstance(result, list)

    def test_run_returns_string(self):
        assert "PennyStockScanner" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 23. CryptoTradingBot
# ──────────────────────────────────────────────────────────────────────────────
class TestCryptoTradingBot:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("crypto_trading_bot", "crypto_trading_bot", "CryptoTradingBot")
        self.bot = cls(tier="pro")

    def test_instantiation(self):
        assert self.bot.tier == "pro"

    def test_execute_trade_returns_dict(self):
        result = self.bot.execute_trade("binance", {"symbol": "BTC/USDT", "price": 50000, "qty": 0.01})
        assert result["status"] == "filled"

    def test_dca_buy_returns_intervals(self):
        result = self.bot.dca_buy("BTC", 1000.0, 5)
        assert len(result) == 5
        assert all(r["action"] == "buy" for r in result)

    def test_setup_grid(self):
        result = self.bot.setup_grid("BTC/USDT", {"lower": 40000, "upper": 50000, "grids": 10})
        assert len(result["levels"]) == 11
        assert result["grids"] == 10

    def test_run_returns_string(self):
        assert "CryptoTradingBot" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 24. TreasuryAnalyzer
# ──────────────────────────────────────────────────────────────────────────────
class TestTreasuryAnalyzer:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("treasury_analyzer", "treasury_analyzer", "TreasuryAnalyzer")
        self.bot = cls(tier="enterprise")

    def test_instantiation(self):
        assert self.bot.tier == "enterprise"

    def test_forecast_cash(self):
        result = self.bot.forecast_cash({"opening_balance": 1_000_000, "inflows": [500_000, 300_000], "outflows": [200_000, 100_000]})
        assert result["forecast_balance"] == pytest.approx(1_500_000.0, rel=1e-5)

    def test_analyze_liquidity(self):
        result = self.bot.analyze_liquidity({"current_assets": 2_000_000, "current_liabilities": 1_000_000})
        assert result["current_ratio"] == pytest.approx(2.0, rel=1e-5)
        assert result["adequate"] is True

    def test_manage_fx_exposure(self):
        exposures = {
            "EUR": {"usd_equivalent": 1_000_000, "hedged_usd": 500_000},
        }
        result = self.bot.manage_fx_exposure(exposures)
        assert result["hedge_ratio"] == pytest.approx(0.5, rel=1e-5)

    def test_run_returns_string(self):
        assert "TreasuryAnalyzer" in self.bot.run()


# ──────────────────────────────────────────────────────────────────────────────
# 25. VentureDealflow
# ──────────────────────────────────────────────────────────────────────────────
class TestVentureDealflow:
    @pytest.fixture(autouse=True)
    def setup(self):
        cls = _load_bot("venture_dealflow", "venture_dealflow", "VentureDealflow")
        self.bot = cls(tier="enterprise")

    def test_instantiation(self):
        assert self.bot.tier == "enterprise"

    def test_source_deals_returns_list(self):
        result = self.bot.source_deals({"stage": "series_a", "sector": "fintech", "limit": 3})
        assert isinstance(result, list)
        assert len(result) == 3

    def test_screen_deal_proceed(self):
        company = {"name": "FinTech Co", "revenue_growth": 50, "team_score": 9, "market_size_bn": 10}
        result = self.bot.screen_deal(company)
        assert result["proceed"] is True

    def test_monitor_portfolio_returns_list(self):
        portfolio = [
            {"name": "StartupA", "mrr_growth": 0.15},
            {"name": "StartupB", "mrr_growth": -0.05},
        ]
        result = self.bot.monitor_portfolio(portfolio)
        assert len(result) == 2
        statuses = {r["company"]: r["status"] for r in result}
        assert statuses["StartupA"] == "on_track"
        assert statuses["StartupB"] == "needs_attention"

    def test_run_returns_string(self):
        assert "VentureDealflow" in self.bot.run()
