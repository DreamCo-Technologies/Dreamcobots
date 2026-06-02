"""Promote sandbox bots to live only when 24h metrics clear the gate."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dreamco_platform.registry.bot_registry import BotRegistryEntry
from dreamco_platform.registry.registry_store import PostgresBotRegistryStore

ROOT = Path(__file__).resolve().parents[1]
METRICS_FILE = ROOT / "reports" / "sandbox_metrics.json"


@dataclass
class PromotionDecision:
    bot_slug: str
    approved: bool
    reasons: list[str]


class PromotionGate:
    """Check sandbox metrics and update registry state when a bot is promotable."""

    def __init__(self, store: PostgresBotRegistryStore | None = None) -> None:
        self.store = store or PostgresBotRegistryStore()

    def _load_metrics(self) -> dict[str, Any]:
        return json.loads(METRICS_FILE.read_text()) if METRICS_FILE.exists() else {}

    async def evaluate(self, bot_slug: str) -> PromotionDecision:
        metrics = self._load_metrics().get(bot_slug, {})
        reasons = []
        if metrics.get("error_rate", 1.0) >= 0.01:
            reasons.append("error_rate must be below 1%")
        if metrics.get("p95_latency_s", 99.0) >= 2.0:
            reasons.append("p95 latency must be below 2 seconds")
        if metrics.get("revenue_simulated", 0.0) <= 0:
            reasons.append("revenue_simulated must be positive")
        approved = not reasons
        if approved:
            entry = await self.store.get_entry(bot_slug)
            if entry is not None:
                payload = entry.to_dict()
                payload["metadata"] = {**payload.get("metadata", {}), "status": "live"}
                await self.store.save_entry(BotRegistryEntry.from_dict(payload))
        return PromotionDecision(bot_slug=bot_slug, approved=approved, reasons=reasons)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("bot_slug")
    args = parser.parse_args()
    decision = asyncio.run(PromotionGate().evaluate(args.bot_slug))
    print(json.dumps(decision.__dict__, indent=2))


if __name__ == "__main__":
    main()
