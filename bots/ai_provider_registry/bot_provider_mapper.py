"""
bot_provider_mapper.py — Bot-to-provider mapping engine.

Maps every DreamCo bot to its recommended AI provider(s) from the catalog,
with primary + fallback assignments and optional cost tier selection.
"""
from __future__ import annotations

from framework import GlobalAISourcesFlow  # noqa: F401

from dataclasses import dataclass, field
from typing import Optional

from bots.ai_provider_registry.provider_schema import AIProviderObject
from bots.ai_provider_registry.provider_catalog import PROVIDER_CATALOG_BY_ID


@dataclass
class BotProviderMapping:
    bot_id: str
    primary_provider_ids: list[str]
    fallback_provider_ids: list[str]
    task_type: str
    notes: str = ""

    def primary_providers(self) -> list[AIProviderObject]:
        return [PROVIDER_CATALOG_BY_ID[i] for i in self.primary_provider_ids
                if i in PROVIDER_CATALOG_BY_ID]

    def fallback_providers(self) -> list[AIProviderObject]:
        return [PROVIDER_CATALOG_BY_ID[i] for i in self.fallback_provider_ids
                if i in PROVIDER_CATALOG_BY_ID]


# ---------------------------------------------------------------------------
# Static mapping registry
# (Extend as bots are added; IDs match PROVIDER_CATALOG_BY_ID keys)
# ---------------------------------------------------------------------------
_BOT_MAPPINGS: list[BotProviderMapping] = [
    # ── Core / LLM Bots ───────────────────────────────────────────────────
    BotProviderMapping(
        "global_sources_ai_bot",
        primary_provider_ids=["openai", "anthropic", "google_ai_platform"],
        fallback_provider_ids=["mistral_ai", "cohere", "xai"],
        task_type="research",
        notes="Primary research and retrieval bot",
    ),
    BotProviderMapping(
        "ai_provider_registry_bot",
        primary_provider_ids=["openai", "pinecone_co", "weaviate_co"],
        fallback_provider_ids=["anthropic", "redis_ai"],
        task_type="vector_search",
        notes="Registry RAG + semantic search",
    ),
    # ── Developer Bots ────────────────────────────────────────────────────
    BotProviderMapping(
        "repo_validation_bot",
        primary_provider_ids=["github_copilot_co", "snyk_ai"],
        fallback_provider_ids=["codeium", "tabnine"],
        task_type="code_review",
    ),
    BotProviderMapping(
        "sandbox_builder_bot",
        primary_provider_ids=["replit_co", "stackblitz", "vercel_ai"],
        fallback_provider_ids=["modal_labs", "replicate_co"],
        task_type="app_deployment",
    ),
    # ── Media / Creative Bots ─────────────────────────────────────────────
    BotProviderMapping(
        "professional_video_editing_bot",
        primary_provider_ids=["runway_co", "pika_labs_co"],
        fallback_provider_ids=["synthesia", "luma_ai_co", "captions_ai"],
        task_type="video_creation",
    ),
    BotProviderMapping(
        "professional_music_editing_bot",
        primary_provider_ids=["suno_co"],
        fallback_provider_ids=["elevenlabs_co", "resemble_ai"],
        task_type="music_composition",
    ),
    BotProviderMapping(
        "buddy_media_transformation_bot",
        primary_provider_ids=["canva_ai_co", "stability_ai"],
        fallback_provider_ids=["midjourney_co", "runway_co"],
        task_type="image_generation",
    ),
    # ── Sales & Marketing Bots ────────────────────────────────────────────
    BotProviderMapping(
        "marketing_bot",
        primary_provider_ids=["jasper_ai_co", "copy_ai_co", "clay_ai"],
        fallback_provider_ids=["writer_ai", "grammarly_co", "lavender_ai"],
        task_type="marketing_funnel",
    ),
    BotProviderMapping(
        "sales_intelligence_bot",
        primary_provider_ids=["gong_io", "apollo_io_ai", "zoominfo_ai"],
        fallback_provider_ids=["chorus_ai", "clearbit_ai", "drift_ai"],
        task_type="lead_generation",
    ),
    # ── Data & Analytics Bots ─────────────────────────────────────────────
    BotProviderMapping(
        "data_ops_bot",
        primary_provider_ids=["databricks_co", "snowflake_ai_co"],
        fallback_provider_ids=["cloudera_ai", "alteryx_ai"],
        task_type="data_pipeline",
    ),
    BotProviderMapping(
        "analytics_bot",
        primary_provider_ids=["thoughtspot", "elastic_ai_co"],
        fallback_provider_ids=["tibco_ai", "fractal_analytics"],
        task_type="analytics_report",
    ),
    # ── Security Bots ─────────────────────────────────────────────────────
    BotProviderMapping(
        "security_bot",
        primary_provider_ids=["darktrace_co", "crowdstrike_co", "sentinelone_co"],
        fallback_provider_ids=["vectra_ai_co", "cybereason", "arctic_wolf"],
        task_type="threat_detection",
    ),
    # ── Healthcare Bots ───────────────────────────────────────────────────
    BotProviderMapping(
        "healthcare_bot",
        primary_provider_ids=["abridge_ai", "tempus_ai_co", "aidoc"],
        fallback_provider_ids=["path_ai", "viz_ai_co", "olive_ai"],
        task_type="medical_imaging",
    ),
    # ── Legal Bots ────────────────────────────────────────────────────────
    BotProviderMapping(
        "legal_bot",
        primary_provider_ids=["harvey_ai_co", "luminance_ai", "ironclad_ai"],
        fallback_provider_ids=["evisort", "relativity_ai_co", "everlaw"],
        task_type="legal_review",
    ),
    # ── Finance Bots ─────────────────────────────────────────────────────
    BotProviderMapping(
        "finance_bot",
        primary_provider_ids=["bloomberg_ai_co", "kensho_ai_co"],
        fallback_provider_ids=["stripe_ai_co", "plaid_ai", "zest_ai"],
        task_type="financial_analysis",
    ),
    # ── Real Estate Bots ─────────────────────────────────────────────────
    BotProviderMapping(
        "real_estate_bot",
        primary_provider_ids=["openai", "databricks_co", "thoughtspot"],
        fallback_provider_ids=["anthropic", "elastic_ai_co"],
        task_type="analytics_report",
        notes="Property analytics & market intelligence",
    ),
    # ── HR Bots ──────────────────────────────────────────────────────────
    BotProviderMapping(
        "hr_bot",
        primary_provider_ids=["workday_ai_co", "rippling_ai", "deel_ai"],
        fallback_provider_ids=["lattice_ai_co", "bamboohr_ai", "gusto_ai"],
        task_type="hr_operations",
    ),
    # ── Automation Bots ───────────────────────────────────────────────────
    BotProviderMapping(
        "automation_bot",
        primary_provider_ids=["uipath_co", "automation_anywhere"],
        fallback_provider_ids=["adept_ai", "uipath_autopilot", "servicenow_ai"],
        task_type="workflow_automation",
    ),
    # ── Education Bots ───────────────────────────────────────────────────
    BotProviderMapping(
        "education_bot",
        primary_provider_ids=["khan_academy_ai", "coursera_ai_co", "duolingo_ai_co"],
        fallback_provider_ids=["speak_ai_co", "udacity_ai"],
        task_type="research",
        notes="Adaptive learning and tutoring",
    ),
    # ── Infrastructure / DevOps Bots ─────────────────────────────────────
    BotProviderMapping(
        "devops_bot",
        primary_provider_ids=["azure_ai_co", "aws_ai_co", "modal_labs"],
        fallback_provider_ids=["together_ai_co", "runpod_ai", "lambda_cloud"],
        task_type="app_deployment",
    ),
]

