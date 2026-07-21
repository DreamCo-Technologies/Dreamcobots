"""Central configuration management for Dreamcobots."""
import json
import os
from pathlib import Path


class ConfigLoader:
    """Loads and manages configuration for all bots."""

    _instance = None
    _config = {}

    def __new__(cls):
        """Singleton pattern - only one config loader instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        """Load configuration from bots/config.json."""
        config_path = Path(__file__).parent.parent / "bots" / "config.json"
        try:
            with open(config_path) as f:
                self._config = json.load(f)
        except Exception:
            self._config = {}

    def get(self, key, default=None):
        """Get a configuration value by key."""
        return self._config.get(key, default)

    def all(self):
        """Return a copy of the full configuration dictionary."""
        return dict(self._config)

    def reload(self):
        """Reload configuration from disk."""
        self._load()


config = ConfigLoader()
