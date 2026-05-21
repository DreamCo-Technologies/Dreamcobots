"""
DreamCo Platform — Strict Event Validator
==========================================

``EventValidator`` enforces the canonical event schema at the boundary where
events enter the bus.  An invalid event raises ``EventValidationError`` rather
than silently propagating bad data into analytics or Dream Brain ingestion.

Validation rules
----------------
1. ``event_id``  — non-empty string
2. ``timestamp`` — positive number (float/int Unix timestamp)
3. ``event_type`` — must match ``<family>.<action>`` format where family is one
   of the ten canonical families
4. ``source``    — non-empty string (field name used by DreamCoEvent)
5. ``severity``  — one of ``debug``, ``info``, ``warning``, ``error``,
   ``critical``
6. ``payload``   — must be a dict (not None)
"""

from __future__ import annotations

import re

from dreamco_platform.events.schema import DreamCoEvent, EventFamily

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VALID_FAMILIES: frozenset[str] = frozenset(f.value for f in EventFamily)
_VALID_SEVERITIES: frozenset[str] = frozenset(
    {"debug", "info", "warning", "error", "critical"}
)
_EVENT_TYPE_RE = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_.]*$")


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------

class EventValidationError(ValueError):
    """Raised when a ``DreamCoEvent`` fails schema validation."""


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class EventValidator:
    """Stateless validator for ``DreamCoEvent`` objects."""

    @classmethod
    def validate(cls, event: DreamCoEvent) -> None:
        """Raise ``EventValidationError`` if *event* violates the schema."""
        errors: list[str] = []

        # 1. event_id
        if not isinstance(event.event_id, str) or not event.event_id.strip():
            errors.append("event_id must be a non-empty string")

        # 2. timestamp — float/int Unix timestamp (positive)
        if not isinstance(event.timestamp, (float, int)) or event.timestamp <= 0:
            errors.append("timestamp must be a positive number (Unix timestamp)")

        # 3. event_type format
        if not isinstance(event.event_type, str):
            errors.append("event_type must be a string")
        elif not _EVENT_TYPE_RE.match(event.event_type):
            errors.append(
                f"event_type '{event.event_type}' must match pattern "
                f"'<family>.<action>' (e.g. 'workflow.started')"
            )
        else:
            family = event.event_type.split(".")[0]
            if family not in _VALID_FAMILIES:
                errors.append(
                    f"event_type family '{family}' is not a canonical family; "
                    f"must be one of {sorted(_VALID_FAMILIES)}"
                )

        # 4. source (DreamCoEvent uses 'source', not 'source_id')
        source = getattr(event, "source", None) or getattr(event, "source_id", None)
        if not isinstance(source, str) or not source.strip():
            errors.append("source must be a non-empty string")

        # 5. severity — optional field, only validate if present
        severity = getattr(event, "severity", None)
        if severity is not None and severity not in _VALID_SEVERITIES:
            errors.append(
                f"severity '{severity}' is invalid; "
                f"must be one of {sorted(_VALID_SEVERITIES)}"
            )

        # 6. payload
        if not isinstance(event.payload, dict):
            errors.append("payload must be a dict")

        if errors:
            raise EventValidationError(
                f"Event validation failed for event_type='{event.event_type}': "
                + "; ".join(errors)
            )

    @classmethod
    def is_valid(cls, event: DreamCoEvent) -> bool:
        """Return True if *event* passes all validation rules."""
        try:
            cls.validate(event)
            return True
        except EventValidationError:
            return False

    @classmethod
    def validation_errors(cls, event: DreamCoEvent) -> list[str]:
        """Return a list of validation error strings (empty → valid)."""
        try:
            cls.validate(event)
            return []
        except EventValidationError as exc:
            msg = str(exc)
            prefix = "]: "
            idx = msg.find(prefix)
            if idx != -1:
                return msg[idx + len(prefix) :].split("; ")
            return [msg]
