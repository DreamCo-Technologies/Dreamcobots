"""Local-only paper trading and deterministic backtesting utilities."""

from .backtest import BacktestConfig, BacktestResult, Bar, run_backtest, sma_crossover_signals
from .paper_broker import Fill, PaperBroker, RiskLimitError

__all__ = [
    "BacktestConfig",
    "BacktestResult",
    "Bar",
    "Fill",
    "PaperBroker",
    "RiskLimitError",
    "run_backtest",
    "sma_crossover_signals",
]