# Fast lookup: bot_id → BotProviderMapping
BOT_MAPPING_REGISTRY: dict[str, BotProviderMapping] = {
    m.bot_id: m for m in _BOT_MAPPINGS
}


class BotProviderMapper:
    """Query and manage bot-to-provider mappings."""

    def __init__(self, mappings: Optional[list[BotProviderMapping]] = None) -> None:
        self._mappings: dict[str, BotProviderMapping] = {
            m.bot_id: m for m in (mappings or _BOT_MAPPINGS)
        }

    def get(self, bot_id: str) -> Optional[BotProviderMapping]:
        return self._mappings.get(bot_id)

    def list_all(self) -> list[BotProviderMapping]:
        return list(self._mappings.values())

    def providers_for_bot(
        self,
        bot_id: str,
        include_fallbacks: bool = False,
    ) -> list[AIProviderObject]:
        m = self._mappings.get(bot_id)
        if not m:
            return []
        providers = m.primary_providers()
        if include_fallbacks:
            providers += m.fallback_providers()
        return providers

    def bots_using_provider(self, provider_id: str) -> list[str]:
        """Return all bot_ids that use a given provider (primary or fallback)."""
        result = []
        for m in self._mappings.values():
            if provider_id in m.primary_provider_ids + m.fallback_provider_ids:
                result.append(m.bot_id)
        return result

    def register(self, mapping: BotProviderMapping) -> None:
        self._mappings[mapping.bot_id] = mapping

    def summary(self) -> dict:
        provider_usage: dict[str, int] = {}
        for m in self._mappings.values():
            for pid in m.primary_provider_ids + m.fallback_provider_ids:
                provider_usage[pid] = provider_usage.get(pid, 0) + 1
        top = sorted(provider_usage.items(), key=lambda x: -x[1])[:10]
        return {
            "total_bots_mapped": len(self._mappings),
            "total_provider_references": sum(provider_usage.values()),
            "top_providers": [{"id": pid, "usage_count": cnt} for pid, cnt in top],
        }


__all__ = [
    "BotProviderMapper",
    "BotProviderMapping",
    "BOT_MAPPING_REGISTRY",
]
