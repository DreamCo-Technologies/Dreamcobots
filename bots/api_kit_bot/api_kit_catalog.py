"""
API Kit Catalog — pre-made AI-as-a-Service bot kits for the DreamCo API Kit Bot.

Provides 20+ ready-to-deploy API kits across industries including healthcare,
finance, e-commerce, HR, education, legal, and more.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass, field
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

HEALTHCARE_DIAGNOSTICS = "healthcare_diagnostics"
PRODUCTIVITY = "productivity"
ENTERTAINMENT = "entertainment"
FINANCE = "finance"
E_COMMERCE = "e_commerce"
HR = "hr"
EDUCATION = "education"
MARKETING = "marketing"
LEGAL = "legal"
LOGISTICS = "logistics"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class EndpointSpec:
    """Specification for a single API endpoint."""

    method: str
    path: str
    description: str
    params: list = field(default_factory=list)
    response_schema: str = "{}"


@dataclass
class APIKit:
    """A pre-made AI-as-a-Service bot kit."""

    kit_id: str
    name: str
    category: str
    description: str
    endpoints: list
    sample_code: str
    monthly_price_usd: float
    setup_fee_usd: float
    ai_model_type: str
    response_time_ms: int

    def to_dict(self) -> dict:
        return {
            "kit_id": self.kit_id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "endpoints": [
                e.__dict__ if hasattr(e, "__dict__") else e for e in self.endpoints
            ],
            "sample_code": self.sample_code,
            "monthly_price_usd": self.monthly_price_usd,
            "setup_fee_usd": self.setup_fee_usd,
            "ai_model_type": self.ai_model_type,
            "response_time_ms": self.response_time_ms,
        }


# ---------------------------------------------------------------------------
# Kit catalogue (20+ kits)
# ---------------------------------------------------------------------------

_KITS: list = [
    APIKit(
        kit_id="kit_001",
        name="MedDiagnosis AI",
        category=HEALTHCARE_DIAGNOSTICS,
        description="Symptom checker and triage assistant powered by clinical NLP.",
        endpoints=[
            EndpointSpec("POST", "/diagnose", "Submit symptoms and receive triage output."),
            EndpointSpec("GET", "/conditions/{id}", "Retrieve condition details."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/meddiagnosis/diagnose",\n'
            '    json={"symptoms": ["fever", "cough"]})\n'
            'print(r.json())'
        ),
        monthly_price_usd=79.0,
        setup_fee_usd=0.0,
        ai_model_type="clinical_nlp",
        response_time_ms=320,
    ),
    APIKit(
        kit_id="kit_002",
        name="TaskFlow AI",
        category=PRODUCTIVITY,
        description="Intelligent task prioritisation and scheduling assistant.",
        endpoints=[
            EndpointSpec("POST", "/tasks", "Create and prioritise a task list."),
            EndpointSpec("GET", "/schedule", "Retrieve optimised daily schedule."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/taskflow/tasks",\n'
            '    json={"tasks": ["write report", "team standup"]})\n'
            'print(r.json())'
        ),
        monthly_price_usd=19.0,
        setup_fee_usd=0.0,
        ai_model_type="transformer",
        response_time_ms=150,
    ),
    APIKit(
        kit_id="kit_003",
        name="StoryGen AI",
        category=ENTERTAINMENT,
        description="Generative storytelling engine for interactive narratives.",
        endpoints=[
            EndpointSpec("POST", "/story/generate", "Generate a story from a prompt."),
            EndpointSpec("POST", "/story/continue", "Continue an existing story."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/storygen/story/generate",\n'
            '    json={"prompt": "A dragon discovers coffee"})\n'
            'print(r.json())'
        ),
        monthly_price_usd=29.0,
        setup_fee_usd=0.0,
        ai_model_type="gpt_large",
        response_time_ms=480,
    ),
    APIKit(
        kit_id="kit_004",
        name="PortfolioAdvisor AI",
        category=FINANCE,
        description="AI-powered investment portfolio analysis and rebalancing.",
        endpoints=[
            EndpointSpec("POST", "/portfolio/analyse", "Analyse portfolio risk/return."),
            EndpointSpec("POST", "/portfolio/rebalance", "Suggest rebalancing actions."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/portfolioadvisor/portfolio/analyse",\n'
            '    json={"holdings": [{"ticker": "AAPL", "weight": 0.4}]})\n'
            'print(r.json())'
        ),
        monthly_price_usd=99.0,
        setup_fee_usd=49.0,
        ai_model_type="financial_llm",
        response_time_ms=280,
    ),
    APIKit(
        kit_id="kit_005",
        name="ShopAssist AI",
        category=E_COMMERCE,
        description="Personalised product recommendation and upsell engine.",
        endpoints=[
            EndpointSpec("POST", "/recommend", "Get personalised product recommendations."),
            EndpointSpec("POST", "/upsell", "Suggest upsell/cross-sell products."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/shopassist/recommend",\n'
            '    json={"user_id": "u123", "cart": ["SKU-001"]})\n'
            'print(r.json())'
        ),
        monthly_price_usd=49.0,
        setup_fee_usd=0.0,
        ai_model_type="collaborative_filter",
        response_time_ms=95,
    ),
    APIKit(
        kit_id="kit_006",
        name="ResumeScreener AI",
        category=HR,
        description="Automated resume parsing, scoring, and candidate ranking.",
        endpoints=[
            EndpointSpec("POST", "/resume/parse", "Parse and extract resume data."),
            EndpointSpec("POST", "/resume/score", "Score resume against a job description."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/resumescreener/resume/score",\n'
            '    json={"resume_text": "...", "job_description": "..."})\n'
            'print(r.json())'
        ),
        monthly_price_usd=59.0,
        setup_fee_usd=0.0,
        ai_model_type="bert_classifier",
        response_time_ms=220,
    ),
    APIKit(
        kit_id="kit_007",
        name="TutorBot AI",
        category=EDUCATION,
        description="Adaptive learning tutor with quiz generation and progress tracking.",
        endpoints=[
            EndpointSpec("POST", "/tutor/explain", "Explain a concept at desired level."),
            EndpointSpec("POST", "/tutor/quiz", "Generate quiz questions on a topic."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/tutorbot/tutor/explain",\n'
            '    json={"topic": "photosynthesis", "level": "middle_school"})\n'
            'print(r.json())'
        ),
        monthly_price_usd=29.0,
        setup_fee_usd=0.0,
        ai_model_type="gpt_medium",
        response_time_ms=310,
    ),
    APIKit(
        kit_id="kit_008",
        name="CopyWriter AI",
        category=MARKETING,
        description="High-conversion marketing copy and ad creative generator.",
        endpoints=[
            EndpointSpec("POST", "/copy/ad", "Generate ad copy variants."),
            EndpointSpec("POST", "/copy/email", "Draft marketing email sequences."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/copywriter/copy/ad",\n'
            '    json={"product": "running shoes", "tone": "energetic"})\n'
            'print(r.json())'
        ),
        monthly_price_usd=39.0,
        setup_fee_usd=0.0,
        ai_model_type="gpt_large",
        response_time_ms=400,
    ),
    APIKit(
        kit_id="kit_009",
        name="ContractReview AI",
        category=LEGAL,
        description="Legal contract analysis, risk flagging, and clause summarisation.",
        endpoints=[
            EndpointSpec("POST", "/contract/analyse", "Analyse a contract for risks."),
            EndpointSpec("POST", "/contract/summarise", "Summarise key clauses."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/contractreview/contract/analyse",\n'
            '    json={"contract_text": "..."})\n'
            'print(r.json())'
        ),
        monthly_price_usd=129.0,
        setup_fee_usd=99.0,
        ai_model_type="legal_llm",
        response_time_ms=510,
    ),
    APIKit(
        kit_id="kit_010",
        name="RouteOptimizer AI",
        category=LOGISTICS,
        description="Multi-stop route optimisation and ETA prediction engine.",
        endpoints=[
            EndpointSpec("POST", "/route/optimise", "Optimise delivery routes."),
            EndpointSpec("GET", "/route/eta/{route_id}", "Get ETA for a route."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/routeoptimizer/route/optimise",\n'
            '    json={"stops": ["NYC", "Boston", "Philadelphia"]})\n'
            'print(r.json())'
        ),
        monthly_price_usd=69.0,
        setup_fee_usd=0.0,
        ai_model_type="graph_nn",
        response_time_ms=180,
    ),
    APIKit(
        kit_id="kit_011",
        name="FraudShield AI",
        category=FINANCE,
        description="Real-time transaction fraud detection with explainable scores.",
        endpoints=[
            EndpointSpec("POST", "/fraud/score", "Score a transaction for fraud risk."),
            EndpointSpec("GET", "/fraud/rules", "List active fraud detection rules."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/fraudshield/fraud/score",\n'
            '    json={"amount": 999.99, "merchant": "AcmeCorp", "user_id": "u42"})\n'
            'print(r.json())'
        ),
        monthly_price_usd=149.0,
        setup_fee_usd=99.0,
        ai_model_type="xgboost_ensemble",
        response_time_ms=45,
    ),
    APIKit(
        kit_id="kit_012",
        name="SentimentRadar AI",
        category=MARKETING,
        description="Brand sentiment analysis across social media and reviews.",
        endpoints=[
            EndpointSpec("POST", "/sentiment/analyse", "Analyse sentiment of text."),
            EndpointSpec("POST", "/sentiment/batch", "Batch sentiment analysis."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/sentimentradar/sentiment/analyse",\n'
            '    json={"text": "This product changed my life!"})\n'
            'print(r.json())'
        ),
        monthly_price_usd=25.0,
        setup_fee_usd=0.0,
        ai_model_type="roberta_sentiment",
        response_time_ms=90,
    ),
    APIKit(
        kit_id="kit_013",
        name="OnboardingBot AI",
        category=HR,
        description="Automated employee onboarding workflow and checklist manager.",
        endpoints=[
            EndpointSpec("POST", "/onboarding/start", "Initiate onboarding for a new hire."),
            EndpointSpec("GET", "/onboarding/{id}/status", "Get onboarding progress."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/onboardingbot/onboarding/start",\n'
            '    json={"employee_id": "e001", "role": "engineer"})\n'
            'print(r.json())'
        ),
        monthly_price_usd=45.0,
        setup_fee_usd=0.0,
        ai_model_type="workflow_ai",
        response_time_ms=130,
    ),
    APIKit(
        kit_id="kit_014",
        name="DrugInteraction AI",
        category=HEALTHCARE_DIAGNOSTICS,
        description="Medication interaction checker for clinical decision support.",
        endpoints=[
            EndpointSpec("POST", "/drugs/interactions", "Check interactions between drugs."),
            EndpointSpec("GET", "/drugs/{id}", "Get drug information."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/druginteraction/drugs/interactions",\n'
            '    json={"drugs": ["aspirin", "warfarin"]})\n'
            'print(r.json())'
        ),
        monthly_price_usd=89.0,
        setup_fee_usd=49.0,
        ai_model_type="biomedical_nlp",
        response_time_ms=200,
    ),
    APIKit(
        kit_id="kit_015",
        name="CodeReview AI",
        category=PRODUCTIVITY,
        description="Automated code review, bug detection, and style suggestions.",
        endpoints=[
            EndpointSpec("POST", "/code/review", "Submit code for review."),
            EndpointSpec("POST", "/code/explain", "Explain what a code snippet does."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/codereview/code/review",\n'
            '    json={"code": "def foo(): pass", "language": "python"})\n'
            'print(r.json())'
        ),
        monthly_price_usd=35.0,
        setup_fee_usd=0.0,
        ai_model_type="codex",
        response_time_ms=260,
    ),
    APIKit(
        kit_id="kit_016",
        name="InventoryPredict AI",
        category=LOGISTICS,
        description="Demand forecasting and inventory optimisation for retail.",
        endpoints=[
            EndpointSpec("POST", "/inventory/forecast", "Forecast demand for SKUs."),
            EndpointSpec("POST", "/inventory/reorder", "Generate reorder recommendations."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/inventorypredict/inventory/forecast",\n'
            '    json={"sku": "SKU-999", "horizon_days": 30})\n'
            'print(r.json())'
        ),
        monthly_price_usd=55.0,
        setup_fee_usd=0.0,
        ai_model_type="time_series_lstm",
        response_time_ms=340,
    ),
    APIKit(
        kit_id="kit_017",
        name="EduPath AI",
        category=EDUCATION,
        description="Personalised learning path generator for professional upskilling.",
        endpoints=[
            EndpointSpec("POST", "/path/generate", "Generate a personalised learning path."),
            EndpointSpec("GET", "/path/{id}/progress", "Track learning path progress."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/edupath/path/generate",\n'
            '    json={"goal": "machine learning engineer", "current_skills": ["python"]})\n'
            'print(r.json())'
        ),
        monthly_price_usd=39.0,
        setup_fee_usd=0.0,
        ai_model_type="graph_recommender",
        response_time_ms=290,
    ),
    APIKit(
        kit_id="kit_018",
        name="PriceOptimizer AI",
        category=E_COMMERCE,
        description="Dynamic pricing engine with competitor price tracking.",
        endpoints=[
            EndpointSpec("POST", "/price/optimise", "Get optimal price for a product."),
            EndpointSpec("GET", "/price/competitors/{sku}", "Get competitor prices."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/priceoptimizer/price/optimise",\n'
            '    json={"sku": "SKU-007", "cost": 12.50, "market_data": {}})\n'
            'print(r.json())'
        ),
        monthly_price_usd=65.0,
        setup_fee_usd=0.0,
        ai_model_type="rl_pricing",
        response_time_ms=120,
    ),
    APIKit(
        kit_id="kit_019",
        name="ComplianceChecker AI",
        category=LEGAL,
        description="Regulatory compliance scanning for GDPR, HIPAA, and SOC2.",
        endpoints=[
            EndpointSpec("POST", "/compliance/scan", "Scan documents for compliance issues."),
            EndpointSpec("GET", "/compliance/frameworks", "List supported frameworks."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/compliancechecker/compliance/scan",\n'
            '    json={"document": "...", "framework": "GDPR"})\n'
            'print(r.json())'
        ),
        monthly_price_usd=159.0,
        setup_fee_usd=149.0,
        ai_model_type="legal_llm",
        response_time_ms=450,
    ),
    APIKit(
        kit_id="kit_020",
        name="GameNarrator AI",
        category=ENTERTAINMENT,
        description="Real-time AI game master for tabletop RPG and interactive fiction.",
        endpoints=[
            EndpointSpec("POST", "/game/action", "Process a player action."),
            EndpointSpec("POST", "/game/world/describe", "Describe a game world location."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/gamenarrator/game/action",\n'
            '    json={"session_id": "s1", "action": "open the treasure chest"})\n'
            'print(r.json())'
        ),
        monthly_price_usd=34.0,
        setup_fee_usd=0.0,
        ai_model_type="gpt_large",
        response_time_ms=390,
    ),
    APIKit(
        kit_id="kit_021",
        name="CreditScore AI",
        category=FINANCE,
        description="Alternative credit scoring using non-traditional data signals.",
        endpoints=[
            EndpointSpec("POST", "/credit/score", "Generate an alternative credit score."),
            EndpointSpec("GET", "/credit/factors/{id}", "Explain score factors."),
        ],
        sample_code=(
            'import requests\n'
            'r = requests.post("https://api.dreamco.ai/creditscore/credit/score",\n'
            '    json={"applicant_id": "a001", "data_sources": ["bank", "utility"]})\n'
            'print(r.json())'
        ),
        monthly_price_usd=119.0,
        setup_fee_usd=99.0,
        ai_model_type="gradient_boost",
        response_time_ms=165,
    ),
]

_KIT_INDEX: dict = {kit.kit_id: kit for kit in _KITS}


# ---------------------------------------------------------------------------
# Catalog class
# ---------------------------------------------------------------------------

class APIKitCatalog:
    """Browse, search, and retrieve pre-made AI-as-a-Service bot kits."""

    def get_kit(self, kit_id: str) -> Optional[APIKit]:
        """Return a kit by its ID, or None if not found."""
        return _KIT_INDEX.get(kit_id)

    def list_kits(self, category: Optional[str] = None) -> list:
        """Return all kits, optionally filtered by category."""
        if category is None:
            return list(_KITS)
        return [k for k in _KITS if k.category == category]

    def search_kits(self, query: str) -> list:
        """Full-text search across name, description, and category."""
        q = query.lower()
        return [
            k for k in _KITS
            if q in k.name.lower()
            or q in k.description.lower()
            or q in k.category.lower()
            or q in k.ai_model_type.lower()
        ]

    def get_popular_kits(self, n: int = 5) -> list:
        """Return the top-n kits ranked by monthly price (proxy for popularity)."""
        sorted_kits = sorted(_KITS, key=lambda k: k.monthly_price_usd, reverse=True)
        return sorted_kits[:n]

    def get_kit_pricing(self) -> list:
        """Return a pricing summary for all kits."""
        return [
            {
                "kit_id": k.kit_id,
                "name": k.name,
                "category": k.category,
                "monthly_price_usd": k.monthly_price_usd,
                "setup_fee_usd": k.setup_fee_usd,
            }
            for k in _KITS
        ]
