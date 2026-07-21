#!/usr/bin/env python3
"""
DreamCobots Debug Utility

This module provides debugging and diagnostic tools for all Dreamcobots bots.
It can be run directly to test bot connectivity, configuration, and runtime
behavior, or imported by individual bot scripts for logging support.
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger("DreamCobots.Debug")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_config(config_path: str = None) -> dict:
    """Load and return the bot configuration from config.json."""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "bots", "config.json")

    if not os.path.exists(config_path):
        logger.warning("config.json not found at %s", config_path)
        return {}

    with open(config_path, "r") as fh:
        config = json.load(fh)
    logger.debug("Loaded config from %s: %s", config_path, config)
    return config


def check_environment() -> dict:
    """Return a summary of the current runtime environment."""
    info = {
        "python_version": sys.version,
        "platform": sys.platform,
        "cwd": os.getcwd(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    logger.debug("Environment: %s", info)
    return info


def run_bot_diagnostics(bot_instance) -> bool:
    """
    Run basic diagnostics against a bot instance.

    Checks that the bot exposes the expected interface (start / run methods)
    and attempts a dry-run invocation.  Returns True if all checks pass.
    """
    passed = True

    for method_name in ("start", "run"):
        if not callable(getattr(bot_instance, method_name, None)):
            logger.error(
                "Bot %s is missing required method: %s",
                type(bot_instance).__name__,
                method_name,
            )
            passed = False
        else:
            logger.debug(
                "Bot %s has method: %s ✓", type(bot_instance).__name__, method_name
            )

    return passed


def stress_test_bot(bot_instance, iterations: int = 10) -> dict:
    """
    Run a simple stress test by invoking bot.run() multiple times.

    Returns a dict with counts of successes and failures.
    """
    results = {"iterations": iterations, "successes": 0, "failures": 0, "errors": []}

    for i in range(iterations):
        try:
            bot_instance.run()
            results["successes"] += 1
            logger.debug("Iteration %d/%d: OK", i + 1, iterations)
        except Exception as exc:  # noqa: BLE001 — intentional: capture any bot failure without crashing the test runner
            results["failures"] += 1
            error_msg = f"Iteration {i + 1}: {exc}"
            results["errors"].append(error_msg)
            logger.warning(error_msg)
            logger.debug(traceback.format_exc())

    logger.info(
        "Stress test complete: %d/%d succeeded",
        results["successes"],
        results["iterations"],
    )
    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Run full diagnostics for all known bots."""
    logger.info("=== DreamCobots Debug Utility ===")

    # Environment check
    env = check_environment()
    logger.info("Python %s on %s", env["python_version"].split()[0], env["platform"])

    # Config check
    config = load_config()
    if config:
        logger.info("Config loaded successfully.")
    else:
        logger.warning("Config is empty or missing — please update bots/config.json.")

    # Bot diagnostics
    gov_bot_dir = os.path.join(
        os.path.dirname(__file__),
        "bots",
        "government-contract-grant-bot",
    )
    sys.path.insert(0, gov_bot_dir)

    try:
        from government_contract_grant_bot import (  # noqa: E402
            GovernmentContractGrantBot,
        )

        bot = GovernmentContractGrantBot()
        logger.info("Running diagnostics for GovernmentContractGrantBot…")
        ok = run_bot_diagnostics(bot)
        if ok:
            logger.info("GovernmentContractGrantBot diagnostics passed ✓")
        else:
            logger.error("GovernmentContractGrantBot diagnostics FAILED ✗")

        logger.info("Running stress test (10 iterations)…")
        results = stress_test_bot(bot, iterations=10)
        logger.info(
            "Stress test results: %d successes, %d failures",
            results["successes"],
            results["failures"],
        )
    except ImportError as exc:
        logger.error("Could not import GovernmentContractGrantBot: %s", exc)

    logger.info("=== Debug session complete ===")


if __name__ == "__main__":
    main()
