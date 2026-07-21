"""
DreamCo Platform — Capability Extractor
==========================================

``CapabilityExtractor`` performs the refactor operation described in TIER 2
of the Phase 2 plan:

    Before: lead_gen_bot / lead_generator_bot / lead_scraper_bot
    After:  capability.lead.scrape / capability.lead.enrich / capability.lead.score

This module:
1. Accepts a mapping of bot_id → code/description blobs
2. Detects shared logical groups (by keyword/pattern similarity)
3. Proposes ``CapabilityEntry`` objects for extraction
4. Returns a structured ``ExtractionPlan``

In a full implementation, step 2 is powered by the ``EmbeddingStore``
(nearest-neighbour clustering).  Here we use a keyword-matching heuristic
that is deterministic, testable, and dependency-free.

Usage::

    extractor = CapabilityExtractor()
    plan = extractor.analyse([
        BotDescriptor("lead_gen_bot", description="scrapes and enriches leads"),
        BotDescriptor("lead_scraper_bot", description="scrapes leads from web"),
        BotDescriptor("lead_enricher_bot", description="enriches lead data"),
    ])
    plan.proposed_capabilities   # ["capability.lead.scrape", ...]
    plan.merge_suggestions       # [(bot_a, bot_b), ...]
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Input type
# ---------------------------------------------------------------------------

@dataclass
class BotDescriptor:
    bot_id: str
    description: str
    tags: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------

@dataclass
class ProposedCapability:
    capability_id: str
    source_bots: list[str]
    rationale: str
    confidence: float  # 0.0 – 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "source_bots": self.source_bots,
            "rationale": self.rationale,
            "confidence": self.confidence,
        }


@dataclass
class ExtractionPlan:
    proposed_capabilities: list[ProposedCapability] = field(default_factory=list)
    merge_suggestions: list[tuple[str, str]] = field(default_factory=list)
    redundant_bots: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposed_capabilities": [c.to_dict() for c in self.proposed_capabilities],
            "merge_suggestions": [list(pair) for pair in self.merge_suggestions],
            "redundant_bots": self.redundant_bots,
            "summary": self.summary,
        }


# ---------------------------------------------------------------------------
# Keyword groups used for capability clustering
# ---------------------------------------------------------------------------

_CAPABILITY_PATTERNS: list[tuple[str, list[str]]] = [
    ("capability.lead.scrape",    ["scrape", "scrapes", "crawl", "extract", "harvest"]),
    ("capability.lead.enrich",    ["enrich", "enriches", "augment", "append"]),
    ("capability.lead.score",     ["score", "rank", "qualify", "grade"]),
    ("capability.finance.invoice", ["invoice", "billing", "bill"]),
    ("capability.finance.revenue", ["revenue", "income", "profit"]),
    ("capability.deploy.release",  ["deploy", "release", "ship", "publish"]),
    ("capability.learn.train",     ["train", "learn", "fine-tune", "finetune"]),
    ("capability.marketplace.list", ["marketplace", "listing", "catalog"]),
    ("capability.auth.verify",     ["auth", "verify", "authenticate", "login"]),
    ("capability.monitor.health",  ["health", "monitor", "heartbeat", "uptime"]),
]


def _tokenize(text: str) -> set[str]:
    return set(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())


def _match_score(tokens: set[str], keywords: list[str]) -> float:
    matches = sum(1 for kw in keywords if kw in tokens)
    return matches / len(keywords) if keywords else 0.0


# ---------------------------------------------------------------------------
# Extractor
# ---------------------------------------------------------------------------

class CapabilityExtractor:
    """Analyse a set of bot descriptors and propose capability extractions."""

    def __init__(self, confidence_threshold: float = 0.25) -> None:
        self._threshold = confidence_threshold

    def analyse(self, bots: list[BotDescriptor]) -> ExtractionPlan:
        """Return an ``ExtractionPlan`` for the given *bots*."""
        plan = ExtractionPlan()

        # Map capability_id → bots that match it
        capability_to_bots: dict[str, list[str]] = defaultdict(list)

        for bot in bots:
            tokens = _tokenize(bot.description + " " + " ".join(bot.tags + bot.capabilities))
            for cap_id, keywords in _CAPABILITY_PATTERNS:
                score = _match_score(tokens, keywords)
                if score >= self._threshold:
                    capability_to_bots[cap_id].append(bot.bot_id)

        # Build proposed capabilities
        for cap_id, bot_ids in capability_to_bots.items():
            keywords = next(kws for cid, kws in _CAPABILITY_PATTERNS if cid == cap_id)
            matching_kws = [kw for kw in keywords if any(
                kw in _tokenize(b.description) for b in bots if b.bot_id in bot_ids
            )]
            plan.proposed_capabilities.append(ProposedCapability(
                capability_id=cap_id,
                source_bots=bot_ids,
                rationale=f"Shared keywords: {', '.join(matching_kws)}",
                confidence=min(1.0, len(bot_ids) * 0.3 + 0.4),
            ))

        # Merge suggestions: bots sharing ≥2 capabilities
        bot_caps: dict[str, set[str]] = defaultdict(set)
        for cap_id, bot_ids in capability_to_bots.items():
            for bid in bot_ids:
                bot_caps[bid].add(cap_id)

        bot_ids_list = list(bot_caps.keys())
        for i in range(len(bot_ids_list)):
            for j in range(i + 1, len(bot_ids_list)):
                a, b = bot_ids_list[i], bot_ids_list[j]
                shared = bot_caps[a] & bot_caps[b]
                if len(shared) >= 2:
                    plan.merge_suggestions.append((a, b))

        # Redundant bots: identical capability sets
        cap_set_to_bots: dict[str, list[str]] = defaultdict(list)
        for bid, caps in bot_caps.items():
            key = ",".join(sorted(caps))
            cap_set_to_bots[key].append(bid)
        for key, group in cap_set_to_bots.items():
            if len(group) > 1:
                plan.redundant_bots.extend(group[1:])  # keep first, flag rest

        n_caps = len(plan.proposed_capabilities)
        n_merge = len(plan.merge_suggestions)
        n_redund = len(plan.redundant_bots)
        plan.summary = (
            f"Found {n_caps} extractable capabilities, "
            f"{n_merge} merge suggestions, "
            f"{n_redund} redundant bots."
        )

        return plan
