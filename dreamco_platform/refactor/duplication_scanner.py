"""
DreamCo Platform — Duplication Scanner
=========================================

``DuplicationScanner`` audits the bot registry for overlapping bots that
should be consolidated into capability primitives.

Overlap categories
------------------
* **Name overlap** — bot IDs share common tokens (e.g. ``lead_gen_bot``,
  ``lead_generator_bot``)
* **Capability overlap** — two bots expose identical or near-identical
  capability lists
* **Event overlap** — two bots both emit and consume the same event types

Output is a ``DuplicationReport`` with actionable merge and extract suggestions.

Usage::

    scanner = DuplicationScanner()
    report = scanner.scan(registry)
    report.name_overlaps       # [("lead_gen_bot", "lead_generator_bot")]
    report.capability_overlaps # [...]
    report.summary
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# BotSnapshot (minimal input type, decoupled from registry)
# ---------------------------------------------------------------------------

@dataclass
class BotSnapshot:
    bot_id: str
    capabilities: list[str] = field(default_factory=list)
    events_emitted: list[str] = field(default_factory=list)
    events_consumed: list[str] = field(default_factory=list)
    description: str = ""


# ---------------------------------------------------------------------------
# Report types
# ---------------------------------------------------------------------------

@dataclass
class OverlapEntry:
    bot_a: str
    bot_b: str
    overlap_type: str  # "name" | "capability" | "event"
    shared_items: list[str]
    suggestion: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "bot_a": self.bot_a,
            "bot_b": self.bot_b,
            "overlap_type": self.overlap_type,
            "shared_items": self.shared_items,
            "suggestion": self.suggestion,
        }


@dataclass
class DuplicationReport:
    name_overlaps: list[OverlapEntry] = field(default_factory=list)
    capability_overlaps: list[OverlapEntry] = field(default_factory=list)
    event_overlaps: list[OverlapEntry] = field(default_factory=list)
    summary: str = ""

    @property
    def all_overlaps(self) -> list[OverlapEntry]:
        return self.name_overlaps + self.capability_overlaps + self.event_overlaps

    def to_dict(self) -> dict[str, Any]:
        return {
            "name_overlaps": [e.to_dict() for e in self.name_overlaps],
            "capability_overlaps": [e.to_dict() for e in self.capability_overlaps],
            "event_overlaps": [e.to_dict() for e in self.event_overlaps],
            "summary": self.summary,
        }


# ---------------------------------------------------------------------------
# Helper: extract name tokens
# ---------------------------------------------------------------------------

def _name_tokens(bot_id: str) -> set[str]:
    import re
    parts = re.split(r"[_\-\s]+", bot_id.lower())
    # Remove common suffixes that don't carry semantic meaning
    noise = {"bot", "agent", "service", "manager", "handler"}
    return {p for p in parts if p and p not in noise}


# ---------------------------------------------------------------------------
# DuplicationScanner
# ---------------------------------------------------------------------------

class DuplicationScanner:
    """Scans a list of ``BotSnapshot`` objects for duplication."""

    def __init__(
        self,
        name_token_threshold: int = 2,
        capability_overlap_threshold: float = 0.5,
        event_overlap_threshold: float = 0.5,
    ) -> None:
        self._name_thresh = name_token_threshold
        self._cap_thresh = capability_overlap_threshold
        self._evt_thresh = event_overlap_threshold

    def scan(self, bots: list[BotSnapshot]) -> DuplicationReport:
        report = DuplicationReport()

        for i in range(len(bots)):
            for j in range(i + 1, len(bots)):
                a, b = bots[i], bots[j]

                # Name overlap
                shared_tokens = _name_tokens(a.bot_id) & _name_tokens(b.bot_id)
                if len(shared_tokens) >= self._name_thresh:
                    report.name_overlaps.append(OverlapEntry(
                        bot_a=a.bot_id,
                        bot_b=b.bot_id,
                        overlap_type="name",
                        shared_items=sorted(shared_tokens),
                        suggestion=f"Consider merging '{a.bot_id}' and '{b.bot_id}' or extracting shared capabilities.",
                    ))

                # Capability overlap
                shared_caps = set(a.capabilities) & set(b.capabilities)
                if shared_caps:
                    jaccard = len(shared_caps) / len(set(a.capabilities) | set(b.capabilities)) if (set(a.capabilities) | set(b.capabilities)) else 0
                    if jaccard >= self._cap_thresh:
                        report.capability_overlaps.append(OverlapEntry(
                            bot_a=a.bot_id,
                            bot_b=b.bot_id,
                            overlap_type="capability",
                            shared_items=sorted(shared_caps),
                            suggestion=f"Extract shared capabilities {sorted(shared_caps)} into capability primitives.",
                        ))

                # Event overlap (both emit AND consume same events)
                shared_emits = set(a.events_emitted) & set(b.events_emitted)
                shared_consumes = set(a.events_consumed) & set(b.events_consumed)
                combined_shared = shared_emits | shared_consumes
                total_events = len(set(a.events_emitted + a.events_consumed) | set(b.events_emitted + b.events_consumed))
                if combined_shared and total_events > 0:
                    jaccard = len(combined_shared) / total_events
                    if jaccard >= self._evt_thresh:
                        report.event_overlaps.append(OverlapEntry(
                            bot_a=a.bot_id,
                            bot_b=b.bot_id,
                            overlap_type="event",
                            shared_items=sorted(combined_shared),
                            suggestion=f"High event overlap — route through shared orchestrator.",
                        ))

        n = len(report.name_overlaps) + len(report.capability_overlaps) + len(report.event_overlaps)
        report.summary = (
            f"Scanned {len(bots)} bots; found {n} overlaps "
            f"({len(report.name_overlaps)} name, "
            f"{len(report.capability_overlaps)} capability, "
            f"{len(report.event_overlaps)} event)."
        )
        return report
