#!/usr/bin/env python3
"""Supplier/manufacturing exchange primitives for DreamCo.

Focus: direct buyer-to-supplier discovery, U.S. manufacturing growth, dropship
and private-label sourcing, RFQs, and auditable comparison. It does not act as
a broker or silently commit buyers/suppliers to contracts.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal


BusinessMode = Literal["dropship", "wholesale", "private_label", "contract_manufacturing", "us_manufacturing", "services"]


@dataclass(frozen=True)
class Supplier:
    supplier_id: str
    name: str
    country: str
    state: str | None
    capabilities: tuple[str, ...]
    moq: int
    unit_cost: float
    shipping_cost: float
    lead_days: int
    quality_score: float
    verified: bool
    dropship: bool
    custom_manufacturing: bool


@dataclass(frozen=True)
class RFQ:
    buyer_id: str
    product: str
    quantity: int
    target_country: str
    mode: BusinessMode
    requirements: tuple[str, ...] = ()
    max_landed_unit_cost: float | None = None


SUPPLIERS: tuple[Supplier, ...] = (
    Supplier("demo-us-001", "DreamCo Manufacturing Network — Midwest", "US", "IL", ("assembly", "private_label", "packaging", "light_manufacturing"), 50, 8.50, 2.00, 14, .90, False, False, True),
    Supplier("demo-us-002", "DreamCo Manufacturing Network — Southeast", "US", "GA", ("injection_molding", "assembly", "packaging"), 250, 4.75, 1.50, 28, .93, False, False, True),
    Supplier("demo-global-001", "DreamCo Supplier Network — Global", "CN", None, ("dropship", "private_label", "electronics", "consumer_goods"), 10, 3.25, 2.25, 21, .82, False, True, True),
)


def landed_unit_cost(supplier: Supplier) -> float:
    return round(supplier.unit_cost + supplier.shipping_cost, 4)


def match_rfq(rfq: RFQ, suppliers: tuple[Supplier, ...] = SUPPLIERS) -> list[dict]:
    if rfq.quantity <= 0:
        raise ValueError("quantity must be positive")
    requirement_set = {x.lower() for x in rfq.requirements}
    results: list[dict] = []
    for supplier in suppliers:
        if rfq.mode == "dropship" and not supplier.dropship:
            continue
        if rfq.mode in {"private_label", "contract_manufacturing", "us_manufacturing"} and not supplier.custom_manufacturing:
            continue
        if supplier.moq > rfq.quantity:
            continue
        capabilities = {x.lower() for x in supplier.capabilities}
        coverage = len(requirement_set & capabilities) / max(1, len(requirement_set))
        landed = landed_unit_cost(supplier)
        if rfq.max_landed_unit_cost is not None and landed > rfq.max_landed_unit_cost:
            continue
        results.append({
            **asdict(supplier),
            "landed_unit_cost": landed,
            "requirement_coverage": round(coverage, 3),
            "total_estimated_product_cost": round(landed * rfq.quantity, 2),
            "fit_score": round((coverage * .35 + supplier.quality_score * .35 + (1 / max(1, supplier.lead_days)) * 8 * .15 + (1 if supplier.verified else .35) * .15) * 100, 2),
        })
    return sorted(results, key=lambda x: (-x["fit_score"], x["landed_unit_cost"], x["lead_days"]))


def create_rfq_payload(rfq: RFQ) -> dict:
    if not rfq.product.strip():
        raise ValueError("product is required")
    return {
        "type": "RFQ",
        "buyer_id": rfq.buyer_id,
        "product": rfq.product,
        "quantity": rfq.quantity,
        "target_country": rfq.target_country,
        "mode": rfq.mode,
        "requirements": list(rfq.requirements),
        "max_landed_unit_cost": rfq.max_landed_unit_cost,
        "direct_deal": True,
        "dreamco_role": "marketplace_software_and_workflow",
        "human_approval_required_before_contract": True,
        "verification_required": ["supplier_identity", "samples_or_quality_evidence", "landed_cost", "shipping_terms", "payment_terms", "applicable_compliance"],
    }


def nonprofit_programs() -> list[dict]:
    return [
        {"id": "teen-enterprise", "audience": "teens", "safe_uses": ["entrepreneurship education", "maker projects", "tutoring", "content creation", "supervised ecommerce"], "guardrails": ["age-appropriate accounts", "adult/guardian controls where required", "no prohibited work", "education-first"]},
        {"id": "reentry-enterprise", "audience": "people returning from incarceration", "safe_uses": ["job readiness", "skills training", "legal business formation education", "remote work preparation", "manufacturing apprenticeships"], "guardrails": ["lawful opportunities", "employer eligibility rules", "privacy minimization", "no exploitative fees"]},
        {"id": "community-manufacturing", "audience": "nonprofits and community groups", "safe_uses": ["local supplier discovery", "maker spaces", "workforce training", "small-batch production", "procurement education"], "guardrails": ["grant/program rules", "safety requirements", "human review for contracts"]},
    ]
