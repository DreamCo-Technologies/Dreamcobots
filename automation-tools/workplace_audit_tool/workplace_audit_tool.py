# GLOBAL AI SOURCES FLOW
"""Workplace Audit Tool - 5S methodology audit system."""
import sys
import os
import importlib.util
_TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_TOOL_DIR, '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
# Load local tiers.py by path to avoid sys.modules conflicts with other tiers modules
_tiers_spec = importlib.util.spec_from_file_location('_local_tiers', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS


class WorkplaceAuditTool:
    """5S Workplace Audit Tool: Sort, Set in Order, Shine, Standardize, Sustain."""

    PILLARS = ["sort", "set_in_order", "shine", "standardize", "sustain"]

    def __init__(self, tier: str = "free"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["free"])

    def run_audit(self, category: str, items: list) -> dict:
        """Run a 5S audit for a given category and list of items."""
        scores = {}
        for pillar in self.PILLARS:
            pillar_items = [i for i in items if i.get("pillar") == pillar]
            avg = sum(i.get("score", 0) for i in pillar_items) / len(pillar_items) if pillar_items else 0.0
            scores[pillar] = round(avg, 2)

        total_score = round(sum(scores.values()) / len(self.PILLARS), 2) if scores else 0.0
        return {
            "category": category,
            "scores": scores,
            "total_score": total_score,
            "tier": self.tier,
            "items_audited": len(items),
        }

    def generate_score(self, responses: list) -> float:
        """Generate an overall score (0-100) from a list of response dicts."""
        if not responses:
            return 0.0
        total = sum(r.get("value", 0) for r in responses)
        max_possible = len(responses) * 10
        return round((total / max_possible) * 100, 2) if max_possible else 0.0

    def get_recommendations(self, score: float) -> list:
        """Return improvement recommendations based on score."""
        if score >= 80:
            return [
                "Maintain current standards with regular reviews.",
                "Consider advanced kaizen events for continuous improvement.",
                "Document and share best practices across teams.",
            ]
        elif score >= 60:
            return [
                "Focus on sustain: build habit-forming routines.",
                "Increase frequency of 5S audits.",
                "Provide refresher training on 5S principles.",
            ]
        elif score >= 40:
            return [
                "Address shine pillar: schedule deep-clean days.",
                "Standardize labeling and storage systems.",
                "Hold weekly 5S stand-up meetings.",
            ]
        else:
            return [
                "Start from scratch with a full 5S reset event.",
                "Assign 5S champions in each work zone.",
                "Implement visual management boards immediately.",
                "Schedule daily 5-minute 5S activities.",
            ]
