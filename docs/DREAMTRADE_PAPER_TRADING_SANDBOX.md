# DreamTrade Paper-Trading Sandbox

This is a local, deterministic paper-trading teaching environment for the FreeCodeCamp algorithmic-trading learning path (source video ID `zH2Mg782XhA`). It is designed for experiments and engineering practice, not investment advice or live execution. The video catalog record is metadata-only; this guide is an original DreamCo implementation exercise, not a transcript or substitute for the video.

## Run the demo

```bash
python -m buddy.trading.demo
python -m unittest tests.test_paper_trading_sandbox
```

The demo uses deterministic synthetic OHLCV bars. It does not connect to a broker, request API credentials, download market data, or submit live orders.

## Components

- `PaperBroker`: local cash/position ledger with fees, slippage, long-only defaults, and notional risk limits.
- `sma_crossover_signals`: a simple baseline strategy. Each signal uses only prior bars.
- `run_backtest`: executes at the next bar open, marks positions to market, and records an equity curve and fills.
- `synthetic_bars`: deterministic sample data so tests and demonstrations are reproducible.
- `calculate_momentum_score` and `rank_momentum_universe`: a 252-bar (12-month proxy) cross-sectional ranking across 50 synthetic symbols. The demo ranks candidates but does not execute multi-symbol portfolio orders.

## Required build sequence

1. Review the source video metadata and verify the rights status of any additional learning material.
2. Explain OHLCV bars, timestamps, market/limit orders, fees, slippage, positions, and portfolio equity.
3. Inspect the synthetic dataset and validate timestamps, OHLC relationships, symbol consistency, and missing values.
4. Implement a baseline strategy with explicit signal timing and no look-ahead bias.
5. Run the strategy through the paper broker; never route an order to a live brokerage.
6. Add position sizing, maximum order notional, maximum position notional, and short-selling restrictions.
7. Add deterministic unit tests for fills, fees, slippage, risk rejection, and edge cases.
8. Evaluate return and drawdown on synthetic or approved historical data; do not interpret a backtest as a profit guarantee.
9. Add walk-forward evaluation, out-of-sample checks, transaction-cost sensitivity, and benchmark comparisons before considering any research result credible.
10. Submit code, test results, assumptions, and limitations for human review.

## Safety boundary

- `LIVE_TRADING_ENABLED` is hard-coded false.
- The package has no brokerage client, network transport, secret lookup, or live-order endpoint.
- Short selling is disabled by default.
- Oversized orders and positions are rejected.
- Use synthetic data or properly licensed historical data only.
- No strategy is guaranteed to be profitable. This sandbox is educational and must not be used as a signal to buy or sell securities.


## Source-course expansion roadmap

The source course describes a larger Django application with market-data ingestion, portfolio/account connectivity, a 12-month momentum strategy across a 50-stock universe, a dashboard, historical backfills, and paper execution. The current DreamTrade package is deliberately a smaller local-only foundation: it now demonstrates a 252-bar momentum ranking across 50 synthetic symbols plus a single-symbol paper backtest, but it does not yet build a multi-symbol portfolio or external integrations. Build the larger system in these reviewed phases:

1. Create Django apps and relational models for symbols, OHLCV bars, portfolio snapshots, strategy runs, signals, orders, and fills.
2. Add Django admin views and validation for market data, portfolios, and strategy configuration.
3. Add a Massive market-data adapter with rate limits, retries, provenance, and credentials held only in an approved secret manager.
4. Add SnapTrade read-only account and holdings access; do not request trading permissions for the learning environment.
5. Implement and test the 12-month momentum calculation and 50-symbol universe, including survivorship-bias, look-ahead, missing-data, and transaction-cost checks.
6. Connect Alpaca only through its paper-trading environment after explicit configuration and sandbox verification; do not add a live-order endpoint.
7. Build the Django dashboard for portfolio state, strategy signals, backtest results, and immutable audit history.
8. Backfill approved historical data, run out-of-sample and walk-forward tests, and require human review before any integration is enabled.

These are planned phases, not claims that the external integrations already exist. The local synthetic demo remains the default Buddy demonstration.
