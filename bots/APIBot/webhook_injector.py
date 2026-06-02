"""
APIWebhookInjector — scans all bots for missing webhook integration and
auto-injects WebhooksBot calls into each bot's main.py.

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  GLOBAL AI SOURCES FLOW

logger = logging.getLogger(__name__)

BOTS_ROOT = Path(__file__).resolve().parents[2] / "bots"

WEBHOOK_IMPORT_BLOCK = """\
# ── WebhooksBot integration (auto-injected by APIBot v1.0) ─────────────────
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), "..", ".."))
try:
    from bots.WebhooksBot import WebhooksBot as _WB, WebhookEventType as _WET
    _dreamco_webhooks = _WB()
    _dreamco_webhooks.register(
        "{bot_id}",
        "https://hooks.dreamco.io/bots/{bot_id}",
        list(_WET),
    )
except Exception as _e:
    pass  # Webhook integration optional in standalone mode
# ───────────────────────────────────────────────────────────────────────────
"""


class APIWebhookInjector:
    """
    Scans every bot in bots/ and injects WebhooksBot integration
    into main.py files that do not already have it.

    Dry-run by default; set dry_run=False to write files.

    GLOBAL AI SOURCES FLOW
    """

    def __init__(self, dry_run: bool = True) -> None:
        self._flow = GlobalAISourcesFlow(bot_name="APIWebhookInjector")
        self.dry_run = dry_run
        self._results: List[Dict[str, Any]] = []

    def inject_all(self) -> Dict[str, Any]:
        """Scan all bots and inject webhooks where missing."""
        injected = 0
        skipped = 0
        errors = 0

        for bot_dir in sorted(BOTS_ROOT.iterdir()):
            if not bot_dir.is_dir() or bot_dir.name in ("WebhooksBot", "APIBot"):
                continue
            result = self._inject_bot(bot_dir)
            self._results.append(result)
            if result["status"] == "injected":
                injected += 1
            elif result["status"] == "skipped":
                skipped += 1
            else:
                errors += 1

        pipeline = self._flow.run_pipeline(
            raw_data={"injected": injected, "skipped": skipped, "errors": errors},
            learning_method="supervised",
        )

        return {
            "injected": injected,
            "skipped": skipped,
            "errors": errors,
            "dry_run": self.dry_run,
            "pipeline": pipeline,
            "details": self._results,
        }

    def _inject_bot(self, bot_dir: Path) -> Dict[str, Any]:
        bot_id = bot_dir.name.lower().replace("-", "_")
        main_py = bot_dir / "main.py"

        if not main_py.exists():
            return {"bot_id": bot_id, "status": "skipped", "reason": "no main.py"}

        try:
            content = main_py.read_text(errors="ignore")
        except OSError as exc:
            return {"bot_id": bot_id, "status": "error", "reason": str(exc)}

        if "_dreamco_webhooks" in content or "WebhooksBot" in content:
            return {"bot_id": bot_id, "status": "skipped", "reason": "already integrated"}

        snippet = WEBHOOK_IMPORT_BLOCK.replace("{bot_id}", bot_id)
        new_content = snippet + content

        if not self.dry_run:
            try:
                main_py.write_text(new_content)
            except OSError as exc:
                return {"bot_id": bot_id, "status": "error", "reason": str(exc)}

        return {
            "bot_id": bot_id,
            "status": "injected",
            "dry_run": self.dry_run,
            "bytes_added": len(snippet),
        }

    def get_results(self) -> List[Dict[str, Any]]:
        return list(self._results)

    def get_injection_report(self) -> Dict[str, Any]:
        total = len(self._results)
        injected = sum(1 for r in self._results if r["status"] == "injected")
        return {
            "total_bots_scanned": total,
            "injected": injected,
            "coverage_pct": injected / max(1, total) * 100,
            "dry_run": self.dry_run,
        }
