"""Hustle Bot - Revenue goal tracking and task optimization."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from datetime import datetime
from core.base_bot import BaseBot


class HustleBot(BaseBot):
    """AI bot for setting revenue goals, tracking progress, and optimizing hustle."""

    def __init__(self):
        """Initialize the HustleBot."""
        super().__init__(
            name="hustle-bot",
            description="Tracks revenue goals, suggests income-generating tasks, and optimizes revenue streams.",
            version="2.0.0",
        )
        self.priority = "high"
        self._goals = []
        self._milestones = []
        self._tasks_completed = []
        self.session_revenue = 0.0

    def run(self):
        """Run the hustle bot main workflow."""
        self.start()
        summary = self.generate_daily_summary()
        return summary

    def set_goal(self, goal: str, target_revenue: float) -> dict:
        """Set a new revenue goal with a target amount."""
        goal_entry = {
            "id": len(self._goals) + 1,
            "goal": goal,
            "target_revenue": target_revenue,
            "current_revenue": self.revenue,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
        }
        self._goals.append(goal_entry)
        self.log(f"Goal set: {goal} (target: ${target_revenue:.2f})")
        return goal_entry

    def track_progress(self) -> dict:
        """Return progress toward all active goals."""
        progress = []
        for goal in self._goals:
            if goal["status"] == "active":
                pct = (self.revenue / goal["target_revenue"] * 100) if goal["target_revenue"] > 0 else 0
                progress.append({
                    "goal": goal["goal"],
                    "target": goal["target_revenue"],
                    "current": self.revenue,
                    "percent_complete": round(min(pct, 100), 1),
                    "remaining": max(0, goal["target_revenue"] - self.revenue),
                    "on_track": pct >= 50,
                })
        return {
            "total_goals": len(self._goals),
            "active_goals": len(progress),
            "total_revenue": self.revenue,
            "progress": progress,
        }

    def suggest_tasks(self) -> list:
        """Return a list of high-impact revenue-generating tasks."""
        return [
            {
                "task": "Apply for 3 new government contracts via SAM.gov",
                "estimated_value": "$5,000 - $50,000",
                "time_required": "2 hours",
                "difficulty": "medium",
                "priority": "high",
            },
            {
                "task": "Create and launch a digital product (eBook, template, course)",
                "estimated_value": "$500 - $5,000/month",
                "time_required": "8 hours",
                "difficulty": "medium",
                "priority": "high",
            },
            {
                "task": "Reach out to 10 potential clients via LinkedIn",
                "estimated_value": "$1,000 - $10,000",
                "time_required": "1 hour",
                "difficulty": "easy",
                "priority": "high",
            },
            {
                "task": "Set up affiliate marketing on your website",
                "estimated_value": "$200 - $2,000/month passive",
                "time_required": "3 hours",
                "difficulty": "easy",
                "priority": "medium",
            },
            {
                "task": "Launch a referral program with 50% commission",
                "estimated_value": "Variable",
                "time_required": "2 hours",
                "difficulty": "easy",
                "priority": "medium",
            },
            {
                "task": "List services on Upwork, Fiverr, and Toptal",
                "estimated_value": "$50 - $500/project",
                "time_required": "1 hour",
                "difficulty": "easy",
                "priority": "medium",
            },
            {
                "task": "Run a limited-time flash sale (24-48 hours)",
                "estimated_value": "30-50% revenue boost",
                "time_required": "30 minutes",
                "difficulty": "easy",
                "priority": "medium",
            },
        ]

    def log_milestone(self, milestone: str) -> dict:
        """Log an achievement milestone."""
        entry = {
            "id": len(self._milestones) + 1,
            "milestone": milestone,
            "revenue_at_milestone": self.revenue,
            "logged_at": datetime.utcnow().isoformat(),
        }
        self._milestones.append(entry)
        self.log(f"Milestone logged: {milestone}")
        return entry

    def generate_daily_summary(self) -> dict:
        """Generate a daily revenue and task performance summary."""
        tasks = self.suggest_tasks()
        return {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "total_revenue": self.revenue,
            "session_revenue": self.session_revenue,
            "milestones_logged": len(self._milestones),
            "active_goals": sum(1 for g in self._goals if g["status"] == "active"),
            "recommended_tasks_today": tasks[:3],
            "motivational_message": "Every action you take today compounds into tomorrow's success.",
            "revenue_streams_active": 3,
        }

    def optimize_revenue_streams(self) -> dict:
        """Return optimization suggestions for increasing revenue."""
        return {
            "current_streams": ["freelancing", "digital products", "affiliate"],
            "optimization_tips": [
                {
                    "stream": "Freelancing",
                    "tip": "Raise your rate by 20% - most clients expect periodic increases",
                    "potential_increase": "20%",
                },
                {
                    "stream": "Digital Products",
                    "tip": "Create a bundle of your top 3 products at 70% of individual price",
                    "potential_increase": "35%",
                },
                {
                    "stream": "Affiliate Marketing",
                    "tip": "Focus on high-ticket affiliates ($100+ commissions) over volume",
                    "potential_increase": "300%",
                },
                {
                    "stream": "New Stream",
                    "tip": "Add a subscription/retainer model for predictable MRR",
                    "potential_increase": "New income",
                },
            ],
            "90_day_projection": self.revenue * 3.5,
        }
