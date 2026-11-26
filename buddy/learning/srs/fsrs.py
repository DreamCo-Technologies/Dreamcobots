"""Buddy adapter for the official FSRS-6 implementation.

Pinned dependency: fsrs==6.3.3. Fuzzing is disabled by default so a fixed
review-event stream and parameter set replay deterministically.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from fsrs import Card, Rating, Scheduler


FSRS_SCHEDULER_VERSION = "FSRS-6/py-fsrs-6.3.3"
_RATING_NAMES = {"again": Rating.Again, "hard": Rating.Hard, "good": Rating.Good, "easy": Rating.Easy}


@dataclass(frozen=True)
class FSRSConfig:
    desired_retention: float = 0.9
    maximum_interval_days: int = 36500
    learning_steps_seconds: tuple[int, ...] = (60, 600)
    relearning_steps_seconds: tuple[int, ...] = (600,)
    enable_fuzzing: bool = False
    parameters: tuple[float, ...] | None = None

    @classmethod
    def from_scheduler_dict(cls, value: dict[str, Any]) -> "FSRSConfig":
        return cls(
            desired_retention=float(value["desired_retention"]),
            maximum_interval_days=int(value["maximum_interval"]),
            learning_steps_seconds=tuple(int(x) for x in value["learning_steps"]),
            relearning_steps_seconds=tuple(int(x) for x in value["relearning_steps"]),
            enable_fuzzing=bool(value["enable_fuzzing"]),
            parameters=tuple(float(x) for x in value["parameters"]),
        )

    def __post_init__(self) -> None:
        if not 0.7 < self.desired_retention < 0.97:
            raise ValueError("desired_retention must be between 0.70 and 0.97")
        if self.maximum_interval_days < 1:
            raise ValueError("maximum_interval_days must be positive")
        for name, steps in (
            ("learning_steps_seconds", self.learning_steps_seconds),
            ("relearning_steps_seconds", self.relearning_steps_seconds),
        ):
            if any(not isinstance(step, int) or step <= 0 for step in steps):
                raise ValueError(f"{name} must contain positive whole seconds")
        if tuple(sorted(set(self.learning_steps_seconds))) != self.learning_steps_seconds:
            raise ValueError("learning_steps_seconds must be strictly increasing")
        if tuple(sorted(set(self.relearning_steps_seconds))) != self.relearning_steps_seconds:
            raise ValueError("relearning_steps_seconds must be strictly increasing")


@dataclass(frozen=True)
class FSRSReviewResult:
    scheduler: str
    scheduler_version: str
    card_id: int
    rating: int
    reviewed_at_utc: str
    due_at_utc: str
    interval_seconds: float
    desired_retention: float
    parameter_set_id: str
    predicted_retrievability: float
    actual_recall: bool
    mastery_awarded: bool
    prior_state: dict[str, Any]
    resulting_state: dict[str, Any]
    review_log: dict[str, Any]
    scheduler_config: dict[str, Any]


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("review timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def stable_fsrs_card_id(learner_id: str, deck_id: str, item_id: str) -> int:
    """Map the stable logical key to FSRS' integer card ID."""
    if not all(isinstance(value, str) and value.strip() for value in (learner_id, deck_id, item_id)):
        raise ValueError("learner_id, deck_id and item_id are required")
    digest = hashlib.sha256(f"{learner_id}\0{deck_id}\0{item_id}".encode()).hexdigest()
    return int(digest[:15], 16)


class FSRSAdapter:
    """Single shared FSRS-6 adapter for every Buddy division."""

    name = "fsrs"

    def __init__(self, config: FSRSConfig | None = None) -> None:
        self.config = config or FSRSConfig()
        scheduler_kwargs = {
            "desired_retention": self.config.desired_retention,
            maximum_interval=self.config.maximum_interval_days,
            learning_steps=[timedelta(seconds=value) for value in self.config.learning_steps_seconds],
            relearning_steps=[timedelta(seconds=value) for value in self.config.relearning_steps_seconds],
            "enable_fuzzing": self.config.enable_fuzzing,
        }
        if self.config.parameters is not None:
            scheduler_kwargs["parameters"] = self.config.parameters
        self.scheduler = Scheduler(**scheduler_kwargs)
        canonical = json.dumps(self.scheduler.to_dict(), sort_keys=True, separators=(",", ":"))
        self.parameter_set_id = hashlib.sha256(canonical.encode()).hexdigest()[:20]

    def new_card(self, learner_id: str, deck_id: str, item_id: str, created_at: datetime) -> Card:
        created_at = _utc(created_at)
        return Card(
            card_id=stable_fsrs_card_id(learner_id, deck_id, item_id),
            due=created_at,
        )

    def review(
        self,
        *,
        learner_id: str,
        deck_id: str,
        item_id: str,
        rating: int | str,
        reviewed_at: datetime,
        state_json: str | None = None,
        review_duration_ms: int | None = None,
    ) -> FSRSReviewResult:
        when = _utc(reviewed_at)
        if review_duration_ms is not None and review_duration_ms < 0:
            raise ValueError("review_duration_ms cannot be negative")
        if isinstance(rating, bool):
            raise ValueError("rating must be 1..4")
        if isinstance(rating, str):
            try:
                parsed_rating = _RATING_NAMES[rating.strip().lower()]
            except KeyError as exc:
                raise ValueError("rating must be Again, Hard, Good or Easy") from exc
        else:
            try:
                parsed_rating = Rating(int(rating))
            except (TypeError, ValueError) as exc:
                raise ValueError("rating must be 1..4") from exc

        expected_id = stable_fsrs_card_id(learner_id, deck_id, item_id)
        card = Card.from_json(state_json) if state_json else self.new_card(learner_id, deck_id, item_id, when)
        if card.card_id != expected_id:
            raise ValueError("FSRS state does not belong to this learner/deck/item")
        prior_state = card.to_dict()
        predicted = self.scheduler.get_card_retrievability(card, current_datetime=when)
        updated, log = self.scheduler.review_card(
            card=card,
            rating=parsed_rating,
            review_datetime=when,
            review_duration=review_duration_ms,
        )
        due_at = updated.due.astimezone(timezone.utc)
        return FSRSReviewResult(
            scheduler=self.name,
            scheduler_version=FSRS_SCHEDULER_VERSION,
            card_id=updated.card_id,
            rating=int(parsed_rating),
            reviewed_at_utc=when.isoformat(),
            due_at_utc=due_at.isoformat(),
            interval_seconds=(due_at - when).total_seconds(),
            desired_retention=self.config.desired_retention,
            parameter_set_id=self.parameter_set_id,
            predicted_retrievability=float(predicted),
            actual_recall=parsed_rating != Rating.Again,
            mastery_awarded=False,
            prior_state=prior_state,
            resulting_state=updated.to_dict(),
            review_log=log.to_dict(),
            scheduler_config=self.scheduler.to_dict(),
        )
