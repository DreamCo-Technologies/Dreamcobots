"""Adapter-neutral execution; no device takeover or implicit network access.

Construct adapters and grants inside an authenticated host, never from model or
HTTP request data. Pairing/authentication and permission prompts belong to that
host. A transport name alone never proves an action is supported.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from time import time
from typing import Callable, Protocol

from buddy.fleet_runtime.permissions import decide


@dataclass(frozen=True)
class Action:
    id: str
    instruction: str
    level: str = "external_side_effect"


class Adapter(Protocol):
    """Trusted adapter verifies outcomes and classifies risk, not the model."""
    id: str
    revision: str
    transport: str

    def discover(self) -> tuple[Action, ...]: ...
    def execute(self, action: str, arguments: dict) -> bool: ...


def fingerprint(adapter: Adapter, action: Action, arguments: dict) -> str:
    payload = [adapter.id, adapter.revision, action.id, action.level, arguments]
    return sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class Grant:
    """Host-issued, one-use approval for exact arguments, identity and revision."""
    digest: str
    expires_at: float


class Session:
    def __init__(self, adapter: Adapter, *, paired: Callable[[], bool],
                 emit: Callable[[dict], None], clock: Callable[[], float] = time):
        self.adapter, self.paired, self.emit, self.clock = adapter, paired, emit, clock
        self.stopped = False
        self.paused = False
        self._grants: set[Grant] = set()

    def approve(self, action_id: str, arguments: dict, ttl: float = 60) -> Grant:
        """Only the authenticated approval UI may call this after showing preview."""
        if not 0 < ttl <= 300:
            raise ValueError("Approval lifetime must be 1–300 seconds")
        if not self.paired():
            raise PermissionError("Pair this adapter first")
        action = self._action(action_id)
        if action is None:
            raise ValueError("Adapter does not advertise this action")
        grant = Grant(fingerprint(self.adapter, action, arguments), self.clock() + ttl)
        self._grants.add(grant)
        return grant

    def stop(self) -> None:
        self.stopped = True
        self._grants.clear()

    def _action(self, action_id: str) -> Action | None:
        actions = self.adapter.discover()
        if len({a.id for a in actions}) != len(actions):
            raise ValueError("Adapter advertised duplicate action IDs")
        return next((a for a in actions if a.id == action_id), None)

    def step(self, action_id: str, arguments: dict, *, mode: str = "watch",
             grant: Grant | None = None) -> dict:
        if mode not in {"watch", "guided"}:
            raise ValueError("Choose watch or guided mode")
        # Snapshot arguments: concurrent mutation must not change the approved action.
        arguments = json.loads(json.dumps(arguments, allow_nan=False))
        event = {"adapter": self.adapter.id, "action": action_id, "executed": False}
        def finish(status: str, instruction: str) -> dict:
            event.update(status=status, instruction=instruction)
            self.emit(dict(event))  # No arguments, tokens, model prompts or device IDs.
            return event
        if self.stopped or self.paused:
            return finish("stopped" if self.stopped else "paused", "Resume or start a new session.")
        if not self.paired():
            self._grants.clear()
            return finish("pairing_required", "Connect and authorize this app or device.")
        try:
            action = self._action(action_id)
            if action is None:
                return finish("guided", "Open the target app and demonstrate this step to Buddy.")
            if mode == "guided":
                return finish("guided", action.instruction)
            unattended = decide("sandbox", action.level)["allowed"]
            # Higher-risk operations retain existing secondary/release gates.
            if action.level not in {"read_only", "sandbox", "external_side_effect"}:
                return finish("host_gate_required", action.instruction)
            if not unattended:
                expected = fingerprint(self.adapter, action, arguments)
                if grant not in self._grants or grant is None or grant.expires_at <= self.clock() or grant.digest != expected:
                    return finish("approval_required", action.instruction)
                self._grants.remove(grant)  # Consume BEFORE attempting an external effect.
            self.emit({**event, "status": "running"})
            if self.stopped or self.paused or not self.paired():
                return finish("interrupted", action.instruction)
            event["executed"] = True
            verified = self.adapter.execute(action_id, arguments)
            return finish("verified" if verified is True else "needs_review", action.instruction)
        except Exception:
            # Adapter failures may contain secrets. Never auto-retry an uncertain write.
            return finish("needs_review", "Check the app's current state before continuing manually.")


def distill_observations(records: list[dict]) -> list[dict]:
    """Export authorized observable I/O, never private reasoning or model weights.

    This returns a dataset in memory; storage stays private in the calling host.
    Records require explicit data/teacher permission and training consent.
    """
    output = []
    for record in records:
        if not all(record.get(k) is True for k in
                   ("data_authorized", "teacher_terms_allow", "training_consent", "verified", "redacted")):
            continue
        if record.get("split") != "train":
            continue  # Evaluation/holdout data must never become training data.
        if not all(isinstance(record.get(k), str) and record[k].strip()
                   for k in ("source", "revision", "input", "output", "customization")):
            continue
        output.append({k: record[k] for k in
                       ("source", "revision", "input", "output", "customization")})
    return output
