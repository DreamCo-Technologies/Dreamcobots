"""Opt-in, evidence-backed Buddy learning and capability acquisition proposals.

This module does not observe users, access networks, execute adapters or train weights.
An authenticated host must supply tenant identity and authorized, redacted records.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any, Mapping

DOMAINS = frozenset({"personal", "business", "technical", "creative", "education", "research", "operations"})
SPLITS = frozenset({"train", "validation", "holdout"})
SENSITIVE = frozenset({"password", "token", "secret", "api_key", "private_key", "payment_card",
                       "screen_capture", "hidden_reasoning", "chain_of_thought", "holdout_answer"})
RISKY = frozenset({"external_side_effect", "financial", "physical", "destructive", "production"})


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")
    return value.strip()


def _fingerprint(data: Mapping[str, Any]) -> str:
    return sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class LearningEvent:
    tenant_id: str
    task_id: str
    domain: str
    goal: str
    workflow: str
    outcome: str
    source: str
    source_revision: str
    split: str = "train"
    rating: int | None = None
    duration_seconds: float | None = None
    consent: bool = False
    redacted: bool = False
    verified: bool = False
    notes: str = ""

    def validate(self) -> None:
        for key in ("tenant_id", "task_id", "goal", "workflow", "outcome", "source", "source_revision"):
            _text(getattr(self, key), key)
        if self.domain not in DOMAINS or self.split not in SPLITS:
            raise ValueError("unsupported domain or split")
        if self.rating is not None and (type(self.rating) is not int or not 1 <= self.rating <= 5):
            raise ValueError("rating must be 1 through 5")
        if self.duration_seconds is not None and (
            isinstance(self.duration_seconds, bool) or not isinstance(self.duration_seconds, (int, float))
            or not 0 <= self.duration_seconds < float("inf")
        ):
            raise ValueError("invalid duration")
        if not self.consent or not self.redacted:
            raise PermissionError("explicit capture consent and redaction required")
        if not self.verified:
            raise ValueError("unverified outcomes must not enter the evidence ledger")


@dataclass
class LearningLedger:
    """In-memory, per-tenant opt-in evidence; host owns durable private persistence."""

    _events: dict[str, dict[str, LearningEvent]] = field(default_factory=dict)

    def record(self, event: LearningEvent) -> str:
        event.validate()
        identifier = _fingerprint({"tenant": event.tenant_id, "task": event.task_id,
                                   "source_revision": event.source_revision, "split": event.split})
        partition = self._events.setdefault(event.tenant_id, {})
        if identifier in partition and partition[identifier] != event:
            raise ValueError("conflicting event revision; submit a new source revision")
        partition[identifier] = event
        return identifier

    def forget(self, tenant_id: str) -> int:
        """Delete this tenant's evidence; caller must also delete external backups."""
        return len(self._events.pop(_text(tenant_id, "tenant_id"), {}))

    def retrieve(self, tenant_id: str, *, domain: str | None = None,
                 workflow: str | None = None, split: str = "train") -> list[LearningEvent]:
        _text(tenant_id, "tenant_id")
        if split not in SPLITS:
            raise ValueError("invalid split")
        return [e for e in self._events.get(tenant_id, {}).values()
                if e.split == split and (domain is None or e.domain == domain)
                and (workflow is None or e.workflow == workflow)]

    def recommendations(self, tenant_id: str, domain: str) -> dict[str, Any]:
        """Suggest, never autonomously execute. Holdouts cannot influence recommendations."""
        if domain not in DOMAINS:
            raise ValueError("unsupported domain")
        rows = self.retrieve(tenant_id, domain=domain, split="train")
        by_workflow: dict[str, list[LearningEvent]] = {}
        for row in rows:
            by_workflow.setdefault(row.workflow, []).append(row)
        candidates = []
        for workflow, events in sorted(by_workflow.items()):
            successes = sum(e.outcome == "success" for e in events)
            failures = sum(e.outcome == "failure" for e in events)
            ratings = [e.rating for e in events if e.rating is not None]
            candidates.append({"workflow": workflow, "observations": len(events),
                               "successes": successes, "failures": failures,
                               "mean_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
                               "confidence": "limited" if len(events) < 5 else "observational",
                               "automation": "human_review_required"})
        candidates.sort(key=lambda c: (-c["successes"], c["failures"], c["workflow"]))
        return {"domain": domain, "observations": len(rows), "candidates": candidates,
                "next_step": "Collect more consented, verified outcomes before automating."}


@dataclass(frozen=True)
class Capability:
    capability_id: str
    adapter_id: str
    revision: str
    actions: tuple[str, ...]
    evidence_id: str
    tested: bool
    approved: bool
    risk: str = "read_only"

    def validate(self) -> None:
        for key in ("capability_id", "adapter_id", "revision", "evidence_id"):
            _text(getattr(self, key), key)
        if not self.actions or any(not isinstance(a, str) or not a.strip() for a in self.actions):
            raise ValueError("capability must advertise concrete actions")
        if len(set(self.actions)) != len(self.actions):
            raise ValueError("duplicate actions")
        if self.risk not in {"read_only", "sandbox", *RISKY}:
            raise ValueError("unknown risk classification")


@dataclass
class CapabilityRegistry:
    """Verified capabilities only; discovery does not imply access or execution."""
    _capabilities: dict[str, Capability] = field(default_factory=dict)

    def register(self, capability: Capability) -> None:
        capability.validate()
        if not capability.tested or not capability.approved:
            raise PermissionError("test evidence and human approval required")
        existing = self._capabilities.get(capability.capability_id)
        if existing and existing != capability:
            raise ValueError("existing capability requires explicit versioned replacement")
        self._capabilities[capability.capability_id] = capability

    def propose(self, goal: str, required_actions: list[str], *, risk: str = "sandbox") -> dict[str, Any]:
        _text(goal, "goal")
        if not required_actions or any(not isinstance(a, str) or not a.strip() for a in required_actions):
            raise ValueError("required_actions must be nonempty strings")
        if risk not in {"read_only", "sandbox", *RISKY}:
            raise ValueError("unknown risk")
        matched = {action: cap.capability_id for action in required_actions
                   for cap in sorted(self._capabilities.values(), key=lambda c: c.capability_id)
                   if action in cap.actions and action not in []}
        missing = list(dict.fromkeys(action for action in required_actions if action not in matched))
        return {"goal": goal, "matched": matched, "missing": missing, "risk": risk,
                "status": "capability_gap" if missing else "ready_for_host_permission_review",
                "steps": (["Retrieve authorized documentation", "Propose bounded adapter",
                           "Sandbox test and capture evidence", "Obtain human approval"]
                          if missing else ["Confirm host pairing, identity, exact-action grants and policy"]),
                "executed": False, "weights_trained": False}


def benchmark_gate(baseline: list[float], candidate: list[float], holdout: list[float],
                   *, min_gain: float = .05) -> dict[str, Any]:
    """Conservative evaluation helper; never writes to the model registry."""
    for group in (baseline, candidate, holdout):
        if len(group) < 3 or any(isinstance(x, bool) or not isinstance(x, (int, float))
                                 or not 0 <= x <= 1 for x in group):
            raise ValueError("three or more normalized scores required per group")
    means = [sum(group) / len(group) for group in (baseline, candidate, holdout)]
    promote = means[1] - means[0] >= min_gain and means[2] >= .75
    return {"promote": promote, "baseline": round(means[0], 4),
            "candidate": round(means[1], 4), "holdout": round(means[2], 4),
            "status": "requires_independent_review" if promote else "insufficient_evidence"}
