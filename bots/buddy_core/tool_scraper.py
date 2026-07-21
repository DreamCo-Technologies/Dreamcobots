"""
Tool Scraper — Behavior Analysis Module for Buddy Core.

Analyzes external tools, APIs, SaaS platforms, and code libraries by
inspecting their public metadata (endpoint patterns, documentation keywords,
capability tags) to produce a structured ``ToolProfile`` that the
``ToolReplicationEngine`` can use to generate Buddy-native equivalents.

Part of the Buddy Core System — adheres to the GLOBAL AI SOURCES FLOW framework.

Architecture
------------
The scraper participates in Stage 1 (Data Ingestion) of the GLOBAL AI SOURCES
FLOW pipeline:

  External Tool / API / Platform
          │
          ▼
  ToolScraper.analyze(...)          ← behavior + capability extraction
          │
          ▼
  ToolProfile                       ← structured capability map
          │
          ▼
  ToolReplicationEngine             ← generates Buddy-native equivalent
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class PlatformType(Enum):
    """High-level category of the external tool being analyzed."""
    SAAS = "saas"
    API = "api"
    CODE_LIBRARY = "code_library"
    AUTOMATION = "automation"
    DATABASE = "database"
    MESSAGING = "messaging"
    PAYMENT = "payment"
    ANALYTICS = "analytics"
    CRM = "crm"
    DEVOPS = "devops"
    AI_ML = "ai_ml"
    ECOMMERCE = "ecommerce"
    HEALTHCARE = "healthcare"
    IOT = "iot"
    UNKNOWN = "unknown"


class CapabilityTag(Enum):
    """Atomic capability that a tool provides."""
    CRUD = "crud"
    WEBHOOKS = "webhooks"
    STREAMING = "streaming"
    OAUTH = "oauth"
    API_KEY_AUTH = "api_key_auth"
    RATE_LIMITING = "rate_limiting"
    PAGINATION = "pagination"
    BATCH_OPERATIONS = "batch_operations"
    SEARCH = "search"
    ANALYTICS = "analytics"
    NOTIFICATIONS = "notifications"
    FILE_UPLOAD = "file_upload"
    REAL_TIME = "real_time"
    WORKFLOW_AUTOMATION = "workflow_automation"
    PAYMENT_PROCESSING = "payment_processing"
    SUBSCRIPTION_BILLING = "subscription_billing"
    EMAIL_DELIVERY = "email_delivery"
    SMS_DELIVERY = "sms_delivery"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    MACHINE_LEARNING = "machine_learning"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    GEOLOCATION = "geolocation"
    SCHEDULING = "scheduling"
    REPORTING = "reporting"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ToolProfile:
    """
    Structured capability map extracted from an external tool.

    This is the primary output of :class:`ToolScraper`.  A ToolProfile
    contains everything the :class:`ToolReplicationEngine` needs to build a
    Buddy-native equivalent.
    """

    tool_name: str
    platform_type: PlatformType
    description: str
    base_url: Optional[str]
    capabilities: list[CapabilityTag] = field(default_factory=list)
    industry_tags: list[str] = field(default_factory=list)
    auth_type: str = "api_key"
    is_open_source: bool = False
    has_free_tier: bool = True
    language_hints: list[str] = field(default_factory=list)
    workflow_steps: list[str] = field(default_factory=list)
    replication_priority: int = 5  # 1 (low) – 10 (high)
    raw_metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialise to a plain dictionary."""
        return {
            "tool_name": self.tool_name,
            "platform_type": self.platform_type.value,
            "description": self.description,
            "base_url": self.base_url,
            "capabilities": [c.value for c in self.capabilities],
            "industry_tags": self.industry_tags,
            "auth_type": self.auth_type,
            "is_open_source": self.is_open_source,
            "has_free_tier": self.has_free_tier,
            "language_hints": self.language_hints,
            "workflow_steps": self.workflow_steps,
            "replication_priority": self.replication_priority,
        }


# ---------------------------------------------------------------------------
# Keyword → capability mapping
# ---------------------------------------------------------------------------

