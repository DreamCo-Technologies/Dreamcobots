"""
Tool Database for the Buddy Core System.

Pre-built catalogue of 80+ API/library tools that can be auto-injected
into generated bots based on industry and purpose.  Covers all major
code libraries, SaaS platforms, web APIs, automation tools, and developer
frameworks.

Part of the Buddy Core System — adheres to the GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ToolDBError(Exception):
    """Raised when a ToolDB operation fails."""


class ToolCategory(Enum):
    API = "api"
    LIBRARY = "library"
    WEBHOOK = "webhook"
    PAYMENT = "payment"
    SCRAPER = "scraper"
    CRM = "crm"
    ANALYTICS = "analytics"
    DEVOPS = "devops"
    DATABASE = "database"
    MESSAGING = "messaging"
    AUTOMATION = "automation"
    AI_ML = "ai_ml"
    STORAGE = "storage"
    MONITORING = "monitoring"


@dataclass
class Tool:
    """Represents a single integration tool."""

    tool_id: str
    name: str
    category: ToolCategory
    description: str
    industry_tags: list
    api_endpoint: Optional[str]
    is_free: bool
    monthly_cost_usd: float


# ---------------------------------------------------------------------------
# Pre-built catalogue
# ---------------------------------------------------------------------------

_CATALOGUE: list[Tool] = [
    Tool(
        tool_id="zillow_api",
        name="Zillow API",
        category=ToolCategory.API,
        description="Real-estate listing data, home values, and market trends.",
        industry_tags=["real_estate"],
        api_endpoint="https://api.zillow.com/v2",
        is_free=False,
        monthly_cost_usd=49.0,
    ),
    Tool(
        tool_id="trulia",
        name="Trulia",
        category=ToolCategory.SCRAPER,
        description="Property listings and neighbourhood insights scraper.",
        industry_tags=["real_estate"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="google_maps",
        name="Google Maps API",
        category=ToolCategory.API,
        description="Geocoding, routing, and place search.",
        industry_tags=["real_estate", "logistics", "general"],
        api_endpoint="https://maps.googleapis.com/maps/api",
        is_free=False,
        monthly_cost_usd=0.0,  # pay-per-use
    ),
    Tool(
        tool_id="stripe",
        name="Stripe",
        category=ToolCategory.PAYMENT,
        description="Online payment processing and subscription billing.",
        industry_tags=["finance", "general", "freelance", "marketing"],
        api_endpoint="https://api.stripe.com/v1",
        is_free=False,
        monthly_cost_usd=0.0,  # per-transaction fees
    ),
    Tool(
        tool_id="plaid",
        name="Plaid",
        category=ToolCategory.PAYMENT,
        description="Bank account linking and financial data aggregation.",
        industry_tags=["finance"],
        api_endpoint="https://production.plaid.com",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="fiverr_api",
        name="Fiverr API",
        category=ToolCategory.API,
        description="Access Fiverr gig marketplace data and automation.",
        industry_tags=["freelance"],
        api_endpoint="https://api.fiverr.com/v1",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="upwork_api",
        name="Upwork API",
        category=ToolCategory.API,
        description="Freelancer and job listing data from Upwork.",
        industry_tags=["freelance"],
        api_endpoint="https://www.upwork.com/api",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="hubspot_crm",
        name="HubSpot CRM",
        category=ToolCategory.CRM,
        description="Contact management, pipelines, and email sequences.",
        industry_tags=["marketing", "general", "freelance"],
        api_endpoint="https://api.hubapi.com",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="salesforce",
        name="Salesforce",
        category=ToolCategory.CRM,
        description="Enterprise CRM with advanced reporting.",
        industry_tags=["marketing", "finance", "general"],
        api_endpoint="https://login.salesforce.com/services/oauth2",
        is_free=False,
        monthly_cost_usd=75.0,
    ),
    Tool(
        tool_id="linkedin_scraper",
        name="LinkedIn Scraper",
        category=ToolCategory.SCRAPER,
        description="Extract professional profiles and company data.",
        industry_tags=["marketing", "freelance", "general"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="twitter_api",
        name="Twitter/X API",
        category=ToolCategory.API,
        description="Tweets, user data, and trend monitoring.",
        industry_tags=["marketing", "general"],
        api_endpoint="https://api.twitter.com/2",
        is_free=False,
        monthly_cost_usd=100.0,
    ),
    Tool(
        tool_id="mailchimp",
        name="Mailchimp",
        category=ToolCategory.ANALYTICS,
        description="Email marketing, automation, and audience analytics.",
        industry_tags=["marketing", "general"],
        api_endpoint="https://api.mailchimp.com/3.0",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="openai_api",
        name="OpenAI API",
        category=ToolCategory.AI_ML,
        description="GPT models for text generation, embeddings, and chat.",
        industry_tags=["general", "marketing", "health", "finance"],
        api_endpoint="https://api.openai.com/v1",
        is_free=False,
        monthly_cost_usd=20.0,
    ),
    Tool(
        tool_id="twilio",
        name="Twilio",
        category=ToolCategory.WEBHOOK,
        description="SMS, voice, and WhatsApp messaging platform.",
        industry_tags=["general", "marketing", "health"],
        api_endpoint="https://api.twilio.com/2010-04-01",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="sendgrid",
        name="SendGrid",
        category=ToolCategory.WEBHOOK,
        description="Transactional and marketing email delivery.",
        industry_tags=["general", "marketing"],
        api_endpoint="https://api.sendgrid.com/v3",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # Automation & workflow tools
    # ------------------------------------------------------------------
    Tool(
        tool_id="zapier",
        name="Zapier",
        category=ToolCategory.AUTOMATION,
        description="No-code workflow automation connecting 5,000+ apps.",
        industry_tags=["general", "marketing", "freelance"],
        api_endpoint="https://api.zapier.com/v1",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="n8n",
        name="n8n",
        category=ToolCategory.AUTOMATION,
        description="Open-source, self-hosted workflow automation.",
        industry_tags=["general", "devops"],
        api_endpoint="https://n8n.io/api/v1",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="make_com",
        name="Make (formerly Integromat)",
        category=ToolCategory.AUTOMATION,
        description="Visual automation platform for complex multi-step workflows.",
        industry_tags=["general", "marketing"],
        api_endpoint="https://www.make.com/api/v2",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="github_actions",
        name="GitHub Actions",
        category=ToolCategory.DEVOPS,
        description="CI/CD and automation workflows inside GitHub repositories.",
        industry_tags=["devops", "general"],
        api_endpoint="https://api.github.com/repos/{owner}/{repo}/actions",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="github_api",
        name="GitHub API",
        category=ToolCategory.API,
        description="Access repositories, commits, issues, PRs, and workflows.",
        industry_tags=["devops", "general"],
        api_endpoint="https://api.github.com",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="docker",
        name="Docker",
        category=ToolCategory.DEVOPS,
        description="Containerised application packaging and orchestration.",
        industry_tags=["devops", "general"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="kubernetes",
        name="Kubernetes",
        category=ToolCategory.DEVOPS,
        description="Container orchestration at scale.",
        industry_tags=["devops", "general"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # Databases
    # ------------------------------------------------------------------
    Tool(
        tool_id="postgresql",
        name="PostgreSQL",
        category=ToolCategory.DATABASE,
        description="Open-source relational database with full SQL support.",
        industry_tags=["general", "finance", "health"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="mongodb",
        name="MongoDB",
        category=ToolCategory.DATABASE,
        description="Document-oriented NoSQL database for flexible schemas.",
        industry_tags=["general", "marketing"],
        api_endpoint="https://cloud.mongodb.com/api/atlas/v1.0",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="redis",
        name="Redis",
        category=ToolCategory.DATABASE,
        description="In-memory key-value store for caching and queues.",
        industry_tags=["general", "devops"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="supabase",
        name="Supabase",
        category=ToolCategory.DATABASE,
        description="Open-source Firebase alternative with Postgres backend.",
        industry_tags=["general", "marketing", "freelance"],
        api_endpoint="https://api.supabase.io/v1",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="firebase",
        name="Firebase",
        category=ToolCategory.DATABASE,
        description="Google real-time database, auth, and cloud functions.",
        industry_tags=["general", "marketing"],
        api_endpoint="https://firebase.googleapis.com",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # Cloud storage
    # ------------------------------------------------------------------
    Tool(
        tool_id="aws_s3",
        name="AWS S3",
        category=ToolCategory.STORAGE,
        description="Scalable object storage for any data type.",
        industry_tags=["general", "devops", "finance"],
        api_endpoint="https://s3.amazonaws.com",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="google_cloud_storage",
        name="Google Cloud Storage",
        category=ToolCategory.STORAGE,
        description="Unified object storage with global edge caching.",
        industry_tags=["general", "devops"],
        api_endpoint="https://storage.googleapis.com",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="azure_blob",
        name="Azure Blob Storage",
        category=ToolCategory.STORAGE,
        description="Microsoft Azure massively scalable object store.",
        industry_tags=["general", "devops", "finance"],
        api_endpoint="https://myaccount.blob.core.windows.net",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # Messaging & collaboration
    # ------------------------------------------------------------------
    Tool(
        tool_id="slack_api",
        name="Slack API",
        category=ToolCategory.MESSAGING,
        description="Send messages, create channels, and manage Slack workspaces.",
        industry_tags=["general", "devops", "marketing"],
        api_endpoint="https://slack.com/api",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="discord_api",
        name="Discord API",
        category=ToolCategory.MESSAGING,
        description="Build bots and integrations for Discord servers.",
        industry_tags=["general", "marketing"],
        api_endpoint="https://discord.com/api/v10",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="telegram_bot",
        name="Telegram Bot API",
        category=ToolCategory.MESSAGING,
        description="Create rich Telegram bots with inline menus and media.",
        industry_tags=["general", "marketing"],
        api_endpoint="https://api.telegram.org/bot{token}",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="whatsapp_business",
        name="WhatsApp Business API",
        category=ToolCategory.MESSAGING,
        description="Programmatic WhatsApp messaging for business outreach.",
        industry_tags=["general", "marketing", "health"],
        api_endpoint="https://graph.facebook.com/v17.0",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # AI / ML libraries & APIs
    # ------------------------------------------------------------------
    Tool(
        tool_id="anthropic_api",
        name="Anthropic (Claude) API",
        category=ToolCategory.AI_ML,
        description="Claude LLM models for reasoning and conversational AI.",
        industry_tags=["general", "health", "finance", "marketing"],
        api_endpoint="https://api.anthropic.com/v1",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="huggingface",
        name="Hugging Face Inference API",
        category=ToolCategory.AI_ML,
        description="Hosted NLP, vision, and audio models via REST.",
        industry_tags=["general", "health"],
        api_endpoint="https://api-inference.huggingface.co/models",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="langchain",
        name="LangChain",
        category=ToolCategory.AI_ML,
        description="Python/JS framework for building LLM-powered applications.",
        industry_tags=["general", "devops"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="tensorflow",
        name="TensorFlow",
        category=ToolCategory.AI_ML,
        description="End-to-end open-source ML platform by Google.",
        industry_tags=["general", "health", "finance"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="pytorch",
        name="PyTorch",
        category=ToolCategory.AI_ML,
        description="Deep learning framework with dynamic computation graphs.",
        industry_tags=["general", "health", "finance"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="scikit_learn",
        name="scikit-learn",
        category=ToolCategory.AI_ML,
        description="Machine learning library for classical ML algorithms.",
        industry_tags=["general", "finance", "health"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="pandas",
        name="pandas",
        category=ToolCategory.LIBRARY,
        description="Data manipulation and analysis library for Python.",
        industry_tags=["general", "finance", "real_estate"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="numpy",
        name="NumPy",
        category=ToolCategory.LIBRARY,
        description="Fundamental package for numerical computation in Python.",
        industry_tags=["general", "finance"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="fastapi",
        name="FastAPI",
        category=ToolCategory.LIBRARY,
        description="High-performance Python web framework for building APIs.",
        industry_tags=["general", "devops"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="flask",
        name="Flask",
        category=ToolCategory.LIBRARY,
        description="Lightweight Python web framework for microservices.",
        industry_tags=["general", "devops"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="django",
        name="Django",
        category=ToolCategory.LIBRARY,
        description="Full-stack Python web framework with ORM and admin.",
        industry_tags=["general", "devops", "finance"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="react",
        name="React",
        category=ToolCategory.LIBRARY,
        description="JavaScript UI library for building component-based UIs.",
        industry_tags=["general", "marketing", "freelance"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="nextjs",
        name="Next.js",
        category=ToolCategory.LIBRARY,
        description="React framework with SSR, SSG, and full-stack capabilities.",
        industry_tags=["general", "marketing"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="nodejs",
        name="Node.js",
        category=ToolCategory.LIBRARY,
        description="JavaScript runtime for server-side and API development.",
        industry_tags=["general", "devops"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="express",
        name="Express.js",
        category=ToolCategory.LIBRARY,
        description="Minimal Node.js web framework for REST APIs.",
        industry_tags=["general", "devops"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # Monitoring & observability
    # ------------------------------------------------------------------
    Tool(
        tool_id="datadog",
        name="Datadog",
        category=ToolCategory.MONITORING,
        description="Cloud monitoring, APM, logging, and alerting platform.",
        industry_tags=["devops", "general"],
        api_endpoint="https://api.datadoghq.com/api/v1",
        is_free=False,
        monthly_cost_usd=15.0,
    ),
    Tool(
        tool_id="sentry",
        name="Sentry",
        category=ToolCategory.MONITORING,
        description="Real-time error tracking and performance monitoring.",
        industry_tags=["devops", "general"],
        api_endpoint="https://sentry.io/api/0",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="pagerduty",
        name="PagerDuty",
        category=ToolCategory.MONITORING,
        description="Incident management and on-call scheduling.",
        industry_tags=["devops", "general"],
        api_endpoint="https://api.pagerduty.com",
        is_free=False,
        monthly_cost_usd=21.0,
    ),
    # ------------------------------------------------------------------
    # E-commerce & marketplace
    # ------------------------------------------------------------------
    Tool(
        tool_id="shopify_api",
        name="Shopify API",
        category=ToolCategory.API,
        description="Build Shopify apps, manage products, orders, and customers.",
        industry_tags=["ecommerce", "marketing", "general"],
        api_endpoint="https://{shop}.myshopify.com/admin/api/2023-04",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="woocommerce",
        name="WooCommerce REST API",
        category=ToolCategory.API,
        description="Manage WordPress/WooCommerce stores programmatically.",
        industry_tags=["ecommerce", "marketing"],
        api_endpoint="https://yourstore.com/wp-json/wc/v3",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="amazon_sp_api",
        name="Amazon Selling Partner API",
        category=ToolCategory.API,
        description="Manage Amazon listings, inventory, orders, and FBA.",
        industry_tags=["ecommerce"],
        api_endpoint="https://sellingpartnerapi-na.amazon.com",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # Additional payment & fintech
    # ------------------------------------------------------------------
    Tool(
        tool_id="paypal",
        name="PayPal API",
        category=ToolCategory.PAYMENT,
        description="PayPal payments, subscriptions, and refunds.",
        industry_tags=["finance", "general", "ecommerce"],
        api_endpoint="https://api.paypal.com/v1",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="square",
        name="Square API",
        category=ToolCategory.PAYMENT,
        description="Point-of-sale payments, invoices, and catalog management.",
        industry_tags=["finance", "general", "ecommerce"],
        api_endpoint="https://connect.squareup.com/v2",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="coinbase_commerce",
        name="Coinbase Commerce",
        category=ToolCategory.PAYMENT,
        description="Accept cryptocurrency payments for digital goods.",
        industry_tags=["finance", "general"],
        api_endpoint="https://api.commerce.coinbase.com",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # Analytics & BI
    # ------------------------------------------------------------------
    Tool(
        tool_id="google_analytics",
        name="Google Analytics 4",
        category=ToolCategory.ANALYTICS,
        description="Web and app analytics with audience and conversion tracking.",
        industry_tags=["marketing", "general", "ecommerce"],
        api_endpoint="https://analyticsdata.googleapis.com/v1beta",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="mixpanel",
        name="Mixpanel",
        category=ToolCategory.ANALYTICS,
        description="Product analytics for user behaviour and funnel analysis.",
        industry_tags=["marketing", "general"],
        api_endpoint="https://api.mixpanel.com",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="segment",
        name="Segment",
        category=ToolCategory.ANALYTICS,
        description="Customer data platform for tracking and routing events.",
        industry_tags=["marketing", "general"],
        api_endpoint="https://api.segment.io/v1",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="amplitude",
        name="Amplitude",
        category=ToolCategory.ANALYTICS,
        description="Digital analytics platform with behavioural cohorts.",
        industry_tags=["marketing", "general"],
        api_endpoint="https://api.amplitude.com/2/httpapi",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # Project management & collaboration
    # ------------------------------------------------------------------
    Tool(
        tool_id="jira",
        name="Jira API",
        category=ToolCategory.API,
        description="Issue tracking and agile project management.",
        industry_tags=["devops", "general"],
        api_endpoint="https://yoursite.atlassian.net/rest/api/3",
        is_free=False,
        monthly_cost_usd=7.75,
    ),
    Tool(
        tool_id="notion_api",
        name="Notion API",
        category=ToolCategory.API,
        description="Read and write Notion databases, pages, and blocks.",
        industry_tags=["general", "marketing"],
        api_endpoint="https://api.notion.com/v1",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="airtable",
        name="Airtable API",
        category=ToolCategory.API,
        description="Flexible spreadsheet-database for structured data.",
        industry_tags=["general", "marketing", "real_estate"],
        api_endpoint="https://api.airtable.com/v0",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="trello_api",
        name="Trello API",
        category=ToolCategory.API,
        description="Kanban-style boards for task and project management.",
        industry_tags=["general", "marketing"],
        api_endpoint="https://api.trello.com/1",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # Communication / customer support
    # ------------------------------------------------------------------
    Tool(
        tool_id="zendesk",
        name="Zendesk API",
        category=ToolCategory.CRM,
        description="Customer support ticketing and help-desk management.",
        industry_tags=["general", "marketing", "health"],
        api_endpoint="https://{subdomain}.zendesk.com/api/v2",
        is_free=False,
        monthly_cost_usd=55.0,
    ),
    Tool(
        tool_id="intercom",
        name="Intercom API",
        category=ToolCategory.CRM,
        description="Conversational relationship platform with live chat and bots.",
        industry_tags=["general", "marketing"],
        api_endpoint="https://api.intercom.io",
        is_free=False,
        monthly_cost_usd=74.0,
    ),
    Tool(
        tool_id="freshdesk",
        name="Freshdesk API",
        category=ToolCategory.CRM,
        description="Cloud-based customer support and ticketing.",
        industry_tags=["general", "marketing"],
        api_endpoint="https://{domain}.freshdesk.com/api/v2",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # Map / geo
    # ------------------------------------------------------------------
    Tool(
        tool_id="mapbox",
        name="Mapbox API",
        category=ToolCategory.API,
        description="Custom maps, geocoding, and navigation services.",
        industry_tags=["real_estate", "logistics", "general"],
        api_endpoint="https://api.mapbox.com",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="openstreetmap",
        name="OpenStreetMap / Nominatim",
        category=ToolCategory.API,
        description="Free, editable world map data with geocoding.",
        industry_tags=["real_estate", "logistics", "general"],
        api_endpoint="https://nominatim.openstreetmap.org",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # Weather & environmental
    # ------------------------------------------------------------------
    Tool(
        tool_id="openweather",
        name="OpenWeatherMap API",
        category=ToolCategory.API,
        description="Current weather, forecasts, and historical climate data.",
        industry_tags=["general", "logistics"],
        api_endpoint="https://api.openweathermap.org/data/2.5",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # HR / Recruitment
    # ------------------------------------------------------------------
    Tool(
        tool_id="indeed_api",
        name="Indeed Publisher API",
        category=ToolCategory.API,
        description="Job listing search and employer branding.",
        industry_tags=["freelance", "general"],
        api_endpoint="https://api.indeed.com/ads/apisearch",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="workday",
        name="Workday API",
        category=ToolCategory.API,
        description="Enterprise HR, payroll, and financial management.",
        industry_tags=["finance", "general"],
        api_endpoint="https://wd2-impl-services1.workday.com/ccx/api",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # Healthcare
    # ------------------------------------------------------------------
    Tool(
        tool_id="fhir_api",
        name="HL7 FHIR API",
        category=ToolCategory.API,
        description="Standardised healthcare data exchange and EHR integration.",
        industry_tags=["health"],
        api_endpoint="https://api.fhir.org/R4",
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="epic_api",
        name="Epic MyChart API",
        category=ToolCategory.API,
        description="Patient portal and EHR data access via Epic Systems.",
        industry_tags=["health"],
        api_endpoint="https://open.epic.com/interface/FHIR",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
    # ------------------------------------------------------------------
    # IoT / hardware
    # ------------------------------------------------------------------
    Tool(
        tool_id="mqtt",
        name="MQTT (Mosquitto)",
        category=ToolCategory.WEBHOOK,
        description="Lightweight pub/sub messaging protocol for IoT devices.",
        industry_tags=["iot", "general"],
        api_endpoint=None,
        is_free=True,
        monthly_cost_usd=0.0,
    ),
    Tool(
        tool_id="aws_iot",
        name="AWS IoT Core",
        category=ToolCategory.API,
        description="Managed cloud service for IoT device connectivity.",
        industry_tags=["iot", "devops"],
        api_endpoint="https://iot.amazonaws.com",
        is_free=False,
        monthly_cost_usd=0.0,
    ),
]

_CATALOGUE_MAP: dict[str, Tool] = {t.tool_id: t for t in _CATALOGUE}


class ToolDB:
    """In-memory tool catalogue with search and injection helpers."""

    def search(self, query: str, industry: str = "") -> list[Tool]:
        """Search tools by keywords and optional industry filter."""
        lower = query.lower()
        results: list[Tool] = []
        for tool in _CATALOGUE:
            text = (
                tool.name.lower()
                + " "
                + tool.description.lower()
                + " "
                + " ".join(tool.industry_tags)
            )
            if lower in text:
                if not industry or industry.lower() in tool.industry_tags:
                    results.append(tool)
        return results

    def get_tools_for_industry(self, industry: str) -> list[Tool]:
        """Return all tools tagged for the given industry."""
        lower = industry.lower()
        return [t for t in _CATALOGUE if lower in t.industry_tags or "general" in t.industry_tags]

    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """Return a tool by its ID, or None."""
        return _CATALOGUE_MAP.get(tool_id)

    def inject_tools(self, bot_name: str, industry: str) -> list[Tool]:
        """Auto-select the best tools for a bot given its industry."""
        lower = industry.lower()
        # Prefer industry-specific tools; add general ones as fill
        specific = [t for t in _CATALOGUE if lower in t.industry_tags]
        general = [t for t in _CATALOGUE if "general" in t.industry_tags and t not in specific]
        combined = specific + general
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[Tool] = []
        for t in combined:
            if t.tool_id not in seen:
                seen.add(t.tool_id)
                unique.append(t)
        return unique[:6]  # cap at 6 injected tools

    def list_all(self) -> list[Tool]:
        """Return the full catalogue."""
        return list(_CATALOGUE)
