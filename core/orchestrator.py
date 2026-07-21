"""
DreamCo Core — Master Orchestrator

Coordinates all DreamCo OS bots, wires them to the shared event bus, and
runs the full pipeline:

    [Bot Runner] → [Event Bus] → [Bot Network] → [Money Actions]

Usage
-----
    python core/orchestrator.py

or programmatically::

    from core.orchestrator import Orchestrator
    orch = Orchestrator()
    orch.start()
"""

from __future__ import annotations

import importlib
import os
import sys
from typing import Any, List, Optional

# ---------------------------------------------------------------------------
# Ensure the repo root is on sys.path so that sibling packages (event_bus,
# python_bots, etc.) are importable whether this file is run as a script
# (python core/orchestrator.py) or imported as a module.
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from event_bus.redis_bus import RedisEventBus
from python_bots.base_bot import BaseBot
from python_bots.real_estate.bot import RealEstateBot
from core.bot_lab import BotLab
from core.bot_registry import register_bot, get_registered_bots, clear_registry

# ---------------------------------------------------------------------------
# Money pipeline handler
# ---------------------------------------------------------------------------


def handle_deal(data: Any) -> None:
    """
    Handle a ``deal_found`` event from any bot.

    Parameters
    ----------
    data : dict
        Deal payload with at minimum ``profit`` key.
    """
    print(f"💰 DEAL RECEIVED: {data}")

    profit = data.get("profit", 0) if isinstance(data, dict) else 0
    if profit > 10000:
        print("🔥 HIGH VALUE DEAL — eligible for automated outreach / Stripe trigger")
        # Future: send email, add to CRM, trigger Stripe payment
        # requests.post("payment_endpoint", json=data)


# ---------------------------------------------------------------------------
# Auto bot discovery
# ---------------------------------------------------------------------------


def _load_bots_from_dirs(bot_dirs: List[str], repo_root: str) -> List[BaseBot]:
    """
    Auto-discover and instantiate all ``BaseBot`` subclasses found in
    *bot_dirs*.

    Parameters
    ----------
    bot_dirs : list of str
        Directory names (relative to *repo_root*) to scan.
    repo_root : str
        Absolute path to the repository root.

    Returns
    -------
    list of BaseBot instances
    """
    bots: List[BaseBot] = []

    for bot_dir in bot_dirs:
        dir_path = os.path.join(repo_root, bot_dir)
        if not os.path.isdir(dir_path):
            continue

        for filename in os.listdir(dir_path):
            if not filename.endswith(".py") or filename.startswith("_"):
                continue

            module_name = f"{bot_dir}.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
            except Exception as exc:  # pylint: disable=broad-except
                print(f"⚠️  Could not import {module_name}: {exc}")
                continue

            for attr_name in dir(module):
                obj = getattr(module, attr_name)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, BaseBot)
                    and obj is not BaseBot
                ):
                    try:
                        bots.append(obj(attr_name))
                    except Exception:  # pylint: disable=broad-except
                        pass

    return bots


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class Orchestrator:
    """
    DreamCo OS master orchestrator.

    Parameters
    ----------
    repo_root : str, optional
        Absolute path to the repository root used for bot auto-discovery.
        Defaults to the parent directory of this file.
    auto_discover : bool
        When ``True`` additional bots are auto-discovered from
        ``python_bots/`` and ``Real_Estate_bots/`` directories.
    """

    def __init__(
        self,
        repo_root: Optional[str] = None,
        auto_discover: bool = True,
    ) -> None:
        self.repo_root = repo_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        self.bus = RedisEventBus()
        self.lab = BotLab()
        self.auto_discover = auto_discover

        # Insert repo root so relative imports work when run as __main__
        if self.repo_root not in sys.path:
            sys.path.insert(0, self.repo_root)

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _register_listeners(self) -> None:
        """Subscribe system-level handlers to the event bus."""
        self.bus.subscribe("deal_found", handle_deal)

    def _build_bot_list(self) -> List[BaseBot]:
        """
        Return the list of bots to run.

        Core bots are always included.  When ``auto_discover`` is enabled
        additional bots are found by scanning known directories.
        """
        # Core bots — always included
        core_bots: List[BaseBot] = [
            RealEstateBot("real_estate"),
        ]

        # Try to include Feature1Bot from the existing Real_Estate_bots folder
        try:
            from Real_Estate_bots.feature_1 import Feature1Bot  # type: ignore[import]
            core_bots.append(Feature1Bot("feature_1"))
        except Exception:  # pylint: disable=broad-except
            pass

        if not self.auto_discover:
            return core_bots

        # Auto-discovered bots (deduplicate by class)
        discovered = _load_bots_from_dirs(
            ["python_bots"],
            self.repo_root,
        )
        seen_classes = {type(b) for b in core_bots}
        for bot in discovered:
            if type(bot) not in seen_classes:
                core_bots.append(bot)
                seen_classes.add(type(bot))

        return core_bots

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Start the DreamCo OS:

        1. Register event listeners.
        2. Build the bot list.
        3. Test each bot via ``BotLab``.
        4. Register approved bots.
        5. Run approved bots against the shared event bus.
        """
        print("🚀 DreamCo OS Starting")
        clear_registry()

        self._register_listeners()
        bots = self._build_bot_list()

        print(f"🤖 {len(bots)} bot(s) queued")

        for bot in bots:
            # Quick sanity test before full run
            test_bus = RedisEventBus()
            passed = self.lab.test_bot(bot, test_bus)

            if passed:
                register_bot({"name": bot.name, "type": type(bot).__name__, "status": "approved"})
                bot.run(self.bus)
            else:
                register_bot({"name": bot.name, "type": type(bot).__name__, "status": "failed_test"})

        summary = get_registered_bots()
        approved = [b for b in summary if b["status"] == "approved"]
        failed = [b for b in summary if b["status"] != "approved"]

        print(f"\n✅ DreamCo OS run complete — {len(approved)} approved, {len(failed)} failed")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    orch = Orchestrator()
    orch.start()
