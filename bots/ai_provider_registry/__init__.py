"""
bots/ai_provider_registry — DreamCo AI Provider Registry System.

Exposes the full normalized provider catalog, all 4 router-brain engines,
the bot-to-provider mapper, and the DB ingestion/export pipeline.
"""

from bots.ai_provider_registry.provider_schema import AIProviderObject
from bots.ai_provider_registry.taxonomy import (
    CATEGORY_TAXONOMY,
    AI_CLUSTERS,
    PRICING_TIERS,
    VALID_LAYERS,
    ALL_CATEGORIES,
)
from bots.ai_provider_registry.provider_catalog import PROVIDER_CATALOG, PROVIDER_CATALOG_BY_ID
from bots.ai_provider_registry.registry_db import RegistryDB, ingest_catalog, export_json
from bots.ai_provider_registry.router_brain import (
    RouterBrain,
    ProviderSelectorEngine,
    CostOptimizerEngine,
    CapabilityGraphEngine,
    FailureRedundancyEngine,
    RouterResult,
    TASK_CAPABILITY_MAP,
)
from bots.ai_provider_registry.bot_provider_mapper import (
    BotProviderMapper,
    BotProviderMapping,
    BOT_MAPPING_REGISTRY,
)

__all__ = [
    # Schema
    "AIProviderObject",
    # Taxonomy
    "CATEGORY_TAXONOMY",
    "AI_CLUSTERS",
    "PRICING_TIERS",
    "VALID_LAYERS",
    "ALL_CATEGORIES",
    # Catalog
    "PROVIDER_CATALOG",
    "PROVIDER_CATALOG_BY_ID",
    # DB
    "RegistryDB",
    "ingest_catalog",
    "export_json",
    # Router Brain
    "RouterBrain",
    "ProviderSelectorEngine",
    "CostOptimizerEngine",
    "CapabilityGraphEngine",
    "FailureRedundancyEngine",
    "RouterResult",
    "TASK_CAPABILITY_MAP",
    # Bot Mapper
    "BotProviderMapper",
    "BotProviderMapping",
    "BOT_MAPPING_REGISTRY",
]
