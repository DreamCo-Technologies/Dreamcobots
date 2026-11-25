from __future__ import annotations

import json
import unittest
from pathlib import Path

from buddy.trading.backtest import BacktestConfig, Bar, run_backtest, sma_crossover_signals
from buddy.trading.demo import synthetic_bars
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

    def test_backtest_rejects_mixed_symbols_and_bad_signals(self):
        bars = synthetic_bars(12)
        mixed = [*bars[:-1], Bar("last", "OTHER", 100, 101, 99, 100, 100)]
        with self.assertRaisesRegex(ValueError, "one symbol"):
            run_backtest(mixed)
        with self.assertRaisesRegex(ValueError, "one long/flat value"):
            run_backtest(bars, signals=[2] * len(bars))


if __name__ == "__main__":
    unittest.main()
