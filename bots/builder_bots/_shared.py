# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Shared helpers for the builder_bots package.

Provides utilities reused across all builder bots:
  • append_bot_ideas — thread-safe append of bot ideas to a log file.
"""

from __future__ import annotations

import threading
from typing import List

_file_lock = threading.Lock()


def append_bot_ideas(log_path: str, section: str, ideas: List[str]) -> None:
    """
    Append a named section of bot ideas to *log_path*.

    Parameters
    ----------
    log_path : str
        Path to the ideas log file (e.g. ``bot_ideas_log.txt``).
    section : str
        Heading for this section (usually the bot name).
    ideas : list of str
        Individual idea strings to record.
    """
    lines = [f"\n## {section}\n"] + [f"- {idea}\n" for idea in ideas]
    with _file_lock:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.writelines(lines)
