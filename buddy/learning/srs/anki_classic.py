"""Configurable Anki Classic-style compatibility scheduler.

This preserves legacy ease/interval state and learning/relearning steps. It is
not advertised as byte-for-byte parity with a specific Anki scheduler release.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Any


_RATINGS = {"again": 1, "hard": 2, "good": 3, "easy": 4}


@dataclass(frozen=True)
class AnkiClassicConfig:
    learning_steps_seconds: tuple[int, ...] = (60, 600)
    relearning_steps_seconds: tuple[int, ...] = (600,)
    graduating_interval_days: int = 1
    easy_interval_days: int = 4
    starting_ease: float = 2.5
    minimum_ease: float = 1.3
    lapse_ease_penalty: float = 0.2
    hard_interval_multiplier: float = 1.2
    easy_bonus: float = 1.3
    interval_modifier: float = 1.0
    lapse_new_interval: float = 0.0
    maximum_interval_days: int = 36500

    def __post_init__(self) -> None:
        for name, steps in (("learning_steps_seconds", self.learning_steps_seconds),
                            ("relearning_steps_seconds", self.relearning_steps_seconds)):
            if any(not isinstance(step, int) or step <= 0 for step in steps):
                raise ValueError(f"{name} must contain positive whole seconds")
        if self.graduating_interval_days < 1 or self.easy_interval_days < 1 or self.maximum_interval_days < 1:
            raise ValueError("interval day values must be positive")
        if self.minimum_ease < 1.3 or self.starting_ease < self.minimum_ease:
            raise ValueError("ease values must respect the minimum ease")
        if self.interval_modifier <= 0 or self.hard_interval_multiplier <= 0 or self.easy_bonus <= 0:
            raise ValueError("interval multipliers must be positive")
        if not 0 <= self.lapse_new_interval <= 1:
            raise ValueError("lapse_new_interval must be between 0 and 1")


@dataclass(frozen=True)
class AnkiClassicCard:
    card_id: str
    state: str = "new"
    step_index: int = 0
    interval_days: int = 0
    ease_factor: float = 2.5
    due_at_utc: str = ""
    repetitions: int = 0
    lapses: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "card_id": self.card_id, "state": self.state, "step_index": self.step_index,
            "interval_days": self.interval_days, "ease_factor": self.ease_factor,
            "due_at_utc": self.due_at_utc, "repetitions": self.repetitions, "lapses": self.lapses,
        }


@dataclass(frozen=True)
class AnkiClassicReviewResult:
    scheduler: str
    scheduler_version: str
    rating: int
    reviewed_at_utc: str
    due_at_utc: str
    interval_seconds: float
    actual_recall: bool
    mastery_awarded: bool
    prior_state: dict[str, Any]
    resulting_state: dict[str, Any]


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("review timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def _rating(value: int | str) -> int:
    if isinstance(value, str):
        try:
            return _RATINGS[value.strip().lower()]
        except KeyError as exc:
            raise ValueError("rating must be Again, Hard, Good or Easy") from exc
    if isinstance(value, bool) or value not in (1, 2, 3, 4):
        raise ValueError("rating must be 1..4")
    return int(value)


class AnkiClassicScheduler:
    name = "anki_classic"
    version = "dreamco-anki-classic-profile.v1"

    def __init__(self, config: AnkiClassicConfig | None = None) -> None:
        self.config = config or AnkiClassicConfig()

    def review(self, card: AnkiClassicCard, rating: int | str, reviewed_at: datetime) -> AnkiClassicReviewResult:
        when = _utc(reviewed_at)
        grade = _rating(rating)
        prior = card.to_dict()
        cfg = self.config
        state = card.state
        step = card.step_index
        interval = card.interval_days
        ease = cfg.starting_ease if state == "new" else card.ease_factor
        lapses = card.lapses
        reps = card.repetitions + 1

        if state in ("new", "learning", "relearning"):
            steps = cfg.relearning_steps_seconds if state == "relearning" else cfg.learning_steps_seconds
            if not steps:
                steps = ()
            if grade == 1:
                if steps:
                    state, step = ("relearning" if state == "relearning" else "learning"), 0
                    due = when + timedelta(seconds=steps[0])
                else:
                    state, step = "review", 0
                    interval = max(1, cfg.graduating_interval_days)
                    due = when + timedelta(days=interval)
            elif grade == 2:
                if steps:
                    step = min(step, len(steps) - 1)
                    seconds = ((steps[0] + steps[1]) / 2) if step == 0 and len(steps) > 1 else steps[step] * (1.5 if step == 0 else 1)
                    due = when + timedelta(seconds=seconds)
                    state = "relearning" if state == "relearning" else "learning"
                else:
                    state, step = "review", 0
                    interval = max(1, cfg.graduating_interval_days)
                    due = when + timedelta(days=interval)
            elif grade == 3 and steps and step + 1 < len(steps):
                step += 1
                state = "relearning" if state == "relearning" else "learning"
                due = when + timedelta(seconds=steps[step])
            else:
                state, step = "review", 0
                if card.state == "relearning":
                    interval = max(1, round(max(1, interval) * cfg.lapse_new_interval))
                else:
                    interval = cfg.easy_interval_days if grade == 4 else cfg.graduating_interval_days
                interval = min(cfg.maximum_interval_days, max(1, interval))
                due = when + timedelta(days=interval)
        elif state == "review":
            if grade == 1:
                lapses += 1
                ease = max(cfg.minimum_ease, ease - cfg.lapse_ease_penalty)
                interval = min(cfg.maximum_interval_days, max(1, round(interval * cfg.lapse_new_interval)))
                if cfg.relearning_steps_seconds:
                    state, step = "relearning", 0
                    due = when + timedelta(seconds=cfg.relearning_steps_seconds[0])
                else:
                    due = when + timedelta(days=interval)
            else:
                multiplier = cfg.hard_interval_multiplier if grade == 2 else ease
                if grade == 4:
                    multiplier *= cfg.easy_bonus
                interval = min(cfg.maximum_interval_days, max(1, round(interval * multiplier * cfg.interval_modifier)))
                due = when + timedelta(days=interval)
        else:
            raise ValueError(f"unsupported Anki Classic card state: {state}")

        updated = replace(
            card, state=state, step_index=step, interval_days=interval,
            ease_factor=round(ease, 4), due_at_utc=due.isoformat(),
            repetitions=reps, lapses=lapses,
        )
        return AnkiClassicReviewResult(
            scheduler=self.name, scheduler_version=self.version, rating=grade,
            reviewed_at_utc=when.isoformat(), due_at_utc=due.isoformat(),
            interval_seconds=(due - when).total_seconds(), actual_recall=grade != 1,
            mastery_awarded=False, prior_state=prior, resulting_state=updated.to_dict(),
        )
