"""
Enterprise Integrations Bot — DreamCo hub for Big Tech & AI services.

Provides a unified gateway covering the major service categories offered by
leading global tech and AI companies, including:

  * **Big Tech & AI APIs**: Google Cloud AI, Enterprise AI, Microsoft Azure AI,
    Nvidia AI, AWS AI services.
  * **Cloud / Compute**: Amazon Web Services, Enterprise Cloud, Oracle Cloud,
    Google Cloud.
  * **Big Data AI & Analytics**: Databricks, Palantir, Snowflake, Tableau.
  * **Communication & Collaboration**: Slack, Microsoft Teams, Zoom.
  * **Subscription Resales**: Dynamic e-commerce portal that directly
    licenses and monetises enterprise subscriptions for any integrated
    provider.
  * **Proprietary Dream AI Models**: DreamCo's own foundational model
    layer — DreamLLM, DreamVision, DreamVoice, DreamCode, DreamAnalytics,
    and DreamCollab — competing with every major product category.

All integrations use mock adapters that simulate realistic API responses
without making real network calls, so the bot runs fully offline.  Replace
the built-in ``_adapter`` callables with live HTTP clients in production.

GLOBAL AI SOURCES FLOW: framework imported below.
"""

from __future__ import annotations

import sys
import os
import uuid
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.enterprise_integrations_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class EnterpriseIntegrationsBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class EnterpriseIntegrationsBotError(Exception):
    """Raised when an integration operation fails."""


class ProviderNotFoundError(EnterpriseIntegrationsBotError):
    """Raised when referencing an unknown provider."""


class SubscriptionError(EnterpriseIntegrationsBotError):
    """Raised for subscription management failures."""


# ---------------------------------------------------------------------------
# Provider categories
# ---------------------------------------------------------------------------

class ProviderCategory(str, Enum):
    BIG_TECH_AI = "big_tech_ai"
    CLOUD_COMPUTE = "cloud_compute"
    BIG_DATA_ANALYTICS = "big_data_analytics"
    COMMUNICATION = "communication"
    DREAM_PROPRIETARY = "dream_proprietary"


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

@dataclass
class Provider:
    """Describes a third-party or proprietary integration provider."""

    provider_id: str
    name: str
    category: ProviderCategory
    description: str
    services: List[str]
    min_tier: Tier = Tier.FREE
    adapter: Optional[Callable[[str, dict], dict]] = field(default=None, repr=False)

    def to_dict(self) -> dict:
        return {
            "provider_id": self.provider_id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "services": self.services,
            "min_tier": self.min_tier.value,
        }


# ---------------------------------------------------------------------------
# Mock adapters — replace with live HTTP clients in production
# ---------------------------------------------------------------------------

def _google_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "google_cloud_ai",
        "action": action,
        "status": "ok",
        "result": f"[Google Cloud AI mock] {action} completed",
        "model": payload.get("model", "gemini-pro"),
        "tokens_used": 120,
        "latency_ms": 340,
    }


def _enterprise_ai_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "enterprise_ai",
        "action": action,
        "status": "ok",
        "result": f"[Enterprise AI mock] {action} completed",
        "model": payload.get("model", "granite-13b"),
        "confidence": 0.94,
        "latency_ms": 280,
    }


def _microsoft_azure_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "microsoft_azure_ai",
        "action": action,
        "status": "ok",
        "result": f"[Azure AI mock] {action} completed",
        "model": payload.get("model", "gpt-4o"),
        "tokens_used": 150,
        "latency_ms": 310,
    }


def _nvidia_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "nvidia_ai",
        "action": action,
        "status": "ok",
        "result": f"[Nvidia AI mock] {action} completed",
        "model": payload.get("model", "llama3-70b-nim"),
        "gpu_utilization": "87%",
        "latency_ms": 95,
    }


def _aws_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "aws_ai",
        "action": action,
        "status": "ok",
        "result": f"[AWS AI mock] {action} completed",
        "service": payload.get("service", "bedrock"),
        "model": payload.get("model", "claude-3-sonnet"),
        "latency_ms": 260,
    }


def _databricks_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "databricks",
        "action": action,
        "status": "ok",
        "result": f"[Databricks mock] {action} completed",
        "cluster": payload.get("cluster", "default"),
        "rows_processed": 1_250_000,
        "latency_ms": 820,
    }


def _palantir_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "palantir",
        "action": action,
        "status": "ok",
        "result": f"[Palantir Foundry mock] {action} completed",
        "ontology_objects": 42_000,
        "pipeline": payload.get("pipeline", "default"),
        "latency_ms": 610,
    }


