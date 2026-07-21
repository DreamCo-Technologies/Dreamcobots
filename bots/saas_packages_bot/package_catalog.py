"""
Package Catalog — industry-specific SaaS packages for the DreamCo SaaS Packages Bot.

Provides 15+ pre-built SaaS packages across 10 industry verticals, each with
modules, pricing, and feature details ready for deployment.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class Industry(Enum):
    E_COMMERCE = "e_commerce"
    CRM = "crm"
    HR_AUTOMATION = "hr_automation"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    LEGAL = "legal"
    MARKETING = "marketing"
    LOGISTICS = "logistics"
    REAL_ESTATE = "real_estate"


@dataclass
class SaaSPackage:
    """Represents a single SaaS package in the catalog."""

    package_id: str
    name: str
    industry: Industry
    description: str
    modules: list
    monthly_price_usd: float
    setup_fee_usd: float
    users_included: int
    features: list

    def to_dict(self) -> dict:
        return {
            "package_id": self.package_id,
            "name": self.name,
            "industry": self.industry.value,
            "description": self.description,
            "modules": self.modules,
            "monthly_price_usd": self.monthly_price_usd,
            "setup_fee_usd": self.setup_fee_usd,
            "users_included": self.users_included,
            "features": self.features,
        }


# ---------------------------------------------------------------------------
# Catalog data
# ---------------------------------------------------------------------------

_CATALOG: list = [
    SaaSPackage(
        package_id="ecom-001",
        name="ShopStream Pro",
        industry=Industry.E_COMMERCE,
        description="Full-stack e-commerce platform with inventory, payments, and storefront.",
        modules=["storefront", "inventory", "payments", "shipping", "reviews"],
        monthly_price_usd=79.0,
        setup_fee_usd=199.0,
        users_included=5,
        features=["multi-currency", "abandoned-cart", "product-analytics", "SEO-tools"],
    ),
    SaaSPackage(
        package_id="ecom-002",
        name="MarketPlace Builder",
        industry=Industry.E_COMMERCE,
        description="Multi-vendor marketplace with vendor portals and commission management.",
        modules=["vendor-portal", "commission-engine", "payments", "search", "ratings"],
        monthly_price_usd=149.0,
        setup_fee_usd=499.0,
        users_included=20,
        features=["multi-vendor", "commission-splits", "fraud-detection", "bulk-import"],
    ),
    SaaSPackage(
        package_id="crm-001",
        name="LeadFlow CRM",
        industry=Industry.CRM,
        description="Sales pipeline and lead management CRM with AI-driven scoring.",
        modules=["leads", "pipeline", "contacts", "email-automation", "reports"],
        monthly_price_usd=59.0,
        setup_fee_usd=149.0,
        users_included=10,
        features=["lead-scoring", "email-sequences", "deal-forecasting", "integrations"],
    ),
    SaaSPackage(
        package_id="crm-002",
        name="ClientVault Enterprise CRM",
        industry=Industry.CRM,
        description="Enterprise CRM with account management, territory planning, and advanced analytics.",
        modules=["accounts", "opportunities", "territory", "analytics", "forecasting"],
        monthly_price_usd=199.0,
        setup_fee_usd=999.0,
        users_included=50,
        features=["territory-management", "AI-forecasting", "360-customer-view", "custom-fields"],
    ),
    SaaSPackage(
        package_id="hr-001",
        name="PeopleCore HR",
        industry=Industry.HR_AUTOMATION,
        description="End-to-end HR automation: hiring, onboarding, payroll, and performance.",
        modules=["recruiting", "onboarding", "payroll", "performance", "time-tracking"],
        monthly_price_usd=89.0,
        setup_fee_usd=299.0,
        users_included=25,
        features=["ATS", "e-signatures", "payroll-automation", "review-cycles"],
    ),
    SaaSPackage(
        package_id="hr-002",
        name="TalentBridge Workforce",
        industry=Industry.HR_AUTOMATION,
        description="Workforce planning and talent analytics platform for scaling teams.",
        modules=["workforce-planning", "talent-analytics", "succession", "learning", "benefits"],
        monthly_price_usd=129.0,
        setup_fee_usd=499.0,
        users_included=100,
        features=["succession-planning", "skills-gap-analysis", "LMS-integration", "benefits-admin"],
    ),
    SaaSPackage(
        package_id="fin-001",
        name="FinEdge Accounting",
        industry=Industry.FINANCE,
        description="Cloud accounting with invoicing, expenses, and financial reporting.",
        modules=["invoicing", "expenses", "bank-reconciliation", "reports", "tax"],
        monthly_price_usd=69.0,
        setup_fee_usd=199.0,
        users_included=5,
        features=["multi-currency", "tax-automation", "bank-feeds", "financial-dashboards"],
    ),
    SaaSPackage(
        package_id="fin-002",
        name="TreasuryMax Enterprise",
        industry=Industry.FINANCE,
        description="Enterprise treasury management with cash flow, FX, and risk analytics.",
        modules=["cash-management", "fx-hedging", "risk-analytics", "payments", "compliance"],
        monthly_price_usd=499.0,
        setup_fee_usd=2999.0,
        users_included=20,
        features=["FX-hedging", "cash-forecasting", "risk-dashboards", "SWIFT-integration"],
    ),
    SaaSPackage(
        package_id="health-001",
        name="CareConnect EHR",
        industry=Industry.HEALTHCARE,
        description="Electronic health records with patient portal and appointment scheduling.",
        modules=["ehr", "patient-portal", "scheduling", "billing", "prescriptions"],
        monthly_price_usd=199.0,
        setup_fee_usd=999.0,
        users_included=10,
        features=["HIPAA-compliant", "telemedicine", "e-prescriptions", "insurance-billing"],
    ),
    SaaSPackage(
        package_id="edu-001",
        name="LearnHub LMS",
        industry=Industry.EDUCATION,
        description="Learning management system with courses, quizzes, and certifications.",
        modules=["courses", "quizzes", "certifications", "student-portal", "analytics"],
        monthly_price_usd=49.0,
        setup_fee_usd=149.0,
        users_included=100,
        features=["SCORM-support", "live-classes", "gamification", "custom-branding"],
    ),
    SaaSPackage(
        package_id="legal-001",
        name="LexTrack Legal",
        industry=Industry.LEGAL,
        description="Matter management, billing, and document management for law firms.",
        modules=["matter-management", "billing", "documents", "time-tracking", "client-portal"],
        monthly_price_usd=149.0,
        setup_fee_usd=499.0,
        users_included=10,
        features=["matter-tracking", "trust-accounting", "e-discovery", "conflict-checks"],
    ),
    SaaSPackage(
        package_id="mkt-001",
        name="CampaignDrive Marketing",
        industry=Industry.MARKETING,
        description="Multi-channel marketing automation with email, SMS, and social campaigns.",
        modules=["email-campaigns", "sms", "social-scheduler", "landing-pages", "analytics"],
        monthly_price_usd=79.0,
        setup_fee_usd=199.0,
        users_included=5,
        features=["A/B-testing", "segmentation", "drip-campaigns", "ROI-tracking"],
    ),
    SaaSPackage(
        package_id="log-001",
        name="FreightFlow Logistics",
        industry=Industry.LOGISTICS,
        description="End-to-end logistics management with shipment tracking and fleet management.",
        modules=["shipment-tracking", "fleet-management", "warehouse", "routing", "reports"],
        monthly_price_usd=129.0,
        setup_fee_usd=499.0,
        users_included=15,
        features=["real-time-tracking", "route-optimization", "warehouse-management", "carrier-integration"],
    ),
    SaaSPackage(
        package_id="re-001",
        name="PropTech Realty CRM",
        industry=Industry.REAL_ESTATE,
        description="Real estate CRM with property listings, lead nurturing, and transaction management.",
        modules=["listings", "leads", "transactions", "documents", "portal"],
        monthly_price_usd=99.0,
        setup_fee_usd=299.0,
        users_included=10,
        features=["MLS-integration", "e-signatures", "deal-tracking", "client-portal"],
    ),
    SaaSPackage(
        package_id="re-002",
        name="AssetPlex Property Management",
        industry=Industry.REAL_ESTATE,
        description="Property management platform for landlords with tenant portal and maintenance.",
        modules=["tenant-portal", "maintenance", "rent-collection", "accounting", "leases"],
        monthly_price_usd=79.0,
        setup_fee_usd=199.0,
        users_included=5,
        features=["online-rent-collection", "maintenance-requests", "lease-management", "financial-reports"],
    ),
]


class PackageCatalog:
    """Industry-specific SaaS package catalog.

    Provides discovery and pricing methods over the 15+ built-in packages.
    """

    def __init__(self) -> None:
        self._packages: dict = {pkg.package_id: pkg for pkg in _CATALOG}

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_package(self, package_id: str) -> Optional[SaaSPackage]:
        """Return a package by its ID, or None if not found."""
        return self._packages.get(package_id)

    def list_packages(self, industry: Optional[Industry] = None) -> list:
        """List all packages, optionally filtered by industry."""
        pkgs = list(self._packages.values())
        if industry is not None:
            pkgs = [p for p in pkgs if p.industry == industry]
        return pkgs

    def search_packages(self, query: str) -> list:
        """Full-text search across name, description, and features."""
        q = query.lower()
        return [
            p for p in self._packages.values()
            if q in p.name.lower()
            or q in p.description.lower()
            or any(q in f.lower() for f in p.features)
            or any(q in m.lower() for m in p.modules)
        ]

    def get_by_industry(self, industry: Industry) -> list:
        """Return all packages for a given industry."""
        return [p for p in self._packages.values() if p.industry == industry]

    def get_pricing_summary(self) -> list:
        """Return a pricing summary list sorted by monthly price."""
        return sorted(
            [
                {
                    "package_id": p.package_id,
                    "name": p.name,
                    "industry": p.industry.value,
                    "monthly_price_usd": p.monthly_price_usd,
                    "setup_fee_usd": p.setup_fee_usd,
                    "users_included": p.users_included,
                }
                for p in self._packages.values()
            ],
            key=lambda x: x["monthly_price_usd"],
        )

    def count(self) -> int:
        return len(self._packages)