_KEYWORD_CAPABILITY_MAP: list[tuple[list[str], CapabilityTag]] = [
    (["webhook", "hook", "callback"], CapabilityTag.WEBHOOKS),
    (["stream", "real-time", "realtime", "websocket", "sse"], CapabilityTag.STREAMING),
    (["oauth", "oauth2", "openid"], CapabilityTag.OAUTH),
    (["api key", "apikey", "bearer token", "secret key"], CapabilityTag.API_KEY_AUTH),
    (["rate limit", "throttle", "quota"], CapabilityTag.RATE_LIMITING),
    (["pagination", "page", "cursor", "offset"], CapabilityTag.PAGINATION),
    (["batch", "bulk"], CapabilityTag.BATCH_OPERATIONS),
    (["search", "query", "filter"], CapabilityTag.SEARCH),
    (["analytics", "metric", "statistic", "report"], CapabilityTag.ANALYTICS),
    (["notif", "push", "alert"], CapabilityTag.NOTIFICATIONS),
    (["file", "upload", "attachment", "media"], CapabilityTag.FILE_UPLOAD),
    (["real-time", "live", "socket", "push"], CapabilityTag.REAL_TIME),
    (["workflow", "automate", "trigger", "action"], CapabilityTag.WORKFLOW_AUTOMATION),
    (["payment", "charge", "transaction", "checkout"], CapabilityTag.PAYMENT_PROCESSING),
    (["subscription", "billing", "recurring", "invoice"], CapabilityTag.SUBSCRIPTION_BILLING),
    (["email", "smtp", "send mail", "transactional"], CapabilityTag.EMAIL_DELIVERY),
    (["sms", "text message", "twilio"], CapabilityTag.SMS_DELIVERY),
    (["export", "csv", "download"], CapabilityTag.DATA_EXPORT),
    (["import", "ingest", "upload data"], CapabilityTag.DATA_IMPORT),
    (["machine learning", "ml model", "train", "predict"], CapabilityTag.MACHINE_LEARNING),
    (["nlp", "natural language", "gpt", "llm", "text generation"], CapabilityTag.NLP),
    (["image", "vision", "detect", "ocr"], CapabilityTag.COMPUTER_VISION),
    (["geo", "location", "coordinates", "map", "geocod"], CapabilityTag.GEOLOCATION),
    (["schedule", "cron", "calendar", "task"], CapabilityTag.SCHEDULING),
    (["report", "dashboard", "insight", "kpi"], CapabilityTag.REPORTING),
    (["create", "read", "update", "delete", "crud", "rest"], CapabilityTag.CRUD),
]

# Keyword → platform type (ordered: most-specific first)
_PLATFORM_TYPE_MAP: list[tuple[list[str], PlatformType]] = [
    (["payment", "billing", "stripe", "paypal", "square"], PlatformType.PAYMENT),
    (["crm", "salesforce", "hubspot", "contact"], PlatformType.CRM),
    (["analytics", "mixpanel", "amplitude", "segment"], PlatformType.ANALYTICS),
    (["messaging", "slack", "discord", "telegram", "whatsapp"], PlatformType.MESSAGING),
    (["database", "postgres", "mongo", "redis", "mysql"], PlatformType.DATABASE),
    (["devops", "ci/cd", "docker", "kubernetes", "github actions"], PlatformType.DEVOPS),
    (["automation", "zapier", "n8n", "make.com", "workflow automate"], PlatformType.AUTOMATION),
    (["ml", "ai", "tensorflow", "pytorch", "openai", "gpt"], PlatformType.AI_ML),
    (["ecommerce", "shopify", "woocommerce", "amazon"], PlatformType.ECOMMERCE),
    (["healthcare", "ehr", "fhir", "health", "medical"], PlatformType.HEALTHCARE),
    (["iot", "mqtt", "device", "sensor", "hardware"], PlatformType.IOT),
    (["library", "package", "sdk", "pip", "npm", "pypi"], PlatformType.CODE_LIBRARY),
    (["saas", "platform", "service"], PlatformType.SAAS),
]


# ---------------------------------------------------------------------------
# Tool Scraper
# ---------------------------------------------------------------------------

class ToolScraperError(Exception):
    """Raised when tool analysis fails."""