def _snowflake_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "snowflake",
        "action": action,
        "status": "ok",
        "result": f"[Snowflake mock] {action} completed",
        "warehouse": payload.get("warehouse", "COMPUTE_WH"),
        "credits_used": 0.5,
        "rows_returned": 50_000,
        "latency_ms": 390,
    }


def _tableau_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "tableau",
        "action": action,
        "status": "ok",
        "result": f"[Tableau mock] {action} completed",
        "view": payload.get("view", "default"),
        "embed_url": "https://tableau.dreamco.ai/embed/mock",
        "latency_ms": 200,
    }


def _slack_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "slack",
        "action": action,
        "status": "ok",
        "result": f"[Slack mock] {action} completed",
        "channel": payload.get("channel", "#general"),
        "ts": str(time.time()),
    }


def _teams_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "microsoft_teams",
        "action": action,
        "status": "ok",
        "result": f"[Teams mock] {action} completed",
        "channel": payload.get("channel", "General"),
        "message_id": str(uuid.uuid4()),
    }


def _zoom_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "zoom",
        "action": action,
        "status": "ok",
        "result": f"[Zoom mock] {action} completed",
        "meeting_id": payload.get("meeting_id", str(uuid.uuid4())),
        "join_url": "https://zoom.us/j/mock",
    }


def _dream_llm_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "dream_llm",
        "action": action,
        "status": "ok",
        "result": f"[DreamLLM mock] {action} completed",
        "model": "dreamllm-1.5",
        "tokens_used": 200,
        "proprietary": True,
        "latency_ms": 150,
    }


def _dream_analytics_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "dream_analytics",
        "action": action,
        "status": "ok",
        "result": f"[DreamAnalytics mock] {action} completed",
        "model": "dream-analytics-3",
        "insights": 7,
        "proprietary": True,
        "latency_ms": 175,
    }


def _dream_collab_adapter(action: str, payload: dict) -> dict:
    return {
        "provider": "dream_collab",
        "action": action,
        "status": "ok",
        "result": f"[DreamCollab mock] {action} completed",
        "workspace": payload.get("workspace", "default"),
        "participants": 0,
        "proprietary": True,
        "latency_ms": 120,
    }


# ---------------------------------------------------------------------------
# Provider catalogue
# ---------------------------------------------------------------------------

