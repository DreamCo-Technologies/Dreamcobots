# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class SubscriptionPlan(Enum):
    STARTER = "starter"
    GROWTH = "growth"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

@dataclass
class PlanConfig:
    plan_id: str
    name: str
    price_usd_monthly: float
    max_plugins: Optional[int]
    features: list

PLAN_CATALOGUE = {
    SubscriptionPlan.STARTER.value: PlanConfig(
        plan_id="starter", name="Starter", price_usd_monthly=9.0, max_plugins=5,
        features=["basic_alerts", "5 plugins"]),
    SubscriptionPlan.GROWTH.value: PlanConfig(
        plan_id="growth", name="Growth", price_usd_monthly=29.0, max_plugins=15,
        features=["alerts", "analytics", "15 plugins"]),
    SubscriptionPlan.PROFESSIONAL.value: PlanConfig(
        plan_id="professional", name="Professional", price_usd_monthly=79.0, max_plugins=50,
        features=["alerts", "analytics", "all features", "50 plugins"]),
    SubscriptionPlan.ENTERPRISE.value: PlanConfig(
        plan_id="enterprise", name="Enterprise", price_usd_monthly=299.0, max_plugins=None,
        features=["alerts", "analytics", "all features", "white_label", "custom_plugins", "priority_support", "unlimited plugins"]),
}

class SubscriptionManager:
    def __init__(self):
        self._subscriptions: dict = {}

    def get_plan(self, plan: SubscriptionPlan) -> PlanConfig:
        return PLAN_CATALOGUE[plan.value]

    def list_plans(self) -> list:
        return [PLAN_CATALOGUE[p.value] for p in SubscriptionPlan]

    def subscribe(self, user_id: str, plan: SubscriptionPlan) -> dict:
        cfg = self.get_plan(plan)
        sub = {"user_id": user_id, "plan": plan.value, "status": "active", "plan_config": cfg}
        self._subscriptions[user_id] = sub
        return {"user_id": user_id, "plan": plan.value, "status": "active", "price": cfg.price_usd_monthly}

    def get_subscription(self, user_id: str) -> dict:
        if user_id not in self._subscriptions:
            return {"user_id": user_id, "status": "none"}
        sub = self._subscriptions[user_id]
        return {"user_id": user_id, "plan": sub["plan"], "status": sub["status"]}

    def upgrade_plan(self, user_id: str, new_plan: SubscriptionPlan) -> dict:
        cfg = self.get_plan(new_plan)
        if user_id not in self._subscriptions:
            return self.subscribe(user_id, new_plan)
        self._subscriptions[user_id]["plan"] = new_plan.value
        self._subscriptions[user_id]["plan_config"] = cfg
        return {"user_id": user_id, "plan": new_plan.value, "status": "upgraded", "price": cfg.price_usd_monthly}

    def cancel_subscription(self, user_id: str):
        if user_id in self._subscriptions:
            self._subscriptions[user_id]["status"] = "cancelled"
