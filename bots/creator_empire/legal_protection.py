"""
Legal & Protection Layer for CreatorEmpire.

Provides contract analysis, royalty calculation, and red-flag scanning
to protect talent on the DreamCo platform.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from dataclasses import dataclass, field
from typing import Optional
from tiers import Tier


class LegalProtectionError(Exception):
    """Raised when a legal operation fails or is not available on the tier."""


# ---------------------------------------------------------------------------
# Red-flag dictionary
# ---------------------------------------------------------------------------

_RED_FLAG_PATTERNS: list[dict] = [
    {
        "keyword": "in perpetuity",
        "severity": "high",
        "explanation": "Rights assigned 'in perpetuity' never expire. Negotiate a time-limited license instead.",
    },
    {
        "keyword": "irrevocable",
        "severity": "high",
        "explanation": "'Irrevocable' rights cannot be taken back. Seek revocability clauses.",
    },
    {
        "keyword": "sole discretion",
        "severity": "medium",
        "explanation": "'Sole discretion' gives the other party unilateral power. Request mutual agreement language.",
    },
    {
        "keyword": "work for hire",
        "severity": "high",
        "explanation": "'Work for hire' transfers full copyright to the employer. Ensure proper compensation.",
    },
    {
        "keyword": "all rights reserved",
        "severity": "medium",
        "explanation": "Broad rights reservation — clarify which specific rights are being transferred.",
    },
    {
        "keyword": "non-compete",
        "severity": "medium",
        "explanation": "Non-compete clauses limit future career opportunities. Negotiate scope and duration.",
    },
    {
        "keyword": "liquidated damages",
        "severity": "medium",
        "explanation": "Pre-set penalties for breach — verify amounts are reasonable.",
    },
    {
        "keyword": "indemnify",
        "severity": "low",
        "explanation": "Indemnification clauses shift liability. Confirm the scope is limited and reciprocal.",
    },
    {
        "keyword": "waive",
        "severity": "medium",
        "explanation": "Waivers give up rights. Ensure you understand exactly what is being waived.",
    },
    {
        "keyword": "exclusivity",
        "severity": "medium",
        "explanation": "Exclusive deals restrict other partnerships. Negotiate carve-outs for existing deals.",
    },
]


@dataclass
class RedFlag:
    """A potential issue identified in contract text."""
    keyword: str
    severity: str        # "low" | "medium" | "high"
    explanation: str
    context_snippet: str = ""

    def to_dict(self) -> dict:
        return {
            "keyword": self.keyword,
            "severity": self.severity,
            "explanation": self.explanation,
            "context_snippet": self.context_snippet,
        }


@dataclass
class ContractAnalysis:
    """Result of a contract analysis scan."""
    contract_id: str
    red_flags: list[RedFlag] = field(default_factory=list)
    overall_risk: str = "low"   # "low" | "medium" | "high"
    recommendations: list[str] = field(default_factory=list)
    word_count: int = 0

    def to_dict(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "red_flags": [rf.to_dict() for rf in self.red_flags],
            "overall_risk": self.overall_risk,
            "recommendations": self.recommendations,
            "word_count": self.word_count,
            "flag_count": len(self.red_flags),
        }


# ---------------------------------------------------------------------------
# Royalty calculator helpers
# ---------------------------------------------------------------------------

_STREAMING_RATES: dict[str, float] = {
    "spotify": 0.004,         # USD per stream
    "apple_music": 0.01,
    "tidal": 0.0125,
    "amazon_music": 0.004,
    "youtube_music": 0.002,
    "deezer": 0.006,
    "soundcloud": 0.0025,
}


class LegalProtectionLayer:
    """
    Analyzes contracts for red flags and calculates royalty earnings.

    Parameters
    ----------
    tier : Tier
        PRO and ENTERPRISE tiers are required for full contract analysis
        and royalty calculation features.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._analyses: dict[str, ContractAnalysis] = {}

    # ------------------------------------------------------------------
    # Contract analysis
    # ------------------------------------------------------------------

    def analyze_contract(self, contract_id: str, contract_text: str) -> ContractAnalysis:
        """
        Scan contract text for red flags and return an analysis report.

        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise LegalProtectionError(
                "Contract analysis requires the Pro tier or higher."
            )

        text_lower = contract_text.lower()
        flags: list[RedFlag] = []

        for pattern in _RED_FLAG_PATTERNS:
            kw = pattern["keyword"]
            if kw in text_lower:
                idx = text_lower.find(kw)
                snippet_start = max(0, idx - 40)
                snippet_end = min(len(contract_text), idx + len(kw) + 40)
                snippet = "..." + contract_text[snippet_start:snippet_end] + "..."
                flags.append(RedFlag(
                    keyword=kw,
                    severity=pattern["severity"],
                    explanation=pattern["explanation"],
                    context_snippet=snippet,
                ))

        risk = self._compute_risk(flags)
        recommendations = self._build_recommendations(flags, risk)

        analysis = ContractAnalysis(
            contract_id=contract_id,
            red_flags=flags,
            overall_risk=risk,
            recommendations=recommendations,
            word_count=len(contract_text.split()),
        )
        self._analyses[contract_id] = analysis
        return analysis

    def get_analysis(self, contract_id: str) -> dict:
        """Return a previously computed analysis."""
        if contract_id not in self._analyses:
            raise LegalProtectionError(f"No analysis found for contract '{contract_id}'.")
        return self._analyses[contract_id].to_dict()

    def scan_for_red_flags(self, text: str) -> list[dict]:
        """
        Quick red-flag scan without saving the result.

        Available on all tiers (simplified version without full analysis).
        Returns a list of flag dicts.
        """
        text_lower = text.lower()
        results = []
        for pattern in _RED_FLAG_PATTERNS:
            if pattern["keyword"] in text_lower:
                results.append({
                    "keyword": pattern["keyword"],
                    "severity": pattern["severity"],
                    "explanation": pattern["explanation"],
                })
        return results

    # ------------------------------------------------------------------
    # Royalty calculator
    # ------------------------------------------------------------------

    def calculate_streaming_royalties(
        self,
        streams: dict[str, int],
        artist_share_pct: float = 100.0,
    ) -> dict:
        """
        Calculate streaming royalties given stream counts per platform.

        Parameters
        ----------
        streams : dict[str, int]
            Mapping of platform name (lowercase) to stream count.
        artist_share_pct : float
            Percentage of gross royalties going to the artist (default 100%).

        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise LegalProtectionError(
                "Royalty calculation requires the Pro tier or higher."
            )

        breakdown: dict[str, dict] = {}
        total_gross = 0.0
        for platform, count in streams.items():
            rate = _STREAMING_RATES.get(platform.lower(), 0.003)
            gross = round(count * rate, 4)
            total_gross += gross
            breakdown[platform] = {
                "streams": count,
                "rate_per_stream": rate,
                "gross_earnings": gross,
            }

        total_gross = round(total_gross, 4)
        artist_net = round(total_gross * artist_share_pct / 100, 4)

        return {
            "breakdown": breakdown,
            "total_gross_usd": total_gross,
            "artist_share_pct": artist_share_pct,
            "artist_net_usd": artist_net,
        }

    def estimate_nil_value(
        self,
        follower_count: int,
        engagement_rate_pct: float,
        sport: str = "general",
    ) -> dict:
        """
        Estimate NIL deal value based on social media metrics.

        Requires ENTERPRISE tier.
        """
        if self.tier != Tier.ENTERPRISE:
            raise LegalProtectionError(
                "NIL value estimation requires the Enterprise tier."
            )
        # Simplified CPM-based model
        cpm_rates = {
            "basketball": 8.0,
            "football": 7.5,
            "soccer": 6.0,
            "general": 5.0,
        }
        cpm = cpm_rates.get(sport.lower(), cpm_rates["general"])
        estimated_impressions = follower_count * (engagement_rate_pct / 100)
        estimated_value = round((estimated_impressions / 1000) * cpm, 2)
        return {
            "follower_count": follower_count,
            "engagement_rate_pct": engagement_rate_pct,
            "sport": sport,
            "estimated_impressions_per_post": int(estimated_impressions),
            "cpm_usd": cpm,
            "estimated_nil_value_per_post_usd": estimated_value,
        }

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        return {
            "tier": self.tier.value,
            "contracts_analyzed": len(self._analyses),
            "supported_platforms_for_royalties": list(_STREAMING_RATES.keys()),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_risk(self, flags: list[RedFlag]) -> str:
        high_count = sum(1 for f in flags if f.severity == "high")
        medium_count = sum(1 for f in flags if f.severity == "medium")
        if high_count >= 2 or (high_count >= 1 and medium_count >= 2):
            return "high"
        if high_count == 1 or medium_count >= 2:
            return "medium"
        return "low"

    def _build_recommendations(self, flags: list[RedFlag], risk: str) -> list[str]:
        recs = []
        if risk == "high":
            recs.append("Consult a qualified entertainment attorney before signing.")
        if any(f.keyword == "in perpetuity" for f in flags):
            recs.append("Negotiate a 5–7 year license term instead of perpetual rights.")
        if any(f.keyword == "work for hire" for f in flags):
            recs.append("Ensure a flat-fee buyout or royalty share is clearly documented.")
        if any(f.keyword == "non-compete" for f in flags):
            recs.append("Limit non-compete scope to direct competitors only.")
        if not flags:
            recs.append("No major red flags detected. Standard legal review recommended.")
        return recs
