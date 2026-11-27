"""Local-only paper trading and deterministic backtesting utilities."""

from .backtest import BacktestConfig, BacktestResult, Bar, run_backtest, sma_crossover_signals
from .paper_broker import Fill, PaperBroker, RiskLimitError
from .momentum import calculate_momentum_score, rank_momentum_universe

__all__ = [
    "BacktestConfig",
    "BacktestResult",
    "Bar",
    "Fill",
    "PaperBroker",
    "RiskLimitError",
    "run_backtest",
    "sma_crossover_signals",
    "calculate_momentum_score",
    "rank_momentum_universe",
]
