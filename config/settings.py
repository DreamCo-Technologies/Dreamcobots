"""
DreamCo Configuration — Central settings module.

Reads API keys and runtime configuration from environment variables or an
optional ``.env`` file (loaded automatically if ``python-dotenv`` is installed).

Usage
-----
    from config.settings import settings

    print(settings.openai_api_key)
    print(settings.stripe_api_key)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

# Load .env file if python-dotenv is available (optional dependency)
try:
    from dotenv import load_dotenv  # type: ignore[import-not-found]
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed — use environment variables directly


# ---------------------------------------------------------------------------
# Settings dataclass
# ---------------------------------------------------------------------------


@dataclass
class Settings:
    """
    Runtime configuration for the DreamCo Autonomous AI Business OS.

    All fields fall back to safe defaults when the corresponding environment
    variable is not set, so the system can operate in simulation mode without
    any API keys.
    """

    # ---- External API keys ------------------------------------------------
    zillow_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ZILLOW_API_KEY")
    )
    stripe_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("STRIPE_API_KEY")
    )
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    # AI-Integrations module key — use AI_INTEGRATIONS_OPENAI_API_KEY when a
    # separate key is required for the ai-models-integration bot; falls back to
    # the general OPENAI_API_KEY when the dedicated variable is not set.
    ai_integrations_openai_api_key: Optional[str] = field(
        default_factory=lambda: (
            os.getenv("AI_INTEGRATIONS_OPENAI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
    )
    # Custom OpenAI-compatible base URL (leave empty for the default
    # https://api.openai.com/v1).
    openai_endpoint: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_ENDPOINT")
    )
    github_token: Optional[str] = field(
        default_factory=lambda: os.getenv("GITHUB_TOKEN")
    )
    scraper_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("SCRAPER_API_KEY")
    )

    # ---- Runtime flags ----------------------------------------------------
    simulation_mode: bool = field(
        default_factory=lambda: os.getenv("SIMULATION_MODE", "true").lower()
        in ("true", "1", "yes")
    )
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    money_loop_cycles: int = field(
        default_factory=lambda: int(os.getenv("MONEY_LOOP_CYCLES", "1"))
    )

    # ---- Revenue thresholds (can be overridden via env) ------------------
    scale_threshold_usd: float = field(
        default_factory=lambda: float(os.getenv("SCALE_THRESHOLD_USD", "1000.0"))
    )
    maintain_threshold_usd: float = field(
        default_factory=lambda: float(os.getenv("MAINTAIN_THRESHOLD_USD", "100.0"))
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def is_real_mode(self) -> bool:
        """Return ``True`` when NOT in simulation mode (live API calls)."""
        return not self.simulation_mode

    def has_key(self, key_name: str) -> bool:
        """Return ``True`` if the named API key is set and non-empty."""
        value = getattr(self, key_name, None)
        return bool(value)

    def active_keys(self) -> list[str]:
        """Return the names of all API keys that are currently set."""
        key_fields = [
            "zillow_api_key",
            "stripe_api_key",
            "openai_api_key",
            "ai_integrations_openai_api_key",
            "github_token",
            "scraper_api_key",
        ]
        return [k for k in key_fields if getattr(self, k)]

    def to_dict(self) -> dict:
        """Return a sanitised (no raw secrets) view of the settings."""
        return {
            "simulation_mode": self.simulation_mode,
            "log_level": self.log_level,
            "money_loop_cycles": self.money_loop_cycles,
            "scale_threshold_usd": self.scale_threshold_usd,
            "maintain_threshold_usd": self.maintain_threshold_usd,
            "keys_configured": self.active_keys(),
        }


# ---------------------------------------------------------------------------
# Module-level singleton — import this object everywhere
# ---------------------------------------------------------------------------

settings = Settings()
