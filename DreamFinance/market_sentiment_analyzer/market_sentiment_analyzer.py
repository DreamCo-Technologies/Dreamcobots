# GLOBAL AI SOURCES FLOW
"""Market Sentiment Analyzer — financial intelligence bot."""
import sys
import os
import importlib.util
_TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_TOOL_DIR, '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
# Load local tiers.py by path to avoid sys.modules conflicts with other tiers modules
_tiers_spec = importlib.util.spec_from_file_location(
    '_local_tiers_market_sentiment_analyzer', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class MarketSentimentAnalyzer:
    """Market Sentiment Analyzer bot for financial analysis."""

    def __init__(self, tier: str = "pro"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["pro"])

    def analyze_news(self, headlines: list) -> dict:
        """Analyze news — Market Sentiment Analyzer."""
        scores = [{"headline": h, "sentiment": "positive" if i % 3 != 0 else "negative", "score": round(0.5 + (i % 5) * 0.1, 2)} for i, h in enumerate(headlines)]
        return {"sentiment_scores": scores, "overall": "bullish" if len(scores) > 0 else "neutral", "disclaimer": DISCLAIMER}

    def track_social(self, posts: list) -> dict:
        """Track social — Market Sentiment Analyzer."""
        pulse = [{"post": p[:40], "sentiment": "positive" if i % 2 == 0 else "negative"} for i, p in enumerate(posts)]
        return {"pulse": pulse, "volume": len(posts), "disclaimer": DISCLAIMER}

    def analyze_filing(self, text: str) -> dict:
        """Analyze filing — Market Sentiment Analyzer."""
        keywords = ["revenue", "profit", "loss", "growth", "risk"]
        found = [k for k in keywords if k in text.lower()]
        return {"keywords_found": found, "tone": "positive" if "profit" in found else "cautious", "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"MarketSentimentAnalyzer running: {self.tier} tier"
