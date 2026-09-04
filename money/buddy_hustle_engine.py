#!/usr/bin/env python3
"""Executable, evidence-first opportunity engine for Buddy.

This module ranks lawful revenue opportunities and emits bounded next actions.
It never promises income and never performs external transactions by itself.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable


@dataclass(frozen=True)
class HustleProfile:
    skills: tuple[str, ...] = ()
    interests: tuple[str, ...] = ()
    hours_per_week: float = 5.0
    budget: float = 0.0
    target_income: float = 0.0
    location: str = ""
    assets: tuple[str, ...] = ()
    audience: tuple[str, ...] = ()
    risk_tolerance: float = 0.25


@dataclass(frozen=True)
class Opportunity:
    id: str
    category: str
    name: str
    startup_cost: float
    time_hours: float
    evidence_quality: float
    automation_potential: float
    demand_signal: float
    risk: float
    required_skills: tuple[str, ...]
    next_actions: tuple[str, ...]


CATALOG: tuple[Opportunity, ...] = (
    Opportunity("service-productization", "services", "Productized skill service", 0, 4, .85, .80, .80, .20, ("writing", "design", "coding", "repair"), ("define offer", "price", "create sample", "publish listing", "measure leads")),
    Opportunity("local-automation", "services", "Local business automation service", 0, 6, .82, .86, .78, .25, ("coding", "automation", "sales"), ("choose niche", "build demo", "contact opted-in prospects", "book discovery calls")),
    Opportunity("digital-product", "products", "Digital product or template", 0, 5, .78, .92, .68, .20, ("writing", "design", "education", "coding"), ("validate demand", "create MVP", "publish", "track conversion")),
    Opportunity("ecommerce-sourcing", "commerce", "Supplier-backed ecommerce product", 100, 7, .76, .84, .75, .45, ("ecommerce", "sales", "marketing"), ("find suppliers", "compare landed cost", "request samples", "publish offer", "test demand")),
    Opportunity("resale", "commerce", "Resale and flipping research", 50, 5, .80, .55, .72, .40, ("sales", "repair", "research"), ("source inventory", "verify condition", "calculate margin", "list", "reinvest only after results")),
    Opportunity("freelance", "services", "Freelance contract work", 0, 8, .88, .55, .82, .20, ("coding", "design", "writing", "marketing", "repair"), ("build profile", "prepare samples", "find matching contracts", "submit tailored proposals")),
    Opportunity("affiliate-content", "media", "Affiliate/content business", 0, 6, .70, .90, .62, .35, ("content", "marketing", "video"), ("select lawful niche", "create useful content", "disclose affiliate relationships", "measure conversion")),
    Opportunity("micro-saas", "software", "Micro-SaaS", 25, 12, .79, .95, .70, .45, ("coding", "product", "sales"), ("validate problem", "ship MVP", "charge only for delivered value", "monitor retention")),
    Opportunity("procurement", "contracts", "Government/procurement opportunity research", 0, 6, .86, .65, .66, .35, ("research", "writing", "business"), ("verify official opportunity", "check eligibility", "prepare draft", "human-review submission")),
    Opportunity("training", "education", "Training or tutoring product", 0, 4, .84, .80, .72, .15, ("education", "writing", "coding", "repair"), ("choose subject", "create lesson", "pilot", "collect feedback")),
)


def _norm(values: Iterable[str]) -> set[str]:
    return {v.strip().lower() for v in values if v and v.strip()}


def score(profile: HustleProfile, opportunity: Opportunity) -> float:
    user = _norm((*profile.skills, *profile.interests, *profile.assets))
    required = _norm(opportunity.required_skills)
    fit = 1.0 if not required else min(1.0, len(user & required) / max(1, len(required)))
    budget_fit = 1.0 if opportunity.startup_cost <= profile.budget else max(0.0, profile.budget / opportunity.startup_cost) if opportunity.startup_cost else 1.0
    time_fit = min(1.0, profile.hours_per_week / max(1.0, opportunity.time_hours))
    risk_fit = max(0.0, 1.0 - abs(profile.risk_tolerance - opportunity.risk))
    value = opportunity.demand_signal * opportunity.evidence_quality * (0.5 + 0.5 * fit)
    value *= (0.5 + 0.5 * budget_fit) * (0.5 + 0.5 * time_fit)
    value *= (0.5 + 0.5 * opportunity.automation_potential) * risk_fit
    return round(value * 100, 2)


def rank(profile: HustleProfile, limit: int = 10) -> list[dict]:
    ranked = []
    for opportunity in CATALOG:
        ranked.append({"score": score(profile, opportunity), **asdict(opportunity)})
    return sorted(ranked, key=lambda x: (-x["score"], x["startup_cost"], x["time_hours"]))[:limit]


def build_bounded_execution_plan(profile: HustleProfile, opportunity_id: str, max_spend: float = 0.0) -> dict:
    matches = [o for o in CATALOG if o.id == opportunity_id]
    if not matches:
        raise ValueError(f"unknown opportunity: {opportunity_id}")
    opportunity = matches[0]
    if max_spend < 0:
        raise ValueError("max_spend must be non-negative")
    return {
        "opportunity": opportunity.id,
        "score": score(profile, opportunity),
        "autonomy": "bounded_user_approved",
        "max_spend": min(max_spend, profile.budget),
        "actions": list(opportunity.next_actions),
        "approval_required": ["external_account_connection", "paid_purchase", "contract", "regulated_submission"],
        "stop_conditions": ["budget_exceeded", "unexpected_fee", "policy_violation", "evidence_failure", "user_pause"],
        "truth_policy": "No guaranteed income; actual revenue is recorded only from verified results.",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(rank(HustleProfile(skills=("coding", "repair"), hours_per_week=15, budget=100)), indent=2))
