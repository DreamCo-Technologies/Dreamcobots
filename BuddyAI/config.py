"""
config.py – Configuration and API key management for BuddyAI.

All sensitive values should be supplied via environment variables or a
local `config.json` file (never committed to version control).  The
module provides sensible defaults so the system works out-of-the-box for
testing without real credentials.
"""

import json
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Default configuration
# ---------------------------------------------------------------------------
_DEFAULTS: dict = {
    # ── Income source API endpoints / credentials ──────────────────────────
    "youtube_api_key": "",
    "youtube_channel_id": "",
    "adsense_api_key": "",
    "blog_analytics_api_key": "",
    "affiliate_api_key": "",
    "saas_api_key": "",

    # ── Content generation ─────────────────────────────────────────────────
    "openai_api_key": "",
    "content_output_dir": "output/content",

    # ── Market analysis ────────────────────────────────────────────────────
    "trends_api_key": "",
    "market_scan_interval_hours": 24,
    "top_trends_limit": 10,

    # ── ML optimizer ──────────────────────────────────────────────────────
    "ml_model_dir": "output/models",
    "training_data_dir": "output/training_data",
    "optimization_iterations": 100,

    # ── Dashboard ─────────────────────────────────────────────────────────
    "dashboard_output_dir": "output/dashboard",
    "report_format": "text",          # "text" | "json"

    # ── General ────────────────────────────────────────────────────────────
    "log_level": "INFO",
    "buddy_bot_name": "BuddyBot",
}


def load_config(config_path: str | None = None) -> dict:
    """Return the merged configuration dictionary.

    Resolution order (highest priority first):
    1. Environment variables (prefixed with ``BUDDYAI_``).
    2. JSON file at *config_path* (default: ``BuddyAI/config.json``).
    3. Built-in defaults.
    """
    cfg = dict(_DEFAULTS)

    # 1. JSON file
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.isfile(config_path):
        with open(config_path, "r", encoding="utf-8") as fh:
            file_cfg = json.load(fh)
        cfg.update(file_cfg)

    # 2. Environment variables
    for key in list(cfg.keys()):
        env_key = f"BUDDYAI_{key.upper()}"
        if env_key in os.environ:
            cfg[key] = os.environ[env_key]

    return cfg


def ensure_output_dirs(cfg: dict) -> None:
    """Create output directories referenced in *cfg* if they don't exist."""
    for dir_key in ("content_output_dir", "ml_model_dir",
                    "training_data_dir", "dashboard_output_dir"):
        path = cfg.get(dir_key, "")
        if path:
            Path(path).mkdir(parents=True, exist_ok=True)
