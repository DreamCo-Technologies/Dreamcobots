"""
Decision Engine — replaces random AI decisions with real data-driven logic
based on revenue and leads metrics.

Logic:
  - leads < 20  → "scale_leads"
  - revenue < 200 → "increase_outreach"
  - revenue > 1000 → "scale_system"
  - else → "optimize"

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Decision constants
# ---------------------------------------------------------------------------

DECISION_SCALE_LEADS = "scale_leads"
DECISION_INCREASE_OUTREACH = "increase_outreach"
DECISION_SCALE_SYSTEM = "scale_system"
DECISION_OPTIMIZE = "optimize"
DECISION_CREATE_SCALING_BOT = "create_scaling_bot"
DECISION_CREATE_RECOVERY_BOT = "create_recovery_bot"

# Thresholds
LEADS_THRESHOLD_LOW: int = 20
REVENUE_THRESHOLD_LOW: float = 200.0
REVENUE_THRESHOLD_HIGH: float = 1000.0
REVENUE_THRESHOLD_SCALE: float = 1000.0
REVENUE_THRESHOLD_RECOVERY: float = 100.0

# Backward-compat aliases
LOW_REVENUE_THRESHOLD = REVENUE_THRESHOLD_LOW
HIGH_REVENUE_THRESHOLD = REVENUE_THRESHOLD_HIGH

BOTTLENECK_ERROR_RATE_THRESHOLD: float = 0.10
BOTTLENECK_HIGH_SEVERITY_THRESHOLD: float = 0.25

ACTIONS = [
    {"key": DECISION_SCALE_LEADS,         "label": "Scale Leads",          "description": "Scale lead generation"},
    {"key": DECISION_INCREASE_OUTREACH,   "label": "Increase Outreach",    "description": "Increase outreach campaigns"},
    {"key": DECISION_SCALE_SYSTEM,        "label": "Scale System",         "description": "Scale the overall system"},
    {"key": DECISION_OPTIMIZE,            "label": "Optimize",             "description": "Optimize current operations"},
    {"key": DECISION_CREATE_SCALING_BOT,  "label": "Create Scaling Bot",   "description": "Create a new scaling bot"},
    {"key": DECISION_CREATE_RECOVERY_BOT, "label": "Create Recovery Bot",  "description": "Create a recovery bot"},
    {"key": "fix_bottleneck",             "label": "Fix Bottleneck",       "description": "Fix a workflow bottleneck"},
    {"key": "optimize_sales",             "label": "Optimize Sales",       "description": "Optimize sales funnel"},
    {"key": "focus_real_estate",          "label": "Focus Real Estate",    "description": "Focus on real estate revenue"},
    {"key": "build_new_bot",              "label": "Build New Bot",        "description": "Build a new bot to fill gaps"},
]

_ACTIONS_MAP: Dict[str, Dict[str, str]] = {a["key"]: a for a in ACTIONS}


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class DecisionEngineTierError(Exception):
    """Raised when an action is not permitted on the current tier."""


# ---------------------------------------------------------------------------
# Decision Engine
# ---------------------------------------------------------------------------

class DecisionEngine:
    """
    Real data-driven decision engine for DreamCo bots.

    Replaces random/fake decisions with logic grounded in real revenue
    and lead metrics.
    """

    def __init__(
        self,
        tier: Any = None,
        metrics: Optional[Dict[str, Any]] = None,
        auto_generate_bots: bool = False,
    ) -> None:
        # Import Tier lazily to handle cross-module enum issues
        try:
            import sys as _sys
            import os as _os
            _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), "..", "ai-models-integration"))
            from tiers import Tier as _Tier
        except ImportError:
            _Tier = None

        if tier is None:
            if _Tier is not None:
                self.tier = _Tier.FREE
            else:
                self.tier = None
        else:
            self.tier = tier

        self.config: Dict[str, Any] = {
            "leads_threshold_low": LEADS_THRESHOLD_LOW,
            "revenue_threshold_low": REVENUE_THRESHOLD_LOW,
            "revenue_threshold_high": REVENUE_THRESHOLD_HIGH,
            "bottleneck_threshold": BOTTLENECK_ERROR_RATE_THRESHOLD,
        }
        self.metrics: Dict[str, Any] = metrics or {}
        self._decision_history: List[Dict[str, Any]] = []
        self._auto_generate_bots = auto_generate_bots
        self._flow = GlobalAISourcesFlow(bot_name="DecisionEngine")

    def _tier_value(self) -> str:
        if self.tier is None:
            return "free"
        return getattr(self.tier, "value", str(self.tier)).lower()

    # ------------------------------------------------------------------
    # Analysis helpers
    # ------------------------------------------------------------------

    def analyze_revenue(self, revenue_data: Dict[str, float]) -> Dict[str, Any]:
        """Analyse revenue by source and return signals."""
        if not revenue_data:
            return {
                "total": 0.0,
                "lowest": {"source": None, "value": 0.0},
                "highest": {"source": None, "value": 0.0},
                "signals": [DECISION_SCALE_LEADS],
            }

        total = sum(revenue_data.values())
        sorted_items = sorted(revenue_data.items(), key=lambda x: x[1])
        lowest = {"source": sorted_items[0][0], "value": sorted_items[0][1]}
        highest = {"source": sorted_items[-1][0], "value": sorted_items[-1][1]}

        signals: List[str] = []

        if total < REVENUE_THRESHOLD_LOW:
            signals.append(DECISION_SCALE_LEADS)
        elif total > REVENUE_THRESHOLD_HIGH:
            signals.append("optimize_sales")

        # Sector-specific signals
        re_rev = revenue_data.get("real_estate", 0.0)
        if re_rev > 0 and re_rev < 100.0:
            signals.append("focus_real_estate")

        if not signals:
            signals.append(DECISION_OPTIMIZE)

        return {
            "total": total,
            "lowest": lowest,
            "highest": highest,
            "signals": signals,
        }

    def analyze_crm_trends(self, crm_data: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Analyse CRM conversion data and return signals."""
        if not crm_data:
            return {"top_bot": None, "bottom_bot": None, "signals": []}

        sorted_bots = sorted(crm_data.items(), key=lambda x: x[1].get("conversion_rate", 0.0))
        bottom_bot = sorted_bots[0][0]
        top_bot = sorted_bots[-1][0]

        signals: List[str] = []
        low_rate = sorted_bots[0][1].get("conversion_rate", 0.0)

        if low_rate < 0.05:
            if "lead_gen" in bottom_bot:
                signals.append(DECISION_SCALE_LEADS)
            elif "sales" in bottom_bot:
                signals.append(DECISION_INCREASE_OUTREACH)
            elif "real_estate" in bottom_bot:
                signals.append("focus_real_estate")
            else:
                signals.append(DECISION_INCREASE_OUTREACH)

        return {
            "top_bot": top_bot,
            "bottom_bot": bottom_bot,
            "signals": signals,
        }

    def detect_bottlenecks(self, workflow_data: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """Identify bottleneck steps in the workflow."""
        result = []
        for step, info in workflow_data.items():
            error_rate = info.get("error_rate", 0.0)
            if error_rate >= BOTTLENECK_ERROR_RATE_THRESHOLD:
                severity = "high" if error_rate >= BOTTLENECK_HIGH_SEVERITY_THRESHOLD else "medium"
                result.append({"step": step, "error_rate": error_rate, "severity": severity})
        return result

    def make_decision(
        self,
        revenue_data: Optional[Dict[str, float]] = None,
        crm_data: Optional[Dict[str, Dict[str, float]]] = None,
        workflow_data: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> Dict[str, Any]:
        """Make a data-driven decision and record it in history."""
        revenue_analysis = self.analyze_revenue(revenue_data or self.metrics.get("revenue", {}))
        crm_analysis = self.analyze_crm_trends(crm_data or self.metrics.get("crm", {}))
        bottlenecks = self.detect_bottlenecks(workflow_data or self.metrics.get("workflow", {}))

        scores: Dict[str, float] = {a["key"]: 0.0 for a in ACTIONS}

        # Score based on revenue signals
        for signal in revenue_analysis["signals"]:
            if signal in scores:
                scores[signal] += 10.0

        # Score based on CRM signals
        for signal in crm_analysis["signals"]:
            if signal in scores:
                scores[signal] += 8.0

        # Score bottleneck fix (PRO/ENTERPRISE only)
        tier_val = self._tier_value()
        if bottlenecks and tier_val in ("pro", "enterprise"):
            scores["fix_bottleneck"] += 15.0 + sum(1.0 for b in bottlenecks if b["severity"] == "high")

        # Default scores
        scores[DECISION_OPTIMIZE] = max(scores[DECISION_OPTIMIZE], 1.0)

        all_scores_list = sorted(
            [{"key": k, "score": v, **(_ACTIONS_MAP.get(k) or {"label": k, "description": k})}
             for k, v in scores.items()],
            key=lambda x: x["score"],
            reverse=True,
        )

        top = all_scores_list[0]
        decision = {
            "key": top["key"],
            "label": top.get("label", top["key"]),
            "description": top.get("description", ""),
            "score": top["score"],
            "reason": f"Highest scored action based on current data.",
        }

        result = {
            "decision": decision,
            "all_scores": all_scores_list,
            "revenue_analysis": revenue_analysis,
            "crm_analysis": crm_analysis,
            "bottlenecks": bottlenecks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._decision_history.append(result)
        return result

    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Return decision history (PRO/ENTERPRISE only)."""
        tier_val = self._tier_value()
        if tier_val == "free":
            raise DecisionEngineTierError(
                "Decision history requires PRO or ENTERPRISE tier."
            )
        return list(self._decision_history)

    def decide(self, metrics: Optional[Dict[str, Any]] = None) -> str:
        """Legacy method — return a single decision string."""
        m = metrics or self.metrics
        leads = m.get("leads", 0)
        revenue = m.get("revenue", 0.0)

        if leads < LEADS_THRESHOLD_LOW:
            return DECISION_SCALE_LEADS
        if revenue < REVENUE_THRESHOLD_LOW:
            return DECISION_INCREASE_OUTREACH
        if revenue > REVENUE_THRESHOLD_SCALE:
            return DECISION_SCALE_SYSTEM
        return DECISION_OPTIMIZE

    def run(self, metrics: Optional[Dict[str, Any]] = None) -> str:
        """Run the decision engine and return the decision key string."""
        m = metrics or self.metrics
        revenue = m.get("revenue", 0)
        leads = m.get("leads", 0)
        if isinstance(revenue, (int, float)) and isinstance(leads, (int, float)):
            if leads < LEADS_THRESHOLD_LOW:
                key = DECISION_SCALE_LEADS
            elif revenue < REVENUE_THRESHOLD_LOW:
                key = DECISION_INCREASE_OUTREACH
            elif revenue > REVENUE_THRESHOLD_SCALE:
                if self._auto_generate_bots:
                    key = DECISION_CREATE_SCALING_BOT
                else:
                    key = DECISION_SCALE_SYSTEM
            else:
                key = DECISION_OPTIMIZE
            self._decision_history.append({"decision": key, "revenue": revenue, "leads": leads})
            return f"Decision: {key}"
        result = self.make_decision(
            revenue_data=m.get("revenue", {}),
            crm_data=m.get("crm", {}),
            workflow_data=m.get("workflow", {}),
        )
        key = result["decision"]["key"]
        return f"Decision: {key}"

    def get_latest_decision(self) -> Optional[Dict[str, Any]]:
        """Return the most recent decision log entry, or None if empty."""
        if not self._decision_history:
            return None
        return self._decision_history[-1]

    def get_decision_log(self) -> List[Dict[str, Any]]:
        """Return the full decision log history."""
        return list(self._decision_history)

    def get_decision_summary(self) -> Dict[str, Any]:
        """Return a summary of all decisions made."""
        return {
            "total": len(self._decision_history),
            "decisions": list(self._decision_history),
        }

    def evaluate_for_bot_creation(self, revenue: float) -> Optional[str]:
        """Return the type of bot to create based on revenue."""
        if revenue > REVENUE_THRESHOLD_SCALE:
            return "scaling_bot"
        if revenue < REVENUE_THRESHOLD_RECOVERY:
            return "recovery_bot"
        return None
