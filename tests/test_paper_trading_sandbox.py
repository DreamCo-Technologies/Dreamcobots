from __future__ import annotations

import json
import unittest
from pathlib import Path

from buddy.trading.backtest import BacktestConfig, Bar, run_backtest, sma_crossover_signals
from buddy.trading.demo import synthetic_bars, synthetic_momentum_universe
from buddy.trading.momentum import calculate_momentum_score, rank_momentum_universe
from buddy.trading.paper_broker import LIVE_TRADING_ENABLED, PaperBroker, RiskLimitError


class PaperBrokerTests(unittest.TestCase):
    def test_broker_is_paper_only_and_charges_fees_and_slippage(self):
        broker = PaperBroker(
            10_000,
            fee_bps=10,
            slippage_bps=10,
            max_order_notional=5_000,
            max_position_notional=5_000,
        )
        fill = broker.submit_market_order("xyz", "buy", 10, 100, "t1")
        self.assertEqual(broker.mode, "paper_only")
        self.assertFalse(LIVE_TRADING_ENABLED)
        self.assertFalse(broker.live_orders_enabled)
        self.assertEqual(fill.symbol, "XYZ")
        self.assertAlmostEqual(fill.execution_price, 100.1)
        self.assertGreater(fill.fee, 0)
        self.assertEqual(broker.positions["XYZ"], 10)
        self.assertLess(broker.cash, 10_000)

    def test_short_selling_is_rejected_by_default(self):
        broker = PaperBroker(10_000)
        with self.assertRaisesRegex(RiskLimitError, "short selling is disabled"):
            broker.submit_market_order("XYZ", "sell", 1, 100, "t1")

    def test_order_and_position_limits_are_enforced(self):
        broker = PaperBroker(
            100_000,
            max_order_notional=1_000,
            max_position_notional=1_000,
        )
        with self.assertRaisesRegex(RiskLimitError, "max_order_notional"):
            broker.submit_market_order("XYZ", "buy", 20, 100, "t1")
        broker.submit_market_order("XYZ", "buy", 5, 100, "t2")
        with self.assertRaisesRegex(RiskLimitError, "max_position_notional"):
            broker.submit_market_order("XYZ", "buy", 6, 100, "t3")


    def test_reducing_a_long_position_is_allowed_after_marked_value_grows(self):
        broker = PaperBroker(
            10_000,
            max_order_notional=1_000,
            max_position_notional=1_000,
        )
        broker.submit_market_order("XYZ", "buy", 5, 100, "t1")
        fill = broker.submit_market_order("XYZ", "sell", 1, 300, "t2")
        self.assertEqual(fill.side, "sell")
        self.assertEqual(broker.positions["XYZ"], 4)

    def test_equity_requires_a_mark_for_every_open_position(self):
        broker = PaperBroker(10_000)
        broker.submit_market_order("XYZ", "buy", 1, 100, "t1")
        with self.assertRaisesRegex(ValueError, "missing mark price"):
            broker.equity({})



    def test_freecodecamp_trading_path_uses_the_paper_only_demo(self):
        root = Path(__file__).resolve().parents[1]
        config = json.loads(
            (root / "config/freecodecamp-division-routing-overrides.json").read_text(encoding="utf-8")
        )
        lesson = next(row for row in config["entries"] if row["video_id"] == "zH2Mg782XhA")
        self.assertIn("python -m buddy.trading.demo", lesson["buddy_demo"])
        self.assertTrue(any("python -m buddy.trading.demo" in step for step in lesson["implementation_steps"]))
        self.assertIn("paper-only", lesson["buddy_demo"].lower())


    def test_252_bar_momentum_score_uses_exact_lookback(self):
        prices = [100.0] + [101.0] * 252
        self.assertAlmostEqual(calculate_momentum_score(prices, lookback=252), 0.01)

    def test_momentum_universe_ranks_highest_score_first_with_stable_ties(self):
        histories = {
            "AAA": [100.0, 110.0],
            "CCC": [100.0, 120.0],
            "BBB": [100.0, 120.0],
        }
        ranked = rank_momentum_universe(histories, lookback=1, top_n=3)
        self.assertEqual([row["symbol"] for row in ranked], ["BBB", "CCC", "AAA"])
        self.assertGreater(ranked[0]["momentum_score"], ranked[-1]["momentum_score"])

    def test_momentum_requires_sufficient_finite_positive_prices(self):
        with self.assertRaisesRegex(ValueError, "at least"):
            calculate_momentum_score([100.0, 101.0], lookback=2)
        with self.assertRaisesRegex(ValueError, "finite and positive"):
            calculate_momentum_score([100.0, 0.0], lookback=1)

    def test_demo_uses_a_50_symbol_252_bar_synthetic_universe(self):
        universe = synthetic_momentum_universe()
        self.assertEqual(len(universe), 50)
        self.assertTrue(all(len(history) == 253 for history in universe.values()))
        self.assertEqual(len(rank_momentum_universe(universe, lookback=252, top_n=5)), 5)

class BacktestTests(unittest.TestCase):
    def test_sma_signal_uses_only_prior_bars(self):
        bars = [
            Bar(str(i), "XYZ", close, close + 1, close - 1, close, 100)
            for i, close in enumerate([10, 10, 10, 20, 20, 20, 20])
        ]
        signals = sma_crossover_signals(bars, fast_window=2, slow_window=3)
        self.assertEqual(signals[:4], [0, 0, 0, 0])
        self.assertEqual(signals[4], 1)

    def test_backtest_is_deterministic_and_never_enables_live_orders(self):
        bars = synthetic_bars(80)
        config = BacktestConfig(
            initial_cash=10_000,
            allocation_fraction=0.2,
            fee_bps=1,
            slippage_bps=5,
            max_order_notional=2_000,
            max_position_notional=2_000,
        )
        first = run_backtest(bars, config=config)
        second = run_backtest(bars, config=config)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(first.mode, "paper_only")
        self.assertFalse(first.live_orders_enabled)
        self.assertGreater(first.fill_count, 0)
        self.assertGreaterEqual(first.max_drawdown, 0)
        self.assertEqual(len(first.equity_curve), len(bars) + 1)


    def test_backtest_splits_large_exit_after_price_appreciation(self):
        bars = [
            Bar("t0", "XYZ", 100, 101, 99, 100, 100),
            Bar("t1", "XYZ", 150, 151, 149, 150, 100),
            Bar("t2", "XYZ", 200, 201, 199, 200, 100),
            Bar("t3", "XYZ", 200, 201, 199, 200, 100),
        ]
        result = run_backtest(
            bars,
            signals=[1, 1, 1, 0],
            config=BacktestConfig(
                initial_cash=10_000,
                allocation_fraction=1.0,
                max_order_notional=1_000,
                max_position_notional=1_000,
                slippage_bps=5,
            ),
        )
        self.assertGreaterEqual(result.fill_count, 3)
        self.assertEqual(result.ending_cash, result.ending_equity)

    def test_backtest_rejects_mixed_symbols_and_bad_signals(self):
        bars = synthetic_bars(12)
        mixed = [*bars[:-1], Bar("last", "OTHER", 100, 101, 99, 100, 100)]
        with self.assertRaisesRegex(ValueError, "one symbol"):
            run_backtest(mixed)
        with self.assertRaisesRegex(ValueError, "one long/flat value"):
            run_backtest(bars, signals=[2] * len(bars))


if __name__ == "__main__":
    unittest.main()
