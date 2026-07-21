"""
Business Launch Pad — main bot module.

Provides a unified interface for launching a business: plan generation,
market research, legal formation, brand identity, and website setup.
"""

from framework import GlobalAISourcesFlow  # GLOBAL AI SOURCES FLOW — framework compliance

from bots.business_launch_pad.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    list_tiers,
    FEATURE_PLAN_GENERATOR,
    FEATURE_MARKET_RESEARCH,
    FEATURE_LEGAL_FORMATION,
    FEATURE_BRAND_IDENTITY,
    FEATURE_WEBSITE_SETUP,
    FEATURE_FINANCIAL_PROJECTIONS,
    FEATURE_PITCH_DECK,
    FEATURE_TAM_ANALYSIS,
    FEATURE_SWOT_ANALYSIS,
    FEATURE_COMPLIANCE_MONITORING,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
)
from bots.business_launch_pad.plan_generator import PlanGenerator
from bots.business_launch_pad.market_research import MarketResearch
from bots.business_launch_pad.legal_formation import LegalFormation, EntityType
from bots.business_launch_pad.brand_identity import BrandIdentity
from bots.business_launch_pad.website_setup import WebsiteSetup, WebsiteTemplate


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class BusinessLaunchPadError(Exception):
    """Base exception for BusinessLaunchPad errors."""


