"""
Enterprise Scaler — infrastructure scaling advisor for the DreamCo SaaS Packages Bot.

Assesses scale tiers, generates scaling plans, estimates infrastructure costs,
and produces Fortune 500 integration specifications.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Scale tier definitions
# ---------------------------------------------------------------------------

class ScaleTier:
    STARTUP = "STARTUP"
    GROWTH = "GROWTH"
    SCALE = "SCALE"
    ENTERPRISE = "ENTERPRISE"
    FORTUNE500 = "FORTUNE500"


_SCALE_TIERS: list = [
    {"name": ScaleTier.STARTUP,    "min": 1,     "max": 10},
    {"name": ScaleTier.GROWTH,     "min": 11,    "max": 100},
    {"name": ScaleTier.SCALE,      "min": 101,   "max": 1_000},
    {"name": ScaleTier.ENTERPRISE, "min": 1_001, "max": 10_000},
    {"name": ScaleTier.FORTUNE500, "min": 10_001, "max": None},
]

# Base monthly compute cost per user (USD)
_COMPUTE_COST_PER_USER = 2.5
# Storage cost per user (USD)
_STORAGE_COST_PER_USER = 0.5
# Bandwidth cost per user (USD)
_BANDWIDTH_COST_PER_USER = 0.3
# Support cost multiplier by tier
_SUPPORT_COSTS: dict = {
    ScaleTier.STARTUP:    0.0,
    ScaleTier.GROWTH:     50.0,
    ScaleTier.SCALE:      200.0,
    ScaleTier.ENTERPRISE: 800.0,
    ScaleTier.FORTUNE500: 2_500.0,
}

_INTEGRATION_TYPES = {
    "ERP", "SALESFORCE", "SAP", "ORACLE", "MICROSOFT_365", "SLACK", "JIRA"
}


class EnterpriseScaler:
    """Scaling advisor for SaaS plans.

    Provides scale tier assessment, scaling plans, infrastructure cost
    estimates, and Fortune 500 integration specifications.
    """

    # ------------------------------------------------------------------
    # Scale tier assessment
    # ------------------------------------------------------------------

    def assess_scale_tier(self, user_count: int) -> str:
        """Return the scale tier name for a given user count."""
        if user_count < 1:
            raise ValueError("user_count must be at least 1.")
        for tier in _SCALE_TIERS:
            if tier["max"] is None or user_count <= tier["max"]:
                return tier["name"]
        return ScaleTier.FORTUNE500

    # ------------------------------------------------------------------
    # Scaling plan
    # ------------------------------------------------------------------

    def generate_scaling_plan(
        self,
        plan_id: str,
        current_users: int,
        projected_users: int,
    ) -> dict:
        """Generate a scaling plan from current to projected user count.

        Returns infrastructure recommendations, cost estimates, and timeline.
        """
        current_tier = self.assess_scale_tier(current_users)
        projected_tier = self.assess_scale_tier(projected_users)
        current_cost = self.estimate_infrastructure_cost(current_users, [])
        projected_cost = self.estimate_infrastructure_cost(projected_users, [])
        growth_ratio = projected_users / max(current_users, 1)

        recommendations = self._build_recommendations(projected_tier)

        return {
            "plan_id": plan_id,
            "current_users": current_users,
            "projected_users": projected_users,
            "current_tier": current_tier,
            "projected_tier": projected_tier,
            "growth_ratio": round(growth_ratio, 2),
            "infrastructure_recommendations": recommendations,
            "current_monthly_cost_usd": current_cost["total_monthly_usd"],
            "projected_monthly_cost_usd": projected_cost["total_monthly_usd"],
            "cost_increase_usd": round(
                projected_cost["total_monthly_usd"] - current_cost["total_monthly_usd"], 2
            ),
            "timeline_months": max(1, int(growth_ratio * 2)),
        }

    def _build_recommendations(self, tier: str) -> list:
        base = ["Enable auto-scaling", "Set up monitoring and alerting", "Configure CDN"]
        tier_extras: dict = {
            ScaleTier.STARTUP:    [],
            ScaleTier.GROWTH:     ["Implement load balancing", "Set up staging environment"],
            ScaleTier.SCALE:      [
                "Implement load balancing",
                "Database read replicas",
                "Redis caching layer",
                "Dedicated DevOps team",
            ],
            ScaleTier.ENTERPRISE: [
                "Multi-region deployment",
                "Database clustering",
                "Dedicated security team",
                "SLA 99.99% uptime",
                "SIEM integration",
            ],
            ScaleTier.FORTUNE500: [
                "Global multi-region deployment",
                "Active-active database cluster",
                "Zero-trust security architecture",
                "24/7 dedicated SRE team",
                "Custom SLA negotiation",
                "Compliance certifications (SOC2, ISO 27001)",
            ],
        }
        return base + tier_extras.get(tier, [])

    # ------------------------------------------------------------------
    # Infrastructure cost estimation
    # ------------------------------------------------------------------

    def estimate_infrastructure_cost(
        self,
        user_count: int,
        modules: list,
    ) -> dict:
        """Estimate monthly infrastructure cost for a given user count and module list.

        Returns a cost breakdown: compute, storage, bandwidth, support, total.
        """
        compute = round(_COMPUTE_COST_PER_USER * user_count, 2)
        storage = round(_STORAGE_COST_PER_USER * user_count, 2)
        bandwidth = round(_BANDWIDTH_COST_PER_USER * user_count, 2)
        tier = self.assess_scale_tier(max(user_count, 1))
        support = _SUPPORT_COSTS.get(tier, 0.0)

        # Each module adds a small infrastructure overhead
        module_overhead = round(len(modules) * 5.0, 2)

        total = round(compute + storage + bandwidth + support + module_overhead, 2)
        return {
            "user_count": user_count,
            "scale_tier": tier,
            "compute_usd": compute,
            "storage_usd": storage,
            "bandwidth_usd": bandwidth,
            "support_usd": support,
            "module_overhead_usd": module_overhead,
            "total_monthly_usd": total,
        }

    # ------------------------------------------------------------------
    # Fortune 500 integrations
    # ------------------------------------------------------------------

    def generate_fortune500_integration(
        self,
        company_name: str,
        integration_type: str,
    ) -> dict:
        """Generate a Fortune 500 integration specification.

        Parameters
        ----------
        company_name : str
            Name of the enterprise company to integrate with.
        integration_type : str
            One of: ERP, SALESFORCE, SAP, ORACLE, MICROSOFT_365, SLACK, JIRA.
        """
        itype = integration_type.upper()
        if itype not in _INTEGRATION_TYPES:
            return {
                "error": f"Unknown integration type '{integration_type}'.",
                "supported_types": sorted(_INTEGRATION_TYPES),
            }

        specs: dict = {
            "ERP": {
                "protocol": "REST/SOAP",
                "auth": "OAuth 2.0 / API Key",
                "sync_frequency": "real-time",
                "features": ["bi-directional sync", "master data management", "financial consolidation"],
            },
            "SALESFORCE": {
                "protocol": "Salesforce REST API / Bulk API",
                "auth": "OAuth 2.0",
                "sync_frequency": "real-time",
                "features": ["lead sync", "opportunity mapping", "contact sync", "custom objects"],
            },
            "SAP": {
                "protocol": "SAP RFC / REST OData",
                "auth": "SAP SSO / OAuth 2.0",
                "sync_frequency": "batch (hourly) or real-time",
                "features": ["FI/CO integration", "MM sync", "HR data transfer", "S/4HANA support"],
            },
            "ORACLE": {
                "protocol": "Oracle REST Data Services",
                "auth": "OAuth 2.0 / JWT",
                "sync_frequency": "real-time",
                "features": ["ERP Cloud sync", "HCM integration", "financial data bridge"],
            },
            "MICROSOFT_365": {
                "protocol": "Microsoft Graph API",
                "auth": "OAuth 2.0 / Azure AD",
                "sync_frequency": "real-time",
                "features": ["Teams integration", "SharePoint sync", "Outlook calendar", "SSO"],
            },
            "SLACK": {
                "protocol": "Slack API / Webhooks",
                "auth": "OAuth 2.0",
                "sync_frequency": "real-time",
                "features": ["notifications", "slash commands", "workflow builder", "alert routing"],
            },
            "JIRA": {
                "protocol": "Jira REST API",
                "auth": "API Token / OAuth 2.0",
                "sync_frequency": "real-time",
                "features": ["issue sync", "project mapping", "sprint tracking", "webhook events"],
            },
        }

        spec = specs[itype]
        return {
            "company_name": company_name,
            "integration_type": itype,
            "protocol": spec["protocol"],
            "authentication": spec["auth"],
            "sync_frequency": spec["sync_frequency"],
            "features": spec["features"],
            "implementation_timeline_weeks": self._implementation_timeline(itype),
            "estimated_setup_cost_usd": self._integration_setup_cost(itype),
            "support_level": "Dedicated Fortune 500 Integration Team",
        }

    def _implementation_timeline(self, itype: str) -> int:
        timelines = {
            "ERP": 12,
            "SALESFORCE": 4,
            "SAP": 16,
            "ORACLE": 12,
            "MICROSOFT_365": 3,
            "SLACK": 1,
            "JIRA": 2,
        }
        return timelines.get(itype, 8)

    def _integration_setup_cost(self, itype: str) -> float:
        costs = {
            "ERP": 9_999.0,
            "SALESFORCE": 2_999.0,
            "SAP": 14_999.0,
            "ORACLE": 9_999.0,
            "MICROSOFT_365": 1_999.0,
            "SLACK": 499.0,
            "JIRA": 999.0,
        }
        return costs.get(itype, 4_999.0)