_PROVIDERS: List[Provider] = [
    # -----------------------------------------------------------------------
    # Big Tech AI
    # -----------------------------------------------------------------------
    Provider(
        provider_id="google_cloud_ai",
        name="Google Cloud AI",
        category=ProviderCategory.BIG_TECH_AI,
        description="Google's AI platform — Vertex AI, Gemini, Speech, Vision, NLP.",
        services=["vertex_ai", "gemini", "speech_to_text", "text_to_speech",
                  "vision", "natural_language", "translation", "automl"],
        min_tier=Tier.FREE,
        adapter=_google_adapter,
    ),
    Provider(
        provider_id="enterprise_ai",
        name="Enterprise AI Platform",
        category=ProviderCategory.BIG_TECH_AI,
        description="Enterprise AI's enterprise AI platform — Enterprise Assistant, Discovery, NLU, enterprise AI.",
        services=["enterprise_ai_assistant", "enterprise_ai_discovery", "nlu",
                  "enterprise_ai_speech", "enterprise_ai", "granite_models"],
        min_tier=Tier.FREE,
        adapter=_enterprise_ai_adapter,
    ),
    Provider(
        provider_id="microsoft_azure_ai",
        name="Microsoft Azure AI",
        category=ProviderCategory.BIG_TECH_AI,
        description="Azure AI services — Cognitive Services, Azure OpenAI, Copilot.",
        services=["azure_openai", "cognitive_services", "form_recognizer",
                  "speech_service", "computer_vision", "language_service",
                  "azure_ml", "copilot_studio"],
        min_tier=Tier.PRO,
        adapter=_microsoft_azure_adapter,
    ),
    Provider(
        provider_id="nvidia_ai",
        name="Nvidia AI",
        category=ProviderCategory.BIG_TECH_AI,
        description="Nvidia AI inference — NIM microservices, DGX Cloud, CUDA AI.",
        services=["nim_microservices", "dgx_cloud", "cuda_toolkit",
                  "triton_inference", "nemo", "rapids"],
        min_tier=Tier.PRO,
        adapter=_nvidia_adapter,
    ),
    Provider(
        provider_id="aws_ai",
        name="Amazon AWS AI",
        category=ProviderCategory.BIG_TECH_AI,
        description="AWS AI services — Bedrock, SageMaker, Rekognition, Polly, Lex.",
        services=["bedrock", "sagemaker", "rekognition", "polly",
                  "lex", "comprehend", "textract", "transcribe"],
        min_tier=Tier.PRO,
        adapter=_aws_adapter,
    ),
    # -----------------------------------------------------------------------
    # Cloud / Compute
    # -----------------------------------------------------------------------
    Provider(
        provider_id="aws_cloud",
        name="Amazon Web Services (Cloud)",
        category=ProviderCategory.CLOUD_COMPUTE,
        description="AWS compute, storage, and networking services.",
        services=["ec2", "s3", "lambda", "rds", "cloudfront", "eks", "ecs"],
        min_tier=Tier.PRO,
        adapter=_aws_adapter,
    ),
    Provider(
        provider_id="enterprise_ai_cloud",
        name="Enterprise Cloud",
        category=ProviderCategory.CLOUD_COMPUTE,
        description="Enterprise AI's hybrid cloud platform with AI-optimised workloads.",
        services=["virtual_servers", "code_engine", "cloud_databases",
                  "cloud_object_storage", "openshift"],
        min_tier=Tier.PRO,
        adapter=_enterprise_ai_adapter,
    ),
    Provider(
        provider_id="google_cloud",
        name="Google Cloud Platform",
        category=ProviderCategory.CLOUD_COMPUTE,
        description="Google's cloud compute, storage, and data services.",
        services=["compute_engine", "gke", "cloud_run", "bigquery",
                  "cloud_storage", "cloud_sql", "cloud_spanner"],
        min_tier=Tier.PRO,
        adapter=_google_adapter,
    ),
    Provider(
        provider_id="oracle_cloud",
        name="Oracle Cloud Infrastructure",
        category=ProviderCategory.CLOUD_COMPUTE,
        description="Oracle Cloud — compute, autonomous DB, AI infrastructure.",
        services=["oci_compute", "autonomous_database", "ai_services",
                  "object_storage", "container_engine"],
        min_tier=Tier.ENTERPRISE,
        adapter=lambda a, p: {
            "provider": "oracle_cloud", "action": a, "status": "ok",
            "result": f"[Oracle Cloud mock] {a} completed"
        },
    ),
    # -----------------------------------------------------------------------
    # Big Data AI & Analytics
    # -----------------------------------------------------------------------
    Provider(
        provider_id="databricks",
        name="Databricks",
        category=ProviderCategory.BIG_DATA_ANALYTICS,
        description="Databricks Lakehouse — unified data engineering, ML, and analytics.",
        services=["delta_lake", "mlflow", "spark_sql", "databricks_sql",
                  "automl", "feature_store", "unity_catalog"],
        min_tier=Tier.PRO,
        adapter=_databricks_adapter,
    ),
    Provider(
        provider_id="palantir",
        name="Palantir Foundry",
        category=ProviderCategory.BIG_DATA_ANALYTICS,
        description="Palantir — ontology-driven AI for enterprise data operations.",
        services=["foundry", "gotham", "apollo", "aip",
                  "ontology_builder", "pipeline_builder"],
        min_tier=Tier.ENTERPRISE,
        adapter=_palantir_adapter,
    ),
    Provider(
        provider_id="snowflake",
        name="Snowflake",
        category=ProviderCategory.BIG_DATA_ANALYTICS,
        description="Snowflake Data Cloud — elastic SQL, data sharing, and Cortex AI.",
        services=["snowpark", "cortex_ai", "dynamic_tables",
                  "streamlit", "data_sharing", "marketplace"],
        min_tier=Tier.PRO,
        adapter=_snowflake_adapter,
    ),
    Provider(
        provider_id="tableau",
        name="Tableau",
        category=ProviderCategory.BIG_DATA_ANALYTICS,
        description="Tableau Analytics — interactive dashboards and embedded analytics.",
        services=["tableau_desktop", "tableau_server", "tableau_cloud",
                  "embedded_analytics", "tableau_prep", "ask_data"],
        min_tier=Tier.PRO,
        adapter=_tableau_adapter,
    ),
    # -----------------------------------------------------------------------
    # Communication & Collaboration
    # -----------------------------------------------------------------------
    Provider(
        provider_id="slack",
        name="Slack",
        category=ProviderCategory.COMMUNICATION,
        description="Slack — messaging, workflows, and app integrations.",
        services=["messages", "channels", "workflows", "bots",
                  "webhooks", "block_kit", "canvas"],
        min_tier=Tier.FREE,
        adapter=_slack_adapter,
    ),
    Provider(
        provider_id="microsoft_teams",
        name="Microsoft Teams",
        category=ProviderCategory.COMMUNICATION,
        description="Microsoft Teams — enterprise chat, meetings, and Power Platform bots.",
        services=["channels", "meetings", "bots", "tabs",
                  "messaging_extensions", "power_automate", "graph_api"],
        min_tier=Tier.PRO,
        adapter=_teams_adapter,
    ),
    Provider(
        provider_id="zoom",
        name="Zoom",
        category=ProviderCategory.COMMUNICATION,
        description="Zoom — video meetings, webinars, phone, and Zoom Apps.",
        services=["meetings", "webinars", "phone", "zoom_apps",
                  "contact_center", "rooms", "video_sdk"],
        min_tier=Tier.PRO,
        adapter=_zoom_adapter,
    ),
    # -----------------------------------------------------------------------
    # Proprietary Dream AI Models
    # -----------------------------------------------------------------------
    Provider(
        provider_id="dream_llm",
        name="DreamLLM",
        category=ProviderCategory.DREAM_PROPRIETARY,
        description="DreamCo's proprietary foundation language model — "
                    "competing with GPT-4 / Gemini / Claude.",
        services=["chat", "completion", "summarisation",
                  "translation", "code_generation", "embeddings"],
        min_tier=Tier.FREE,
        adapter=_dream_llm_adapter,
    ),
    Provider(
        provider_id="dream_vision",
        name="DreamVision",
        category=ProviderCategory.DREAM_PROPRIETARY,
        description="DreamCo multimodal vision model — competing with GPT-4o / Gemini Vision.",
        services=["image_analysis", "ocr", "object_detection",
                  "image_generation", "visual_qa"],
        min_tier=Tier.PRO,
        adapter=lambda a, p: {
            "provider": "dream_vision", "action": a, "status": "ok",
            "result": f"[DreamVision mock] {a} completed",
            "model": "dreamvision-1.0", "proprietary": True
        },
    ),
    Provider(
        provider_id="dream_voice",
        name="DreamVoice",
        category=ProviderCategory.DREAM_PROPRIETARY,
        description="DreamCo speech synthesis & recognition — competing with AWS Polly / Azure Speech.",
        services=["text_to_speech", "speech_to_text",
                  "voice_cloning", "real_time_translation"],
        min_tier=Tier.PRO,
        adapter=lambda a, p: {
            "provider": "dream_voice", "action": a, "status": "ok",
            "result": f"[DreamVoice mock] {a} completed",
            "model": "dreamvoice-2.0", "proprietary": True
        },
    ),
    Provider(
        provider_id="dream_code",
        name="DreamCode",
        category=ProviderCategory.DREAM_PROPRIETARY,
        description="DreamCo code generation model — competing with GitHub Copilot / Claude Code.",
        services=["code_completion", "code_review",
                  "test_generation", "refactoring", "documentation"],
        min_tier=Tier.PRO,
        adapter=lambda a, p: {
            "provider": "dream_code", "action": a, "status": "ok",
            "result": f"[DreamCode mock] {a} completed",
            "model": "dreamcode-1.2", "proprietary": True
        },
    ),
    Provider(
        provider_id="dream_analytics",
        name="DreamAnalytics",
        category=ProviderCategory.DREAM_PROPRIETARY,
        description="DreamCo analytics engine — competing with Tableau / Databricks.",
        services=["dashboard", "sql_query", "ml_pipeline",
                  "forecasting", "anomaly_detection", "report_generation"],
        min_tier=Tier.PRO,
        adapter=_dream_analytics_adapter,
    ),
    Provider(
        provider_id="dream_collab",
        name="DreamCollab",
        category=ProviderCategory.DREAM_PROPRIETARY,
        description="DreamCo collaboration workspace — competing with Slack / Teams / Zoom.",
        services=["messaging", "video_calls", "file_sharing",
                  "task_boards", "docs", "ai_assistant"],
        min_tier=Tier.PRO,
        adapter=_dream_collab_adapter,
    ),
]

