"""
Operational Cost Reduction Engine for DreamOps.

Analyzes cost drivers, identifies waste, and scores
automation opportunities across departments.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from framework import GlobalAISourcesFlow  # noqa: F401

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class CostData:
    dept_id: str
    monthly_spend: float
    categories: Dict[str, float]   # category -> spend amount
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WasteItem:
    item_id: str
    description: str
    estimated_waste_usd: float
    automation_score: float   # 0.0 - 10.0


class CostReductionEngine:
    """Identifies and quantifies operational cost reduction opportunities."""

    def __init__(self) -> None:
        self._cost_data: Dict[str, CostData] = {}
        self._waste_items: Dict[str, List[WasteItem]] = {}
        self._reduction_plans: Dict[str, dict] = {}

    def analyze_costs(self, dept_id: str, cost_data: CostData) -> dict:
        """Store and analyze department cost data."""
        self._cost_data[dept_id] = cost_data
        if not cost_data.categories:
            return {
                "dept_id": dept_id,
                "monthly_spend": cost_data.monthly_spend,
                "top_cost_driver": "N/A",
                "top_driver_spend": 0.0,
                "categories_analyzed": 0,
            }
        top_category = max(cost_data.categories, key=cost_data.categories.get)
        analysis = {
            "dept_id": dept_id,
            "monthly_spend": cost_data.monthly_spend,
            "top_cost_driver": top_category,
            "top_driver_spend": cost_data.categories.get(top_category, 0.0),
            "categories_analyzed": len(cost_data.categories),
        }
        return analysis

    def identify_waste(self, dept_id: str) -> List[WasteItem]:
        """Identify waste items in a department's spending."""
        cost_data = self._cost_data.get(dept_id)
        if not cost_data:
            return []
        items = []
        for category, spend in cost_data.categories.items():
            # Heuristic: categories with >20% of total spend flagged for review
            ratio = spend / max(cost_data.monthly_spend, 1.0)
            if ratio > 0.20:
                waste_estimate = spend * 0.15  # 15% estimated reducible
                items.append(WasteItem(
                    item_id=str(uuid.uuid4()),
                    description=f"High spend in '{category}' ({ratio*100:.1f}% of budget)",
                    estimated_waste_usd=round(waste_estimate, 2),
                    automation_score=round(min(ratio * 20, 10.0), 2),
                ))
        self._waste_items[dept_id] = items
        return items

    def score_automation_opportunity(self, process_id: str, process_config: Optional[dict] = None) -> dict:
        """Score the automation potential of a process."""
        config = process_config or {}
        repetitiveness = config.get("repetitiveness", 0.7)
        rule_based = config.get("rule_based", True)
        volume = config.get("monthly_volume", 100)
        score = repetitiveness * 4.0
        score += 3.0 if rule_based else 1.0
        score += min(volume / 200.0, 3.0)
        score = min(score, 10.0)
        return {
            "process_id": process_id,
            "automation_score": round(score, 2),
            "recommendation": "automate" if score >= 7.0 else ("consider" if score >= 4.0 else "manual"),
            "estimated_hours_saved_monthly": round(volume * 0.1 * score / 10.0, 1),
        }

    def generate_reduction_plan(self, dept_id: str) -> dict:
        """Create a cost reduction action plan for a department."""
        waste_items = self._waste_items.get(dept_id, [])
        total_waste = sum(w.estimated_waste_usd for w in waste_items)
        actions = [
            {
                "action": f"Address: {w.description}",
                "estimated_saving_usd": w.estimated_waste_usd,
                "automation_score": w.automation_score,
            }
            for w in sorted(waste_items, key=lambda x: x.estimated_waste_usd, reverse=True)
        ]
        plan = {
            "dept_id": dept_id,
            "total_identifiable_waste_usd": round(total_waste, 2),
            "actions": actions,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._reduction_plans[dept_id] = plan
        return plan

    def estimate_savings(self) -> dict:
        """Aggregate savings estimates across all departments."""
        total = sum(
            plan["total_identifiable_waste_usd"]
            for plan in self._reduction_plans.values()
        )
        return {
            "total_departments": len(self._reduction_plans),
            "total_estimated_monthly_savings_usd": round(total, 2),
            "total_estimated_annual_savings_usd": round(total * 12, 2),
        }

    def get_cost_summary(self) -> dict:
        """Return a high-level cost summary across all tracked departments."""
        return {
            dept_id: {
                "monthly_spend": data.monthly_spend,
                "categories": len(data.categories),
            }
            for dept_id, data in self._cost_data.items()
        }
