"""Entrepreneur Bot - Business planning, market research, and startup guidance."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.base_bot import BaseBot


class EntrepreneurBot(BaseBot):
    """AI bot for entrepreneurs: business plans, market research, and funding guidance."""

    def __init__(self):
        """Initialize the EntrepreneurBot."""
        super().__init__(
            name="entrepreneur-bot",
            description="Generates business plans, researches markets, finds funding, and guides startups from idea to launch.",
            version="2.0.0",
        )
        self.priority = "medium"

    def run(self):
        """Run the entrepreneur bot main workflow."""
        self.start()
        return self.startup_checklist()

    def generate_business_plan(self, business_idea: str, industry: str) -> dict:
        """Generate a structured business plan for a given idea and industry."""
        self.log(f"Generating business plan: {business_idea[:60]}")
        return {
            "executive_summary": {
                "business_name": f"{industry.title()} Ventures",
                "mission": f"To revolutionize the {industry} industry through {business_idea}.",
                "vision": "Become the market leader within 5 years.",
                "core_values": ["Innovation", "Integrity", "Customer Focus", "Excellence"],
            },
            "business_description": {
                "idea": business_idea,
                "industry": industry,
                "business_model": "B2B SaaS with annual contracts",
                "stage": "Pre-seed / Ideation",
                "legal_structure": "LLC (recommended)",
            },
            "market_analysis": self.research_market(industry, "SMB"),
            "products_services": {
                "primary_offering": business_idea,
                "pricing_model": "Subscription ($49/mo - $499/mo)",
                "usp": f"First AI-powered solution for {industry} businesses",
                "competitive_advantage": "Faster, cheaper, and more accurate than alternatives",
            },
            "financial_projections": {
                "year_1_revenue": "$120,000",
                "year_2_revenue": "$480,000",
                "year_3_revenue": "$1,200,000",
                "break_even_month": "Month 14",
                "initial_investment_needed": "$75,000",
            },
            "funding_plan": self.find_funding("seed", 75000),
            "team_structure": {
                "founder_ceo": "Required",
                "cto_technical_lead": "Required",
                "sales_marketing": "Hire at Month 6",
                "customer_success": "Hire at Month 12",
            },
            "go_to_market": {
                "phase_1": "Launch MVP to 50 beta users (Month 1-3)",
                "phase_2": "Paid acquisition via Google/LinkedIn Ads (Month 4-6)",
                "phase_3": "Partner channel + enterprise sales (Month 7-12)",
            },
            "risk_factors": [
                "Competitive market with established players",
                "Technical execution risk",
                "Customer acquisition cost (CAC) uncertainty",
            ],
        }

    def research_market(self, industry: str, target_market: str) -> dict:
        """Perform market analysis for a given industry and target market."""
        self.log(f"Researching market: {industry} / {target_market}")
        market_sizes = {
            "technology": "$5.2T", "healthcare": "$4.1T", "real estate": "$3.7T",
            "education": "$7.3T", "finance": "$22.5T", "retail": "$26.7T",
        }
        tam = market_sizes.get(industry.lower(), "$1.2T")
        return {
            "industry": industry,
            "target_market": target_market,
            "total_addressable_market": tam,
            "serviceable_available_market": f"~${round(float(tam[1:].replace('T', '')) * 100 if 'T' in tam else float(tam[1:].replace('B', ''))):.0f}B",
            "serviceable_obtainable_market": "$50M (Year 1 target: 0.1%)",
            "growth_rate": "12-18% CAGR",
            "key_trends": [
                f"AI adoption accelerating in {industry}",
                "Remote and hybrid work driving digital transformation",
                "Regulatory compliance creating new demand",
                "Consolidation creating acquisition opportunities",
            ],
            "competitors": [
                {"name": "CompetitorA", "market_share": "18%", "weakness": "High pricing"},
                {"name": "CompetitorB", "market_share": "12%", "weakness": "Poor UX"},
                {"name": "CompetitorC", "market_share": "8%", "weakness": "Limited features"},
            ],
            "customer_segments": [
                f"Small {industry} businesses (1-50 employees): 65% of target",
                f"Mid-market {industry} companies (51-500): 25% of target",
                f"Enterprise {industry} organizations (500+): 10% of target",
            ],
        }

    def find_funding(self, business_stage: str, amount_needed: float) -> dict:
        """Find appropriate funding sources based on business stage and amount needed."""
        self.log(f"Finding funding: stage={business_stage}, amount=${amount_needed}")
        sources = {
            "grants": [
                {"source": "SBIR Phase I", "amount": "$275,000", "match": "High", "type": "non-dilutive"},
                {"source": "SBA Microloan", "amount": "Up to $50,000", "match": "High", "type": "debt"},
            ],
            "investors": [
                {"type": "Angel Investors", "typical_check": "$25K-$250K", "equity": "5-15%"},
                {"type": "Seed VC", "typical_check": "$500K-$2M", "equity": "15-25%"},
            ],
            "crowdfunding": [
                {"platform": "Republic", "type": "equity crowdfunding", "max_raise": "$5M"},
                {"platform": "Kickstarter", "type": "rewards-based", "best_for": "consumer products"},
            ],
            "bootstrapping": {
                "strategy": "Reinvest early revenue; aim for profitability before raising",
                "advantage": "Retain 100% equity",
            },
            "recommended": "SBIR Grant + Angel round" if amount_needed < 500000 else "Seed VC round",
            "amount_needed": f"${amount_needed:,.0f}",
        }
        return sources

    def suggest_legal_structure(self, business_type: str) -> dict:
        """Suggest appropriate legal structure based on business type."""
        structures = {
            "LLC": {
                "best_for": "Most small businesses, solopreneurs, service businesses",
                "pros": ["Pass-through taxation", "Limited liability", "Flexible management", "Low cost"],
                "cons": ["Cannot issue stock", "Some investors prefer C-Corp"],
                "setup_cost": "$50-$500 (filing fees vary by state)",
                "formation_time": "1-2 weeks",
            },
            "C-Corporation": {
                "best_for": "Venture-backed startups, businesses planning IPO",
                "pros": ["Issue stock", "VC-friendly", "Unlimited shareholders", "QSBS tax benefits"],
                "cons": ["Double taxation", "More complex compliance", "Higher setup cost"],
                "setup_cost": "$500-$2,000",
                "formation_time": "1-3 weeks",
            },
            "S-Corporation": {
                "best_for": "Small profitable businesses wanting pass-through taxation with corporate benefits",
                "pros": ["Pass-through taxation", "Limited liability", "Credibility"],
                "cons": ["100 shareholder limit", "Only US citizens/residents", "Single class of stock"],
                "setup_cost": "$500-$1,500",
                "formation_time": "2-4 weeks",
            },
        }
        if "tech" in business_type.lower() or "startup" in business_type.lower():
            recommended = "C-Corporation"
        elif "freelance" in business_type.lower() or "consulting" in business_type.lower():
            recommended = "LLC"
        else:
            recommended = "LLC"
        return {
            "business_type": business_type,
            "recommended": recommended,
            "all_options": structures,
            "next_step": f"File your {recommended} in Delaware or your home state for best protection",
        }

    def build_revenue_model(self, business_type: str) -> dict:
        """Build a revenue model with multiple streams for a business type."""
        return {
            "business_type": business_type,
            "primary_revenue_stream": "Subscription / SaaS ($49-$499/month)",
            "secondary_streams": [
                {"stream": "Professional Services / Consulting", "margin": "60-80%"},
                {"stream": "Marketplace Transaction Fees (2-5%)", "margin": "85-95%"},
                {"stream": "Data/Analytics Licensing", "margin": "90%+"},
                {"stream": "White-Label Licensing", "margin": "70%"},
            ],
            "pricing_strategy": "Value-based pricing with freemium entry",
            "ltv_cac_target": "3:1 or better",
            "churn_target": "<5% monthly",
            "unit_economics": {
                "avg_contract_value": "$1,800/year",
                "gross_margin": "75%",
                "payback_period": "8 months",
            },
        }

    def generate_business_name(self, industry: str, keywords: list) -> list:
        """Generate creative business name ideas for a given industry and keywords."""
        kw = keywords[0].capitalize() if keywords else industry.capitalize()
        return [
            f"{kw}AI Solutions",
            f"Pro{kw}Hub",
            f"{industry.capitalize()}Forge",
            f"Smart{kw}Tech",
            f"{kw}Flow Systems",
            f"Apex{kw}Group",
            f"{kw}Ventures Co",
            f"Nova{kw}Labs",
        ]

    def create_pitch_outline(self, business_idea: str) -> dict:
        """Create a pitch deck structure for a business idea."""
        return {
            "slide_count": 12,
            "slides": [
                {"slide": 1, "title": "Cover Slide", "content": "Company name, tagline, presenter info"},
                {"slide": 2, "title": "Problem", "content": f"The {business_idea} problem costs businesses $X billion annually"},
                {"slide": 3, "title": "Solution", "content": f"How {business_idea} solves this uniquely"},
                {"slide": 4, "title": "Market Opportunity", "content": "$TAM / $SAM / $SOM breakdown"},
                {"slide": 5, "title": "Product Demo", "content": "Screenshots / mockups / demo video link"},
                {"slide": 6, "title": "Business Model", "content": "How you make money - revenue streams"},
                {"slide": 7, "title": "Traction", "content": "Users, revenue, growth metrics, logos"},
                {"slide": 8, "title": "Go-to-Market", "content": "Customer acquisition strategy"},
                {"slide": 9, "title": "Competition", "content": "Competitive landscape and your advantages"},
                {"slide": 10, "title": "Team", "content": "Founders and key team with relevant experience"},
                {"slide": 11, "title": "Financials", "content": "3-year projections, unit economics"},
                {"slide": 12, "title": "The Ask", "content": "Funding amount, use of funds, milestones"},
            ],
            "tip": "Keep each slide to ONE key message. Less is more.",
        }

    def startup_checklist(self) -> dict:
        """Return a comprehensive step-by-step startup guide."""
        return {
            "phase_1_validate": [
                "Write a one-page business model canvas",
                "Interview 20 potential customers about the problem",
                "Build and test an MVP or prototype",
                "Get 3 letters of intent from potential customers",
                "Validate willingness to pay",
            ],
            "phase_2_build": [
                "Register LLC or C-Corp (use Stripe Atlas or LegalZoom)",
                "Open a business bank account",
                "Set up accounting (QuickBooks or Wave)",
                "Hire first contractor or employee",
                "Build v1.0 of product",
            ],
            "phase_3_launch": [
                "Launch landing page with email capture",
                "Announce on Product Hunt, Hacker News, LinkedIn",
                "Onboard first 10 paying customers",
                "Set up customer success process",
                "Start collecting testimonials and case studies",
            ],
            "phase_4_grow": [
                "Raise pre-seed or seed funding if needed",
                "Hire sales and marketing",
                "Scale customer acquisition channels",
                "Build partner/channel program",
                "Prepare for Series A metrics",
            ],
        }