class ToolScraper:
    """
    Analyzes external tools and APIs to produce :class:`ToolProfile` objects.

    The scraper operates on publicly available metadata (tool name, description,
    endpoint URL, documentation text) and applies keyword heuristics to infer
    platform type, capabilities, industry tags, and replication priority.

    In production this class would make live HTTP calls to public documentation
    and API specification endpoints.  The current implementation uses
    keyword-based analysis so it works offline and in sandboxed environments.

    Part of Stage 1 (Data Ingestion) of the GLOBAL AI SOURCES FLOW pipeline.

    Usage
    -----
    ::

        scraper = ToolScraper()
        profile = scraper.analyze(
            tool_name="Stripe",
            description="Online payment processing and subscription billing.",
            base_url="https://api.stripe.com/v1",
        )
        print(profile.capabilities)
    """

    # ------------------------------------------------------------------
    # Core analysis
    # ------------------------------------------------------------------

    def analyze(
        self,
        tool_name: str,
        description: str,
        base_url: Optional[str] = None,
        extra_keywords: Optional[list[str]] = None,
        is_open_source: bool = False,
        has_free_tier: bool = True,
    ) -> ToolProfile:
        """
        Analyze a tool and return a structured :class:`ToolProfile`.

        Parameters
        ----------
        tool_name : str
            Human-readable name of the tool (e.g. ``"Stripe"``).
        description : str
            One or two sentence description of what the tool does.
        base_url : str, optional
            Base API endpoint (used for URL pattern analysis).
        extra_keywords : list[str], optional
            Additional keywords to supplement capability detection.
        is_open_source : bool
            Whether the tool is open source.
        has_free_tier : bool
            Whether the tool offers a free plan.

        Returns
        -------
        ToolProfile
        """
        if not tool_name or not tool_name.strip():
            raise ToolScraperError("tool_name must be a non-empty string.")
        if not description or not description.strip():
            raise ToolScraperError("description must be a non-empty string.")

        corpus = " ".join(
            list(filter(None, [tool_name.lower(), description.lower(), base_url or ""]))
            + [kw.lower() for kw in (extra_keywords or [])]
        )

        platform_type = self._detect_platform_type(corpus)
        capabilities = self._detect_capabilities(corpus)
        industry_tags = self._detect_industry_tags(corpus)
        auth_type = self._detect_auth_type(corpus)
        language_hints = self._detect_language_hints(corpus)
        workflow_steps = self._infer_workflow_steps(capabilities)
        priority = self._compute_priority(capabilities, industry_tags)

        return ToolProfile(
            tool_name=tool_name,
            platform_type=platform_type,
            description=description,
            base_url=base_url,
            capabilities=capabilities,
            industry_tags=industry_tags,
            auth_type=auth_type,
            is_open_source=is_open_source,
            has_free_tier=has_free_tier,
            language_hints=language_hints,
            workflow_steps=workflow_steps,
            replication_priority=priority,
            raw_metadata={
                "source": "ToolScraper.analyze",
                "corpus_length": len(corpus),
            },
        )

    def analyze_batch(self, tools: list[dict]) -> list[ToolProfile]:
        """
        Analyze multiple tools in one call.

        Parameters
        ----------
        tools : list[dict]
            Each dict must contain at minimum ``"tool_name"`` and
            ``"description"`` keys.  Optional keys mirror :meth:`analyze`
            parameters.

        Returns
        -------
        list[ToolProfile]
        """
        profiles = []
        for spec in tools:
            profile = self.analyze(
                tool_name=spec["tool_name"],
                description=spec["description"],
                base_url=spec.get("base_url"),
                extra_keywords=spec.get("extra_keywords", []),
                is_open_source=spec.get("is_open_source", False),
                has_free_tier=spec.get("has_free_tier", True),
            )
            profiles.append(profile)
        return profiles

    # ------------------------------------------------------------------
    # Detection helpers
    # ------------------------------------------------------------------

    def _detect_platform_type(self, corpus: str) -> PlatformType:
        for keywords, ptype in _PLATFORM_TYPE_MAP:
            if any(kw in corpus for kw in keywords):
                return ptype
        return PlatformType.UNKNOWN

    def _detect_capabilities(self, corpus: str) -> list[CapabilityTag]:
        found: list[CapabilityTag] = []
        seen: set[CapabilityTag] = set()
        for keywords, cap in _KEYWORD_CAPABILITY_MAP:
            if any(kw in corpus for kw in keywords) and cap not in seen:
                found.append(cap)
                seen.add(cap)
        return found

    def _detect_industry_tags(self, corpus: str) -> list[str]:
        tag_map: list[tuple[list[str], str]] = [
            (["real_estate", "property", "zillow", "mortgage", "mls"], "real_estate"),
            (["finance", "fintech", "banking", "invest", "stock", "trade"], "finance"),
            (["health", "medical", "clinical", "patient", "ehr", "fhir"], "health"),
            (["marketing", "campaign", "email marketing", "seo", "ads"], "marketing"),
            (["freelance", "gig", "fiverr", "upwork", "contractor"], "freelance"),
            (["ecommerce", "shop", "store", "product", "inventory"], "ecommerce"),
            (["devops", "ci/cd", "deploy", "container", "cloud"], "devops"),
            (["iot", "sensor", "device", "hardware", "mqtt"], "iot"),
            (["logistics", "shipping", "delivery", "fleet"], "logistics"),
        ]
        tags: list[str] = []
        seen: set[str] = set()
        for keywords, tag in tag_map:
            if any(kw in corpus for kw in keywords) and tag not in seen:
                tags.append(tag)
                seen.add(tag)
        if not tags:
            tags.append("general")
        return tags

    def _detect_auth_type(self, corpus: str) -> str:
        if any(kw in corpus for kw in ("oauth", "oauth2", "openid")):
            return "oauth2"
        if any(kw in corpus for kw in ("jwt", "bearer")):
            return "jwt"
        if any(kw in corpus for kw in ("api key", "apikey", "secret")):
            return "api_key"
        if any(kw in corpus for kw in ("basic auth", "username", "password")):
            return "basic"
        return "api_key"

    def _detect_language_hints(self, corpus: str) -> list[str]:
        lang_map = {
            "python": ["python", "pip", "django", "flask", "fastapi", "pandas"],
            "javascript": ["javascript", "node", "npm", "react", "express"],
            "typescript": ["typescript", "ts", "angular"],
            "java": ["java", "spring", "maven", "gradle"],
            "go": ["golang", "go module"],
            "ruby": ["ruby", "rails", "gem"],
            "php": ["php", "laravel", "composer"],
            "rust": ["rust", "cargo"],
        }
        hints: list[str] = []
        for lang, keywords in lang_map.items():
            if any(kw in corpus for kw in keywords):
                hints.append(lang)
        return hints or ["python", "javascript"]

    def _infer_workflow_steps(self, capabilities: list[CapabilityTag]) -> list[str]:
        """Map detected capabilities to generic workflow step descriptions."""
        step_map: dict[CapabilityTag, str] = {
            CapabilityTag.OAUTH: "1. Authenticate via OAuth2 flow",
            CapabilityTag.API_KEY_AUTH: "1. Load API key from environment variable",
            CapabilityTag.CRUD: "2. Perform CRUD operations via REST endpoints",
            CapabilityTag.WEBHOOKS: "3. Register webhook endpoint for real-time events",
            CapabilityTag.STREAMING: "3. Open streaming connection for live data",
            CapabilityTag.PAGINATION: "4. Paginate through result sets",
            CapabilityTag.BATCH_OPERATIONS: "4. Send batch requests to reduce API calls",
            CapabilityTag.NOTIFICATIONS: "5. Dispatch notifications on trigger events",
            CapabilityTag.DATA_EXPORT: "6. Export results to CSV/JSON",
            CapabilityTag.ANALYTICS: "7. Feed metrics into analytics pipeline",
        }
        steps: list[str] = []
        for cap in capabilities:
            step = step_map.get(cap)
            if step and step not in steps:
                steps.append(step)
        if not steps:
            steps = [
                "1. Authenticate with the API",
                "2. Fetch data via REST endpoints",
                "3. Process and normalise results",
                "4. Store or forward processed data",
            ]
        return steps

    def _compute_priority(
        self,
        capabilities: list[CapabilityTag],
        industry_tags: list[str],
    ) -> int:
        """
        Compute a replication priority score (1–10).

        Higher scores are assigned to tools with payment, analytics, or
        automation capabilities, and tools that serve multiple industries.
        """
        score = 5
        high_value_caps = {
            CapabilityTag.PAYMENT_PROCESSING,
            CapabilityTag.SUBSCRIPTION_BILLING,
            CapabilityTag.WORKFLOW_AUTOMATION,
            CapabilityTag.MACHINE_LEARNING,
            CapabilityTag.NLP,
        }
        score += sum(1 for c in capabilities if c in high_value_caps)
        score += min(len(industry_tags) - 1, 2)
        return min(max(score, 1), 10)

    # ------------------------------------------------------------------
    # Catalogue helpers
    # ------------------------------------------------------------------

    def analyze_known_platform(self, platform_name: str) -> Optional[ToolProfile]:
        """
        Return a pre-built :class:`ToolProfile` for a well-known platform.

        This avoids live HTTP calls for the most commonly replicated tools.

        Parameters
        ----------
        platform_name : str
            Case-insensitive platform name (e.g. ``"zapier"``, ``"stripe"``).

        Returns
        -------
        ToolProfile | None
        """
        name_lower = platform_name.strip().lower()
        spec = _KNOWN_PLATFORMS.get(name_lower)
        if spec is None:
            return None
        return self.analyze(**spec)

    def list_known_platforms(self) -> list[str]:
        """Return the list of pre-catalogued platform names."""
        return list(_KNOWN_PLATFORMS.keys())


