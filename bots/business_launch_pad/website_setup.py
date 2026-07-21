# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""Website Setup module for Business Launch Pad."""

import uuid
import random
from dataclasses import dataclass, field
from enum import Enum


class DomainStatus(Enum):
    AVAILABLE = "available"
    TAKEN = "taken"
    PREMIUM = "premium"


class WebsiteTemplate(Enum):
    LANDING_PAGE = "landing_page"
    ECOMMERCE = "ecommerce"
    PORTFOLIO = "portfolio"
    BLOG = "blog"
    SAAS = "saas"
    CORPORATE = "corporate"


@dataclass
class DomainResult:
    domain: str
    status: DomainStatus
    price_usd: float
    alternatives: list[str]


@dataclass
class WebsiteProject:
    project_id: str
    business_name: str
    domain: str
    template: WebsiteTemplate
    seo_score: int
    pages: list[str]
    launched: bool


_INDUSTRY_TEMPLATES: dict[str, WebsiteTemplate] = {
    "technology": WebsiteTemplate.SAAS,
    "e-commerce": WebsiteTemplate.ECOMMERCE,
    "retail": WebsiteTemplate.ECOMMERCE,
    "consulting": WebsiteTemplate.CORPORATE,
    "finance": WebsiteTemplate.CORPORATE,
    "healthcare": WebsiteTemplate.CORPORATE,
    "education": WebsiteTemplate.LANDING_PAGE,
    "entertainment": WebsiteTemplate.PORTFOLIO,
    "photography": WebsiteTemplate.PORTFOLIO,
    "blog": WebsiteTemplate.BLOG,
    "food & beverage": WebsiteTemplate.LANDING_PAGE,
    "real estate": WebsiteTemplate.CORPORATE,
}

_TEMPLATE_PAGES: dict[WebsiteTemplate, list[str]] = {
    WebsiteTemplate.LANDING_PAGE: ["Home", "About", "Features", "Pricing", "Contact"],
    WebsiteTemplate.ECOMMERCE: ["Home", "Shop", "Product", "Cart", "Checkout", "About", "Contact"],
    WebsiteTemplate.PORTFOLIO: ["Home", "Portfolio", "About", "Services", "Contact"],
    WebsiteTemplate.BLOG: ["Home", "Blog", "About", "Archive", "Contact"],
    WebsiteTemplate.SAAS: ["Home", "Features", "Pricing", "Docs", "Blog", "Contact", "Login"],
    WebsiteTemplate.CORPORATE: ["Home", "About", "Services", "Team", "Case Studies", "Contact"],
}

# Deterministic domain simulation: domains ending in known TLDs are "taken" if name length < 6
def _simulate_domain_status(domain: str) -> DomainStatus:
    name_part = domain.split(".")[0]
    if len(name_part) < 5:
        return DomainStatus.TAKEN
    if len(name_part) > 12:
        return DomainStatus.PREMIUM
    # Use hash for determinism in tests
    return DomainStatus.AVAILABLE if (hash(domain) % 3) != 0 else DomainStatus.TAKEN


class WebsiteSetup:
    """Handles domain checking, website creation, SEO setup, and launch."""

    def __init__(self) -> None:
        self._projects: list[WebsiteProject] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_domain(self, domain: str) -> DomainResult:
        """Check availability and pricing for a domain."""
        status = _simulate_domain_status(domain)
        if status == DomainStatus.AVAILABLE:
            price = 12.99
        elif status == DomainStatus.PREMIUM:
            price = 299.99
        else:
            price = 0.0

        name_part = domain.split(".")[0]
        alternatives = [
            f"{name_part}.io",
            f"{name_part}.co",
            f"get{name_part}.com",
            f"{name_part}app.com",
            f"try{name_part}.com",
        ]
        # Remove current domain from alternatives
        alternatives = [a for a in alternatives if a != domain][:4]

        return DomainResult(domain=domain, status=status, price_usd=price, alternatives=alternatives)

    def create_website(self, business_name: str, domain: str, template: WebsiteTemplate) -> WebsiteProject:
        """Create a new website project."""
        pages = list(_TEMPLATE_PAGES.get(template, ["Home", "About", "Contact"]))
        project = WebsiteProject(
            project_id=str(uuid.uuid4()),
            business_name=business_name,
            domain=domain,
            template=template,
            seo_score=0,
            pages=pages,
            launched=False,
        )
        self._projects.append(project)
        return project

    def select_template(self, industry: str) -> WebsiteTemplate:
        """Recommend a website template for the given industry."""
        return _INDUSTRY_TEMPLATES.get(industry.lower(), WebsiteTemplate.CORPORATE)

    def setup_seo(self, project_id: str) -> dict:
        """Configure SEO for a website project and update its seo_score."""
        project = self.get_project(project_id)
        seo_data = {
            "keywords": [
                f"{project.business_name.lower()} services",
                f"best {project.business_name.lower()}",
                f"{project.business_name.lower()} online",
                f"{project.template.value.replace('_', ' ')} website",
            ],
            "meta_title": f"{project.business_name} | Official Website",
            "meta_description": f"Discover {project.business_name} — your trusted partner. Explore our services, pricing, and more.",
            "sitemap_url": f"https://{project.domain}/sitemap.xml",
            "robots_txt": "User-agent: *\nAllow: /",
            "open_graph": {
                "og:title": project.business_name,
                "og:description": f"Welcome to {project.business_name}",
                "og:url": f"https://{project.domain}",
                "og:type": "website",
            },
            "schema_markup": "Organization",
            "page_speed_target": "90+",
        }
        project.seo_score = 85
        return seo_data

    def launch_website(self, project_id: str) -> WebsiteProject:
        """Mark a website project as launched."""
        project = self.get_project(project_id)
        project.launched = True
        return project

    def list_projects(self) -> list[WebsiteProject]:
        """Return all website projects."""
        return list(self._projects)

    def get_project(self, project_id: str) -> WebsiteProject:
        """Retrieve a project by ID; raises KeyError if not found."""
        for project in self._projects:
            if project.project_id == project_id:
                return project
        raise KeyError(f"Project '{project_id}' not found")
