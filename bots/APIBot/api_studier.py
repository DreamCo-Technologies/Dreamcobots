"""
APIStudier — deep-studies all APIs in the DreamCo ecosystem and builds a
comprehensive knowledge base of endpoints, schemas, rate limits, and patterns.

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  GLOBAL AI SOURCES FLOW

logger = logging.getLogger(__name__)

BOTS_ROOT = Path(__file__).resolve().parents[2] / "bots"


@dataclass
class APIKnowledge:
    """Structured knowledge about a discovered API."""
    api_name: str
    bot_id: str
    base_url: str
    auth_type: str
    endpoints_discovered: List[str] = field(default_factory=list)
    sdk_imports: List[str] = field(default_factory=list)
    env_keys: List[str] = field(default_factory=list)
    rate_limit_rpm: int = 60
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "api_name": self.api_name,
            "bot_id": self.bot_id,
            "base_url": self.base_url,
            "auth_type": self.auth_type,
            "endpoints_discovered": self.endpoints_discovered,
            "sdk_imports": self.sdk_imports,
            "env_keys": self.env_keys,
            "rate_limit_rpm": self.rate_limit_rpm,
            "notes": self.notes,
        }


class APIStudier:
    """
    Scans all bot source files to extract API usage patterns,
    builds a living knowledge base, and feeds it into the GlobalAI pipeline.

    GLOBAL AI SOURCES FLOW
    """

    # Patterns to detect API usage in bot source code
    API_URL_MARKERS = [
        "openai.com", "stripe.com", "github.com/api", "zillow", "scraperapi",
        "linkedin.com", "googleapis.com", "apollo.io", "fiverr.com",
        "upwork.com", "twilio.com", "sendgrid.com", "replit.com", "neon.tech",
        "pinecone.io", "anthropic.com", "cohere.com", "huggingface.co",
    ]

    SDK_MARKERS = {
        "openai": "openai",
        "stripe": "stripe",
        "github": "PyGithub",
        "twilio": "twilio",
        "sendgrid": "sendgrid",
        "anthropic": "anthropic",
        "cohere": "cohere",
        "pinecone": "pinecone",
        "langchain": "langchain",
    }

    def __init__(self) -> None:
        self._flow = GlobalAISourcesFlow(bot_name="APIStudier")
        self._knowledge: Dict[str, List[APIKnowledge]] = {}

    def study_bot(self, bot_dir: Path) -> List[APIKnowledge]:
        """Scan a single bot directory and extract API knowledge."""
        bot_id = bot_dir.name.lower().replace("-", "_")
        knowledge_list: List[APIKnowledge] = []

        py_files = list(bot_dir.glob("*.py"))
        all_text = ""
        for py_file in py_files:
            try:
                all_text += py_file.read_text(errors="ignore")
            except OSError:
                pass

        # Detect APIs by URL marker
        for marker in self.API_URL_MARKERS:
            if marker in all_text:
                api_name = marker.split(".")[0].replace("/api", "")
                knowledge = APIKnowledge(
                    api_name=api_name,
                    bot_id=bot_id,
                    base_url=f"https://{marker}",
                    auth_type="bearer",
                    notes=f"Detected via URL marker '{marker}'",
                )
                knowledge_list.append(knowledge)

        # Detect SDK imports
        for sdk_name, sdk_pkg in self.SDK_MARKERS.items():
            if f"import {sdk_name}" in all_text or f"from {sdk_name}" in all_text:
                knowledge = APIKnowledge(
                    api_name=sdk_name,
                    bot_id=bot_id,
                    base_url=f"https://api.{sdk_name}.com",
                    auth_type="bearer",
                    sdk_imports=[sdk_pkg],
                    notes=f"Detected via SDK import '{sdk_name}'",
                )
                knowledge_list.append(knowledge)

        # Detect env var keys
        import re
        env_keys = re.findall(r'os\.(?:environ|getenv)\s*[\[\(]["\']([A-Z_]+)["\']', all_text)
        for k in knowledge_list:
            k.env_keys = list(set(env_keys))

        self._knowledge[bot_id] = knowledge_list
        return knowledge_list

    def study_all_bots(self) -> Dict[str, Any]:
        """Scan every bot directory and return the full API knowledge base."""
        total_apis = 0
        for bot_dir in sorted(BOTS_ROOT.iterdir()):
            if not bot_dir.is_dir():
                continue
            knowledge = self.study_bot(bot_dir)
            total_apis += len(knowledge)

        # Run through GlobalAI pipeline
        result = self._flow.run_pipeline(
            raw_data={"bots_studied": len(self._knowledge), "total_apis": total_apis},
            learning_method="transfer_learning",
        )

        return {
            "bots_studied": len(self._knowledge),
            "total_api_usages": total_apis,
            "knowledge_base": {
                bot_id: [k.to_dict() for k in ks]
                for bot_id, ks in self._knowledge.items()
                if ks
            },
            "pipeline": result,
        }

    def get_most_used_apis(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Return the top N most commonly used APIs across all bots."""
        counts: Dict[str, int] = {}
        for knowledge_list in self._knowledge.values():
            for k in knowledge_list:
                counts[k.api_name] = counts.get(k.api_name, 0) + 1
        sorted_apis = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [{"api": api, "bot_count": count} for api, count in sorted_apis[:top_n]]

    def export_knowledge_json(self, output_path: str) -> str:
        """Export the full knowledge base to a JSON file."""
        data = {
            bot_id: [k.to_dict() for k in ks]
            for bot_id, ks in self._knowledge.items()
        }
        Path(output_path).write_text(json.dumps(data, indent=2))
        logger.info("API knowledge base exported to %s", output_path)
        return output_path