# Lookup index
_PROVIDER_INDEX: Dict[str, Provider] = {p.provider_id: p for p in _PROVIDERS}


# ---------------------------------------------------------------------------
# Subscription record
# ---------------------------------------------------------------------------

@dataclass
class Subscription:
    """Represents a resold third-party or Dream subscription seat."""

    subscription_id: str
    provider_id: str
    plan: str
    seats: int
    price_per_seat_usd: float
    resale_markup_pct: float
    buyer_id: str
    status: str = "active"
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None

    @property
    def total_price_usd(self) -> float:
        return round(self.seats * self.price_per_seat_usd * (1 + self.resale_markup_pct / 100), 2)

    def to_dict(self) -> dict:
        return {
            "subscription_id": self.subscription_id,
            "provider_id": self.provider_id,
            "plan": self.plan,
            "seats": self.seats,
            "price_per_seat_usd": self.price_per_seat_usd,
            "resale_markup_pct": self.resale_markup_pct,
            "total_price_usd": self.total_price_usd,
            "buyer_id": self.buyer_id,
            "status": self.status,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
        }


# ---------------------------------------------------------------------------
# API call record
# ---------------------------------------------------------------------------

@dataclass
class APICallRecord:
    """Tracks a single outbound API call made through the bot."""

    call_id: str
    provider_id: str
    action: str
    payload: dict
    response: dict
    user_id: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "call_id": self.call_id,
            "provider_id": self.provider_id,
            "action": self.action,
            "payload": self.payload,
            "response": self.response,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Main bot
