"""
Feature 2: Business Project Management Bot
Functionality: Helps track project progress, deadlines, team assignments,
  and milestone completion. Includes Gantt-style timeline and priority scoring.
Use Cases: Managers overseeing multiple projects and distributed teams.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example project records
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "name": "Website Redesign",         "owner": "Alice",   "team": ["Dev1","Design1"],   "deadline": "2025-06-01", "progress_pct": 65, "priority": "high",   "status": "in_progress", "budget_usd": 15000, "tags": ["design","web"]},
    {"id": 2,  "name": "Mobile App Launch",         "owner": "Bob",     "team": ["Dev2","Dev3","QA1"],"deadline": "2025-07-15", "progress_pct": 40, "priority": "critical","status": "in_progress", "budget_usd": 50000, "tags": ["mobile","product"]},
    {"id": 3,  "name": "Q2 Marketing Campaign",     "owner": "Carol",   "team": ["Mkt1","Content1"],  "deadline": "2025-05-31", "progress_pct": 80, "priority": "high",   "status": "in_progress", "budget_usd": 8000,  "tags": ["marketing"]},
    {"id": 4,  "name": "API Integration v2",        "owner": "Dave",    "team": ["Dev4","Arch1"],     "deadline": "2025-06-15", "progress_pct": 50, "priority": "medium", "status": "in_progress", "budget_usd": 12000, "tags": ["backend","api"]},
    {"id": 5,  "name": "Customer Onboarding Flow",  "owner": "Emma",    "team": ["CS1","Dev5"],       "deadline": "2025-05-20", "progress_pct": 90, "priority": "high",   "status": "review",      "budget_usd": 5000,  "tags": ["ux","onboarding"]},
    {"id": 6,  "name": "Security Audit",            "owner": "Frank",   "team": ["Security1","IT1"],  "deadline": "2025-05-25", "progress_pct": 75, "priority": "critical","status": "in_progress", "budget_usd": 20000, "tags": ["security"]},
    {"id": 7,  "name": "Data Warehouse Migration",  "owner": "Grace",   "team": ["Data1","Dev6"],     "deadline": "2025-08-01", "progress_pct": 20, "priority": "medium", "status": "in_progress", "budget_usd": 35000, "tags": ["data","infrastructure"]},
    {"id": 8,  "name": "Sales CRM Implementation",  "owner": "Henry",   "team": ["Sales1","Dev7"],    "deadline": "2025-06-30", "progress_pct": 35, "priority": "high",   "status": "in_progress", "budget_usd": 18000, "tags": ["sales","crm"]},
    {"id": 9,  "name": "HR Policy Update 2025",     "owner": "Isabella","team": ["HR1","Legal1"],     "deadline": "2025-05-15", "progress_pct": 100,"priority": "medium", "status": "completed",   "budget_usd": 3000,  "tags": ["hr","compliance"]},
    {"id": 10, "name": "Brand Identity Refresh",    "owner": "Jack",    "team": ["Design2","Mkt2"],   "deadline": "2025-06-10", "progress_pct": 55, "priority": "medium", "status": "in_progress", "budget_usd": 10000, "tags": ["brand","design"]},
    {"id": 11, "name": "AI Chatbot Integration",    "owner": "Karen",   "team": ["Dev8","AI1"],       "deadline": "2025-07-01", "progress_pct": 30, "priority": "high",   "status": "in_progress", "budget_usd": 25000, "tags": ["ai","product"]},
    {"id": 12, "name": "Partner Portal Development","owner": "Leo",     "team": ["Dev9","PM1"],       "deadline": "2025-08-15", "progress_pct": 15, "priority": "low",    "status": "in_progress", "budget_usd": 22000, "tags": ["partnerships","web"]},
    {"id": 13, "name": "Q3 OKR Planning",           "owner": "Mary",    "team": ["CEO","Leadership1"],"deadline": "2025-06-05", "progress_pct": 60, "priority": "high",   "status": "review",      "budget_usd": 0,     "tags": ["strategy"]},
    {"id": 14, "name": "Content Library Expansion", "owner": "Nick",    "team": ["Content2","SEO1"],  "deadline": "2025-06-20", "progress_pct": 45, "priority": "medium", "status": "in_progress", "budget_usd": 6000,  "tags": ["content","seo"]},
    {"id": 15, "name": "DevOps Pipeline Upgrade",   "owner": "Olivia",  "team": ["DevOps1","Dev10"],  "deadline": "2025-07-10", "progress_pct": 25, "priority": "high",   "status": "in_progress", "budget_usd": 15000, "tags": ["devops","infrastructure"]},
    {"id": 16, "name": "Annual Report 2024",        "owner": "Paul",    "team": ["Finance1","Design3"],"deadline": "2025-05-10","progress_pct": 100,"priority": "high",   "status": "completed",   "budget_usd": 4000,  "tags": ["finance","reporting"]},
    {"id": 17, "name": "Product Pricing Overhaul",  "owner": "Quinn",   "team": ["PM2","Finance2"],   "deadline": "2025-06-01", "progress_pct": 70, "priority": "critical","status": "review",      "budget_usd": 0,     "tags": ["product","strategy"]},
    {"id": 18, "name": "Global Expansion — EU",     "owner": "Rachel",  "team": ["BizDev1","Legal2"], "deadline": "2025-09-01", "progress_pct": 10, "priority": "medium", "status": "planned",     "budget_usd": 100000,"tags": ["expansion","international"]},
    {"id": 19, "name": "Customer Support Overhaul", "owner": "Sam",     "team": ["CS2","Dev11"],      "deadline": "2025-06-25", "progress_pct": 50, "priority": "high",   "status": "in_progress", "budget_usd": 12000, "tags": ["support","ux"]},
    {"id": 20, "name": "Affiliate Program Launch",  "owner": "Tina",    "team": ["Mkt3","Dev12"],     "deadline": "2025-07-20", "progress_pct": 40, "priority": "medium", "status": "in_progress", "budget_usd": 8000,  "tags": ["marketing","partnerships"]},
    {"id": 21, "name": "Employee Training Program", "owner": "Uma",     "team": ["HR2","Training1"],  "deadline": "2025-06-15", "progress_pct": 65, "priority": "medium", "status": "in_progress", "budget_usd": 7000,  "tags": ["hr","training"]},
    {"id": 22, "name": "Infrastructure Cost Audit", "owner": "Victor",  "team": ["IT2","Finance3"],   "deadline": "2025-05-30", "progress_pct": 85, "priority": "high",   "status": "review",      "budget_usd": 0,     "tags": ["infrastructure","finance"]},
    {"id": 23, "name": "Social Media Strategy 2025","owner": "Wendy",   "team": ["Mkt4","Content3"],  "deadline": "2025-05-20", "progress_pct": 100,"priority": "medium", "status": "completed",   "budget_usd": 5000,  "tags": ["marketing","social"]},
    {"id": 24, "name": "Accessibility Compliance",  "owner": "Xander",  "team": ["Dev13","Design4"],  "deadline": "2025-07-01", "progress_pct": 20, "priority": "high",   "status": "in_progress", "budget_usd": 9000,  "tags": ["compliance","ux"]},
    {"id": 25, "name": "B2B Lead Generation System","owner": "Yara",    "team": ["Sales2","Dev14"],   "deadline": "2025-06-30", "progress_pct": 55, "priority": "critical","status": "in_progress", "budget_usd": 20000, "tags": ["sales","automation"]},
    {"id": 26, "name": "Newsletter Redesign",        "owner": "Zach",    "team": ["Design5","Content4"],"deadline": "2025-05-25","progress_pct": 75, "priority": "low",    "status": "review",      "budget_usd": 3000,  "tags": ["email","design"]},
    {"id": 27, "name": "Payment Gateway Switch",     "owner": "Amy",     "team": ["Dev15","Finance4"], "deadline": "2025-06-10", "progress_pct": 45, "priority": "critical","status": "in_progress", "budget_usd": 8000,  "tags": ["payments","backend"]},
    {"id": 28, "name": "AI Model Fine-tuning",       "owner": "Brian",   "team": ["AI2","Data2"],      "deadline": "2025-08-01", "progress_pct": 15, "priority": "medium", "status": "in_progress", "budget_usd": 40000, "tags": ["ai","ml"]},
    {"id": 29, "name": "Customer Portal v2",         "owner": "Cindy",   "team": ["Dev16","UX1"],      "deadline": "2025-07-15", "progress_pct": 30, "priority": "high",   "status": "in_progress", "budget_usd": 18000, "tags": ["product","ux"]},
    {"id": 30, "name": "Carbon Offset Initiative",   "owner": "Derek",   "team": ["ESG1","Ops1"],      "deadline": "2025-12-31", "progress_pct": 5,  "priority": "low",    "status": "planned",     "budget_usd": 15000, "tags": ["esg","operations"]},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_projects": 3,    "gantt": False, "budget_tracking": False, "ai_priority": False},
    "PRO":        {"price_usd": 29,  "max_projects": 25,   "gantt": True,  "budget_tracking": True,  "ai_priority": False},
    "ENTERPRISE": {"price_usd": 99,  "max_projects": None, "gantt": True,  "budget_tracking": True,  "ai_priority": True},
}


class ProjectManagementBot:
    """Tracks and manages projects — deadlines, budgets, progress, and priorities.

    Competes with Asana and Monday.com by integrating AI-powered priority scoring
    and budget burn-rate alerts directly into the bot workflow.
    Monetization: $29/month PRO or $99/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="ProjectManagementBot")

    def _available_projects(self) -> list[dict]:
        limit = self._config["max_projects"]
        return EXAMPLES[:limit] if limit else EXAMPLES

    def get_projects_by_status(self, status: str) -> list[dict]:
        """Return projects with a specific status."""
        valid = {"in_progress", "completed", "planned", "review"}
        if status not in valid:
            raise ValueError(f"Invalid status. Choose from {valid}")
        return [p for p in self._available_projects() if p["status"] == status]

    def get_projects_by_priority(self, priority: str) -> list[dict]:
        """Return projects filtered by priority: critical, high, medium, low."""
        valid = {"critical", "high", "medium", "low"}
        if priority not in valid:
            raise ValueError(f"Invalid priority. Choose from {valid}")
        return [p for p in self._available_projects() if p["priority"] == priority]

    def get_at_risk_projects(self, threshold_pct: int = 50) -> list[dict]:
        """Return in-progress projects with progress below the threshold."""
        return [
            p for p in self._available_projects()
            if p["status"] == "in_progress" and p["progress_pct"] < threshold_pct
        ]

    def get_overdue_projects(self, today: str = "2025-05-14") -> list[dict]:
        """Return projects whose deadline has passed and progress < 100%."""
        return [
            p for p in self._available_projects()
            if p["deadline"] < today and p["progress_pct"] < 100
        ]

    def get_budget_summary(self) -> dict:
        """Return total and per-project budget allocation (PRO/ENTERPRISE)."""
        if not self._config["budget_tracking"]:
            raise PermissionError(
                "Budget tracking requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        projects = self._available_projects()
        total = sum(p["budget_usd"] for p in projects)
        spent_estimate = sum(
            round(p["budget_usd"] * p["progress_pct"] / 100) for p in projects
        )
        return {
            "total_budget_usd": total,
            "estimated_spent_usd": spent_estimate,
            "estimated_remaining_usd": total - spent_estimate,
            "projects_over_50pct_budget": [
                p["name"] for p in projects if p["progress_pct"] > 50 and p["budget_usd"] > 0
            ],
        }

    def get_ai_priority_score(self, project_id: int) -> dict:
        """Return an AI-generated priority score for a project (ENTERPRISE)."""
        if not self._config["ai_priority"]:
            raise PermissionError(
                "AI priority scoring requires ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        project = next((p for p in EXAMPLES if p["id"] == project_id), None)
        if project is None:
            raise ValueError(f"Project ID {project_id} not found.")
        priority_map = {"critical": 40, "high": 30, "medium": 20, "low": 10}
        urgency = 100 - project["progress_pct"]
        base_score = priority_map.get(project["priority"], 10)
        score = min(100, base_score + urgency // 3)
        return {
            "project_id": project_id,
            "name": project["name"],
            "ai_score": score,
            "recommendation": "Focus immediately" if score >= 70 else "On track" if score >= 40 else "Low priority",
        }

    def get_dashboard(self) -> dict:
        """Return a full project dashboard summary."""
        projects = self._available_projects()
        completed = [p for p in projects if p["status"] == "completed"]
        in_progress = [p for p in projects if p["status"] == "in_progress"]
        critical = [p for p in projects if p["priority"] == "critical"]
        avg_progress = round(sum(p["progress_pct"] for p in projects) / len(projects), 1) if projects else 0
        return {
            "total_projects": len(projects),
            "completed": len(completed),
            "in_progress": len(in_progress),
            "critical_priority": len(critical),
            "avg_progress_pct": avg_progress,
            "at_risk": len(self.get_at_risk_projects()),
            "tier": self.tier,
        }

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_projects"] if cfg["max_projects"] else "unlimited"
        lines = [
            f"=== ProjectManagementBot — {self.tier} Tier ===",
            f"  Monthly price   : ${cfg['price_usd']}/month",
            f"  Max projects    : {limit}",
            f"  Gantt timeline  : {'enabled' if cfg['gantt'] else 'disabled'}",
            f"  Budget tracking : {'enabled' if cfg['budget_tracking'] else 'disabled'}",
            f"  AI priority     : {'enabled' if cfg['ai_priority'] else 'disabled (ENTERPRISE)'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "project_management", "projects_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "dashboard": self.get_dashboard()}


if __name__ == "__main__":
    bot = ProjectManagementBot(tier="PRO")
    dashboard = bot.get_dashboard()
    print(f"Projects: {dashboard['total_projects']} total | {dashboard['in_progress']} in progress | {dashboard['completed']} completed")
    print(f"Average progress: {dashboard['avg_progress_pct']}%")
    print(f"At risk: {dashboard['at_risk']} projects")
    critical = bot.get_projects_by_priority("critical")
    print(f"Critical projects: {[p['name'] for p in critical]}")
    print(bot.describe_tier())


CRMBot = ProjectManagementBot


# ---------------------------------------------------------------------------
# Tier system additions for test compatibility
# ---------------------------------------------------------------------------
import random as _random_tier
from enum import Enum as _TierEnum


class Tier(_TierEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


_TIER_MONTHLY_PRICE = {"free": 0, "pro": 29, "enterprise": 99}


class ProjectManagementBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_projectmanagement_bot_init = ProjectManagementBot.__init__


def _projectmanagement_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_projectmanagement_bot_init(self, tier_val.upper())
    self.tier = tier if isinstance(tier, Tier) else Tier(tier_val)


ProjectManagementBot.__init__ = _projectmanagement_bot_new_init
ProjectManagementBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _projectmanagement_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _projectmanagement_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _projectmanagement_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise ProjectManagementBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _projectmanagement_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _projectmanagement_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "ProjectManagementBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _projectmanagement_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "ProjectManagementBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


ProjectManagementBot.monthly_price = _projectmanagement_bot_monthly_price
ProjectManagementBot.get_tier_info = _projectmanagement_bot_get_tier_info
ProjectManagementBot._enforce_tier = _projectmanagement_bot_enforce_tier
ProjectManagementBot.list_items = _projectmanagement_bot_list_items
ProjectManagementBot.analyze = _projectmanagement_bot_analyze
ProjectManagementBot.export_report = _projectmanagement_bot_export_report
