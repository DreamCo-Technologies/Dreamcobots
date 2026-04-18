"""
DreamCo — main.py

System entry point.  Starts the DreamCo platform by:

  1. Adding the repository root to ``sys.path``.
  2. Loading all available bots via auto-discovery.
  3. Triggering the Control Center (Controller).
  4. Running one automation loop cycle.
  5. Executing one AI Learning Loop cycle.

Run:
    python main.py

GLOBAL AI SOURCES FLOW compliant.
"""

from __future__ import annotations

import logging
import os
import sys

# Ensure the repository root is always importable regardless of cwd.
_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Add ai-models-integration to path for tiers module used by control_center
_AI_MODELS_DIR = os.path.join(_REPO_ROOT, "bots", "ai-models-integration")
if _AI_MODELS_DIR not in sys.path:
    sys.path.insert(0, _AI_MODELS_DIR)

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)
from bots.control_center.controller import Controller
from bots.bot_generator_bot.generator import Generator
from bots.ai_learning_system.learning_loop import LearningLoop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dreamco.main")


def start() -> dict:
    """
    Start the DreamCo self-building system.

    Returns
    -------
    dict
        A summary dict with keys ``controller_status``, ``loop_results``,
        and ``learning_cycle``.
    """
    logger.info("=== DreamCo System Starting ===")

    # ------------------------------------------------------------------
    # 1. Initialise Controller (wraps ControlCenter)
    # ------------------------------------------------------------------
    controller = Controller()
    logger.info("Controller initialised.")

    # ------------------------------------------------------------------
    # 2. Initialise Generator (bot factory) and attach controller
    # ------------------------------------------------------------------
    bots_dir = os.path.join(_REPO_ROOT, "bots")
    generator = Generator(bots_root=bots_dir, controller=controller)
    logger.info("Generator initialised (bots_root=%s).", bots_dir)

    # ------------------------------------------------------------------
    # 3. Auto-discover and load all bots
    # ------------------------------------------------------------------
    discovered = controller.auto_discover_bots(bots_package_path=bots_dir)
    logger.info("Auto-discovered %d bot(s): %s", len(discovered), discovered)

    # ------------------------------------------------------------------
    # 4. Trigger control center — run one automation loop cycle
    # ------------------------------------------------------------------
    logger.info("Starting automation loop (1 cycle)...")
    loop_results = controller.run_loop(iterations=1)
    logger.info("Automation loop complete. Cycles run: %d", len(loop_results))

    # ------------------------------------------------------------------
    # 5. AI Learning Loop — analyse and evolve
    # ------------------------------------------------------------------
    learning_loop = LearningLoop(generator=generator)
    # Feed this cycle's results into the learning loop
    learning_loop.ingest_cycle_results(loop_results)
    learning_cycle = learning_loop.analyse()
    logger.info(
        "Learning loop analysis: %d healthy, %d underperforming, %d suggestion(s).",
        len(learning_cycle.get("healthy", [])),
        len(learning_cycle.get("underperforming", [])),
        len(learning_cycle.get("suggestions", [])),
    )

    # ------------------------------------------------------------------
    # 6. Summary
    # ------------------------------------------------------------------
    controller_status = controller.get_status()
    summary = {
        "controller_status": controller_status,
        "loop_results": loop_results,
        "learning_cycle": learning_cycle,
    }
    logger.info(
        "=== DreamCo System Ready — %d bot(s) registered ===",
        controller_status["control_center"]["total_bots"],
    )
    return summary


if __name__ == "__main__":
    result = start()
    registered = result["controller_status"]["control_center"]["total_bots"]
    print(f"\nDreamCo is live! {registered} bot(s) registered and running.")