# ---------------------------------------------------------------------------

class EnterpriseIntegrationsBot:
    """
    DreamCo Enterprise Integrations Bot — unified gateway for Big Tech & AI
    services, analytics platforms, communication tools, subscription resales,
    and proprietary Dream AI Models.

    Tiers
    -----
    FREE       : 5 integrations, 100 calls/month, basic providers.
    PRO        : 30 integrations, 10,000 calls/month, most providers.
    ENTERPRISE : Unlimited integrations & calls, all providers + Dream AI.
    """

    CALL_LIMITS: Dict[Tier, Optional[int]] = {
        Tier.FREE: 100,
        Tier.PRO: 10_000,
        Tier.ENTERPRISE: None,
    }

    INTEGRATION_LIMITS: Dict[Tier, Optional[int]] = {
        Tier.FREE: 5,
        Tier.PRO: 30,
        Tier.ENTERPRISE: None,
    }

    SUBSCRIPTION_SEAT_LIMITS: Dict[Tier, Optional[int]] = {
        Tier.FREE: 0,
        Tier.PRO: 50,
        Tier.ENTERPRISE: None,
    }

    # Default resale markup per tier (%)
    DEFAULT_MARKUP: Dict[Tier, float] = {
        Tier.FREE: 0.0,
        Tier.PRO: 15.0,
        Tier.ENTERPRISE: 25.0,
    }

    def __init__(self, tier: Tier = Tier.FREE, user_id: str = "user"):
        self.tier = tier
        self.user_id = user_id
        self.config = get_tier_config(tier)
        self._call_log: List[APICallRecord] = []
        self._subscriptions: Dict[str, Subscription] = {}
        self._enabled_providers: set = set()
        # Enable providers permitted by this tier automatically
        for p in _PROVIDERS:
            self._check_and_enable_provider(p)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_and_enable_provider(self, provider: Provider) -> bool:
        """Enable a provider if the current tier permits it."""
        tier_order = [Tier.FREE, Tier.PRO, Tier.ENTERPRISE]
        if tier_order.index(self.tier) >= tier_order.index(provider.min_tier):
            self._enabled_providers.add(provider.provider_id)
            return True
        return False

    def _require_tier(self, required: Tier, feature: str) -> None:
        tier_order = [Tier.FREE, Tier.PRO, Tier.ENTERPRISE]
        if tier_order.index(self.tier) < tier_order.index(required):
            raise EnterpriseIntegrationsBotTierError(
                f"'{feature}' requires {required.value.upper()} tier. "
                f"Current tier: {self.tier.value.upper()}. "
                f"Upgrade path: {get_upgrade_path(self.tier)}"
            )

    def _require_provider(self, provider_id: str) -> Provider:
        if provider_id not in _PROVIDER_INDEX:
            raise ProviderNotFoundError(f"Unknown provider: '{provider_id}'")
        provider = _PROVIDER_INDEX[provider_id]
        if provider.provider_id not in self._enabled_providers:
            raise EnterpriseIntegrationsBotTierError(
                f"Provider '{provider.name}' requires "
                f"{provider.min_tier.value.upper()} tier."
            )
        return provider

    def _check_call_quota(self) -> None:
        limit = self.CALL_LIMITS[self.tier]
        if limit is not None and len(self._call_log) >= limit:
            raise EnterpriseIntegrationsBotTierError(
                f"Monthly API call quota ({limit}) exceeded on "
                f"{self.tier.value.upper()} tier. Upgrade to increase limit."
            )

    # ------------------------------------------------------------------
    # Provider management
    # ------------------------------------------------------------------

    def list_providers(
        self,
        category: Optional[ProviderCategory] = None,
    ) -> List[dict]:
        """Return all providers available on the current tier."""
        result = []
        for p in _PROVIDERS:
            if p.provider_id not in self._enabled_providers:
                continue
            if category is not None and p.category != category:
                continue
            result.append(p.to_dict())
        return result

    def list_all_providers(
        self,
        category: Optional[ProviderCategory] = None,
    ) -> List[dict]:
        """Return the full provider catalogue regardless of tier."""
        result = []
        for p in _PROVIDERS:
            if category is not None and p.category != category:
                continue
            d = p.to_dict()
            d["available_on_current_tier"] = (
                p.provider_id in self._enabled_providers
            )
            result.append(d)
        return result

    def get_provider(self, provider_id: str) -> dict:
        """Return details for a single provider."""
        if provider_id not in _PROVIDER_INDEX:
            raise ProviderNotFoundError(f"Unknown provider: '{provider_id}'")
        p = _PROVIDER_INDEX[provider_id]
        d = p.to_dict()
        d["available_on_current_tier"] = (
            p.provider_id in self._enabled_providers
        )
        return d

    # ------------------------------------------------------------------
    # API call routing
    # ------------------------------------------------------------------

    def call_provider(
        self,
        provider_id: str,
        action: str,
        payload: Optional[dict] = None,
    ) -> dict:
        """
        Route an API call to the specified provider.

        Parameters
        ----------
        provider_id : str
            Provider identifier (e.g. ``"google_cloud_ai"``).
        action : str
            Action / endpoint name (e.g. ``"chat"``, ``"query"``).
        payload : dict, optional
            Request payload forwarded to the adapter.
        """
        self._check_call_quota()
        provider = self._require_provider(provider_id)
        payload = payload or {}
        response = provider.adapter(action, payload)
        record = APICallRecord(
            call_id=str(uuid.uuid4()),
            provider_id=provider_id,
            action=action,
            payload=payload,
            response=response,
            user_id=self.user_id,
        )
        self._call_log.append(record)
        return response

    # ------------------------------------------------------------------
    # Convenience wrappers — Big Tech AI
    # ------------------------------------------------------------------

    def google_ai(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call Google Cloud AI."""
        return self.call_provider("google_cloud_ai", action, payload)

    def enterprise_ai(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call Enterprise AI Platform."""
        return self.call_provider("enterprise_ai", action, payload)

    def azure_ai(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call Microsoft Azure AI (PRO+)."""
        return self.call_provider("microsoft_azure_ai", action, payload)

    def nvidia_ai(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call Nvidia AI (PRO+)."""
        return self.call_provider("nvidia_ai", action, payload)

    def aws_ai(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call Amazon AWS AI (PRO+)."""
        return self.call_provider("aws_ai", action, payload)

    # ------------------------------------------------------------------
    # Convenience wrappers — Big Data & Analytics
    # ------------------------------------------------------------------

    def databricks(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call Databricks (PRO+)."""
        return self.call_provider("databricks", action, payload)

    def snowflake(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call Snowflake (PRO+)."""
        return self.call_provider("snowflake", action, payload)

    def tableau(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call Tableau (PRO+)."""
        return self.call_provider("tableau", action, payload)

    def palantir(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call Palantir Foundry (ENTERPRISE)."""
        return self.call_provider("palantir", action, payload)

    # ------------------------------------------------------------------
    # Convenience wrappers — Communication & Collaboration
    # ------------------------------------------------------------------

    def slack(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call Slack."""
        return self.call_provider("slack", action, payload)

    def teams(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call Microsoft Teams (PRO+)."""
        return self.call_provider("microsoft_teams", action, payload)

    def zoom(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call Zoom (PRO+)."""
        return self.call_provider("zoom", action, payload)

    # ------------------------------------------------------------------
    # Convenience wrappers — Proprietary Dream AI Models
    # ------------------------------------------------------------------

    def dream_llm(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call DreamLLM — DreamCo's foundation language model."""
        return self.call_provider("dream_llm", action, payload)

    def dream_vision(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call DreamVision — DreamCo's multimodal vision model (PRO+)."""
        return self.call_provider("dream_vision", action, payload)

    def dream_code(self, action: str, payload: Optional[dict] = None) -> dict:
        """Call DreamCode — DreamCo's code generation model (PRO+)."""
        return self.call_provider("dream_code", action, payload)

    def dream_analytics(
        self, action: str, payload: Optional[dict] = None
    ) -> dict:
        """Call DreamAnalytics — DreamCo's analytics engine (PRO+)."""
        return self.call_provider("dream_analytics", action, payload)

    def dream_collab(
        self, action: str, payload: Optional[dict] = None
    ) -> dict:
        """Call DreamCollab — DreamCo's collaboration workspace (PRO+)."""
        return self.call_provider("dream_collab", action, payload)

    # ------------------------------------------------------------------
    # Multi-provider routing
    # ------------------------------------------------------------------

    def route_to_best(
        self,
        action: str,
        payload: Optional[dict] = None,
        category: ProviderCategory = ProviderCategory.BIG_TECH_AI,
    ) -> dict:
        """
        Route a request to the best available provider in *category*
        (first enabled provider by catalogue order).  Falls back to
        DreamLLM if no third-party provider is available.

        PRO+ tier required for multi-provider routing of external services.
        """
        payload = payload or {}
        candidates = [
            p for p in _PROVIDERS
            if p.category == category and p.provider_id in self._enabled_providers
        ]
        if not candidates:
            return self.dream_llm(action, payload)
        return self.call_provider(candidates[0].provider_id, action, payload)

    # ------------------------------------------------------------------
    # Subscription resales
    # ------------------------------------------------------------------

    def resell_subscription(
        self,
        provider_id: str,
        plan: str,
        seats: int,
        price_per_seat_usd: float,
        buyer_id: str,
        markup_pct: Optional[float] = None,
    ) -> Subscription:
        """
        Create a subscription resale order for a provider (PRO+).

        The bot acts as the reselling intermediary, licensing access to
        the provider's service on behalf of the buyer and applying the
        configured markup for monetisation.

        Parameters
        ----------
        provider_id : str
            Provider to resell (e.g. ``"slack"``, ``"databricks"``).
        plan : str
            The provider's plan name (e.g. ``"pro"``, ``"enterprise"``).
        seats : int
            Number of seats / licences to resell.
        price_per_seat_usd : float
            Cost price per seat (what DreamCo pays the provider).
        buyer_id : str
            Identifier of the purchasing customer.
        markup_pct : float, optional
            Resale markup percentage. Defaults to tier default.
        """
        self._require_tier(Tier.PRO, "subscription resales")
        if provider_id not in _PROVIDER_INDEX:
            raise ProviderNotFoundError(f"Unknown provider: '{provider_id}'")
        if seats <= 0:
            raise SubscriptionError("seats must be a positive integer")
        if price_per_seat_usd < 0:
            raise SubscriptionError("price_per_seat_usd cannot be negative")

        seat_limit = self.SUBSCRIPTION_SEAT_LIMITS[self.tier]
        current_seats = sum(
            s.seats for s in self._subscriptions.values() if s.status == "active"
        )
        if seat_limit is not None and current_seats + seats > seat_limit:
            raise EnterpriseIntegrationsBotTierError(
                f"Seat limit ({seat_limit}) reached on "
                f"{self.tier.value.upper()} tier. Upgrade to ENTERPRISE for unlimited seats."
            )

        effective_markup = markup_pct if markup_pct is not None else self.DEFAULT_MARKUP[self.tier]
        sub = Subscription(
            subscription_id=str(uuid.uuid4()),
            provider_id=provider_id,
            plan=plan,
            seats=seats,
            price_per_seat_usd=price_per_seat_usd,
            resale_markup_pct=effective_markup,
            buyer_id=buyer_id,
        )
        self._subscriptions[sub.subscription_id] = sub
        return sub

    def cancel_subscription(self, subscription_id: str) -> dict:
        """Cancel an active subscription."""
        self._require_tier(Tier.PRO, "subscription management")
        if subscription_id not in self._subscriptions:
            raise SubscriptionError(f"Subscription '{subscription_id}' not found")
        sub = self._subscriptions[subscription_id]
        sub.status = "cancelled"
        return {"subscription_id": subscription_id, "status": "cancelled"}

    def list_subscriptions(self, active_only: bool = True) -> List[dict]:
        """List all resale subscriptions managed by this bot."""
        self._require_tier(Tier.PRO, "subscription management")
        subs = list(self._subscriptions.values())
        if active_only:
            subs = [s for s in subs if s.status == "active"]
        return [s.to_dict() for s in subs]

    def get_resale_revenue(self) -> dict:
        """Return total resale revenue metrics (PRO+)."""
        self._require_tier(Tier.PRO, "resale revenue analytics")
        active = [
            s for s in self._subscriptions.values() if s.status == "active"
        ]
        total_revenue = sum(s.total_price_usd for s in active)
        total_cost = sum(
            s.seats * s.price_per_seat_usd for s in active
        )
        return {
            "active_subscriptions": len(active),
            "total_seats_managed": sum(s.seats for s in active),
            "total_monthly_revenue_usd": round(total_revenue, 2),
            "total_monthly_cost_usd": round(total_cost, 2),
            "gross_profit_usd": round(total_revenue - total_cost, 2),
            "providers_resold": list({s.provider_id for s in active}),
        }

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_usage_stats(self) -> dict:
        """Return API usage statistics for the current session."""
        call_limit = self.CALL_LIMITS[self.tier]
        provider_breakdown: Dict[str, int] = {}
        for record in self._call_log:
            provider_breakdown[record.provider_id] = (
                provider_breakdown.get(record.provider_id, 0) + 1
            )
        return {
            "total_calls": len(self._call_log),
            "call_limit": call_limit,
            "calls_remaining": (
                (call_limit - len(self._call_log)) if call_limit is not None else None
            ),
            "enabled_providers": len(self._enabled_providers),
            "provider_breakdown": provider_breakdown,
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Tier info
    # ------------------------------------------------------------------

    def get_tier_info(self) -> dict:
        """Return tier configuration and feature details."""
        return get_bot_tier_info(self.tier)

    # ------------------------------------------------------------------
    # Chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """Unified natural-language interface for the Enterprise Integrations Bot."""
        msg = message.lower()

        if any(kw in msg for kw in ("providers", "list providers", "available services")):
            providers = self.list_providers()
            return {
                "message": f"{len(providers)} provider(s) available on your tier.",
                "data": providers,
            }

        if any(kw in msg for kw in ("google", "gemini", "vertex")):
            result = self.google_ai("chat", {"prompt": message})
            return {"message": result["result"], "data": result}

        if any(kw in msg for kw in ("enterprise_ai", "enterprise_ai", "enterprise AI")):
            result = self.enterprise_ai("chat", {"prompt": message})
            return {"message": result["result"], "data": result}

        if any(kw in msg for kw in ("azure", "microsoft ai", "copilot")):
            if self.tier == Tier.FREE:
                return {
                    "message": "Microsoft Azure AI requires PRO tier. Upgrade to unlock.",
                    "data": {"upgrade_required": True},
                }
            result = self.azure_ai("chat", {"prompt": message})
            return {"message": result["result"], "data": result}

        if any(kw in msg for kw in ("nvidia", "nim", "dgx")):
            if self.tier == Tier.FREE:
                return {
                    "message": "Nvidia AI requires PRO tier. Upgrade to unlock.",
                    "data": {"upgrade_required": True},
                }
            result = self.nvidia_ai("inference", {"prompt": message})
            return {"message": result["result"], "data": result}

        if any(kw in msg for kw in ("aws", "bedrock", "sagemaker")):
            if self.tier == Tier.FREE:
                return {
                    "message": "AWS AI requires PRO tier. Upgrade to unlock.",
                    "data": {"upgrade_required": True},
                }
            result = self.aws_ai("invoke", {"prompt": message})
            return {"message": result["result"], "data": result}

        if any(kw in msg for kw in ("databricks", "spark", "delta lake")):
            if self.tier == Tier.FREE:
                return {
                    "message": "Databricks requires PRO tier. Upgrade to unlock.",
                    "data": {"upgrade_required": True},
                }
            result = self.databricks("query", {"prompt": message})
            return {"message": result["result"], "data": result}

        if any(kw in msg for kw in ("snowflake", "data cloud")):
            if self.tier == Tier.FREE:
                return {
                    "message": "Snowflake requires PRO tier. Upgrade to unlock.",
                    "data": {"upgrade_required": True},
                }
            result = self.snowflake("query", {"prompt": message})
            return {"message": result["result"], "data": result}

        if any(kw in msg for kw in ("slack", "send message")):
            result = self.slack("post_message", {"channel": "#general", "text": message})
            return {"message": result["result"], "data": result}

        if any(kw in msg for kw in ("teams", "microsoft teams")):
            if self.tier == Tier.FREE:
                return {
                    "message": "Microsoft Teams requires PRO tier. Upgrade to unlock.",
                    "data": {"upgrade_required": True},
                }
            result = self.teams("post_message", {"channel": "General", "text": message})
            return {"message": result["result"], "data": result}

        if any(kw in msg for kw in ("zoom", "meeting")):
            if self.tier == Tier.FREE:
                return {
                    "message": "Zoom requires PRO tier. Upgrade to unlock.",
                    "data": {"upgrade_required": True},
                }
            result = self.zoom("create_meeting", {"topic": message})
            return {"message": result["result"], "data": result}

        if any(kw in msg for kw in ("dreamllm", "dream llm", "dream model")):
            result = self.dream_llm("chat", {"prompt": message})
            return {"message": result["result"], "data": result}

        if any(kw in msg for kw in ("subscribe", "resell", "subscription")):
            if self.tier == Tier.FREE:
                return {
                    "message": "Subscription resales require PRO tier. Upgrade to unlock.",
                    "data": {"upgrade_required": True},
                }
            stats = self.get_resale_revenue()
            return {"message": "Subscription resale stats retrieved.", "data": stats}

        if any(kw in msg for kw in ("stats", "usage", "analytics")):
            stats = self.get_usage_stats()
            return {"message": "Usage statistics retrieved.", "data": stats}

        if any(kw in msg for kw in ("tier", "features", "upgrade")):
            info = self.get_tier_info()
            return {
                "message": (
                    f"Current tier: {info['tier']}. Features: {info['features']}"
                ),
                "data": info,
            }

        # Default — route to DreamLLM
        result = self.dream_llm("chat", {"prompt": message})
        return {"message": result["result"], "data": result}
