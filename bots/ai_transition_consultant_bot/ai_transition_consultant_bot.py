"""
AI Transition Consultant Bot — Main Entry Point

An AI-powered business transformation and AI adoption consultant for the DreamCobots ecosystem.

Core capabilities:
  • Business Assessment       — Evaluate AI readiness with a scored maturity framework (FREE+)
  • Solution Recommendations  — Tailored AI solution roadmaps based on assessment results (PRO+)
  • Training Module Creation  — Auto-generated workforce training content (PRO+)
  • Workflow Integration Plan — Step-by-step AI integration blueprint for existing workflows (ENTERPRISE)

Tier limits:
  - FREE:       3 consultations/month, basic AI readiness assessment.
  - PRO:        30 consultations/month, full assessment, recommendations, training modules.
  - ENTERPRISE: Unlimited, workflow integration, dedicated support, white-label.

Usage
-----
    from bots.ai_transition_consultant_bot import AITransitionConsultantBot, Tier
    bot = AITransitionConsultantBot(tier=Tier.PRO)
    assessment = bot.assess_business({"company_name": "Acme Corp", "industry": "Manufacturing"})
    recs = bot.recommend_solutions(assessment["assessment_id"])
    print(bot.get_consultation_dashboard())
"""

from __future__ import annotations

