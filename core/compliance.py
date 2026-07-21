"""Compliance package framework for DreamCobots platform."""


class CompliancePackage:
    """Represents a compliance package for a specific industry or domain."""

    def __init__(self, name: str, category: str, requirements: list,
                 checklist: list, certifications: list, pricing_tiers: dict):
        """Initialize a compliance package with full metadata."""
        self.name = name
        self.category = category
        self.requirements = requirements
        self.checklist = checklist
        self.certifications = certifications
        self.pricing_tiers = pricing_tiers

    def to_dict(self) -> dict:
        """Return package as a dictionary."""
        return {
            "name": self.name,
            "category": self.category,
            "requirements": self.requirements,
            "checklist": self.checklist,
            "certifications": self.certifications,
            "pricing_tiers": self.pricing_tiers,
        }


class ComplianceManager:
    """Manages all compliance packages across the DreamCobots platform."""

    MEDICAL = "MEDICAL"
    LEGAL = "LEGAL"
    FINANCIAL = "FINANCIAL"
    CYBERSECURITY = "CYBERSECURITY"
    EDUCATION = "EDUCATION"
    FUNERAL = "FUNERAL"
    HR = "HR"
    MARKETING = "MARKETING"
    REAL_ESTATE = "REAL_ESTATE"
    ECOMMERCE = "ECOMMERCE"
    GENERAL = "GENERAL"

    def __init__(self):
        """Initialize the compliance manager and load all packages."""
        self._packages = {}
        self._load_packages()

    def _load_packages(self):
        """Load all built-in compliance packages."""
        from compliance.packages import get_all_packages
        for pkg in get_all_packages():
            self._packages[pkg.category] = pkg

    def get_package(self, category: str) -> CompliancePackage:
        """Get a compliance package by category."""
        return self._packages.get(category.upper())

    def list_packages(self) -> list:
        """List all available compliance package summaries."""
        return [
            {"category": cat, "name": pkg.name, "tiers": list(pkg.pricing_tiers.keys())}
            for cat, pkg in self._packages.items()
        ]

    def all_categories(self) -> list:
        """Return all available compliance categories."""
        return list(self._packages.keys())
