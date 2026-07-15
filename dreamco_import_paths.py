"""Shared Python import path bootstrap for DreamCo legacy bot modules."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

LEGACY_IMPORT_PATHS = [
    ROOT,
    ROOT / "analytics-elites" / "algorithmic_trading_bot",
    ROOT / "analytics-elites" / "loyalty_program_impact_simulator",
    ROOT / "analytics-elites" / "predictive_engagement_tool",
    ROOT / "automation-tools" / "color_palette_generator",
    ROOT / "automation-tools" / "smart_meeting_scheduler",
    ROOT / "automation-tools" / "workplace_audit_tool",
    ROOT / "bots" / "ai-models-integration",
    ROOT / "bots" / "dreamco_empire_os",
    ROOT / "bots" / "global_bot_network",
    ROOT / "bots" / "government-contract-grant-bot",
    ROOT / "bots" / "hustle-bot",
    ROOT / "bots" / "job-application-bot",
    ROOT / "bots" / "referral-bot",
    ROOT / "bots" / "saas-selling-bot",
    ROOT / "core",
    ROOT / "dreamco-control-tower" / "backend",
    ROOT / "education-tools" / "recipe_scaling_tool",
    ROOT / "healthcare-tools" / "drug_discovery_pipeline_ai",
    ROOT / "healthcare-tools" / "mental_health_screening_bot",
    ROOT / "real-estate-tools" / "real_estate_cashflow_simulator",
]


def configure_import_paths() -> list[str]:
    """Ensure shared legacy import paths are available once per process."""
    added: list[str] = []
    for path in reversed(LEGACY_IMPORT_PATHS):
        path_string = str(path)
        if path.exists() and path_string not in sys.path:
            sys.path.insert(0, path_string)
            added.append(path_string)
    return added


configure_import_paths()