# ---------------------------------------------------------------------------
# Pre-catalogued platform specs
# ---------------------------------------------------------------------------

_KNOWN_PLATFORMS: dict[str, dict] = {
    "zapier": {
        "tool_name": "Zapier",
        "description": (
            "No-code workflow automation connecting 5,000+ apps via triggers "
            "and actions. Supports webhooks, scheduling, and multi-step Zaps."
        ),
        "base_url": "https://api.zapier.com/v1",
        "extra_keywords": [
            "workflow", "automate", "trigger", "action", "webhook", "schedule",
        ],
        "is_open_source": False,
        "has_free_tier": True,
    },
    "stripe": {
        "tool_name": "Stripe",
        "description": (
            "Online payment processing and subscription billing. Supports "
            "checkout sessions, invoices, webhooks, and advanced analytics."
        ),
        "base_url": "https://api.stripe.com/v1",
        "extra_keywords": [
            "payment", "checkout", "subscription", "invoice", "webhook",
            "api key", "analytics", "pagination",
        ],
        "is_open_source": False,
        "has_free_tier": False,
    },
    "github": {
        "tool_name": "GitHub",
        "description": (
            "Git repository hosting with issues, pull requests, Actions CI/CD, "
            "and a rich REST & GraphQL API."
        ),
        "base_url": "https://api.github.com",
        "extra_keywords": [
            "oauth", "webhook", "ci/cd", "workflow", "search", "pagination",
            "devops",
        ],
        "is_open_source": True,
        "has_free_tier": True,
    },
    "slack": {
        "tool_name": "Slack",
        "description": (
            "Team messaging platform with channels, direct messages, bots, "
            "webhooks, and workflow builder integration."
        ),
        "base_url": "https://slack.com/api",
        "extra_keywords": [
            "messaging", "webhook", "bot", "oauth", "real-time", "notification",
        ],
        "is_open_source": False,
        "has_free_tier": True,
    },
    "shopify": {
        "tool_name": "Shopify",
        "description": (
            "E-commerce platform for online stores. REST and GraphQL Admin "
            "APIs cover products, orders, customers, and webhooks."
        ),
        "base_url": "https://yourshop.myshopify.com/admin/api/2023-04",
        "extra_keywords": [
            "ecommerce", "shop", "product", "order", "webhook", "oauth",
            "pagination", "analytics",
        ],
        "is_open_source": False,
        "has_free_tier": False,
    },
    "notion": {
        "tool_name": "Notion",
        "description": (
            "All-in-one workspace for notes, databases, and project management. "
            "REST API supports reading and writing pages, databases, and blocks."
        ),
        "base_url": "https://api.notion.com/v1",
        "extra_keywords": [
            "crud", "database", "api key", "pagination", "search",
        ],
        "is_open_source": False,
        "has_free_tier": True,
    },
    "openai": {
        "tool_name": "OpenAI API",
        "description": (
            "GPT language models for text generation, embeddings, chat, and "
            "fine-tuning. Supports streaming, function calling, and vision."
        ),
        "base_url": "https://api.openai.com/v1",
        "extra_keywords": [
            "nlp", "gpt", "llm", "stream", "api key", "machine learning",
            "python", "javascript",
        ],
        "is_open_source": False,
        "has_free_tier": False,
    },
    "twilio": {
        "tool_name": "Twilio",
        "description": (
            "Cloud communications platform for SMS, voice calls, and WhatsApp "
            "messaging via a programmable REST API."
        ),
        "base_url": "https://api.twilio.com/2010-04-01",
        "extra_keywords": [
            "sms", "messaging", "webhook", "api key", "notification",
        ],
        "is_open_source": False,
        "has_free_tier": False,
    },
}
