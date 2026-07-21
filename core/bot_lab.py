"""
DreamCo Core — Bot Lab

End-to-end pipeline for loading, testing, and training any bot that is
submitted to the DreamCo OS platform.

Pipeline
--------
    1. :meth:`load_bot`    — dynamically import a bot class
    2. :meth:`test_bot`    — run the bot against a mock event bus
    3. :meth:`train_bot`   — placeholder hook for future AI fine-tuning
    4. :meth:`process_upload` — convenience wrapper for uploaded files
"""

from __future__ import annotations

import importlib
import traceback
from typing import Any, Dict, Optional

from core.bot_validator import validate_bot
from core.sandbox_runner import run_in_sandbox


class BotLab:
    """
    Load, test, and train DreamCo OS bots.

    All methods are safe to call in sequence or independently.
    """

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load_bot(self, module_path: str, class_name: str) -> Optional[Any]:
        """
        Dynamically import *class_name* from the dotted *module_path*.

        Parameters
        ----------
        module_path : str
            Dotted Python module path (e.g. ``"Real_Estate_bots.feature_1"``).
        class_name : str
            Name of the class to instantiate.

        Returns
        -------
        bot instance or ``None`` on failure.
        """
        try:
            module = importlib.import_module(module_path)
            bot_class = getattr(module, class_name)
            return bot_class(class_name)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"❌ BotLab.load_bot failed: {exc}")
            return None

    # ------------------------------------------------------------------
    # Test
    # ------------------------------------------------------------------

    def test_bot(self, bot: Any, event_bus: Any) -> bool:
        """
        Run *bot* against *event_bus* and report success / failure.

        Parameters
        ----------
        bot : BaseBot-like
            Any object with a ``run(event_bus)`` method and a ``name``
            attribute.
        event_bus : BaseEventBus-like
            Event bus instance to pass into the bot.

        Returns
        -------
        bool
            ``True`` if the bot completed without raising an exception.
        """
        try:
            print(f"🧪 BotLab: Testing {bot.name}")
            bot.run(event_bus)
            return True
        except Exception as exc:  # pylint: disable=broad-except
            print(f"❌ BotLab: Test failed for {bot.name}: {exc}")
            traceback.print_exc()
            return False

    # ------------------------------------------------------------------
    # Train
    # ------------------------------------------------------------------

    def train_bot(self, bot: Any) -> bool:
        """
        Run training / optimisation hooks on *bot*.

        Currently a stub; future versions will connect to OpenAI to
        optimise prompts and refine bot outputs.

        Parameters
        ----------
        bot : BaseBot-like

        Returns
        -------
        bool
            Always ``True`` for now.
        """
        print(f"🧠 BotLab: Training {bot.name}")
        # TODO: connect to OpenAI, optimise prompts, refine outputs
        return True

    # ------------------------------------------------------------------
    # Process uploaded file
    # ------------------------------------------------------------------

    def process_upload(self, file_path: str) -> Dict[str, Any]:
        """
        Full pipeline for an uploaded bot file:

        1. Validate (static analysis)
        2. Run in sandbox
        3. Return status report

        Parameters
        ----------
        file_path : str
            Absolute path to the uploaded ``.py`` file.

        Returns
        -------
        dict
            ``{"status": "approved"|"rejected"|"failed", ...}``
        """
        print(f"📦 BotLab: Processing upload: {file_path}")

        # Step 1 — static validation
        valid, msg = validate_bot(file_path)
        if not valid:
            return {"status": "rejected", "reason": msg}

        # Step 2 — sandboxed test run
        result = run_in_sandbox(file_path)
        if not result["success"]:
            return {"status": "failed", "error": result}

        return {"status": "approved", "output": result}
