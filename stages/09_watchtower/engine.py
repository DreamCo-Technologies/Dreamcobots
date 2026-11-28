"""Deterministic, provider-neutral monitoring rules and alert evaluation.

Network collection is deliberately separated into adapters.py. This module is
pure and deterministic so rules can be tested without external services.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Iterable


_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,127}$")
_ALLOWED_ADAPTERS = {"json_feed", "manual", "webhook"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_text(value: Any, limit: int = 4000) -> str:
    if value is None:
        return ""
    return str(value).strip()[:limit]


@dataclass(frozen=True)
class WatchRule:
    rule_id: str
    name: str
    adapter: str
    target: str
    enabled: bool = True
    interval_seconds: int = 900
    min_score: int = 1
    include_any: tuple[str, ...] = ()
    include_all: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    min_price: float | None = None
    max_price: float | None = None
    currency: str | None = None
    cooldown_seconds: int = 3600
    max_items: int = 100

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "WatchRule":
        if not isinstance(raw, dict):
            raise ValueError("Each watch rule must be a JSON object.")
        rule = cls(
            rule_id=_clean_text(raw.get("rule_id"), 128),
            name=_clean_text(raw.get("name"), 160),
            adapter=_clean_text(raw.get("adapter"), 32),
            target=_clean_text(raw.get("target"), 2048),
            enabled=raw.get("enabled", True),
            interval_seconds=raw.get("interval_seconds", 900),
            min_score=raw.get("min_score", 1),
            include_any=tuple(_clean_text(x, 120).lower() for x in raw.get("include_any", [])),
            include_all=tuple(_clean_text(x, 120).lower() for x in raw.get("include_all", [])),
            exclude=tuple(_clean_text(x, 120).lower() for x in raw.get("exclude", [])),
            min_price=raw.get("min_price"),
            max_price=raw.get("max_price"),
            currency=_clean_text(raw.get("currency"), 8).upper() or None,
            cooldown_seconds=raw.get("cooldown_seconds", 3600),
            max_items=raw.get("max_items", 100),
        )
        rule.validate()
        return rule

    def validate(self) -> None:
        if not _ID.fullmatch(self.rule_id):
            raise ValueError("rule_id must be 1-128 safe identifier characters.")
        if not self.name or not self.target:
            raise ValueError(f"Rule {self.rule_id} requires a name and target.")
        if self.adapter not in _ALLOWED_ADAPTERS:
            raise ValueError(f"Unsupported adapter for {self.rule_id}: {self.adapter}")
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be boolean.")
        for name, value, low, high in (
            ("interval_seconds", self.interval_seconds, 60, 604800),
            ("min_score", self.min_score, 0, 100),
            ("cooldown_seconds", self.cooldown_seconds, 0, 2592000),
            ("max_items", self.max_items, 1, 1000),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
                raise ValueError(f"{name} must be an integer from {low} to {high}.")
        for name, value in (("min_price", self.min_price), ("max_price", self.max_price)):
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0):
                raise ValueError(f"{name} must be a non-negative number.")
        if self.min_price is not None and self.max_price is not None and self.min_price > self.max_price:
            raise ValueError("min_price cannot exceed max_price.")
        for values in (self.include_any, self.include_all, self.exclude):
            if not all(isinstance(x, str) and x for x in values):
                raise ValueError("Keyword filters must contain non-empty strings.")


@dataclass(frozen=True)
class Observation:
    item_id: str
    title: str
    source: str
    url: str = ""
    summary: str = ""
    price: float | None = None
    currency: str | None = None
    observed_at: str = field(default_factory=_utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Observation":
        if not isinstance(raw, dict):
            raise ValueError("Each observation must be a JSON object.")
        item = cls(
            item_id=_clean_text(raw.get("item_id"), 256),
            title=_clean_text(raw.get("title"), 500),
            source=_clean_text(raw.get("source"), 120),
            url=_clean_text(raw.get("url"), 2048),
            summary=_clean_text(raw.get("summary"), 4000),
            price=raw.get("price"),
            currency=_clean_text(raw.get("currency"), 8).upper() or None,
            observed_at=_clean_text(raw.get("observed_at"), 80) or _utc_now(),
            metadata=raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {},
        )
        item.validate()
        return item

    def validate(self) -> None:
        if not self.item_id or not self.title or not self.source:
            raise ValueError("Observation requires item_id, title, and source.")
        if self.price is not None and (
            isinstance(self.price, bool) or not isinstance(self.price, (int, float)) or self.price < 0
        ):
            raise ValueError("Observation price must be a non-negative number.")
        if self.url and not self.url.startswith(("https://", "http://")):
            raise ValueError("Observation URL must use HTTP or HTTPS.")

    def fingerprint(self) -> str:
        payload = {
            "item_id": self.item_id,
            "title": self.title,
            "url": self.url,
            "price": self.price,
            "currency": self.currency,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()


@dataclass(frozen=True)
class Alert:
    rule_id: str
    item_id: str
    score: int
    reason: str
    fingerprint: str
    created_at: str
    observation: dict[str, Any]


def score_observation(rule: WatchRule, item: Observation) -> tuple[int, str]:
    haystack = f"{item.title} {item.summary}".lower()
    if any(term in haystack for term in rule.exclude):
        return 0, "excluded by keyword"
    if rule.include_all and not all(term in haystack for term in rule.include_all):
        return 0, "missing required keyword"
    if rule.include_any and not any(term in haystack for term in rule.include_any):
        return 0, "no matching keyword"
    if rule.min_price is not None and (item.price is None or item.price < rule.min_price):
        return 0, "below minimum price or price unavailable"
    if rule.max_price is not None and (item.price is None or item.price > rule.max_price):
        return 0, "above maximum price or price unavailable"
    if rule.currency and item.currency and item.currency != rule.currency:
        return 0, "currency mismatch"
    matched = sum(1 for term in rule.include_any + rule.include_all if term in haystack)
    score = min(100, 50 + matched * 10)
    return score, "matched rule filters"


def evaluate(
    rules: Iterable[WatchRule],
    observations_by_rule: dict[str, Iterable[Observation]],
    previous_state: dict[str, Any] | None = None,
    now: str | None = None,
) -> tuple[list[Alert], dict[str, Any]]:
    """Evaluate observations, emitting only new fingerprints above each rule floor."""
    state = dict(previous_state or {})
    seen = state.setdefault("seen", {})
    if not isinstance(seen, dict):
        raise ValueError("State field 'seen' must be an object.")
    alerts: list[Alert] = []
    timestamp = now or _utc_now()
    for rule in rules:
        rule.validate()
        if not rule.enabled:
            continue
        items = list(observations_by_rule.get(rule.rule_id, ()))[: rule.max_items]
        for item in items:
            item.validate()
            score, reason = score_observation(rule, item)
            if score < rule.min_score:
                continue
            fingerprint = item.fingerprint()
            key = f"{rule.rule_id}:{item.item_id}"
            prior = seen.get(key)
            if isinstance(prior, dict) and prior.get("fingerprint") == fingerprint:
                continue
            alerts.append(Alert(
                rule_id=rule.rule_id,
                item_id=item.item_id,
                score=score,
                reason=reason,
                fingerprint=fingerprint,
                created_at=timestamp,
                observation=asdict(item),
            ))
            seen[key] = {"fingerprint": fingerprint, "last_alert_at": timestamp}
    state["schema"] = "dreamco.watchtower.state.v1"
    state["updated_at"] = timestamp
    return alerts, state
