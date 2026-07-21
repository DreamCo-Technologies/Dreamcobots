"""
Auto-Bot Factory — bots/bot_generator package.

Usage::

    from bots.bot_generator.request_interface import RequestInterface
    from bots.bot_generator.feature_optimizer import FeatureOptimizer
    from bots.bot_generator.code_generator import CodeGenerator
    from bots.bot_generator.competitor_analyzer import CompetitorAnalyzer
    from bots.bot_generator.benchmarking_engine import BenchmarkingEngine
    from bots.bot_generator.revenue_tracker import RevenueTracker
"""

from bots.bot_generator.request_interface import RequestInterface, BotRequest
from bots.bot_generator.feature_optimizer import FeatureOptimizer
from bots.bot_generator.code_generator import CodeGenerator
from bots.bot_generator.competitor_analyzer import CompetitorAnalyzer
from bots.bot_generator.benchmarking_engine import BenchmarkingEngine
from bots.bot_generator.revenue_tracker import RevenueTracker

__all__ = [
    "RequestInterface",
    "BotRequest",
    "FeatureOptimizer",
    "CodeGenerator",
    "CompetitorAnalyzer",
    "BenchmarkingEngine",
    "RevenueTracker",
]
