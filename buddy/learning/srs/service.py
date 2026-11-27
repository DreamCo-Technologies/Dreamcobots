"""Shared Buddy service for adaptive reviews, offline sync and mastery evidence."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from typing import Any

from .fsrs import FSRSAdapter, FSRSConfig
from .store import SRSStore


class BuddySRSService:
    """One learner/item schedule shared by every division membership."""

    def __init__(self, store: SRSStore, config: FSRSConfig | None = None) -> None:
        self.store = store
        self.config = config or FSRSConfig()

    def review_fsrs(
        self,
        *,
        event_id: str,
        learner_id: str,
        deck_id: str,
        item_id: str,
        division_ids: list[str],
        rating: int | str,
        reviewed_at: datetime,
        review_duration_ms: int | None = None,
        provenance: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        existing = self.store.get_review_event(event_id)
        if existing:
            return {"status": "duplicate", "event": existing}
        state = self.store.get_card_state(learner_id, deck_id, item_id)
        if state and state["replay_required"]:
            self.rebuild_card_state(learner_id, deck_id, item_id)
            state = self.store.get_card_state(learner_id, deck_id, item_id)
        adapter = FSRSAdapter(self.config)
        result = adapter.review(
            learner_id=learner_id,
            deck_id=deck_id,
            item_id=item_id,
            rating=rating,
            reviewed_at=reviewed_at,
            state_json=json.dumps(state["state"]) if state else None,
            review_duration_ms=review_duration_ms,
        )
        event = {
            "event_id": event_id,
            "learner_id": learner_id,
            "deck_id": deck_id,
            "item_id": item_id,
            "division_ids": division_ids,
            "scheduler_name": result.scheduler,
            "scheduler_version": result.scheduler_version,
            "rating": result.rating,
            "reviewed_at_utc": result.reviewed_at_utc,
            "due_at_utc": result.due_at_utc,
            "prior_state": result.prior_state,
            "resulting_state": result.resulting_state,
            "predicted_retrievability": result.predicted_retrievability,
            "actual_recall": result.actual_recall,
            "desired_retention": result.desired_retention,
            "parameter_set_id": result.parameter_set_id,
            "scheduler_config": result.scheduler_config,
            "provenance": {**(provenance or {}), "review_log": result.review_log},
        }
        recorded = self.store.record_review(event)
        return {
            "status": recorded.status,
            "review": asdict(result),
            "record": asdict(recorded),
        }

    def sync_offline_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Accept an immutable client event; stale arrivals mark state for replay."""
        return asdict(self.store.record_review(event))

    def rebuild_card_state(self, learner_id: str, deck_id: str, item_id: str) -> dict[str, Any]:
        events = self.store.list_review_events(learner_id, deck_id, item_id)
        if not events:
            raise ValueError("cannot rebuild a card without review history")
        state_json: str | None = None
        last_result = None
        divisions: set[str] = set()
        for event in events:
            if event["scheduler_name"] != "fsrs" or event["scheduler_version"] != "FSRS-6/py-fsrs-6.3.3":
                raise ValueError("automatic replay currently supports only pinned FSRS-6 history")
            config_data = json.loads(event["scheduler_config_json"] or "{}")
            if not config_data:
                raise ValueError("review history is missing its scheduler configuration")
            adapter = FSRSAdapter(FSRSConfig.from_scheduler_dict(config_data))
            last_result = adapter.review(
                learner_id=learner_id,
                deck_id=deck_id,
                item_id=item_id,
                rating=event["rating"],
                reviewed_at=datetime.fromisoformat(event["reviewed_at_utc"]),
                state_json=state_json,
            )
            state_json = json.dumps(last_result.resulting_state)
            divisions.update(json.loads(event["division_ids_json"]))
        assert last_result is not None
        latest = events[-1]
        self.store.commit_replayed_state(
            learner_id=learner_id,
            deck_id=deck_id,
            item_id=item_id,
            state=last_result.resulting_state,
            due_at_utc=last_result.due_at_utc,
            latest_event_id=latest["event_id"],
            division_ids=sorted(divisions),
            scheduler_name=last_result.scheduler,
            scheduler_version=last_result.scheduler_version,
            desired_retention=last_result.desired_retention,
            parameter_set_id=last_result.parameter_set_id,
        )
        return self.store.get_card_state(learner_id, deck_id, item_id) or {}

    def due_items(self, learner_id: str, now_utc: str, division_id: str | None = None) -> list[dict[str, Any]]:
        return self.store.due_items(learner_id, now_utc, division_id)

    def record_mastery_evidence(self, evidence: dict[str, Any]) -> str:
        return self.store.record_mastery_evidence(evidence)
