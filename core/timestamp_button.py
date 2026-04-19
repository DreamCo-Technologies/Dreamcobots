# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Time-Stamp Button — Centralised milestone tracker for the DreamCobots fleet.

Records task completions by builder bots, writes entries to ``logs.txt``
(or a configurable path), and exposes a simple dashboard summary.

Usage
-----
    from core.timestamp_button import TimestampButton

    ts = TimestampButton()
    ts.stamp(event="voice_pipeline_built", detail="3 profiles synthesised")
    print(ts.dashboard())
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Milestone record
# ---------------------------------------------------------------------------


@dataclass
class Milestone:
    """A single timestamped milestone entry."""

    milestone_id: str
    event: str
    detail: str
    iso_timestamp: str
    unix_timestamp: float
    bot: str = "system"

    def format_log_line(self) -> str:
        return (
            f"[{self.iso_timestamp}] [{self.bot}] {self.event}"
            + (f" — {self.detail}" if self.detail else "")
        )

    def to_dict(self) -> dict:
        return {
            "milestone_id": self.milestone_id,
            "event": self.event,
            "detail": self.detail,
            "iso_timestamp": self.iso_timestamp,
            "unix_timestamp": self.unix_timestamp,
            "bot": self.bot,
        }


# ---------------------------------------------------------------------------
# TimestampButton
# ---------------------------------------------------------------------------


class TimestampButton:
    """
    Centralised time-stamp tracker.

    Parameters
    ----------
    log_path : str | Path
        File path where milestones are persisted (default: ``logs.txt``).
    bot_name : str
        Name of the owning bot written into every milestone record.
    """

    def __init__(
        self,
        log_path: str | Path = "logs.txt",
        bot_name: str = "system",
    ) -> None:
        self._log_path = Path(log_path)
        self._bot_name = bot_name
        self._milestones: List[Milestone] = []
        self._counter: int = 0

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def stamp(
        self,
        event: str,
        detail: str = "",
        bot: Optional[str] = None,
    ) -> Milestone:
        """
        Record a milestone and append it to the log file.

        Parameters
        ----------
        event : str
            Short machine-readable event label (e.g. ``"pipeline_built"``).
        detail : str
            Human-readable description of what happened.
        bot : str | None
            Override the default bot name for this entry.

        Returns
        -------
        Milestone
            The recorded milestone instance.
        """
        self._counter += 1
        now = time.time()
        iso = datetime.fromtimestamp(now, tz=timezone.utc).isoformat()
        milestone = Milestone(
            milestone_id=f"ms-{self._counter:04d}",
            event=event,
            detail=detail,
            iso_timestamp=iso,
            unix_timestamp=now,
            bot=bot or self._bot_name,
        )
        self._milestones.append(milestone)
        self._write_log(milestone)
        return milestone

    def get_milestones(self) -> List[Milestone]:
        """Return all recorded milestones (oldest first)."""
        return list(self._milestones)

    def clear(self) -> None:
        """Clear the in-memory milestone list (does NOT truncate the log file)."""
        self._milestones.clear()
        self._counter = 0

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self) -> str:
        """
        Return a formatted text dashboard summarising all milestones.

        Example output::

            ╔══════════════════════════════════════════════╗
            ║        DreamCobots — Time-Stamp Dashboard    ║
            ╠══════════════════════════════════════════════╣
            ║  Total milestones : 3                        ║
            ╠══════════════════════════════════════════════╣
            ║  [2026-04-19T10:00:00+00:00] pipeline_built  ║
            ...
        """
        header = "╔══════════════════════════════════════════════╗"
        title = "║        DreamCobots — Time-Stamp Dashboard    ║"
        divider = "╠══════════════════════════════════════════════╣"
        footer = "╚══════════════════════════════════════════════╝"

        rows = [
            header,
            title,
            divider,
            f"║  Total milestones : {len(self._milestones):<25}║",
            divider,
        ]
        for ms in self._milestones:
            label = f"{ms.iso_timestamp}  {ms.event}"
            if ms.detail:
                label += f"  ({ms.detail})"
            rows.append(f"║  {label[:44]:<44}║")
        rows.append(footer)
        return "\n".join(rows)

    def dashboard_dict(self) -> dict:
        """Return the dashboard as a structured dict (suitable for JSON APIs)."""
        return {
            "total": len(self._milestones),
            "milestones": [ms.to_dict() for ms in self._milestones],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _write_log(self, milestone: Milestone) -> None:
        """Append a single milestone line to the log file."""
        try:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            with self._log_path.open("a", encoding="utf-8") as fh:
                fh.write(milestone.format_log_line() + "\n")
        except OSError:
            # Best-effort logging — never crash the bot over a log write
            pass