class BusinessLaunchPadTierError(BusinessLaunchPadError):
    """Raised when a requested feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Main bot class
# ---------------------------------------------------------------------------

class BusinessLaunchPad:
    """All-in-one business launch assistant."""

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._tier_config: TierConfig = get_tier_config(tier)
        self._plan_generator = PlanGenerator()
        self._market_research = MarketResearch()
        self._legal_formation = LegalFormation()
        self._brand_identity = BrandIdentity()
        self._website_setup = WebsiteSetup()
        self._plan_count = 0

    # ------------------------------------------------------------------
    # Tier gate helper
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self._tier_config.has_feature(feature):
            raise BusinessLaunchPadTierError(
                f"Feature '{feature}' is not available on the {self._tier_config.name} tier. "
                f"Please upgrade to access this feature."
            )

    def _check_plan_quota(self) -> None:
        limit = self._tier_config.max_plans_per_month
        if limit is not None and self._plan_count >= limit:
            raise BusinessLaunchPadTierError(
                f"Monthly plan limit of {limit} reached on the {self._tier_config.name} tier."
            )

    # ------------------------------------------------------------------
    # Core tools
    # ------------------------------------------------------------------

    def create_business_plan(self, business_name: str, industry: str, description: str) -> dict:
        """Generate a business plan (PRO+ unlocks financial projections and pitch deck)."""
        self._require_feature(FEATURE_PLAN_GENERATOR)
        self._check_plan_quota()
        plan = self._plan_generator.generate_plan(business_name, industry, description)
        self._plan_count += 1
        result: dict = {
            "plan_id": plan.plan_id,
            "business_name": plan.business_name,
            "industry": plan.industry,
            "executive_summary": plan.executive_summary,
            "target_market": plan.target_market,
            "revenue_model": plan.revenue_model,
            "created_at": plan.created_at,
        }
        if self._tier_config.has_feature(FEATURE_TAM_ANALYSIS):
            result["tam_usd"] = plan.tam_usd
        if self._tier_config.has_feature(FEATURE_FINANCIAL_PROJECTIONS):
            result["financial_projections"] = plan.financial_projections
        if self._tier_config.has_feature(FEATURE_PITCH_DECK):
            result["pitch_deck"] = self._plan_generator.export_pitch_deck(plan)
        return result

    def run_market_research(self, industry: str) -> dict:
        """Run market research for an industry (PRO+)."""
        self._require_feature(FEATURE_MARKET_RESEARCH)
        report = self._market_research.generate_report(industry)
        result: dict = {
            "report_id": report.report_id,
            "industry": report.industry,
            "competitors": [
                {"name": c.name, "market_share": c.market_share, "strengths": c.strengths, "weaknesses": c.weaknesses}
                for c in report.competitors
            ],
            "personas": [
                {"name": p.name, "age_range": p.age_range, "pain_points": p.pain_points, "goals": p.goals, "channels": p.channels}
                for p in report.personas
            ],
            "trends": report.trends,
        }
        if self._tier_config.has_feature(FEATURE_SWOT_ANALYSIS):
            result["swot"] = report.swot
        return result

    def form_legal_entity(self, business_name: str, entity_type_str: str, state: str) -> dict:
        """Form a legal entity (PRO+)."""
        self._require_feature(FEATURE_LEGAL_FORMATION)
        try:
            entity_type = EntityType(entity_type_str.lower())
        except ValueError:
            valid = [e.value for e in EntityType]
            raise BusinessLaunchPadError(
                f"Invalid entity type '{entity_type_str}'. Valid options: {valid}"
            )
        entity = self._legal_formation.form_entity(business_name, entity_type, state)
        return {
            "entity_id": entity.entity_id,
            "business_name": entity.business_name,
            "entity_type": entity.entity_type.value,
            "state": entity.state,
            "status": entity.status.value,
            "ein": entity.ein,
            "compliance_items": entity.compliance_items,
        }

    def create_brand(self, business_name: str, industry: str) -> dict:
        """Create a brand identity kit (PRO+)."""
        self._require_feature(FEATURE_BRAND_IDENTITY)
        kit = self._brand_identity.create_brand(business_name, industry)
        return {
            "brand_id": kit.brand_id,
            "business_name": kit.business_name,
            "industry": kit.industry,
            "logo_concepts": kit.logo_concepts,
            "color_palette": {
                "primary": kit.color_palette.primary,
                "secondary": kit.color_palette.secondary,
                "accent": kit.color_palette.accent,
                "neutral": kit.color_palette.neutral,
            },
            "brand_voice": kit.brand_voice,
            "tagline": kit.tagline,
            "style_guide": kit.style_guide,
        }

    def setup_website(self, business_name: str, domain: str, template_str: str) -> dict:
        """Set up a website project (PRO+)."""
        self._require_feature(FEATURE_WEBSITE_SETUP)
        try:
            template = WebsiteTemplate(template_str.lower())
        except ValueError:
            valid = [t.value for t in WebsiteTemplate]
            raise BusinessLaunchPadError(
                f"Invalid template '{template_str}'. Valid options: {valid}"
            )
        domain_result = self._website_setup.check_domain(domain)
        project = self._website_setup.create_website(business_name, domain, template)
        seo = self._website_setup.setup_seo(project.project_id)
        return {
            "project_id": project.project_id,
            "business_name": project.business_name,
            "domain": project.domain,
            "domain_status": domain_result.status.value,
            "template": project.template.value,
            "pages": project.pages,
            "seo_score": project.seo_score,
            "seo_setup": seo,
            "launched": project.launched,
        }

    # ------------------------------------------------------------------
    # Dashboard & checklist
    # ------------------------------------------------------------------

    def dashboard(self) -> str:
        """Return a summary of usage stats and available tools by tier."""
        cfg = self._tier_config
        limit = cfg.max_plans_per_month if cfg.max_plans_per_month is not None else "Unlimited"
        plans_remaining = (
            (cfg.max_plans_per_month - self._plan_count)
            if cfg.max_plans_per_month is not None
            else "Unlimited"
        )
        lines = [
            "=" * 50,
            f"  Business Launch Pad — {cfg.name} Tier",
            "=" * 50,
            f"  Price:         ${cfg.price_usd_monthly}/month",
            f"  Plans used:    {self._plan_count} / {limit}",
            f"  Plans left:    {plans_remaining}",
            "",
            "  Available Features:",
        ]
        for feat in cfg.features:
            lines.append(f"    ✓ {feat}")
        lines.append("=" * 50)
        return "\n".join(lines)

    def get_launch_checklist(self) -> list[str]:
        """Return an ordered checklist of steps for launching a business."""
        return [
            "1. Define your business idea and value proposition",
            "2. Conduct market research and competitive analysis",
            "3. Generate a comprehensive business plan",
            "4. Identify your target market and build customer personas",
            "5. Perform SWOT analysis",
            "6. Choose and register your business entity type",
            "7. Apply for an EIN (Employer Identification Number)",
            "8. Open a dedicated business bank account",
            "9. Create your brand identity (logo, colors, voice)",
            "10. Register your domain name",
            "11. Build and launch your website with SEO foundations",
            "12. Set up social media profiles",
            "13. Create a go-to-market strategy",
            "14. Launch marketing campaigns",
            "15. Track KPIs and iterate based on data",
        ]
