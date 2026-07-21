"""
Modular SaaS Builder — custom SaaS plan composer for the DreamCo SaaS Packages Bot.

Lets users assemble bespoke SaaS plans by combining individual modules,
then calculates costs and generates a deployment-ready specification.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from dataclasses import dataclass, field
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Module registry
# ---------------------------------------------------------------------------

class AvailableModule:
    AUTH = "AUTH"
    PAYMENTS = "PAYMENTS"
    CRM = "CRM"
    INVENTORY = "INVENTORY"
    ANALYTICS = "ANALYTICS"
    REPORTING = "REPORTING"
    EMAIL_AUTOMATION = "EMAIL_AUTOMATION"
    CHAT = "CHAT"
    API_GATEWAY = "API_GATEWAY"
    NOTIFICATIONS = "NOTIFICATIONS"
    DASHBOARD = "DASHBOARD"
    USER_MANAGEMENT = "USER_MANAGEMENT"
    AUDIT_LOG = "AUDIT_LOG"
    BACKUP = "BACKUP"
    COMPLIANCE = "COMPLIANCE"


# Monthly cost per module (USD)
MODULE_COSTS: dict = {
    AvailableModule.AUTH: 5.0,
    AvailableModule.PAYMENTS: 30.0,
    AvailableModule.CRM: 25.0,
    AvailableModule.INVENTORY: 20.0,
    AvailableModule.ANALYTICS: 35.0,
    AvailableModule.REPORTING: 15.0,
    AvailableModule.EMAIL_AUTOMATION: 20.0,
    AvailableModule.CHAT: 15.0,
    AvailableModule.API_GATEWAY: 50.0,
    AvailableModule.NOTIFICATIONS: 10.0,
    AvailableModule.DASHBOARD: 10.0,
    AvailableModule.USER_MANAGEMENT: 8.0,
    AvailableModule.AUDIT_LOG: 8.0,
    AvailableModule.BACKUP: 12.0,
    AvailableModule.COMPLIANCE: 40.0,
}

# One-time setup fee per module (USD)
MODULE_SETUP_FEES: dict = {
    AvailableModule.AUTH: 0.0,
    AvailableModule.PAYMENTS: 99.0,
    AvailableModule.CRM: 49.0,
    AvailableModule.INVENTORY: 49.0,
    AvailableModule.ANALYTICS: 99.0,
    AvailableModule.REPORTING: 29.0,
    AvailableModule.EMAIL_AUTOMATION: 49.0,
    AvailableModule.CHAT: 29.0,
    AvailableModule.API_GATEWAY: 199.0,
    AvailableModule.NOTIFICATIONS: 19.0,
    AvailableModule.DASHBOARD: 19.0,
    AvailableModule.USER_MANAGEMENT: 0.0,
    AvailableModule.AUDIT_LOG: 19.0,
    AvailableModule.BACKUP: 29.0,
    AvailableModule.COMPLIANCE: 199.0,
}

AVAILABLE_MODULES: set = set(MODULE_COSTS.keys())

_BASE_PLAN_COST_MONTHLY = 29.0
_BASE_PLAN_SETUP = 99.0


@dataclass
class _Plan:
    plan_id: str
    user_id: str
    plan_name: str
    business_type: str
    description: str
    modules: dict = field(default_factory=dict)  # module_name -> config dict


class ModularSaaSBuilder:
    """Custom SaaS plan builder — compose, price, and spec modular SaaS plans.

    Plans are stored in memory keyed by plan_id.
    """

    def __init__(self) -> None:
        self._plans: dict = {}

    # ------------------------------------------------------------------
    # Plan lifecycle
    # ------------------------------------------------------------------

    def create_saas_plan(
        self,
        user_id: str,
        plan_name: str,
        business_type: str,
        description: str = "",
    ) -> dict:
        """Create a new SaaS plan and return its metadata."""
        plan_id = str(uuid.uuid4())
        plan = _Plan(
            plan_id=plan_id,
            user_id=user_id,
            plan_name=plan_name,
            business_type=business_type,
            description=description,
        )
        self._plans[plan_id] = plan
        return {
            "plan_id": plan_id,
            "user_id": user_id,
            "plan_name": plan_name,
            "business_type": business_type,
            "description": description,
            "modules": [],
            "status": "created",
        }

    def add_module(
        self,
        plan_id: str,
        module_name: str,
        config: Optional[dict] = None,
    ) -> dict:
        """Add a module to an existing plan."""
        plan = self._get_plan(plan_id)
        module_name = module_name.upper()
        if module_name not in AVAILABLE_MODULES:
            return {"error": f"Module '{module_name}' is not available.", "available": sorted(AVAILABLE_MODULES)}
        if module_name in plan.modules:
            return {"error": f"Module '{module_name}' is already in the plan.", "plan_id": plan_id}
        plan.modules[module_name] = config or {}
        return {
            "plan_id": plan_id,
            "module_added": module_name,
            "config": plan.modules[module_name],
            "total_modules": len(plan.modules),
        }

    def remove_module(self, plan_id: str, module_name: str) -> dict:
        """Remove a module from an existing plan."""
        plan = self._get_plan(plan_id)
        module_name = module_name.upper()
        if module_name not in plan.modules:
            return {"error": f"Module '{module_name}' is not in the plan.", "plan_id": plan_id}
        del plan.modules[module_name]
        return {
            "plan_id": plan_id,
            "module_removed": module_name,
            "total_modules": len(plan.modules),
        }

    # ------------------------------------------------------------------
    # Pricing
    # ------------------------------------------------------------------

    def calculate_plan_cost(self, plan_id: str) -> dict:
        """Calculate the full cost of a plan.

        Returns
        -------
        dict
            base_cost, modules_cost, total_monthly, total_setup
        """
        plan = self._get_plan(plan_id)
        modules_monthly = sum(MODULE_COSTS.get(m, 0.0) for m in plan.modules)
        modules_setup = sum(MODULE_SETUP_FEES.get(m, 0.0) for m in plan.modules)
        total_monthly = _BASE_PLAN_COST_MONTHLY + modules_monthly
        total_setup = _BASE_PLAN_SETUP + modules_setup
        return {
            "plan_id": plan_id,
            "base_cost": _BASE_PLAN_COST_MONTHLY,
            "modules_cost": round(modules_monthly, 2),
            "total_monthly": round(total_monthly, 2),
            "total_setup": round(total_setup, 2),
            "modules": list(plan.modules.keys()),
        }

    # ------------------------------------------------------------------
    # Spec generation
    # ------------------------------------------------------------------

    def generate_plan_spec(self, plan_id: str) -> dict:
        """Generate a full deployment-ready specification for a plan."""
        plan = self._get_plan(plan_id)
        cost = self.calculate_plan_cost(plan_id)
        return {
            "spec_version": "1.0",
            "plan_id": plan.plan_id,
            "user_id": plan.user_id,
            "plan_name": plan.plan_name,
            "business_type": plan.business_type,
            "description": plan.description,
            "modules": [
                {
                    "name": m,
                    "config": plan.modules[m],
                    "monthly_cost_usd": MODULE_COSTS.get(m, 0.0),
                    "setup_fee_usd": MODULE_SETUP_FEES.get(m, 0.0),
                }
                for m in plan.modules
            ],
            "pricing": cost,
            "deployment": {
                "environment": "cloud",
                "scalable": True,
                "auto_backup": "BACKUP" in plan.modules,
                "compliance_ready": "COMPLIANCE" in plan.modules,
            },
        }

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_plans(self, user_id: str) -> list:
        """Return all plans belonging to a user."""
        return [
            {
                "plan_id": p.plan_id,
                "plan_name": p.plan_name,
                "business_type": p.business_type,
                "modules": list(p.modules.keys()),
            }
            for p in self._plans.values()
            if p.user_id == user_id
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_plan(self, plan_id: str) -> _Plan:
        plan = self._plans.get(plan_id)
        if plan is None:
            raise KeyError(f"Plan '{plan_id}' not found.")
        return plan