import sys
import os
import uuid
import random
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from bots.ai_transition_consultant_bot.tiers import (
    BOT_FEATURES,
    get_bot_tier_info,
    MONTHLY_LIMITS,
    DAILY_LIMITS,
    FEATURE_BASIC_ASSESSMENT,
    FEATURE_FULL_ASSESSMENT,
    FEATURE_SOLUTION_RECOMMENDATIONS,
    FEATURE_TRAINING_MODULES,
    FEATURE_WORKFLOW_INTEGRATION,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401

_MATURITY_LEVELS = ["Initial", "Developing", "Defined", "Managed", "Optimizing"]
_INDUSTRIES = ["Manufacturing", "Finance", "Healthcare", "Retail", "Technology", "Logistics", "Education"]


class AITransitionConsultantBotError(Exception):
    """Raised when a monthly limit or feature restriction is violated."""


class AITransitionConsultantBot:
    """AI-powered business AI transition consultant with tier-based feature gating.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling monthly limits and feature access.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self.tier_info = get_bot_tier_info(tier)
        self.flow = GlobalAISourcesFlow(bot_name="AITransitionConsultantBot")
        self._monthly_count: int = 0
        self._assessments: dict[str, dict] = {}

    def _check_monthly_limit(self) -> None:
        """Raise AITransitionConsultantBotError if the monthly consultation limit is exceeded."""
        limit = MONTHLY_LIMITS[self.tier.value]
        if limit is not None and self._monthly_count >= limit:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo) for more."
                if upgrade else ""
            )
            raise AITransitionConsultantBotError(
                f"Monthly limit of {limit} consultations reached for the "
                f"{self.tier.value.upper()} tier.{upgrade_msg}"
            )

    def _check_feature(self, feature: str) -> None:
        """Raise AITransitionConsultantBotError if the feature is not available on the current tier."""
        if feature not in BOT_FEATURES[self.tier.value]:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} for access." if upgrade else ""
            )
            raise AITransitionConsultantBotError(
                f"Feature '{feature}' is not available on the {self.tier.value.upper()} tier.{upgrade_msg}"
            )

    def _record(self) -> None:
        self._monthly_count += 1

    def assess_business(self, business_profile: dict) -> dict:
        """Assess a business's AI readiness and return a scored maturity report.

        Parameters
        ----------
        business_profile : dict
            Business data including company_name, industry, employee_count, etc.
        """
        self._check_feature(FEATURE_BASIC_ASSESSMENT)
        self._check_monthly_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "assess_business", "profile": business_profile},
            learning_method="supervised",
        )
        assessment_id = f"asmnt_{uuid.uuid4().hex[:10]}"
        score = random.randint(25, 85) if self.tier == Tier.FREE else random.randint(30, 95)
        maturity = _MATURITY_LEVELS[min(score // 20, 4)]
        assessment = {
            "assessment_id": assessment_id,
            "company_name": business_profile.get("company_name", "Unknown Company"),
            "industry": business_profile.get("industry", random.choice(_INDUSTRIES)),
            "ai_readiness_score": score,
            "maturity_level": maturity,
            "strengths": [
                "Existing data infrastructure capable of supporting AI workloads",
                "Leadership buy-in for digital transformation initiatives",
                "Skilled technical workforce with growth mindset",
            ],
            "gaps": [
                "Limited labeled training data for supervised learning pipelines",
                "No formal AI governance or ethics framework",
                "Integration complexity with legacy ERP systems",
            ],
            "priority_areas": [
                {"area": "Data Quality & Governance", "urgency": "High", "effort": "Medium"},
                {"area": "AI Literacy Training", "urgency": "High", "effort": "Low"},
                {"area": "Pilot Use Case Selection", "urgency": "Medium", "effort": "Low"},
            ],
            "assessed_at": datetime.utcnow().isoformat() + "Z",
            "tier_depth": "full" if FEATURE_FULL_ASSESSMENT in BOT_FEATURES[self.tier.value] else "basic",
            "framework_pipeline": result.get("bot_name"),
        }
        self._assessments[assessment_id] = assessment
        self._record()
        return assessment

    def recommend_solutions(self, assessment_id: str) -> dict:
        """Generate AI solution recommendations based on a prior assessment (PRO+).

        Parameters
        ----------
        assessment_id : str
            The ID returned from ``assess_business``.
        """
        self._check_feature(FEATURE_SOLUTION_RECOMMENDATIONS)
        self._check_monthly_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "recommend_solutions", "assessment_id": assessment_id},
            learning_method="supervised",
        )
        self._record()
        return {
            "assessment_id": assessment_id,
            "recommendations": [
                {
                    "solution": "Predictive Maintenance AI",
                    "priority": "High",
                    "estimated_roi": "320%",
                    "implementation_weeks": 12,
                    "vendor_options": ["Azure ML", "AWS SageMaker", "Google Vertex AI"],
                },
                {
                    "solution": "Intelligent Document Processing",
                    "priority": "High",
                    "estimated_roi": "185%",
                    "implementation_weeks": 8,
                    "vendor_options": ["Microsoft Form Recognizer", "AWS Textract", "Google DocAI"],
                },
                {
                    "solution": "AI-Powered Customer Segmentation",
                    "priority": "Medium",
                    "estimated_roi": "140%",
                    "implementation_weeks": 6,
                    "vendor_options": ["Salesforce Einstein", "HubSpot AI", "Custom ML"],
                },
                {
                    "solution": "Conversational AI & Chatbot",
                    "priority": "Medium",
                    "estimated_roi": "210%",
                    "implementation_weeks": 4,
                    "vendor_options": ["OpenAI GPT-4", "Anthropic Claude", "Google Gemini"],
                },
            ],
            "total_estimated_investment_usd": random.randint(50000, 250000),
            "payback_period_months": random.randint(8, 18),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def create_training_module(self, topic: str, audience: str) -> dict:
        """Generate a structured AI training module for workforce upskilling (PRO+).

        Parameters
        ----------
        topic : str
            Training topic (e.g. 'Machine Learning Fundamentals').
        audience : str
            Target audience (e.g. 'Non-technical managers', 'Data analysts').
        """
        self._check_feature(FEATURE_TRAINING_MODULES)
        self._check_monthly_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "create_training_module", "topic": topic, "audience": audience},
            learning_method="supervised",
        )
        module_id = f"mod_{uuid.uuid4().hex[:10]}"
        self._record()
        return {
            "module_id": module_id,
            "topic": topic,
            "audience": audience,
            "sections": [
                {"title": f"Introduction to {topic}", "duration_min": 15, "format": "video+quiz"},
                {"title": "Core Concepts & Terminology", "duration_min": 20, "format": "interactive"},
                {"title": "Real-World Applications", "duration_min": 25, "format": "case_study"},
                {"title": "Hands-On Exercise", "duration_min": 30, "format": "lab"},
                {"title": "Assessment & Certification", "duration_min": 20, "format": "quiz"},
            ],
            "estimated_duration_min": 110,
            "learning_objectives": [
                f"Understand foundational concepts of {topic}",
                f"Identify practical applications of {topic} relevant to {audience}",
                f"Apply {topic} principles in simulated business scenarios",
                "Pass competency assessment with ≥80% score",
            ],
            "difficulty_level": "Intermediate",
            "prerequisites": ["Basic computer literacy", "Familiarity with business processes"],
            "created_at": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def plan_workflow_integration(self, workflow: dict) -> dict:
        """Create a detailed AI integration plan for an existing business workflow (ENTERPRISE only).

        Parameters
        ----------
        workflow : dict
            Workflow description including name, steps, tools, and pain points.
        """
        self._check_feature(FEATURE_WORKFLOW_INTEGRATION)
        self._check_monthly_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "plan_workflow_integration", "workflow": workflow},
            learning_method="self_supervised",
        )
        workflow_name = workflow.get("name", "Business Workflow")
        self._record()
        return {
            "workflow_name": workflow_name,
            "ai_touchpoints": [
                {
                    "step": "Data Intake & Validation",
                    "ai_capability": "Intelligent Document Processing",
                    "expected_time_saving_pct": 65,
                },
                {
                    "step": "Decision Support",
                    "ai_capability": "Predictive Analytics Dashboard",
                    "expected_time_saving_pct": 40,
                },
                {
                    "step": "Exception Handling",
                    "ai_capability": "Anomaly Detection & Auto-routing",
                    "expected_time_saving_pct": 55,
                },
            ],
            "automation_opportunities": [
                {"task": "Manual data entry", "automation_potential": "Full", "priority": "High"},
                {"task": "Status reporting", "automation_potential": "Full", "priority": "Medium"},
                {"task": "Compliance checks", "automation_potential": "Partial", "priority": "High"},
                {"task": "Customer notifications", "automation_potential": "Full", "priority": "Low"},
            ],
            "integration_timeline_weeks": random.randint(8, 20),
            "estimated_efficiency_gain_pct": random.randint(35, 70),
            "change_management_notes": [
                "Stakeholder alignment workshops recommended in week 1-2",
                "Parallel run period of 4 weeks before full cutover",
                "Dedicated hypercare support for 30 days post-launch",
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def get_consultation_dashboard(self) -> dict:
        """Return dashboard with monthly usage stats and tier information."""
        limit = MONTHLY_LIMITS[self.tier.value]
        upgrade = get_upgrade_path(self.tier)
        return {
            "bot_name": "AITransitionConsultantBot",
            "tier": self.tier.value,
            "tier_display": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "monthly_limit": limit,
            "monthly_count": self._monthly_count,
            "remaining": (limit - self._monthly_count) if limit is not None else "unlimited",
            "assessments_stored": len(self._assessments),
            "features": BOT_FEATURES[self.tier.value],
            "commercial_rights": self.tier_info["commercial_rights"],
            "upgrade_available": upgrade is not None,
            "upgrade_to": upgrade.name if upgrade else None,
            "upgrade_price_usd": upgrade.price_usd_monthly if upgrade else None,
        }
