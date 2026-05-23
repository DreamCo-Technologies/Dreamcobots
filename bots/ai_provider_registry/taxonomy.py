"""
AI Provider Registry — Taxonomy

Defines the 6-layer taxonomy for organizing AI providers inside DreamCo OS,
plus the AI cluster groupings used by the Router Brain.

LAYER HIERARCHY
---------------
A. Intelligence Layer
   - foundation_models
   - conversational_ai
   - search_retrieval

B. Execution Layer
   - developer_tools
   - automation
   - ai_agents

C. Infrastructure Layer
   - cloud_infrastructure
   - hardware_compute
   - data_platforms

D. Industry Layer
   - healthcare
   - finance
   - legal
   - security
   - education

E. Creative Layer
   - vision_image_video
   - music_voice_media

F. Physical Layer
   - robotics
   - autonomous_vehicles
   - defense_ai

GLOBAL AI SOURCES FLOW: This module adheres to the Dreamcobots GLOBAL AI
SOURCES FLOW framework pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Layer constants
# ---------------------------------------------------------------------------

LAYER_INTELLIGENCE    = "intelligence"
LAYER_EXECUTION       = "execution"
LAYER_INFRASTRUCTURE  = "infrastructure"
LAYER_INDUSTRY        = "industry"
LAYER_CREATIVE        = "creative"
LAYER_PHYSICAL        = "physical"

VALID_LAYERS = {
    LAYER_INTELLIGENCE,
    LAYER_EXECUTION,
    LAYER_INFRASTRUCTURE,
    LAYER_INDUSTRY,
    LAYER_CREATIVE,
    LAYER_PHYSICAL,
}

# ---------------------------------------------------------------------------
# Sub-layer constants
# ---------------------------------------------------------------------------

# Intelligence
SUB_FOUNDATION_MODELS = "foundation_models"
SUB_CONVERSATIONAL_AI = "conversational_ai"
SUB_SEARCH_RETRIEVAL  = "search_retrieval"

# Execution
SUB_DEVELOPER_TOOLS   = "developer_tools"
SUB_AUTOMATION        = "automation"
SUB_AI_AGENTS         = "ai_agents"

# Infrastructure
SUB_CLOUD_INFRA       = "cloud_infrastructure"
SUB_HARDWARE_COMPUTE  = "hardware_compute"
SUB_DATA_PLATFORMS    = "data_platforms"

# Industry
SUB_HEALTHCARE        = "healthcare"
SUB_FINANCE           = "finance"
SUB_LEGAL             = "legal"
SUB_SECURITY          = "security"
SUB_EDUCATION         = "education"

# Creative
SUB_VISION_IMAGE_VIDEO   = "vision_image_video"
SUB_MUSIC_VOICE_MEDIA    = "music_voice_media"

# Physical
SUB_ROBOTICS              = "robotics"
SUB_AUTONOMOUS_VEHICLES   = "autonomous_vehicles"
SUB_DEFENSE_AI            = "defense_ai"

# ---------------------------------------------------------------------------
# Category IDs (used in AIProviderObject.categories)
# ---------------------------------------------------------------------------

CATEGORY_FOUNDATION_MODELS = "foundation_models"
CATEGORY_CONVERSATIONAL    = "conversational_ai"
CATEGORY_SEARCH_RETRIEVAL  = "search_retrieval"
CATEGORY_DEVELOPER_TOOLS   = "developer_tools"
CATEGORY_AUTOMATION        = "automation"
CATEGORY_AI_AGENTS         = "ai_agents"
CATEGORY_CLOUD_INFRA       = "cloud_infrastructure"
CATEGORY_HARDWARE_COMPUTE  = "hardware_compute"
CATEGORY_DATA_PLATFORMS    = "data_platforms"
CATEGORY_HEALTHCARE        = "healthcare"
CATEGORY_FINANCE           = "finance"
CATEGORY_LEGAL             = "legal"
CATEGORY_SECURITY          = "security"
CATEGORY_EDUCATION         = "education"
CATEGORY_VISION_IMAGE      = "vision_image"
CATEGORY_VIDEO             = "video"
CATEGORY_MUSIC             = "music"
CATEGORY_VOICE             = "voice"
CATEGORY_MEDIA             = "media"
CATEGORY_ROBOTICS          = "robotics"
CATEGORY_AUTONOMOUS_VEH    = "autonomous_vehicles"
CATEGORY_DEFENSE           = "defense_ai"

ALL_CATEGORIES: list[str] = [
    CATEGORY_FOUNDATION_MODELS,
    CATEGORY_CONVERSATIONAL,
    CATEGORY_SEARCH_RETRIEVAL,
    CATEGORY_DEVELOPER_TOOLS,
    CATEGORY_AUTOMATION,
    CATEGORY_AI_AGENTS,
    CATEGORY_CLOUD_INFRA,
    CATEGORY_HARDWARE_COMPUTE,
    CATEGORY_DATA_PLATFORMS,
    CATEGORY_HEALTHCARE,
    CATEGORY_FINANCE,
    CATEGORY_LEGAL,
    CATEGORY_SECURITY,
    CATEGORY_EDUCATION,
    CATEGORY_VISION_IMAGE,
    CATEGORY_VIDEO,
    CATEGORY_MUSIC,
    CATEGORY_VOICE,
    CATEGORY_MEDIA,
    CATEGORY_ROBOTICS,
    CATEGORY_AUTONOMOUS_VEH,
    CATEGORY_DEFENSE,
]

# ---------------------------------------------------------------------------
# AI Cluster definitions
# ---------------------------------------------------------------------------

@dataclass
class AICluster:
    """A swap-in/swap-out group of interchangeable providers."""
    id: str
    name: str
    description: str
    member_ids: list[str]  # AIProviderObject.id values
    primary_layer: str
    emoji: str = ""

    def contains(self, provider_id: str) -> bool:
        return provider_id in self.member_ids


# Cluster ID constants
CLUSTER_LLM_CORE         = "llm_core"
CLUSTER_OPEN_SOURCE_LLM  = "open_source_llm"
CLUSTER_CODING            = "coding"
CLUSTER_AUTOMATION        = "automation"
CLUSTER_DATA_INTELLIGENCE = "data_intelligence"
CLUSTER_CREATIVE_IMAGE    = "creative_image"
CLUSTER_CREATIVE_VIDEO    = "creative_video"
CLUSTER_CREATIVE_AUDIO    = "creative_audio"
CLUSTER_VECTOR_DB         = "vector_db"
CLUSTER_AI_AGENTS         = "ai_agents"
CLUSTER_CLOUD_INFRA       = "cloud_infra"
CLUSTER_HARDWARE_COMPUTE  = "hardware_compute"
CLUSTER_HEALTHCARE        = "healthcare"
CLUSTER_FINANCE           = "finance"
CLUSTER_LEGAL             = "legal"
CLUSTER_SECURITY          = "security"
CLUSTER_ROBOTICS          = "robotics"
CLUSTER_AUTONOMOUS_VEH    = "autonomous_vehicles"
CLUSTER_DEFENSE           = "defense_ai"
CLUSTER_SEARCH            = "search"
CLUSTER_MARKETING         = "marketing"
CLUSTER_EDUCATION         = "education"

AI_CLUSTERS: dict[str, AICluster] = {
    CLUSTER_LLM_CORE: AICluster(
        id=CLUSTER_LLM_CORE,
        name="LLM Core Cluster",
        description="General-purpose large language model providers for reasoning, writing, and analysis",
        member_ids=["openai", "anthropic", "google_deepmind", "xai", "cohere",
                    "ai21_labs", "aleph_alpha", "inflection", "meta_llama_api",
                    "nvidia_nim", "amazon_nova", "baidu_ernie", "samsung_gauss"],
        primary_layer=LAYER_INTELLIGENCE,
        emoji="🧠",
    ),
    CLUSTER_OPEN_SOURCE_LLM: AICluster(
        id=CLUSTER_OPEN_SOURCE_LLM,
        name="Open-Source LLM Cluster",
        description="Open-weight models deployable on any infrastructure",
        member_ids=["meta_llama", "mistral_ai", "deepseek", "qwen_alibaba",
                    "gemma_google", "phi_microsoft", "falcon_tii"],
        primary_layer=LAYER_INTELLIGENCE,
        emoji="🔓",
    ),
    CLUSTER_CODING: AICluster(
        id=CLUSTER_CODING,
        name="Coding Cluster",
        description="AI tools for writing, reviewing, and deploying code",
        member_ids=["github_copilot", "cursor_ai", "claude_code", "replit_ai",
                    "gemini_code", "tabnine", "codeium", "sourcegraph_cody",
                    "jetbrains_ai", "devin_cognition", "v0_vercel", "bolt_new"],
        primary_layer=LAYER_EXECUTION,
        emoji="💻",
    ),
    CLUSTER_AUTOMATION: AICluster(
        id=CLUSTER_AUTOMATION,
        name="Automation Cluster",
        description="Workflow and business process automation platforms",
        member_ids=["zapier_ai", "make_com", "n8n_ai", "uipath_ai",
                    "pipedream_ai", "retool_ai", "windmill_ai", "temporal_ai",
                    "appsmith_ai", "bubble_ai"],
        primary_layer=LAYER_EXECUTION,
        emoji="⚙️",
    ),
    CLUSTER_DATA_INTELLIGENCE: AICluster(
        id=CLUSTER_DATA_INTELLIGENCE,
        name="Data Intelligence Cluster",
        description="Data platforms, ML ops, and analytics AI",
        member_ids=["databricks_ai", "snowflake_cortex", "palantir_aip",
                    "h2o_ai", "datarobot", "dbt_cloud", "fivetran_ai",
                    "airbyte_ai", "montecarlo", "openai_embeddings"],
        primary_layer=LAYER_INFRASTRUCTURE,
        emoji="📊",
    ),
    CLUSTER_CREATIVE_IMAGE: AICluster(
        id=CLUSTER_CREATIVE_IMAGE,
        name="Image Generation Cluster",
        description="AI image and visual content generation",
        member_ids=["midjourney_ai", "dalle3_openai", "stable_diffusion",
                    "adobe_firefly", "flux_bfl", "topaz_labs",
                    "luminar_neo", "photoroom_ai", "adobe_sensei", "canva_ai"],
        primary_layer=LAYER_CREATIVE,
        emoji="🎨",
    ),
    CLUSTER_CREATIVE_VIDEO: AICluster(
        id=CLUSTER_CREATIVE_VIDEO,
        name="Video Generation Cluster",
        description="AI video creation and editing platforms",
        member_ids=["sora_openai", "runway_ml", "pika_labs",
                    "veo_google", "luma_dream", "descript_ai"],
        primary_layer=LAYER_CREATIVE,
        emoji="🎬",
    ),
    CLUSTER_CREATIVE_AUDIO: AICluster(
        id=CLUSTER_CREATIVE_AUDIO,
        name="Audio & Music Cluster",
        description="AI music generation, voice synthesis, and audio editing",
        member_ids=["suno_ai", "udio_ai", "aiva_music", "soundraw_ai",
                    "mubert_ai", "elevenlabs", "playht_ai", "openai_tts",
                    "whisper_openai", "adobe_podcast", "cleanvoice",
                    "beatoven_ai", "resemble_ai"],
        primary_layer=LAYER_CREATIVE,
        emoji="🎵",
    ),
    CLUSTER_VECTOR_DB: AICluster(
        id=CLUSTER_VECTOR_DB,
        name="Vector DB & Search Cluster",
        description="Vector databases and semantic search infrastructure",
        member_ids=["pinecone_db", "weaviate_db", "qdrant_db",
                    "chroma_db", "algolia_ai", "zilliz_milvus",
                    "typesense_ai", "elasticsearch_ai"],
        primary_layer=LAYER_INTELLIGENCE,
        emoji="🔍",
    ),
    CLUSTER_AI_AGENTS: AICluster(
        id=CLUSTER_AI_AGENTS,
        name="AI Agents Cluster",
        description="Multi-agent orchestration and autonomous AI frameworks",
        member_ids=["crewai_agents", "autogen_ms", "langgraph_lc",
                    "openai_agents", "superagent_ai", "fixie_ai",
                    "agentops_ai", "taskade_ai", "cognosys_ai", "e2b_sandbox"],
        primary_layer=LAYER_EXECUTION,
        emoji="🤖",
    ),
    CLUSTER_CLOUD_INFRA: AICluster(
        id=CLUSTER_CLOUD_INFRA,
        name="Cloud AI Infrastructure Cluster",
        description="Cloud platforms for deploying and scaling AI workloads",
        member_ids=["aws_bedrock", "azure_openai", "google_vertex_ai",
                    "ibm_watsonx", "coreweave", "lambda_cloud",
                    "vast_ai", "runpod_ai", "modal_ai", "together_ai"],
        primary_layer=LAYER_INFRASTRUCTURE,
        emoji="☁️",
    ),
    CLUSTER_HARDWARE_COMPUTE: AICluster(
        id=CLUSTER_HARDWARE_COMPUTE,
        name="Hardware Compute Cluster",
        description="AI chips, accelerators, and compute hardware",
        member_ids=["nvidia_h100", "groq_lpu", "cerebras_ai",
                    "graphcore_ai", "intel_gaudi", "tenstorrent_ai",
                    "amd_mi300", "aws_trainium", "google_tpu", "sambanova_ai"],
        primary_layer=LAYER_INFRASTRUCTURE,
        emoji="⚡",
    ),
    CLUSTER_HEALTHCARE: AICluster(
        id=CLUSTER_HEALTHCARE,
        name="Healthcare AI Cluster",
        description="Clinical, diagnostic, and health management AI",
        member_ids=["med_palm2", "ms_dragon", "nuance_dax",
                    "tempus_ai", "flatiron_health", "viz_ai",
                    "babylon_health", "suki_ai", "nabla_ai", "ambient_clinical"],
        primary_layer=LAYER_INDUSTRY,
        emoji="🏥",
    ),
    CLUSTER_FINANCE: AICluster(
        id=CLUSTER_FINANCE,
        name="Finance AI Cluster",
        description="Trading, banking, forecasting, and financial intelligence AI",
        member_ids=["bloomberg_gpt", "kensho_ai", "alphasense_ai",
                    "c3_ai", "stripe_radar_ai", "kasisto_ai",
                    "yseop_ai", "refinitiv_eikon", "palantir_finance",
                    "symphony_ai"],
        primary_layer=LAYER_INDUSTRY,
        emoji="💰",
    ),
    CLUSTER_LEGAL: AICluster(
        id=CLUSTER_LEGAL,
        name="Legal AI Cluster",
        description="Contract review, legal research, and compliance AI",
        member_ids=["harvey_ai", "casetext_ai", "relativity_ai",
                    "luminance_ai", "robin_ai", "lexisnexis_ai",
                    "cocounsel_ai", "ms_legal_copilot"],
        primary_layer=LAYER_INDUSTRY,
        emoji="⚖️",
    ),
    CLUSTER_SECURITY: AICluster(
        id=CLUSTER_SECURITY,
        name="Security AI Cluster",
        description="Threat detection, fraud prevention, and cybersecurity AI",
        member_ids=["crowdstrike_ai", "darktrace_ai", "sentinelone_ai",
                    "vectra_ai", "cylance_ai", "recorded_future_ai",
                    "ibm_qradar"],
        primary_layer=LAYER_INDUSTRY,
        emoji="🛡️",
    ),
    CLUSTER_ROBOTICS: AICluster(
        id=CLUSTER_ROBOTICS,
        name="Robotics Cluster",
        description="AI-powered physical robots and manipulation systems",
        member_ids=["nvidia_isaac", "tesla_optimus_ai", "figure_robot",
                    "boston_dynamics_ai", "agility_robotics_ai",
                    "apptronik_ai", "sanctuary_ai", "onex_tech",
                    "physical_intel", "unitree_robotics"],
        primary_layer=LAYER_PHYSICAL,
        emoji="🦾",
    ),
    CLUSTER_AUTONOMOUS_VEH: AICluster(
        id=CLUSTER_AUTONOMOUS_VEH,
        name="Autonomous Vehicles Cluster",
        description="Self-driving and autonomous transportation AI",
        member_ids=["tesla_fsd", "waymo_ai", "cruise_gm",
                    "mobileye_ai", "comma_ai", "aurora_ai",
                    "nvidia_drive", "motional_ai", "zoox_ai", "pony_ai"],
        primary_layer=LAYER_PHYSICAL,
        emoji="🚗",
    ),
    CLUSTER_DEFENSE: AICluster(
        id=CLUSTER_DEFENSE,
        name="Defense AI Cluster",
        description="Defense, intelligence, and government AI systems",
        member_ids=["shield_ai", "anduril_ai", "palantir_gov",
                    "leidos_ai", "skydio_ai", "saic_ai",
                    "l3harris_ai", "northrop_ai", "raytheon_ai",
                    "booz_allen_ai"],
        primary_layer=LAYER_PHYSICAL,
        emoji="🎖️",
    ),
    CLUSTER_SEARCH: AICluster(
        id=CLUSTER_SEARCH,
        name="Search & Discovery Cluster",
        description="AI-powered search, research, and information retrieval",
        member_ids=["perplexity_ai", "you_com", "elicit_ai",
                    "consensus_ai", "algolia_ai"],
        primary_layer=LAYER_INTELLIGENCE,
        emoji="🔎",
    ),
    CLUSTER_MARKETING: AICluster(
        id=CLUSTER_MARKETING,
        name="Marketing AI Cluster",
        description="Copywriting, SEO, advertising, and marketing automation AI",
        member_ids=["jasper_ai", "copy_ai", "writesonic_ai",
                    "surfer_ai", "canva_ai", "hubspot_breeze_ai",
                    "salesforce_einstein_ai", "adcreative_ai"],
        primary_layer=LAYER_EXECUTION,
        emoji="📣",
    ),
    CLUSTER_EDUCATION: AICluster(
        id=CLUSTER_EDUCATION,
        name="Education AI Cluster",
        description="AI tutoring, learning, and educational platforms",
        member_ids=["khanmigo_ai", "duolingo_max_ai", "coursera_ai",
                    "carnegie_learning_ai", "synthesis_ai"],
        primary_layer=LAYER_INDUSTRY,
        emoji="🎓",
    ),
}


def get_cluster(cluster_id: str) -> AICluster:
    """Return a cluster by ID, raising KeyError if not found."""
    return AI_CLUSTERS[cluster_id]


def get_clusters_for_provider(provider_id: str) -> list[AICluster]:
    """Return all clusters that contain the given provider ID."""
    return [c for c in AI_CLUSTERS.values() if provider_id in c.member_ids]


def list_clusters() -> list[AICluster]:
    return list(AI_CLUSTERS.values())


# ---------------------------------------------------------------------------
# Pricing tier definitions (used by CostOptimizerEngine)
# ---------------------------------------------------------------------------
@dataclass
class PricingTier:
    id: str
    label: str
    priority: int   # lower = cheaper
    is_free: bool = False
    is_open_source: bool = False


PRICING_TIERS: dict[str, PricingTier] = {
    "free":         PricingTier("free",       "Free",         0, is_free=True),
    "open_source":  PricingTier("open_source","Open-Source",  1, is_open_source=True),
    "freemium":     PricingTier("freemium",   "Freemium",     2),
    "paid":         PricingTier("paid",       "Paid",         3),
    "enterprise":   PricingTier("enterprise", "Enterprise",   4),
}


# ---------------------------------------------------------------------------
# Category taxonomy (flat dict for router lookups)
# ---------------------------------------------------------------------------
@dataclass
class CategoryMeta:
    id: str
    label: str
    layer: str
    sub_layer: str = ""


CATEGORY_TAXONOMY: dict[str, CategoryMeta] = {
    # Intelligence Layer
    "foundation_models":    CategoryMeta("foundation_models",    "Foundation Models",    LAYER_INTELLIGENCE, SUB_FOUNDATION_MODELS),
    "conversational_ai":    CategoryMeta("conversational_ai",    "Conversational AI",    LAYER_INTELLIGENCE, SUB_CONVERSATIONAL_AI),
    "search_retrieval":     CategoryMeta("search_retrieval",     "Search & Retrieval",   LAYER_INTELLIGENCE, SUB_SEARCH_RETRIEVAL),
    # Execution Layer
    "developer_tools":      CategoryMeta("developer_tools",      "Developer Tools",      LAYER_EXECUTION, SUB_DEVELOPER_TOOLS),
    "automation":           CategoryMeta("automation",           "Automation",           LAYER_EXECUTION, SUB_AUTOMATION),
    "ai_agents":            CategoryMeta("ai_agents",            "AI Agents",            LAYER_EXECUTION, SUB_AI_AGENTS),
    # Infrastructure Layer
    "cloud_infrastructure": CategoryMeta("cloud_infrastructure", "Cloud & Infrastructure", LAYER_INFRASTRUCTURE, SUB_CLOUD_INFRA),
    "hardware_compute":     CategoryMeta("hardware_compute",     "Hardware & Compute",   LAYER_INFRASTRUCTURE, SUB_HARDWARE_COMPUTE),
    "data_platforms":       CategoryMeta("data_platforms",       "Data Platforms",       LAYER_INFRASTRUCTURE, SUB_DATA_PLATFORMS),
    # Industry Layer
    "healthcare":           CategoryMeta("healthcare",           "Healthcare",           LAYER_INDUSTRY, SUB_HEALTHCARE),
    "finance":              CategoryMeta("finance",              "Finance",              LAYER_INDUSTRY, SUB_FINANCE),
    "legal":                CategoryMeta("legal",                "Legal",                LAYER_INDUSTRY, SUB_LEGAL),
    "security":             CategoryMeta("security",             "Security",             LAYER_INDUSTRY, SUB_SECURITY),
    "education":            CategoryMeta("education",            "Education",            LAYER_INDUSTRY, SUB_EDUCATION),
    # Creative Layer
    "vision_image_video":   CategoryMeta("vision_image_video",   "Vision / Image / Video", LAYER_CREATIVE, SUB_VISION_IMAGE_VIDEO),
    "music_voice_media":    CategoryMeta("music_voice_media",    "Music / Voice / Media",  LAYER_CREATIVE, SUB_MUSIC_VOICE_MEDIA),
    # Physical Layer
    "robotics":             CategoryMeta("robotics",             "Robotics",             LAYER_PHYSICAL, SUB_ROBOTICS),
    "autonomous_vehicles":  CategoryMeta("autonomous_vehicles",  "Autonomous Vehicles",  LAYER_PHYSICAL, SUB_AUTONOMOUS_VEHICLES),
    "defense_ai":           CategoryMeta("defense_ai",           "Defense AI",           LAYER_PHYSICAL, SUB_DEFENSE_AI),
    # Extended categories (from user's 22-category taxonomy)
    "analytics_automation": CategoryMeta("analytics_automation", "Analytics & Automation", LAYER_EXECUTION),
    "data_search":          CategoryMeta("data_search",          "Data & Search",        LAYER_INFRASTRUCTURE),
    "enterprise_platforms": CategoryMeta("enterprise_platforms", "Enterprise Platforms", LAYER_INDUSTRY),
    "healthcare_bio":       CategoryMeta("healthcare_bio",       "Healthcare & Bio",     LAYER_INDUSTRY),
    "fintech_risk":         CategoryMeta("fintech_risk",         "FinTech & Risk",       LAYER_INDUSTRY),
    "legal_contracts":      CategoryMeta("legal_contracts",      "Legal & Contracts",    LAYER_INDUSTRY),
    "education_training":   CategoryMeta("education_training",   "Education & Training", LAYER_INDUSTRY),
    "sales_marketing":      CategoryMeta("sales_marketing",      "Sales & Marketing",    LAYER_EXECUTION),
    "gaming_simulation":    CategoryMeta("gaming_simulation",    "Gaming & Simulation",  LAYER_CREATIVE),
    "web3_blockchain":      CategoryMeta("web3_blockchain",      "Web3 & Blockchain",    LAYER_INDUSTRY),
    "hr_workforce":         CategoryMeta("hr_workforce",         "HR & Workforce",       LAYER_INDUSTRY),
    "regional_emerging":    CategoryMeta("regional_emerging",    "Regional & Emerging",  LAYER_INTELLIGENCE),
    "vision_speech_media":  CategoryMeta("vision_speech_media",  "Vision, Speech & Media", LAYER_CREATIVE),
    "security_compliance":  CategoryMeta("security_compliance",  "Security & Compliance",  LAYER_INDUSTRY),
    "robotics_physical_ai": CategoryMeta("robotics_physical_ai", "Robotics & Physical AI", LAYER_PHYSICAL),
}
